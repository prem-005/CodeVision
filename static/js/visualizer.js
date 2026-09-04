// CodeVision - Real Code Execution Step Visualizer with Recursion Tree Support
let traceData = null;
let currentStepIdx = 0;
let isPlaying = false;
let playInterval = null;
let playbackSpeedMs = 1000;
let memoryView = 'cards';
let currentDecorations = [];

function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, char => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
    }[char]));
}

function formatMemoryValue(value) {
    if (!value) return '<span class="text-muted">None</span>';
    if (value.kind === 'reference') return `<span class="text-warning fw-bold">→ Object #${value.objectId.split('-').pop()}</span>`;
    if (value.value === null || value.value === undefined) return '<span class="text-muted">None</span>';
    return `<span class="text-info">${escapeHtml(value.value)}</span>`;
}

function renderMemoryCards(memory) {
    const objects = memory.objects || [];
    if (!objects || !objects.length) {
        return `
            <div class="p-3 text-center rounded border border-secondary font-monospace small" style="background: var(--bg-sidebar);">
                <i class="fa-solid fa-cube text-warning fs-5 mb-2 d-block"></i>
                <span class="text-light fw-bold">No Heap Objects Allocated</span>
                <p class="text-secondary mb-0 mt-1" style="font-size: 0.8rem;">
                    Local primitive variables (e.g. <code class="text-warning">n = 5</code>) reside on the <strong>Call Stack</strong>. Objects like lists, dicts, tuples, sets, and class instances will appear here dynamically when instantiated.
                </p>
            </div>
        `;
    }

    return objects.map(object => {
        let entries = '';
        if (object.elements && object.elements.length) {
            entries = object.elements.map(item => `
                <div class="d-flex justify-content-between py-1 border-bottom border-secondary-subtle">
                    <span class="text-secondary font-monospace">[${item.index}]</span>
                    <span class="font-monospace">${formatMemoryValue(item.value)}</span>
                </div>
            `).join('');
        } else if (object.fields && Object.keys(object.fields).length) {
            entries = Object.entries(object.fields).map(([name, value]) => `
                <div class="d-flex justify-content-between py-1 border-bottom border-secondary-subtle">
                    <span class="text-warning font-monospace">${escapeHtml(name)}</span>
                    <span class="font-monospace">${formatMemoryValue(value)}</span>
                </div>
            `).join('');
        } else {
            entries = '<div class="text-secondary small py-1">Empty Object</div>';
        }

        return `
            <div class="cv-card p-3 mb-2" style="background: var(--bg-card); border: 1px solid var(--border-highlight);">
                <div class="d-flex justify-content-between align-items-center border-bottom border-secondary pb-2 mb-2">
                    <strong class="text-light font-monospace"><i class="fa-solid fa-cube text-warning me-1"></i>${escapeHtml(object.label)}</strong>
                    <span class="badge bg-primary font-monospace">${escapeHtml(object.type)}</span>
                </div>
                <div class="text-secondary small font-monospace mb-2">Pointers & References: <strong class="text-warning">${object.referenceCount || 0}</strong></div>
                <div class="small font-monospace">${entries}</div>
            </div>
        `;
    }).join('');
}

function renderMemoryGraph(memory) {
    const objects = memory.objects || [];
    if (!objects || !objects.length) {
        return renderMemoryCards(memory);
    }
    const width = 480;
    const height = Math.max(180, objects.length * 90 + 40);
    const svg = [`<svg class="memory-graph-svg w-100" viewBox="0 0 ${width} ${height}" role="img" aria-label="Object reference graph">`];

    svg.push(`
        <defs>
            <marker id="memory-arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto">
                <path d="M0,0 L0,8 L8,4 z" fill="#f59e0b"/>
            </marker>
        </defs>
    `);

    objects.forEach((object, index) => {
        const y = 50 + index * 90;
        (object.references || []).forEach(ref => {
            const targetIndex = objects.findIndex(item => item.objectId === ref.objectId);
            if (targetIndex >= 0) {
                const targetY = 50 + targetIndex * 90;
                svg.push(`<line x1="240" y1="${y}" x2="240" y2="${targetY}" stroke="#f59e0b" stroke-width="2" marker-end="url(#memory-arrow)"/>`);
            }
        });

        svg.push(`
            <rect x="80" y="${y - 25}" width="320" height="50" rx="8" fill="#161b22" stroke="#2f3e5c" stroke-width="1.5"/>
            <text x="100" y="${y - 3}" fill="#f3f4f6" font-family="JetBrains Mono, monospace" font-size="13" font-weight="bold">${escapeHtml(object.label)} (${escapeHtml(object.type)})</text>
            <text x="100" y="${y + 16}" fill="#9ca3af" font-family="JetBrains Mono, monospace" font-size="11">refs: ${object.referenceCount || 0}</text>
        `);
    });

    svg.push('</svg>');
    return svg.join('');
}

