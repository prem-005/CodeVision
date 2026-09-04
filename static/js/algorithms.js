// CodeVision - Universal DSA & Algorithm Visualizer Engine

let selectedDsaCategory = 'Sorting';
let selectedDsaAlgorithm = 'bubble_sort';
let selectedDsaSteps = [];
let selectedDsaStep = 0;
let selectedDsaTimer = null;
let selectedDsaSpeed = 1.0;

const dsaAlgorithms = {
    Sorting: [
        ['bubble_sort', 'Bubble Sort'],
        ['selection_sort', 'Selection Sort'],
        ['insertion_sort', 'Insertion Sort'],
        ['quick_sort', 'Quick Sort'],
        ['merge_sort', 'Merge Sort'],
        ['heap_sort', 'Heap Sort']
    ],
    Searching: [
        ['binary_search', 'Binary Search'],
        ['linear_search', 'Linear Search']
    ],
    Structures: [
        ['stack', 'Stack (LIFO)'],
        ['queue', 'Queue (FIFO)'],
        ['linked_list', 'Singly Linked List']
    ],
    Trees: [
        ['bst', 'Binary Search Tree (BST)'],
        ['min_heap', 'Min Heap'],
        ['max_heap', 'Max Heap']
    ],
    Graphs: [
        ['bfs', 'Breadth-First Search (BFS)'],
        ['dfs', 'Depth-First Search (DFS)'],
        ['dijkstra', "Dijkstra's Shortest Path"]
    ],
    Recursion: [
        ['factorial', 'Factorial Recursion'],
        ['fibonacci', 'Fibonacci Recursion']
    ],
    DP: [
        ['climbing_stairs', 'Climbing Stairs DP'],
        ['fibonacci_dp', 'Fibonacci DP Table']
    ]
};

// ===== 1. UNIVERSAL INPUT PARSER & VALIDATOR =====
const InputParser = {
    parse(inputStr) {
        const error = document.getElementById('dsaInputError');
        if (error) error.innerText = '';

        if (!inputStr || !inputStr.trim()) {
            if (error) error.innerText = 'Please enter input values.';
            return null;
        }

        const cleaned = inputStr.trim().replace(/[\[\]]/g, '');
        const tokens = cleaned.split(/[\s,]+/).filter(Boolean);

        if (tokens.length === 0) {
            if (error) error.innerText = 'Please enter at least one numeric value.';
            return null;
        }

        if (tokens.length > 100) {
            if (error) error.innerText = 'Maximum 100 values allowed.';
            return null;
        }

        const numbers = [];
        for (let i = 0; i < tokens.length; i++) {
            const num = Number(tokens[i]);
            if (!Number.isFinite(num)) {
                if (error) error.innerText = `Invalid number: "${tokens[i]}" at index ${i}`;
                return null;
            }
            numbers.push(num);
        }

        return numbers;
    }
};

// ===== 2. HIERARCHICAL TREE LAYOUT ENGINE (BST & HEAP) =====
const TreeLayoutEngine = {
    computeLayout(treeNodes) {
        if (!treeNodes || !treeNodes.length) return { nodes: [], width: 600, height: 300 };

        // 1. Build node dictionary
        const nodeMap = {};
        treeNodes.forEach(n => {
            nodeMap[n.id] = { ...n, leftChild: null, rightChild: null };
        });

        // 2. Attach left/right pointers based on isLeft flag
        let root = null;
        treeNodes.forEach(n => {
            if (!n.parentId) {
                root = nodeMap[n.id];
            } else {
                const parent = nodeMap[n.parentId];
                if (parent) {
                    if (n.isLeft) parent.leftChild = nodeMap[n.id];
                    else parent.rightChild = nodeMap[n.id];
                }
            }
        });

        // 3. Compute In-Order Traversal sequence to determine exact X coordinates (Guarantees 0 overlaps)
        const inorderList = [];
        function inorder(curr) {
            if (!curr) return;
            inorder(curr.leftChild);
            inorderList.push(curr);
            inorder(curr.rightChild);
        }
        inorder(root);

        const nodeSpacing = 65;
        const width = Math.max(620, (inorderList.length + 1) * nodeSpacing);
        const maxDepth = Math.max(...treeNodes.map(n => n.depth || 0), 0);
        const height = Math.max(340, (maxDepth + 1) * 90 + 60);

        inorderList.forEach((n, idx) => {
            n.x = (idx + 1) * nodeSpacing;
            n.y = 55 + (n.depth || 0) * 85;
        });

        return { nodes: Object.values(nodeMap), root, width, height };
    }
};

