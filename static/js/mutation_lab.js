/* =========================================================
   MUTATION LAB — static/js/mutation_lab.js
   Side-by-side original vs mutated execution analysis
   ========================================================= */
"use strict";

let mlOrigTrace = [], mlMutTrace = [], mlComparison = null;
let mlOrigEditor = null, mlMutEditor = null;

const ML_DEFAULT_CODE = `def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

result = bubble_sort([64, 34, 25, 12, 22, 11, 90])
print("Sorted:", result)
`;

document.addEventListener("DOMContentLoaded", () => {
    initEditors();
    loadMutations(ML_DEFAULT_CODE);
    bindMLControls();
});

function initEditors() {
    mlOrigEditor = CodeMirror(document.getElementById("ml-orig-cm"), {
        value: ML_DEFAULT_CODE, mode: "python", theme: "dracula",
        lineNumbers: true, readOnly: false, lineWrapping: false,
        indentUnit: 4, tabSize: 4
    });
    mlMutEditor = CodeMirror(document.getElementById("ml-mut-cm"), {
        value: "// Mutated code will appear here after analysis.", mode: "python", theme: "dracula",
        lineNumbers: true, readOnly: true, lineWrapping: false
    });
    mlOrigEditor.on("change", () => loadMutations(mlOrigEditor.getValue()));
}

async function loadMutations(code) {
    try {
        const res  = await fetch("/code-lab/api/mutation/available", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ code }) });
        const data = await res.json();
        if (!data.success) return;
        const sel = document.getElementById("ml-mutation-select");
        sel.innerHTML = '<option value="">-- Select Mutation Type --</option>' +
            (data.mutations || []).map(m => '<option value="'+esc(m.id)+'" title="'+esc(m.description)+'">'+esc(m.name)+'</option>').join("");
    } catch(e) { /* silently ignore */ }
}

async function runMutation() {
    const code          = mlOrigEditor.getValue();
    const mutationType  = document.getElementById("ml-mutation-select").value;
    const stdin         = document.getElementById("ml-custom-input").value.trim();
    const btn           = document.getElementById("ml-run-btn");

    if (!code.trim()) { showMLError("Please enter some code."); return; }

    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Running...'; btn.disabled = true;

    try {
        const res  = await fetch("/code-lab/api/mutation/run", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ code, mutation_type: mutationType || null, stdin }) });
        const data = await res.json();
        if (!data.success) { showMLError(data.error || "Mutation failed."); return; }

        mlOrigTrace   = (data.original_trace && data.original_trace.steps) || [];
        mlMutTrace    = (data.mutated_trace  && data.mutated_trace.steps)  || [];
        mlComparison  = data.comparison || null;

        // Show mutated code
        mlMutEditor.setValue(data.mutated_code || "");

        // Render last step of each
        renderMLSide("orig", mlOrigTrace);
        renderMLSide("mut",  mlMutTrace);
        renderMLComparison(data.comparison);

        // Enable restore/new mutation
        document.getElementById("ml-restore-btn").disabled = false;
        document.getElementById("ml-newmut-btn").disabled  = false;
    } catch (e) { showMLError("Network error: " + e.message); }
    finally { btn.innerHTML = '<i class="fas fa-dna me-1"></i>Mutate &amp; Run'; btn.disabled = false; }
}

function renderMLSide(which, trace) {
    const vizEl    = document.getElementById("ml-" + which + "-viz");
    const inspEl   = document.getElementById("ml-" + which + "-inspector");

    if (!trace || !trace.length) {
        vizEl.innerHTML  = '<div class="text-muted small text-center mt-4">No trace available</div>';
        inspEl.innerHTML = '<div class="text-muted small">No variables.</div>';
        return;
    }

    const step     = trace[trace.length - 1]; // last step = final state
    const vars     = step.variables || {};
    const tree     = step.recursion_tree || [];
    const memory   = step.memory || { objects: [] };

    // Viz
    if (tree.length > 0) {
        vizEl.innerHTML = buildMLRecursionTree(tree, step.active_call_id);
    } else if (memory.objects && memory.objects.length > 0) {
        vizEl.innerHTML = buildMLMemory(memory);
    } else {
        vizEl.innerHTML = '<div style="background:var(--bg-main);border:1px solid var(--border-color);border-radius:8px;padding:1rem;">' +
            '<div class="text-muted small mb-1">Final Output</div>' +
            '<pre style="color:#a3e635;font-size:.8rem;margin:0">' + esc(step.stdout || "(no output)") + '</pre></div>';
    }

    // Inspector variables
    const entries = Object.entries(vars);
    if (!entries.length) { inspEl.innerHTML = '<div class="text-muted small">No variables in scope</div>'; return; }
    inspEl.innerHTML = entries.map(([name, info]) =>
        '<div class="var-row-ml"><span class="var-name-ml">'+esc(name)+'</span><span class="var-val-ml">'+esc(String(info.value ?? ""))+'</span></div>'
    ).join("");
}

