// CodeVision - Resilient Monaco & Fallback Code Editor Engine
let codeEditor = null;

function initMonacoEditor(containerId, initialCode = "", language = "python") {
    return new Promise((resolve) => {
        const container = document.getElementById(containerId);
        if (!container) return resolve(null);

        let resolved = false;

        const setupFallback = () => {
            if (resolved) return;
            resolved = true;
            container.innerHTML = `
                <textarea id="fallback-code-editor" class="w-100 h-100 p-3 font-monospace small" 
                    style="background: #0d1117; color: #f3f4f6; border: none; outline: none; resize: none; line-height: 1.5; font-size: 14px;"
                    placeholder="Type or paste code here...">${initialCode}</textarea>
            `;
            const textarea = document.getElementById('fallback-code-editor');
            codeEditor = {
                getValue: () => textarea.value,
                setValue: (v) => { textarea.value = v; },
                setPosition: () => {},
                revealLineInCenter: () => {},
                deltaDecorations: () => []
            };
            resolve(codeEditor);
        };

        // 3-second timeout fallback if CDN or RequireJS fails/hangs
        const timeoutTimer = setTimeout(() => {
            if (!codeEditor && !resolved) {
                console.warn('Monaco CDN load timeout. Using high-performance code editor fallback.');
                setupFallback();
            }
        }, 3000);

        if (typeof require !== 'undefined' && require.config) {
            try {
                require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs' } });
                require(['vs/editor/editor.main'], function () {
                    if (resolved) return;
                    clearTimeout(timeoutTimer);
                    resolved = true;
                    container.innerHTML = '';
                    codeEditor = monaco.editor.create(container, {
                        value: initialCode,
                        language: language === 'cpp' ? 'cpp' : (language === 'c' ? 'c' : (language === 'javascript' ? 'javascript' : (language === 'java' ? 'java' : 'python'))),
                        theme: 'vs-dark',
                        fontSize: 14,
                        fontFamily: "'JetBrains Mono', Consolas, monospace",
                        automaticLayout: true,
                        minimap: { enabled: false },
                        scrollBeyondLastLine: false,
                        tabSize: 4
                    });
                    resolve(codeEditor);
                }, function (err) {
                    clearTimeout(timeoutTimer);
                    setupFallback();
                });
            } catch (err) {
                clearTimeout(timeoutTimer);
                setupFallback();
            }
        } else {
            clearTimeout(timeoutTimer);
            setupFallback();
        }
    });
}