// ===== 3. DEDICATED RENDERERS =====

// A. Tree & BST Renderer
const BSTRenderer = {
    render(container, step) {
        const treeNodes = step.tree || [];
        if (!treeNodes.length) {
            container.innerHTML = '<div class="text-muted p-4">Empty Binary Search Tree</div>';
            return;
        }

        const layout = TreeLayoutEngine.computeLayout(treeNodes);
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('viewBox', `0 0 ${layout.width} ${layout.height}`);
        svg.classList.add('dsa-tree-svg');

        // Draw direct parent -> child edges
        layout.nodes.forEach(node => {
            if (node.parentId) {
                const parent = layout.nodes.find(p => p.id === node.parentId);
                if (parent) {
                    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    line.setAttribute('x1', parent.x);
                    line.setAttribute('y1', parent.y + 22);
                    line.setAttribute('x2', node.x);
                    line.setAttribute('y2', node.y - 22);
                    line.classList.add('dsa-tree-edge');
                    svg.appendChild(line);
                }
            }
        });

        // Draw node circles & values
        const highlightIds = step.highlight || [];
        layout.nodes.forEach(node => {
            const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');

            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', node.x);
            circle.setAttribute('cy', node.y);
            circle.setAttribute('r', 22);
            circle.classList.add('dsa-tree-node');
            if (highlightIds.includes(node.id) || highlightIds.includes(node.val)) {
                circle.classList.add('current');
            }

            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', node.x);
            text.setAttribute('y', node.y + 5);
            text.setAttribute('text-anchor', 'middle');
            text.textContent = node.val;

            g.append(circle, text);
            svg.appendChild(g);
        });

        container.innerHTML = '';
        container.appendChild(svg);

        // Display Traversals if present
        if (step.inorder) {
            const infoDiv = document.createElement('div');
            infoDiv.className = 'w-100 mt-3 p-3 rounded border border-secondary font-monospace small';
            infoDiv.style.background = 'var(--bg-sidebar)';
            infoDiv.innerHTML = `
                <div class="text-warning fw-bold mb-2"><i class="fa-solid fa-list-ol me-1"></i>BST Traversals</div>
                <div><span class="text-secondary">Inorder (Sorted):</span> <strong class="text-success">${step.inorder.join(' → ')}</strong></div>
                <div><span class="text-secondary">Preorder:</span> <strong class="text-info">${step.preorder.join(' → ')}</strong></div>
                <div><span class="text-secondary">Postorder:</span> <strong class="text-warning">${step.postorder.join(' → ')}</strong></div>
                <div><span class="text-secondary">Level-Order (BFS):</span> <strong class="text-light">${step.levelorder.join(' → ')}</strong></div>
            `;
            container.appendChild(infoDiv);
        }
    }
};

