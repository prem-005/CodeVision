/* =========================================================
   TIME MACHINE — static/js/time_machine.js
   ========================================================= */
"use strict";

let tmTrace = [], tmVarHistory = {}, tmCurrentStep = 0;
let tmPlaying = false, tmPlayTimer = null;
let tmEditor = null, tmLineHandle = null;

const DEFAULT_CODE = `def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)

result = factorial(5)
print("factorial(5) =", result)
`;

document.addEventListener("DOMContentLoaded", () => {
    initEditor(); bindControls(); bindKeyboard(); bindInspectorTabs(); bindVizTabs();
});

function initEditor() {
    tmEditor = CodeMirror(document.getElementById("tm-code-cm"), {
        value: DEFAULT_CODE, mode: "python", theme: "dracula",
        lineNumbers: true, lineWrapping: false, indentUnit: 4, tabSize: 4,
        extraKeys: { "Ctrl-Enter": runCode }
    });
}

async function runCode() {
    const code = tmEditor.getValue(), stdin = document.getElementById("tm-custom-input").value.trim();
    const btn = document.getElementById("tm-run-btn");
    if (!code.trim()) { showError("Please enter some code."); return; }
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Running...'; btn.disabled = true; hideError();
    try {
        const res  = await fetch("/code-lab/api/time-machine/trace", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ code, stdin }) });
        const data = await res.json();
        if (!data.success) { showError(data.error || "Execution failed."); return; }
        tmTrace = data.steps || []; tmVarHistory = data.variable_history || {};
        tmCurrentStep = 0; initTimeline(); goToStep(0);
        document.getElementById("tm-diff-btn").disabled = false;
    } catch (e) { showError("Network error: " + e.message); }
    finally { btn.innerHTML = '<i class="fas fa-play me-1"></i>Run'; btn.disabled = false; }
}

function initTimeline() {
    const s = document.getElementById("tm-slider");
    s.min = 0; s.max = Math.max(0, tmTrace.length - 1); s.value = 0;
    s.disabled = tmTrace.length === 0;
}

function goToStep(idx) {
    if (!tmTrace.length) return;
    idx = Math.max(0, Math.min(idx, tmTrace.length - 1));
    const prev = tmCurrentStep; tmCurrentStep = idx;
    document.getElementById("tm-slider").value = idx;
    document.getElementById("tm-step-label").textContent = "Step " + (idx+1) + " / " + tmTrace.length;
    const s = tmTrace[idx];
    renderCodeHighlight(s); renderEventBadges(s); renderVariables(s);
    renderCallStack(s); renderOutput(s); renderVisualization(s); renderWhatChanged(prev, idx);
}

function renderCodeHighlight(step) {
    if (!tmEditor || !step) return;
    if (tmLineHandle) tmEditor.removeLineClass(tmLineHandle, "background", "cm-highlight-line");
    const ln = (step.lineno || 1) - 1;
    if (ln >= 0 && ln < tmEditor.lineCount()) {
        tmLineHandle = tmEditor.addLineClass(ln, "background", "cm-highlight-line");
        tmEditor.scrollIntoView({ line: ln, ch: 0 }, 60);
    }
    const lb = document.getElementById("tm-line-badge");
    lb.style.display = ""; lb.textContent = "Line " + (step.lineno || "-");
}

function renderEventBadges(step) {
    const ev = step.event || "line";
    const cls = { call:"ev-call", line:"ev-line", return:"ev-return", exception:"ev-exception" }[ev] || "ev-line";
    document.getElementById("tm-event-badges").innerHTML =
        '<span class="step-event-badge ' + cls + '">' + ev.toUpperCase() + "</span>";
}

function renderVariables(step) {
    const vars = step.variables || {}, cont = document.getElementById("inspector-vars");
    const entries = Object.entries(vars);
    if (!entries.length) { cont.innerHTML = '<div class="text-muted small text-center mt-3">No variables in scope</div>'; return; }
    cont.innerHTML = entries.map(([name, info]) =>
        '<div class="var-row" onclick="openVarHistory(\'' + name + '\')">' +
        '<span class="var-name">' + esc(name) + '</span>' +
        '<span class="var-val">' + esc(String(info.value ?? "")) + '</span>' +
        '<span class="var-type">' + esc(info.type || "") + '</span></div>'
    ).join("");
}