// ===== HIERARCHICAL RECURSION TREE RENDERER =====
function renderRecursionTree(step) {
    const treeNodes = step.recursion_tree || [];
    if (!treeNodes || !treeNodes.length) {
        return `
            <div class="p-3 text-center rounded border border-secondary font-monospace small" style="background: var(--bg-sidebar);">
                <i class="fa-solid fa-sitemap text-warning fs-5 mb-2 d-block"></i>
                <span class="text-light fw-bold">No Recursive Calls Detected</span>
                <p class="text-secondary mb-0 mt-1" style="font-size: 0.8rem;">
                    When your code invokes recursive function calls (e.g. <code class="text-warning">factorial(5)</code> or <code class="text-warning">fib(4)</code>), a complete tree layout of all stack activation records will render here automatically.
                </p>
            </div>
        `;
    }

    // 1. Build node dictionary & children map
    const nodeMap = {};
    const childrenMap = {};
    treeNodes.forEach(n => {
        nodeMap[n.id] = { ...n, children: [] };
        childrenMap[n.id] = [];
    });

    let root = null;
    treeNodes.forEach(n => {
        if (!n.parentId) {
            root = nodeMap[n.id];
        } else if (childrenMap[n.parentId]) {
            childrenMap[n.parentId].push(nodeMap[n.id]);
        }
    });

    Object.keys(childrenMap).forEach(id => {
        if (nodeMap[id]) nodeMap[id].children = childrenMap[id];
    });

    // 2. Inorder layout traversal for zero overlaps
    const inorderList = [];
    function inorder(curr) {
        if (!curr) return;
        if (curr.children.length === 0) {
            inorderList.push(curr);
        } else {
            const mid = Math.floor(curr.children.length / 2);
            for (let i = 0; i < mid; i++) inorder(curr.children[i]);
            inorderList.push(curr);
            for (let i = mid; i < curr.children.length; i++) inorder(curr.children[i]);
        }
    }
    inorder(root);

    const nodeSpacing = 110;
    const width = Math.max(540, (inorderList.length + 1) * nodeSpacing);
    const maxDepth = Math.max(...treeNodes.map(n => n.depth || 0), 0);
    const height = Math.max(260, (maxDepth + 1) * 85 + 60);

    inorderList.forEach((n, idx) => {
        n.x = (idx + 1) * nodeSpacing;
        n.y = 45 + (n.depth || 0) * 80;
    });

    const activeId = step.active_call_id;

    // SVG elements
    const svg = [`<svg class="w-100" viewBox="0 0 ${width} ${height}" style="min-height: 240px;">`];

    // Edges
    Object.values(nodeMap).forEach(node => {
        if (node.parentId && nodeMap[node.parentId]) {
            const parent = nodeMap[node.parentId];
            svg.push(`<line x1="${parent.x}" y1="${parent.y + 18}" x2="${node.x}" y2="${node.y - 18}" stroke="#30363d" stroke-width="2"/>`);
        }
    });

    // Nodes
    Object.values(nodeMap).forEach(node => {
        const isActive = (node.id === activeId || (activeId && node.id === activeId));
        const isReturned = (node.status === 'returned');
        const borderColor = isActive ? '#f59e0b' : (isReturned ? '#10b981' : '#30363d');
        const bgColor = isActive ? 'rgba(245, 158, 11, 0.15)' : '#161b22';

        svg.push(`
            <g>
                <rect x="${node.x - 48}" y="${node.y - 18}" width="96" height="36" rx="6" fill="${bgColor}" stroke="${borderColor}" stroke-width="${isActive ? 2.5 : 1.5}"/>
                <text x="${node.x}" y="${node.y + 3}" fill="${isActive ? '#fbbf24' : (isReturned ? '#34d399' : '#f3f4f6')}" font-family="JetBrains Mono, monospace" font-size="11" font-weight="bold" text-anchor="middle">${escapeHtml(node.label)}</text>
                ${isReturned && node.returnVal !== null && node.returnVal !== undefined ? `<text x="${node.x}" y="${node.y + 30}" fill="#34d399" font-family="JetBrains Mono, monospace" font-size="10" font-weight="bold" text-anchor="middle">➜ ${escapeHtml(node.returnVal)}</text>` : ''}
            </g>
        `);
    });

    svg.push('</svg>');
    return svg.join('');
}