// B. Search Renderer (LOW, MID, HIGH Badges)
const SearchRenderer = {
    render(container, step) {
        const array = step.array || [];
        const low = step.low;
        const mid = step.mid;
        const high = step.high;

        const wrapper = document.createElement('div');
        wrapper.className = 'dsa-array-renderer d-flex align-items-end gap-3 justify-content-center py-4';

        array.forEach((val, i) => {
            const cell = document.createElement('div');
            cell.className = 'd-flex flex-column align-items-center gap-1';

            // Pointers badge row above element
            const pointers = [];
            if (i === low) pointers.push('<span class="badge bg-primary">LOW</span>');
            if (i === mid) pointers.push('<span class="badge bg-warning text-dark fw-bold">MID</span>');
            if (i === high) pointers.push('<span class="badge bg-danger">HIGH</span>');

            const ptrRow = document.createElement('div');
            ptrRow.style.height = '24px';
            ptrRow.innerHTML = pointers.join(' ');
            cell.appendChild(ptrRow);

            // Element box
            const box = document.createElement('div');
            box.className = 'dsa-stack-node px-3 py-2 rounded font-monospace fw-bold';
            if (i === mid) box.classList.add('current');
            if (step.found && i === mid) {
                box.style.background = 'rgba(16, 185, 129, 0.25)';
                box.style.borderColor = '#10b981';
                box.style.color = '#34d399';
            }
            box.innerText = val;
            cell.appendChild(box);

            // Index label
            const idxLabel = document.createElement('span');
            idxLabel.className = 'text-secondary small font-monospace';
            idxLabel.innerText = `[${i}]`;
            cell.appendChild(idxLabel);

            wrapper.appendChild(cell);
        });

        container.innerHTML = '';
        container.appendChild(wrapper);
    }
};

// C. Linked List Renderer (HEAD -> [10 | next] -> [20 | next] -> NULL)
const LinkedListRenderer = {
    render(container, step) {
        const array = step.array || [];
        const wrapper = document.createElement('div');
        wrapper.className = 'd-flex align-items-center gap-2 overflow-auto p-4';

        wrapper.innerHTML = '<span class="badge bg-warning text-dark font-monospace me-2">HEAD</span>';

        array.forEach((val, i) => {
            const isHighlight = (step.highlight || []).includes(i);
            const node = document.createElement('div');
            node.className = `dsa-list-node rounded p-2 ${isHighlight ? 'current' : ''}`;
            node.innerHTML = `<strong>${val}</strong><small class="text-secondary ms-1">next</small>`;
            wrapper.appendChild(node);

            if (i < array.length - 1) {
                const arrow = document.createElement('span');
                arrow.className = 'text-info fs-4 fw-bold px-1';
                arrow.innerText = '→';
                wrapper.appendChild(arrow);
            }
        });

        wrapper.insertAdjacentHTML('beforeend', '<span class="text-secondary font-monospace ms-2 fs-5">→ NULL</span>');
        container.innerHTML = '';
        container.appendChild(wrapper);
    }
};

// D. Stack Renderer (Vertical TOP pointer)
const StackRenderer = {
    render(container, step) {
        const array = step.array || [];
        const wrapper = document.createElement('div');
        wrapper.className = 'd-flex flex-column align-items-center justify-content-end h-100 py-3';

        wrapper.innerHTML = '<span class="badge bg-warning text-dark font-monospace mb-2">TOP ↑</span>';

        const stackBox = document.createElement('div');
        stackBox.className = 'dsa-stack-renderer rounded p-2 w-50';

        [...array].reverse().forEach((val, i) => {
            const isTop = (i === 0);
            const item = document.createElement('div');
            item.className = `dsa-stack-node rounded mb-1 p-2 text-center font-monospace fw-bold ${isTop ? 'current' : ''}`;
            item.innerText = val;
            stackBox.appendChild(item);
        });

        wrapper.appendChild(stackBox);
        wrapper.insertAdjacentHTML('beforeend', `<span class="text-secondary small font-monospace mt-2">SIZE: ${array.length}</span>`);

        container.innerHTML = '';
        container.appendChild(wrapper);
    }
};

