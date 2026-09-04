// CodeVision - Project Lab Client
async function submitProjectCode(projectId, language, code) {
    const resBox = document.getElementById('project-results-box');
    if (resBox) resBox.innerHTML = '<div class="text-secondary"><i class="fas fa-spinner fa-spin me-2"></i>Evaluating project milestones and test cases...</div>';

    const res = await CodeVision.api(`/api/projects/${projectId}/submit`, {
        method: 'POST',
        body: JSON.stringify({ language, code })
    });

    if (resBox) {
        if (res.success) {
            resBox.innerHTML = `
                <div class="cv-card p-3 border-success mb-3">
                    <h5 class="text-success"><i class="fas fa-check-circle me-2"></i>Status: ${res.status}</h5>
                    <div class="mb-2">Score: <strong>${res.score}/100</strong> | Milestones: <strong>${res.passed_milestones}/${res.total_milestones}</strong></div>
                    <div class="progress mb-2" style="height: 10px;">
                        <div class="progress-bar bg-success" style="width: ${res.score}%"></div>
                    </div>
                    <div class="text-info small"><i class="fas fa-award me-1"></i> Quality: ${res.quality.score}/100</div>
                </div>
            `;
        } else {
            resBox.innerHTML = `<div class="alert alert-danger">${res.error || 'Submission failed'}</div>`;
        }
    }
}