function renderMemory(memory, step) {
    const box = document.getElementById('memory-box');
    if (!box) return;

    if (memoryView === 'tree') {
        box.innerHTML = renderRecursionTree(step || {});
    } else if (memoryView === 'graph') {
        box.innerHTML = renderMemoryGraph(memory);
    } else {
        box.innerHTML = renderMemoryCards(memory);
    }
}

async function startCodeTrace(code, stdin, language = 'python') {
    const res = await CodeVision.api('/api/visualize', {
        method: 'POST',
        body: JSON.stringify({ code, stdin, language })
    });

    if (res.success && res.steps && res.steps.length > 0) {
        traceData = res.steps;
        currentStepIdx = 0;

        // Automatically switch memoryView to 'tree' if recursion is present!
        const hasRecursion = traceData.some(s => s.recursion_tree && s.recursion_tree.length > 1);
        if (hasRecursion) {
            memoryView = 'tree';
            const treeBtn = document.getElementById('memory-tree-btn');
            const cardsBtn = document.getElementById('memory-cards-btn');
            const graphBtn = document.getElementById('memory-graph-btn');
            treeBtn?.classList.add('cv-btn-primary');
            treeBtn?.classList.remove('cv-btn-secondary');
            cardsBtn?.classList.add('cv-btn-secondary');
            cardsBtn?.classList.remove('cv-btn-primary');
            graphBtn?.classList.add('cv-btn-secondary');
            graphBtn?.classList.remove('cv-btn-primary');
        }

        const slider = document.getElementById('step-slider');
        if (slider) {
            slider.max = traceData.length - 1;
            slider.value = 0;
        }
        renderTraceStep(0);
    } else {
        CodeVision.toast(res.error || 'Unable to trace code.', 'error');
    }
}