// E. Queue Renderer (FRONT ... REAR)
const QueueRenderer = {
    render(container, step) {
        const array = step.array || [];
        const wrapper = document.createElement('div');
        wrapper.className = 'd-flex flex-column align-items-center justify-content-center h-100 p-4';

        const labelRow = document.createElement('div');
        labelRow.className = 'd-flex justify-content-between w-100 mb-2 font-monospace small';
        labelRow.innerHTML = '<span class="badge bg-success">FRONT</span><span class="badge bg-info">REAR</span>';
        wrapper.appendChild(labelRow);

        const qBox = document.createElement('div');
        qBox.className = 'd-flex align-items-center gap-2 border-bottom border-secondary pb-3 w-100 overflow-auto justify-content-center';

        array.forEach((val, i) => {
            const isFront = (i === 0);
            const item = document.createElement('div');
            item.className = `dsa-queue-node rounded p-3 text-center font-monospace fw-bold ${isFront ? 'current' : ''}`;
            item.innerText = val;
            qBox.appendChild(item);
        });

        wrapper.appendChild(qBox);
        wrapper.insertAdjacentHTML('beforeend', `<span class="text-secondary small font-monospace mt-3">SIZE: ${array.length}</span>`);

        container.innerHTML = '';
        container.appendChild(wrapper);
    }
};

// F. Heap Renderer (Synchronized Tree + Array)
const HeapRenderer = {
    render(container, step) {
        const array = step.array || [];
        container.innerHTML = '';

        if (!array.length) {
            container.innerHTML = '<div class="text-muted p-4">Empty Heap</div>';
            return;
        }

        // 1. Build Heap Tree Nodes
        const treeNodes = array.map((val, i) => {
            const depth = Math.floor(Math.log2(i + 1));
            const parentIdx = i > 0 ? Math.floor((i - 1) / 2) : null;
            return {
                id: `heap-${i}`,
                val: val,
                parentId: parentIdx !== null ? `heap-${parentIdx}` : None,
                isLeft: (i % 2 !== 0),
                depth: depth
            };
        });

        const treeStep = { tree: treeNodes, highlight: (step.highlight || []).map(idx => `heap-${idx}`) };

        // Top Tree View
        const treeBox = document.createElement('div');
        treeBox.className = 'w-100';
        BSTRenderer.render(treeBox, treeStep);
        container.appendChild(treeBox);

        // Bottom Array View
        const arrBox = document.createElement('div');
        arrBox.className = 'w-100 mt-4 p-3 rounded border border-secondary';
        arrBox.style.background = 'var(--bg-sidebar)';

        let arrHtml = '<div class="text-warning small font-monospace fw-bold mb-2"><i class="fa-solid fa-table-cells me-1"></i>Heap Array Representation</div><div class="d-flex gap-2 justify-content-center">';
        array.forEach((val, i) => {
            const isHl = (step.highlight || []).includes(i);
            arrHtml += `
                <div class="d-flex flex-column align-items-center">
                    <div class="dsa-stack-node px-3 py-1 rounded font-monospace ${isHl ? 'current' : ''}">${val}</div>
                    <span class="text-secondary small font-monospace mt-1">[${i}]</span>
                </div>
            `;
        });
        arrHtml += '</div>';
        arrBox.innerHTML = arrHtml;
        container.appendChild(arrBox);
    }
};

