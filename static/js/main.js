document.addEventListener('DOMContentLoaded', function() {
    const convertForm = document.getElementById('convertForm');
    const progressSection = document.getElementById('progressSection');
    const downloadSection = document.getElementById('downloadSection');
    const errorSection = document.getElementById('errorSection');
    const progressBar = document.getElementById('progressBar');
    const downloadBtn = document.getElementById('downloadBtn');
    const convertBtn = document.getElementById('convertBtn');

    let currentTaskId = null;
    let progressInterval = null;

    convertForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const urlInput = document.getElementById('videoUrl');
        const url = urlInput.value.trim();

        if (!url) {
            showError('Please enter a video URL');
            return;
        }

        try {
            convertBtn.disabled = true;
            showProgress();
            hideError();
            hideDownload();

            const response = await fetch('/convert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });

            const data = await response.json();

            if (response.ok) {
                currentTaskId = data.task_id;
                startProgressTracking();
            } else {
                throw new Error(data.error || 'Conversion failed');
            }
        } catch (error) {
            showError(error.message);
            hideProgress();
            convertBtn.disabled = false;
        }
    });

    function startProgressTracking() {
        if (progressInterval) {
            clearInterval(progressInterval);
        }

        progressInterval = setInterval(async () => {
            try {
                const response = await fetch(`/progress/${currentTaskId}`);
                const data = await response.json();

                updateProgress(data.progress);

                if (data.progress === 100) {
                    clearInterval(progressInterval);
                    showDownload();
                    hideProgress();
                    convertBtn.disabled = false;
                } else if (data.progress === -1) {
                    clearInterval(progressInterval);
                    showError('Conversion failed');
                    hideProgress();
                    convertBtn.disabled = false;
                }
            } catch (error) {
                clearInterval(progressInterval);
                showError('Failed to track progress');
                hideProgress();
                convertBtn.disabled = false;
            }
        }, 1000);
    }

    downloadBtn.addEventListener('click', function(e) {
        e.preventDefault();
        if (currentTaskId) {
            window.location.href = `/download/${currentTaskId}`;
        }
    });

    function updateProgress(progress) {
        progressBar.style.width = `${progress}%`;
        progressBar.textContent = `${progress}%`;
    }

    function showProgress() {
        progressSection.classList.remove('d-none');
    }

    function hideProgress() {
        progressSection.classList.add('d-none');
    }

    function showDownload() {
        downloadSection.classList.remove('d-none');
    }

    function hideDownload() {
        downloadSection.classList.add('d-none');
    }

    function showError(message) {
        errorSection.classList.remove('d-none');
        document.getElementById('errorMessage').textContent = message;
    }

    function hideError() {
        errorSection.classList.add('d-none');
    }
});