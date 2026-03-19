document.addEventListener('DOMContentLoaded', () => {

    const navLinks = document.querySelectorAll('.nav-links li');
    const sections = document.querySelectorAll('.content-section');
    const navBtns = document.querySelectorAll('.nav-btn');

    // Section Switching Logic
    function switchSection(targetId) {
        // Update nav active state
        navLinks.forEach(link => {
            if (link.dataset.target === targetId) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });

        // Show target section, hide others
        sections.forEach(section => {
            if (section.id === targetId) {
                section.classList.add('active');
            } else {
                section.classList.remove('active');
            }
        });
    }

    // Attach click events to nav links
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            const target = link.dataset.target;
            switchSection(target);
        });
    });

    // Inner page navigation buttons
    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.dataset.target;
            switchSection(target);
        });
    });

    // Handle Form Submission
    const form = document.getElementById('gmc-form');
    const submitBtn = document.getElementById('run-btn');
    const btnText = submitBtn.querySelector('span');
    const loader = submitBtn.querySelector('.loader-spinner');
    const terminalOutput = document.getElementById('console-output');
    
    const iframe = document.getElementById('plot-frame');
    const placeholder = document.querySelector('.placeholder-content');
    const refreshBtn = document.getElementById('refresh-viewer-btn');
    let currentPlotUrl = '';

    function appendToTerminal(text, className = '') {
        const span = document.createElement('span');
        if (className) span.className = className;
        span.textContent = text + '\n';
        terminalOutput.appendChild(span);
        terminalOutput.scrollTop = terminalOutput.scrollHeight;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // UI Loading State
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        loader.style.display = 'block';

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        // Clear terminal wrapper and print command info
        terminalOutput.innerHTML = '<span class="prompt">PS C:\\GMC></span> python main.py ';
        if(data.pred_file) terminalOutput.innerHTML += `--pred-file ${data.pred_file} `;
        if(data.samples) terminalOutput.innerHTML += `--samples ${data.samples} `;
        terminalOutput.innerHTML += '\n';

        appendToTerminal('正在执行计算任务，请稍候...', 'prompt');

        try {
            const response = await fetch('/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.status === 'success') {
                appendToTerminal(result.output, 'success');
                appendToTerminal('\n执行成功！正在生成三维图表...', 'success');
                
                // Update iframe
                currentPlotUrl = result.plot_url;
                iframe.src = currentPlotUrl;
                iframe.style.display = 'block';
                placeholder.style.display = 'none';

                // Automatically switch to viewer after a short delay
                setTimeout(() => {
                    switchSection('viewer');
                }, 1500);
            } else {
                appendToTerminal(result.output || '', '');
                appendToTerminal(result.error || '未知错误', 'error');
            }
        } catch (err) {
            appendToTerminal(`请求失败: ${err.message}`, 'error');
        } finally {
            // Restore btn
            submitBtn.disabled = false;
            btnText.style.display = 'flex';
            loader.style.display = 'none';
        }
    });

    // Refresh Viewer Button
    refreshBtn.addEventListener('click', () => {
        if (currentPlotUrl) {
            iframe.src = iframe.src; // Reload
        }
    });
});