// G. Graph Renderer (BFS / DFS / Dijkstra)
const GraphRenderer = {
    render(container, step) {
        const nodes = step.nodes || ['A', 'B', 'C', 'D', 'E'];
        const edges = step.edges || [];
        const current = step.current;
        const visited = step.visited || [];

        const width = 580;
        const height = 300;
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
        svg.classList.add('dsa-graph-svg');

        // Circular Layout for Graph Nodes
        const radius = 100;
        const cx = width / 2;
        const cy = height / 2;
        const nodePos = {};

        nodes.forEach((n, idx) => {
            const angle = (idx / nodes.length) * 2 * Math.PI - Math.PI / 2;
            nodePos[n] = {
                x: cx + radius * Math.cos(angle),
                y: cy + radius * Math.sin(angle)
            };
        });

        // Draw Edges
        edges.forEach(e => {
            const uPos = nodePos[e.from];
            const vPos = nodePos[e.to];
            if (uPos && vPos) {
                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.setAttribute('x1', uPos.x); line.setAttribute('y1', uPos.y);
                line.setAttribute('x2', vPos.x); line.setAttribute('y2', vPos.y);
                line.classList.add('dsa-graph-edge');
                svg.appendChild(line);

                if (e.weight) {
                    const midX = (uPos.x + vPos.x) / 2;
                    const midY = (uPos.y + vPos.y) / 2;
                    const wText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                    wText.setAttribute('x', midX); wText.setAttribute('y', midY - 5);
                    wText.setAttribute('fill', '#f59e0b'); wText.setAttribute('font-size', '11');
                    wText.setAttribute('text-anchor', 'middle');
                    wText.textContent = e.weight;
                    svg.appendChild(wText);
                }
            }
        });

        // Draw Nodes
        nodes.forEach(n => {
            const pos = nodePos[n];
            const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', pos.x); circle.setAttribute('cy', pos.y); circle.setAttribute('r', 24);
            circle.classList.add('dsa-graph-node');
            if (n === current) circle.classList.add('current');
            if (visited.includes(n)) circle.style.stroke = '#10b981';

            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', pos.x); text.setAttribute('y', pos.y + 5);
            text.setAttribute('text-anchor', 'middle'); text.textContent = n;
            g.append(circle, text);
            svg.appendChild(g);
        });

        container.innerHTML = '';
        container.appendChild(svg);

        // Queue / Stack state bar below graph
        if (step.queue || step.stack || step.distances) {
            const info = document.createElement('div');
            info.className = 'w-100 mt-2 p-2 rounded border border-secondary font-monospace small';
            info.style.background = 'var(--bg-sidebar)';
            let stateStr = '';
            if (step.queue) stateStr += `Queue: [${step.queue.join(', ')}] | `;
            if (step.stack) stateStr += `Stack: [${step.stack.join(', ')}] | `;
            if (step.distances) stateStr += `Distances: ${JSON.stringify(step.distances)}`;
            info.innerHTML = `<span class="text-info">${stateStr}</span>`;
            container.appendChild(info);
        }
    }
};

// H. Sorting Renderer
const SortingRenderer = {
    render(container, step) {
        const array = step.array || [];
        const maxVal = Math.max(...array.map(v => Math.abs(v)), 1);

        const wrapper = document.createElement('div');
        wrapper.className = 'dsa-array-renderer';

        array.forEach((val, i) => {
            const bar = document.createElement('div');
            bar.className = 'dsa-bar';
            bar.style.height = `${Math.max(16, Math.abs(val) / maxVal * 240)}px`;
            if ((step.highlight || []).includes(i)) bar.classList.add('highlight');
            if ((step.sorted || []).includes(i)) bar.classList.add('sorted');
            bar.innerText = val;

            const cell = document.createElement('div');
            cell.className = 'dsa-indexed-cell';
            cell.innerHTML = `<span class="dsa-index">${i}</span>`;
            cell.appendChild(bar);
            wrapper.appendChild(cell);
        });

        container.innerHTML = '';
        container.appendChild(wrapper);
    }
};

// ===== 4. DISPATCHER & CONTROL ENGINE =====

function onCategoryChange() {
    selectedDsaCategory = document.getElementById('dsaCategorySelect').value;
    const select = document.getElementById('algoSelect');
    select.innerHTML = '';
    (dsaAlgorithms[selectedDsaCategory] || []).forEach(([val, label]) => {
        select.add(new Option(label, val));
    });

    const targetGroup = document.getElementById('targetInputGroup');
    if (targetGroup) targetGroup.classList.toggle('d-none', selectedDsaCategory !== 'Searching');

    initSelectedAlgorithm();
}