function renderMLComparison(cmp) {
    if (!cmp) return;
    const panel = document.getElementById("ml-comparison");
    panel.style.display = "";

    document.getElementById("cmp-orig-steps").textContent = cmp.original_total_steps || 0;
    document.getElementById("cmp-mut-steps").textContent  = cmp.mutated_total_steps  || 0;

    const sev = (cmp.severity || "LOW").toLowerCase();
    const sevClass = { critical: "sev-critical", high: "sev-high", medium: "sev-medium", low: "sev-low" }[sev] || "sev-low";
    document.getElementById("cmp-severity").innerHTML = '<span class="severity-badge ' + sevClass + '">' + esc(cmp.severity || "LOW") + "</span>";

    const divStep = cmp.divergence_step;
    document.getElementById("cmp-div-step").textContent = divStep ? "Step " + divStep : "No divergence detected";

    let divDetail = "";
    if (cmp.divergence_details) {
        const d = cmp.divergence_details;
        if (d.type === "Variable State Divergence" && d.differences && d.differences.length) {
            divDetail = d.differences.map(diff =>
                '<span class="badge me-1" style="background:rgba(239,68,68,.15);color:#fca5a5;">' + esc(diff.var) + ': ' + esc(String(diff.original)) + ' → ' + esc(String(diff.mutated)) + '</span>'
            ).join("");
        } else if (d.type) {
            divDetail = '<span class="text-muted small">' + esc(d.original || d.type) + '</span>';
        }
    }
    document.getElementById("cmp-div-detail").innerHTML = divDetail;

    document.getElementById("cmp-orig-out").textContent = cmp.original_output ? "Original: " + cmp.original_output.trim() : "Original: (no output)";
    document.getElementById("cmp-mut-out").textContent  = cmp.mutated_output  ? "Mutated:  " + cmp.mutated_output.trim()  : "Mutated:  (no output)";

    // Color outputs differently if they diverge
    const sameOut = cmp.original_output === cmp.mutated_output;
    document.getElementById("cmp-mut-out").style.borderColor = sameOut ? "rgba(34,197,94,.4)" : "rgba(239,68,68,.4)";

    document.getElementById("cmp-explanation").textContent = cmp.explanation || "";
}

