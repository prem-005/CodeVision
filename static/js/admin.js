// CodeVision - Admin Operations
async function deleteAdminProblem(probId) {
    if (!confirm('Are you sure you want to delete this problem and its test cases?')) return;
    const res = await CodeVision.api(`/admin/api/problems/${probId}`, { method: 'DELETE' });
    if (res.success) {
        CodeVision.toast('Problem deleted successfully', 'success');
        location.reload();
    } else {
        CodeVision.toast(res.error || 'Delete failed', 'error');
    }
}