function initSelectedAlgorithm() {
    selectedDsaAlgorithm = document.getElementById('algoSelect').value;
    const labels = {
        bubble_sort: ['O(N²)', 'O(1)'], selection_sort: ['O(N²)', 'O(1)'], insertion_sort: ['O(N²)', 'O(1)'],
        quick_sort: ['O(N log N)', 'O(log N)'], merge_sort: ['O(N log N)', 'O(N)'], heap_sort: ['O(N log N)', 'O(1)'],
        binary_search: ['O(log N)', 'O(1)'], linear_search: ['O(N)', 'O(1)'],
        bst: ['O(log N)', 'O(N)'], min_heap: ['O(log N)', 'O(N)'], max_heap: ['O(log N)', 'O(N)'],
        bfs: ['O(V + E)', 'O(V)'], dfs: ['O(V + E)', 'O(V)'], dijkstra: ['O((V+E) log V)', 'O(V)'],
        stack: ['O(1)', 'O(N)'], queue: ['O(1)', 'O(N)'], linked_list: ['O(N)', 'O(N)']
    }[selectedDsaAlgorithm] || ['O(N)', 'O(N)'];

    const compTime = document.getElementById('compTime');
    const compSpace = document.getElementById('compSpace');
    if (compTime) compTime.innerText = labels[0];
    if (compSpace) compSpace.innerText = labels[1];

    const canvasTitle = document.getElementById('canvasTitle');
    if (canvasTitle) {
        const titleText = document.getElementById('algoSelect').selectedOptions[0]?.text || 'Visualization';
        canvasTitle.innerHTML = `<i class="fa-solid fa-chart-column me-2 text-warning"></i>${titleText}`;
    }

    resetAlgorithmAnimation();
}

async function startAlgorithmAnimation() {
    clearInterval(selectedDsaTimer);
    selectedDsaSteps = [];

    const inputData = document.getElementById('dsaInputData').value;
    const values = InputParser.parse(inputData);
    if (!values) return;

    if (selectedDsaCategory === 'Trees') {
        if (selectedDsaAlgorithm === 'bst') {
            const res = await CodeVision.api('/api/visualizer/bst', { method: 'POST', body: JSON.stringify({ array: values }) });
            selectedDsaSteps = res.success ? res.data.steps : [];
        } else {
            const res = await CodeVision.api('/api/visualizer/heap', { method: 'POST', body: JSON.stringify({ array: values, type: selectedDsaAlgorithm.split('_')[0] }) });
            selectedDsaSteps = res.success ? res.data.steps : [];
        }
    } else if (selectedDsaCategory === 'Searching') {
        const targetVal = Number(document.getElementById('dsaTargetVal').value || 34);
        const res = await CodeVision.api('/api/visualizer/searching', { method: 'POST', body: JSON.stringify({ algorithm: selectedDsaAlgorithm, array: values, target: targetVal }) });
        selectedDsaSteps = res.success ? res.data.steps : [];
    } else if (selectedDsaCategory === 'Graphs') {
        const res = await CodeVision.api('/api/visualizer/graph', { method: 'POST', body: JSON.stringify({ algorithm: selectedDsaAlgorithm }) });
        selectedDsaSteps = res.success ? res.data.steps : [];
    } else if (selectedDsaCategory === 'Sorting') {
        const res = await CodeVision.api('/api/visualizer/sorting', { method: 'POST', body: JSON.stringify({ algorithm: selectedDsaAlgorithm, array: values }) });
        selectedDsaSteps = res.success ? res.data.steps : [];
    } else {
        // Linear Data Structures (Stack, Queue, Linked List)
        selectedDsaSteps = values.map((val, idx) => ({
            step: idx + 1,
            array: values.slice(0, idx + 1),
            highlight: [idx],
            action: `Pushed/Inserted ${val} into ${selectedDsaAlgorithm}`
        }));
    }

    selectedDsaStep = 0;
    renderSelectedDsaStep();

    selectedDsaTimer = setInterval(() => {
        if (selectedDsaStep >= selectedDsaSteps.length - 1) {
            return clearInterval(selectedDsaTimer);
        }
        selectedDsaStep += 1;
        renderSelectedDsaStep();
    }, 800 / selectedDsaSpeed);
}