// ─── MUTATION HELPERS ─────────────────────────────────────────────────────────
function buildMLRecursionTree(nodes, activeCallId) {
    if (!nodes || !nodes.length) return '<div class="text-muted small">No recursion tree</div>';
    const byId = {}, childrenOf = {};
    nodes.forEach(n => { byId[n.id] = n; });
    nodes.forEach(n => { if (n.parentId) { if (!childrenOf[n.parentId]) childrenOf[n.parentId] = []; childrenOf[n.parentId].push(n.id); } });
    const roots = nodes.filter(n => !n.parentId || !byId[n.parentId]);
    const levels = []; let queue = roots.map(n => ({ id: n.id, depth: 0 }));
    while (queue.length) { const { id, depth } = queue.shift(); if (!levels[depth]) levels[depth] = []; levels[depth].push(id); (childrenOf[id]||[]).forEach(cid => queue.push({ id: cid, depth: depth+1 })); }
    const R=22, DX=70, DY=70, posOf={};
    levels.forEach((lvl, depth) => { const total=lvl.length; lvl.forEach((id,i) => { posOf[id]={ x:(i-(total-1)/2)*DX+200, y:40+depth*DY }; }); });
    const W=Math.max(400, Math.max(...Object.values(posOf).map(p=>p.x+R+20)));
    const H=levels.length*DY+80;
    let edges="", nodesSVG="";
    nodes.forEach(n => {
        const p=posOf[n.id]; if (!p) return;
        if (n.parentId && posOf[n.parentId]) { const pp=posOf[n.parentId]; edges+='<line x1="'+pp.x+'" y1="'+(pp.y+R)+'" x2="'+p.x+'" y2="'+(p.y-R)+'" stroke="rgba(255,255,255,.15)" stroke-width="1.5"/>'; }
        const isA=n.id===activeCallId, isR=n.status==="returned";
        const fill=isA?"rgba(245,158,11,.3)":isR?"rgba(34,197,94,.15)":"#1f293d";
        const stroke=isA?"#f59e0b":isR?"#22c55e":"rgba(255,255,255,.2)";
        const lbl=(n.label||n.fnName||"").substring(0,10);
        const retLbl=isR&&n.returnVal!==null?" ↩ "+n.returnVal:"";
        nodesSVG+='<g><circle cx="'+p.x+'" cy="'+p.y+'" r="'+R+'" fill="'+fill+'" stroke="'+stroke+'" stroke-width="2"/><text x="'+p.x+'" y="'+p.y+'" text-anchor="middle" dominant-baseline="central" style="fill:#e2e8f0;font-size:9px;font-family:JetBrains Mono,monospace">'+esc(lbl)+'</text>'+(retLbl?'<text x="'+p.x+'" y="'+(p.y+R+12)+'" text-anchor="middle" style="fill:#22c55e;font-size:8px">'+esc(retLbl)+'</text>':'')+'</g>';
    });
    return '<svg width="'+W+'" height="'+H+'" style="overflow:visible">'+edges+nodesSVG+'</svg>';
}

function buildMLMemory(memory) {
    const objs = memory.objects || [];
    if (!objs.length) return '<div class="text-muted small text-center mt-3">No heap objects</div>';
    return objs.slice(0,5).map(obj => {
        let inner="";
        if (obj.elements && obj.elements.length) inner = '<div style="font-size:.72rem;color:#94a3b8;">['+obj.elements.slice(0,8).map(e=>esc(JSON.stringify(e.value&&e.value.value!==undefined?e.value.value:e.value))).join(", ")+"]</div>";
        else if (obj.fields) inner = Object.entries(obj.fields).slice(0,5).map(([k,v]) => '<div style="font-size:.72rem;color:#94a3b8;">'+esc(k)+': '+esc(JSON.stringify(v&&v.value!==undefined?v.value:v))+'</div>').join("");
        return '<div style="background:rgba(255,255,255,.03);border:1px solid var(--border-color);border-radius:6px;padding:.6rem;margin-bottom:.5rem;"><div style="font-size:.7rem;font-weight:700;color:var(--primary-accent);margin-bottom:.3rem;">'+esc(obj.label||obj.objectId)+' <span style="color:var(--text-muted)">'+esc(obj.type)+'</span></div>'+inner+'</div>';
    }).join("");
}

function bindMLControls() {
    document.getElementById("ml-run-btn").addEventListener("click", runMutation);
    document.getElementById("ml-restore-btn").addEventListener("click", restoreOriginal);
    document.getElementById("ml-newmut-btn").addEventListener("click",  generateNewMutation);
}

function restoreOriginal() {
    mlMutEditor.setValue(mlOrigEditor.getValue());
    document.getElementById("ml-mut-viz").innerHTML = '<div class="text-muted small text-center mt-4"><i class="fas fa-undo fa-2x mb-2 d-block"></i>Restored to original</div>';
    document.getElementById("ml-mut-inspector").innerHTML = '<div class="text-muted small">Variables will appear here...</div>';
    document.getElementById("ml-comparison").style.display = "none";
}

function generateNewMutation() {
    // Rotate to next mutation in dropdown
    const sel = document.getElementById("ml-mutation-select");
    const opts = Array.from(sel.options);
    const cur  = sel.selectedIndex;
    sel.selectedIndex = cur >= opts.length - 1 ? 1 : cur + 1;
    runMutation();
}

function showMLError(msg) {
    alert("Mutation Lab Error: " + msg);
}

function esc(s) {
    return String(s ?? "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}
