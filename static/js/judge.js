// CodeVision - Online Judge Interactive Client
async function runProblemCode(problemId, language, code, stdin) {
    const resultBox = document.getElementById('run-result-box');
    if (resultBox) resultBox.innerHTML = '<div class="text-secondary"><i class="fas fa-spinner fa-spin me-2"></i>Executing on secure runner...</div>';

    const res = await CodeVision.api('/api/run', {
        method: 'POST',
        body: JSON.stringify({ language, code, stdin })
    });

    if (resultBox) {
        if (res.status === 'Success' || res.status === 'Accepted') {
            resultBox.innerHTML = `
                <div class="alert alert-success p-2 mb-2"><i class="fas fa-check-circle me-1"></i> <strong>${res.status}</strong> (${res.runtime_ms} ms)</div>
                <div class="mb-2"><strong>Standard Output:</strong><pre class="bg-dark p-2 rounded text-light font-monospace mt-1">${res.stdout || '(no output)'}</pre></div>
                ${res.quality ? `<div class="text-info small"><i class="fas fa-microchip me-1"></i> Quality: ${res.quality.score}/100 | Time: ${res.quality.time_complexity} | Space: ${res.quality.space_complexity}</div>` : ''}
            `;
        } else {
            resultBox.innerHTML = `
                <div class="alert alert-danger p-2 mb-2"><i class="fas fa-times-circle me-1"></i> <strong>${res.status}</strong></div>
                <pre class="bg-dark p-2 rounded text-danger font-monospace mt-1">${res.stderr || res.error || 'Execution failed'}</pre>
            `;
        }
    }
    return res;
}

async function submitProblemCode(problemId, language, code, approach = 'Optimal') {
    const submitBox = document.getElementById('submit-result-box');
    if (submitBox) submitBox.innerHTML = '<div class="text-secondary"><i class="fas fa-spinner fa-spin me-2"></i>Evaluating against public & hidden test suites...</div>';

    const res = await CodeVision.api('/api/submit', {
        method: 'POST',
        body: JSON.stringify({ problem_id: problemId, language, code, solution_approach: approach })
    });

    if (submitBox) {
        if (res.status === 'Accepted') {
            submitBox.innerHTML = `
                <div class="cv-card p-3 border-success mb-3">
                    <h5 class="text-success mb-1"><i class="fas fa-check-circle me-2"></i>Accepted!</h5>
                    <div class="text-secondary small mb-2">${res.passed_testcases}/${res.total_testcases} test cases passed. Runtime: ${res.runtime_ms} ms</div>
                    <div class="d-flex gap-2 flex-wrap mb-2">
                        <span class="badge bg-primary">Quality: ${res.quality.score}/100</span>
                        <span class="badge bg-secondary">Time: ${res.quality.time_complexity}</span>
                        <span class="badge bg-secondary">Space: ${res.quality.space_complexity}</span>
                    </div>
                    ${res.skill_update ? `<div class="text-warning small"><i class="fas fa-level-up-alt me-1"></i> ${res.skill_update.topic} Skill updated to ${res.skill_update.new_score}% (+${res.skill_update.delta}%)</div>` : ''}
                </div>
            `;
        } else {
            submitBox.innerHTML = `
                <div class="cv-card p-3 border-danger mb-3">
                    <h5 class="text-danger mb-1"><i class="fas fa-times-circle me-2"></i>${res.status}</h5>
                    <div class="text-secondary small mb-2">${res.passed_testcases}/${res.total_testcases} test cases passed.</div>
                    <pre class="bg-dark text-danger p-2 rounded small font-monospace">${res.error_message || 'Check your edge cases and logic.'}</pre>
                </div>
            `;
        }
    }
    return res;
}