function renderCallStack(step) {
    const stack = step.call_stack || [], cont = document.getElementById("inspector-stack");
    if (!stack.length) { cont.innerHTML = '<div class="text-muted small text-center mt-3">Empty call stack</div>'; return; }
    cont.innerHTML = [...stack].reverse().map((fn, i) =>
        '<div class="cs-frame ' + (i === 0 ? "active" : "") + '">' +
        '<span class="text-warning">' + (i === 0 ? "→" : " ") + '</span>' +
        '<span class="ms-2">' + esc(fn) + '()</span></div>'
    ).join("");
}

function renderOutput(step) {
    const out = step.stdout || "";
    document.getElementById("tm-output-display").textContent = out || "(no output yet)";
    document.getElementById("viz-output").innerHTML = '<pre class="tm-output">' + esc(out || "(no output yet)") + "</pre>";
}

function renderVisualization(step) {
    const tree = step.recursion_tree || [];
    const autoEl = document.getElementById("viz-auto"), recEl = document.getElementById("viz-recursion"), memEl = document.getElementById("viz-memory");
    if (tree.length > 0) { const svg = buildRecursionTreeSVG(tree, step.active_call_id); autoEl.innerHTML = svg; recEl.innerHTML = svg; }
    else { autoEl.innerHTML = buildMemoryHTML(step.memory || { objects: [] }); }
    memEl.innerHTML = buildMemoryHTML(step.memory || { objects: [] });
}

function buildRecursionTreeSVG(nodes, activeCallId) {
    if (!nodes || !nodes.length) return '<div class="text-muted small">No recursion tree</div>';
    const byId = {}, childrenOf = {};
    nodes.forEach(n => { byId[n.id] = n; });
    nodes.forEach(n => { if (n.parentId) { if (!childrenOf[n.parentId]) childrenOf[n.parentId] = []; childrenOf[n.parentId].push(n.id); } });
    const roots = nodes.filter(n => !n.parentId || !byId[n.parentId]);
    const levels = []; let queue = roots.map(n => ({ id: n.id, depth: 0 }));
    while (queue.length) { const { id, depth } = queue.shift(); if (!levels[depth]) levels[depth] = []; levels[depth].push(id); (childrenOf[id] || []).forEach(cid => queue.push({ id: cid, depth: depth + 1 })); }
    const R = 28, DX = 90, DY = 80, posOf = {};
    levels.forEach((lvl, depth) => { const total = lvl.length; lvl.forEach((id, i) => { posOf[id] = { x: (i - (total-1)/2)*DX + 300, y: 50 + depth*DY }; }); });
    const W = Math.max(600, Math.max(...Object.values(posOf).map(p => p.x + R + 20)));
    const H = levels.length * DY + 100;
    let edges = "", nodesSVG = "";
    nodes.forEach(n => {
        const p = posOf[n.id]; if (!p) return;
        if (n.parentId && posOf[n.parentId]) { const pp = posOf[n.parentId]; edges += '<line x1="'+pp.x+'" y1="'+(pp.y+R)+'" x2="'+p.x+'" y2="'+(p.y-R)+'" class="rtree-link"/>'; }
        const isActive = n.id === activeCallId, isRet = n.status === "returned";
        const nc = isActive ? "rtree-node active" : isRet ? "rtree-node returned" : "rtree-node";
        const lbl = (n.label || n.fnName || "").substring(0, 12);
        const retLbl = isRet && n.returnVal !== null ? " ↩ " + n.returnVal : "";
        nodesSVG += '<g class="' + nc + '"><circle cx="'+p.x+'" cy="'+p.y+'" r="'+R+'"/><text x="'+p.x+'" y="'+p.y+'" style="font-size:10px">'+esc(lbl)+'</text>' + (retLbl ? '<text x="'+p.x+'" y="'+(p.y+R+13)+'" style="font-size:9px;fill:#22c55e;text-anchor:middle">'+esc(retLbl)+'</text>' : '') + '</g>';
    });
    return '<svg width="'+W+'" height="'+H+'" style="overflow:visible"><g>'+edges+'</g><g>'+nodesSVG+'</g></svg>';
}

