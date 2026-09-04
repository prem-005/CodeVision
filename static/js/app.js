// CodeVision - Global Application Utility
window.CodeVision = {
    async api(url, options = {}) {
        options.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            ...(options.headers || {})
        };
        try {
            const res = await fetch(url, options);
            const contentType = res.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('Received non-JSON response from server.');
            }
            return await res.json();
        } catch (err) {
            console.error('API Error:', err);
            return { success: false, error: err.message };
        }
    },

    toast(message, type = 'info') {
        const toastEl = document.createElement('div');
        toastEl.className = `cv-toast cv-toast-${type}`;
        toastEl.style.position = 'fixed';
        toastEl.style.bottom = '20px';
        toastEl.style.right = '20px';
        toastEl.style.padding = '10px 18px';
        toastEl.style.borderRadius = '8px';
        toastEl.style.zIndex = '9999';
        toastEl.style.color = '#fff';
        toastEl.style.fontWeight = '600';
        toastEl.style.boxShadow = '0 4px 20px rgba(0,0,0,0.5)';
        toastEl.style.background = type === 'success' ? '#10b981' : (type === 'error' ? '#ef4444' : '#3b82f6');
        toastEl.innerText = message;
        document.body.appendChild(toastEl);
        setTimeout(() => toastEl.remove(), 3500);
    }
};