function renderTraceStep(idx) {
    if (!traceData || idx < 0 || idx >= traceData.length) return;
    currentStepIdx = idx;
    const step = traceData[idx];

    // Update Slider & Step counter
    const slider = document.getElementById('step-slider');
    if (slider) slider.value = idx;

    const counterEl = document.getElementById('step-counter');
    if (counterEl) counterEl.innerText = `Step ${idx + 1} / ${traceData.length}`;

    // Line Highlight in Monaco Editor
    const lineno = step.lineno || step.line || 1;
    if (typeof codeEditor !== 'undefined' && codeEditor && codeEditor.revealLineInCenter) {
        codeEditor.revealLineInCenter(lineno);
        codeEditor.setPosition({ lineNumber: lineno, column: 1 });
        currentDecorations = codeEditor.deltaDecorations(currentDecorations, [
            {
                range: new monaco.Range(lineno, 1, lineno, 1),
                options: {
                    isWholeLine: true,
                    className: 'exec-line-highlight',
                    linesDecorationsClassName: 'exec-line-gutter'
                }
            }
        ]);
    }

    // Variables Table
    const varTbody = document.getElementById('vars-tbody');
    if (varTbody) {
        varTbody.innerHTML = '';
        const keys = Object.keys(step.variables || {});
        if (keys.length === 0) {
            varTbody.innerHTML = '<tr><td colspan="4" class="text-secondary text-center py-3 font-monospace small">No local variables</td></tr>';
        } else {
            keys.forEach(k => {
                const item = step.variables[k];
                const reference = item.reference ? `<span class="text-warning fw-bold">→ #${item.reference.split('-').pop()}</span>` : '—';
                varTbody.innerHTML += `
                    <tr>
                        <td class="text-warning font-monospace fw-semibold">${escapeHtml(k)}</td>
                        <td class="text-info font-monospace">${escapeHtml(item.repr || item.value)}</td>
                        <td class="text-secondary small font-monospace">${escapeHtml(item.type)}</td>
                        <td class="text-info font-monospace">${reference}</td>
                    </tr>`;
            });
        }
    }

    // Call Stack
    const stackBox = document.getElementById('call-stack-box');
    if (stackBox) {
        stackBox.innerHTML = '';
        const stack = step.call_stack || ['main'];
        stack.forEach(fn => {
            stackBox.innerHTML += `<div class="call-stack-item"><i class="fas fa-layer-group me-2 text-warning"></i>${escapeHtml(fn)}()</div>`;
        });
    }

    renderMemory(step.memory || { objects: [] }, step);

    // Console Output
    const outBox = document.getElementById('console-output-box');
    if (outBox) {
        outBox.innerText = step.stdout || '(no output yet)';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const cardsButton = document.getElementById('memory-cards-btn');
    const graphButton = document.getElementById('memory-graph-btn');
    const treeButton = document.getElementById('memory-tree-btn');

    cardsButton?.addEventListener('click', () => {
        memoryView = 'cards';
        cardsButton.classList.add('cv-btn-primary'); cardsButton.classList.remove('cv-btn-secondary');
        graphButton?.classList.add('cv-btn-secondary'); graphButton?.classList.remove('cv-btn-primary');
        treeButton?.classList.add('cv-btn-secondary'); treeButton?.classList.remove('cv-btn-primary');
        if (traceData) renderTraceStep(currentStepIdx);
    });

    graphButton?.addEventListener('click', () => {
        memoryView = 'graph';
        graphButton.classList.add('cv-btn-primary'); graphButton.classList.remove('cv-btn-secondary');
        cardsButton?.classList.add('cv-btn-secondary'); cardsButton?.classList.remove('cv-btn-primary');
        treeButton?.classList.add('cv-btn-secondary'); treeButton?.classList.remove('cv-btn-primary');
        if (traceData) renderTraceStep(currentStepIdx);
    });

    treeButton?.addEventListener('click', () => {
        memoryView = 'tree';
        treeButton.classList.add('cv-btn-primary'); treeButton.classList.remove('cv-btn-secondary');
        cardsButton?.classList.add('cv-btn-secondary'); cardsButton?.classList.remove('cv-btn-primary');
        graphButton?.classList.add('cv-btn-secondary'); graphButton?.classList.remove('cv-btn-primary');
        if (traceData) renderTraceStep(currentStepIdx);
    });
});

function nextStep() {
    if (!traceData || currentStepIdx >= traceData.length - 1) return;
    renderTraceStep(currentStepIdx + 1);
}

function prevStep() {
    if (!traceData || currentStepIdx <= 0) return;
    renderTraceStep(currentStepIdx - 1);
}

function firstStep() {
    if (!traceData) return;
    renderTraceStep(0);
}

function lastStep() {
    if (!traceData) return;
    renderTraceStep(traceData.length - 1);
}

function togglePlay() {
    if (isPlaying) {
        pausePlay();
    } else {
        startPlay();
    }
}

function startPlay() {
    if (!traceData) return;
    isPlaying = true;
    const playBtn = document.getElementById('play-btn');
    if (playBtn) playBtn.innerHTML = '<i class="fas fa-pause"></i>';

    playInterval = setInterval(() => {
        if (currentStepIdx < traceData.length - 1) {
            nextStep();
        } else {
            pausePlay();
        }
    }, playbackSpeedMs);
}

function pausePlay() {
    isPlaying = false;
    if (playInterval) clearInterval(playInterval);
    const playBtn = document.getElementById('play-btn');
    if (playBtn) playBtn.innerHTML = '<i class="fas fa-play"></i>';
}