function buildMemoryHTML(memory) {
    const objs = memory.objects || [];
    if (!objs.length) return '<div class="text-muted small text-center mt-4"><i class="fas fa-database fa-2x mb-2 d-block"></i>No heap objects in scope</div>';
    return objs.map(obj => {
        let inner = "";
        if (obj.elements && obj.elements.length) inner = obj.elements.map(e => '<span class="badge me-1 mb-1" style="background:rgba(255,255,255,.07);color:#e2e8f0;">['+e.index+'] '+esc(JSON.stringify(e.value && e.value.value !== undefined ? e.value.value : e.value))+"</span>").join("");
        else if (obj.fields) inner = Object.entries(obj.fields).map(([k,v]) => '<div style="font-size:.75rem;padding:.2rem 0;border-bottom:1px solid rgba(255,255,255,.04);"><span class="text-warning">'+esc(k)+'</span>: <span class="text-secondary ms-1">'+esc(JSON.stringify(v && v.value !== undefined ? v.value : v))+"</span></div>").join("");
        return '<div style="background:var(--bg-main);border:1px solid var(--border-color);border-radius:8px;padding:.75rem;margin-bottom:.75rem;min-width:180px;"><div style="font-size:.72rem;font-weight:700;color:var(--primary-accent);margin-bottom:.4rem;">'+esc(obj.label||obj.objectId)+' <span style="color:var(--text-muted);font-weight:400;">'+esc(obj.type)+'</span></div>'+inner+'</div>';
    }).join("");
}

function renderWhatChanged(prevIdx, curIdx) {
    const cont = document.getElementById("inspector-changed");
    if (prevIdx === curIdx || !tmTrace.length) { cont.innerHTML = '<div class="text-muted small text-center mt-3">Move the timeline to see changes</div>'; return; }
    const changes = diffSteps(tmTrace[prevIdx], tmTrace[curIdx]);
    if (!changes.length) { cont.innerHTML = '<div class="text-muted small text-center mt-3">No state changes detected</div>'; return; }
    cont.innerHTML = changes.map(c => '<div class="wc-item"><i class="fas fa-check-circle wc-icon"></i><span><span class="wc-cat">'+esc(c.category)+':</span> '+esc(c.description)+'</span></div>').join("");
}

function diffSteps(a, b) {
    if (!a || !b) return [];
    const changes = [];
    if (a.lineno !== b.lineno) changes.push({ category: "Line", description: a.lineno + " → " + b.lineno + ": " + (b.code || "").trim() });
    const va = a.variables || {}, vb = b.variables || {};
    [...new Set([...Object.keys(va), ...Object.keys(vb)])].forEach(k => {
        const v1 = va[k] && va[k].value, v2 = vb[k] && vb[k].value;
        if (v1 !== v2) {
            if (!(k in va)) changes.push({ category: "Created", description: "`"+k+"` = "+v2 });
            else if (!(k in vb)) changes.push({ category: "Removed", description: "`"+k+"`" });
            else changes.push({ category: "Variable", description: "`"+k+"`: "+v1+" → "+v2 });
        }
    });
    const sa = a.call_stack || [], sb = b.call_stack || [];
    if (sa.length < sb.length) changes.push({ category: "Call Stack", description: "Push → " + sb[sb.length-1] + "()" });
    else if (sa.length > sb.length) changes.push({ category: "Call Stack", description: "Pop ← " + sa[sa.length-1] + "()" });
    if ((a.stdout||"") !== (b.stdout||"")) changes.push({ category: "Output", description: (b.stdout||"").trim().slice(-80) });
    return changes;
}

window.openVarHistory = function(varName) {
    const hist = tmVarHistory[varName] || [];
    document.getElementById("varHistTitle").textContent = "Variable History: " + varName;
    document.getElementById("varHistBody").innerHTML = hist.length ? hist.map(h =>
        '<div class="hist-item" onclick="goToStep('+(h.step-1)+'); bootstrap.Modal.getInstance(document.getElementById(\'varHistoryModal\')).hide();">' +
        '<span class="hist-step">Step '+h.step+'</span><span class="hist-val">'+esc(String(h.value ?? ""))+'</span><span class="text-muted small">'+esc(h.type||"")+"</span></div>"
    ).join("") : '<div class="text-muted small">No history available.</div>';
    new bootstrap.Modal(document.getElementById("varHistoryModal")).show();
};

document.getElementById("tm-diff-btn").addEventListener("click", () => {
    document.getElementById("diff-step-a").value = tmCurrentStep + 1;
    document.getElementById("diff-step-b").value = Math.min(tmCurrentStep + 2, tmTrace.length);
    new bootstrap.Modal(document.getElementById("diffModal")).show();
});