function renderSelectedDsaStep() {
    const step = selectedDsaSteps[selectedDsaStep];
    if (!step) return;

    const container = document.getElementById('dsaCanvasContainer') || document.getElementById('dsa-canvas');
    if (!container) return;

    if (selectedDsaCategory === 'Trees' && selectedDsaAlgorithm === 'bst') {
        BSTRenderer.render(container, step);
    } else if (selectedDsaCategory === 'Trees') {
        HeapRenderer.render(container, step);
    } else if (selectedDsaCategory === 'Searching') {
        SearchRenderer.render(container, step);
    } else if (selectedDsaCategory === 'Graphs') {
        GraphRenderer.render(container, step);
    } else if (selectedDsaAlgorithm === 'stack') {
        StackRenderer.render(container, step);
    } else if (selectedDsaAlgorithm === 'queue') {
        QueueRenderer.render(container, step);
    } else if (selectedDsaAlgorithm === 'linked_list') {
        LinkedListRenderer.render(container, step);
    } else {
        SortingRenderer.render(container, step);
    }

    updateDsaStats(step);
}

function updateDsaStats(step) {
    const logText = document.getElementById('dsaLogText') || document.getElementById('dsa-action-text');
    if (logText) logText.innerText = step.action || 'Ready';

    const statusBadge = document.getElementById('dsaStatusBadge');
    if (statusBadge) statusBadge.innerText = `${selectedDsaStep + 1} / ${selectedDsaSteps.length}`;

    const comparisons = document.getElementById('statComparisons');
    if (comparisons) comparisons.innerText = step.comparisons || 0;

    const swaps = document.getElementById('statSwaps');
    if (swaps) swaps.innerText = step.swaps || 0;
}

function resetAlgorithmAnimation() {
    clearInterval(selectedDsaTimer);
    selectedDsaSteps = [];
    selectedDsaStep = 0;
    const values = InputParser.parse(document.getElementById('dsaInputData').value);
    if (values) {
        selectedDsaSteps = [{ array: values, tree: [], action: 'Ready to start visualization.' }];
        renderSelectedDsaStep();
    }
}

function loadDsaExample() {
    const inputData = document.getElementById('dsaInputData');
    if (inputData) inputData.value = '45, 12, 89, 34, 67, 23, 90, 11';
    resetAlgorithmAnimation();
}

function clearDsaInput() {
    const inputData = document.getElementById('dsaInputData');
    if (inputData) inputData.value = '';
    const error = document.getElementById('dsaInputError');
    if (error) error.innerText = '';
    clearInterval(selectedDsaTimer);
    selectedDsaSteps = [];
    const container = document.getElementById('dsaCanvasContainer');
    if (container) container.innerHTML = '';
    const logText = document.getElementById('dsaLogText');
    if (logText) logText.innerText = 'Enter input to start visualization.';
    const statusBadge = document.getElementById('dsaStatusBadge');
    if (statusBadge) statusBadge.innerText = 'Ready';
}

function generateRandomData() {
    const inputData = document.getElementById('dsaInputData');
    if (inputData) inputData.value = Array.from({ length: 8 }, () => Math.floor(Math.random() * 90) + 10).join(', ');
    resetAlgorithmAnimation();
}

function updateDsaSpeed(val) {
    selectedDsaSpeed = Number(val);
    const speedLabel = document.getElementById('speedLabel');
    if (speedLabel) speedLabel.innerText = `${selectedDsaSpeed.toFixed(2)}x`;
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('dsaCategorySelect')) {
        onCategoryChange();
        const inputData = document.getElementById('dsaInputData');
        if (inputData) {
            inputData.addEventListener('keydown', event => {
                if (event.ctrlKey && event.key === 'Enter') startAlgorithmAnimation();
            });
        }
    }
});