document.getElementById("diff-run-btn").addEventListener("click", () => {
    const a = parseInt(document.getElementById("diff-step-a").value) - 1;
    const b = parseInt(document.getElementById("diff-step-b").value) - 1;
    if (a < 0 || b < 0 || a >= tmTrace.length || b >= tmTrace.length) { document.getElementById("diff-result").innerHTML = '<div class="tm-error">Invalid step numbers.</div>'; return; }
    const changes = diffSteps(tmTrace[a], tmTrace[b]);
    document.getElementById("diff-result").innerHTML = changes.length
        ? '<div class="fw-semibold mb-2 text-warning">Changes from Step '+(a+1)+" → Step "+(b+1)+"</div>" + changes.map(c => '<div class="wc-item"><i class="fas fa-arrow-right wc-icon"></i><span class="wc-cat">'+esc(c.category)+':</span> '+esc(c.description)+'</div>').join("")
        : '<div class="text-muted small">No differences found between these steps.</div>';
});

function bindControls() {
    document.getElementById("tm-run-btn").addEventListener("click", runCode);
    document.getElementById("ctrl-first").addEventListener("click", () => { stopPlay(); goToStep(0); });
    document.getElementById("ctrl-last").addEventListener("click",  () => { stopPlay(); goToStep(tmTrace.length - 1); });
    document.getElementById("ctrl-prev").addEventListener("click",  () => { stopPlay(); goToStep(tmCurrentStep - 1); });
    document.getElementById("ctrl-next").addEventListener("click",  () => { stopPlay(); goToStep(tmCurrentStep + 1); });
    document.getElementById("ctrl-play").addEventListener("click",  togglePlay);
    document.getElementById("tm-slider").addEventListener("input",  e => { stopPlay(); goToStep(parseInt(e.target.value)); });
}

function togglePlay() { tmPlaying ? stopPlay() : startPlay(); }
function startPlay() {
    if (!tmTrace.length) return;
    tmPlaying = true; document.getElementById("play-icon").className = "fas fa-pause";
    const delay = parseInt(document.getElementById("tm-speed").value) || 600;
    tmPlayTimer = setInterval(() => { if (tmCurrentStep >= tmTrace.length - 1) { stopPlay(); return; } goToStep(tmCurrentStep + 1); }, delay);
}
function stopPlay() { tmPlaying = false; clearInterval(tmPlayTimer); document.getElementById("play-icon").className = "fas fa-play"; }

function bindKeyboard() {
    document.addEventListener("keydown", e => {
        if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA" || e.ctrlKey || e.metaKey) return;
        if (e.key === "ArrowLeft")  { e.preventDefault(); stopPlay(); goToStep(tmCurrentStep - 1); }
        if (e.key === "ArrowRight") { e.preventDefault(); stopPlay(); goToStep(tmCurrentStep + 1); }
        if (e.key === "Home")       { e.preventDefault(); stopPlay(); goToStep(0); }
        if (e.key === "End")        { e.preventDefault(); stopPlay(); goToStep(tmTrace.length - 1); }
        if (e.key === " ")          { e.preventDefault(); togglePlay(); }
    });
}

function bindInspectorTabs() {
    document.querySelectorAll(".inspector-tab").forEach(tab => {
        tab.addEventListener("click", () => {
            document.querySelectorAll(".inspector-tab").forEach(t => t.classList.remove("active")); tab.classList.add("active");
            const target = "inspector-" + tab.dataset.itab;
            ["inspector-vars","inspector-stack","inspector-changed","inspector-history"].forEach(id => { document.getElementById(id).style.display = id === target ? "" : "none"; });
        });
    });
}

function bindVizTabs() {
    document.querySelectorAll(".tm-viz-tab").forEach(tab => {
        tab.addEventListener("click", () => {
            document.querySelectorAll(".tm-viz-tab").forEach(t => t.classList.remove("active")); tab.classList.add("active");
            const target = tab.dataset.tab;
            ["viz-auto","viz-memory","viz-recursion","viz-output"].forEach(id => { document.getElementById(id).style.display = id === target ? "" : "none"; });
        });
    });
}

function showError(msg) { const el = document.getElementById("tm-error-banner"); el.style.display = ""; el.innerHTML = '<i class="fas fa-exclamation-circle me-2"></i>' + esc(msg); }
function hideError() { document.getElementById("tm-error-banner").style.display = "none"; }
function esc(s) { return String(s ?? "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;"); }
