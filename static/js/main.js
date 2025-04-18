document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const fileInput = document.getElementById('file-input');
    const uploadForm = document.getElementById('upload-form');
    const fileUploadArea = document.getElementById('file-upload-area');
    const fileName = document.getElementById('file-name');
    const markdownOutput = document.getElementById('markdown-output');
    const copyButton = document.getElementById('copy-btn');
    const downloadButton = document.getElementById('download-btn');
    const clearButton = document.getElementById('clear-btn');
    const loadingSpinner = document.getElementById('loading-spinner');
    const llmCheckbox = document.getElementById('use-llm');
    
    // Handle file selection
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            if (fileInput.files.length > 0) {
                fileName.textContent = fileInput.files[0].name;
                fileName.parentElement.classList.remove('d-none');
            } else {
                fileName.textContent = '';
                fileName.parentElement.classList.add('d-none');
            }
        });
    }
    
    // Handle drag and drop
    if (fileUploadArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            fileUploadArea.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            fileUploadArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            fileUploadArea.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            fileUploadArea.classList.add('drag-over');
        }
        
        function unhighlight() {
            fileUploadArea.classList.remove('drag-over');
        }
        
        fileUploadArea.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                fileInput.files = files;
                fileName.textContent = files[0].name;
                fileName.parentElement.classList.remove('d-none');
            }
        }
    }
    
    // Handle form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (!fileInput.files.length) {
                showAlert('Please select a file to convert', 'danger');
                return;
            }
            
            const file = fileInput.files[0];
            const allowedExtensions = ['.html', '.htm', '.pdf', '.docx', '.doc', '.txt', '.md', '.markdown'];
            const fileExt = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
            
            if (!allowedExtensions.includes(fileExt)) {
                showAlert(`Unsupported file format. Supported formats: ${allowedExtensions.join(', ')}`, 'danger');
                return;
            }
            
            // Show loading spinner
            loadingSpinner.style.display = 'block';
            markdownOutput.innerHTML = '';
            
            // Create FormData
            const formData = new FormData();
            formData.append('file', file);
            formData.append('use_llm', llmCheckbox.checked);
            
            // Send request
            fetch('/api/convert', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                loadingSpinner.style.display = 'none';
                
                if (data.error) {
                    showAlert(data.error, 'danger');
                    return;
                }
                
                markdownOutput.textContent = data.markdown;
                document.getElementById('output-section').classList.remove('d-none');
                
                // Enable copy and download buttons
                copyButton.disabled = false;
                downloadButton.disabled = false;
            })
            .catch(error => {
                loadingSpinner.style.display = 'none';
                showAlert('Error converting file: ' + error.message, 'danger');
            });
        });
    }
    
    // Copy to clipboard
    if (copyButton) {
        copyButton.addEventListener('click', function() {
            navigator.clipboard.writeText(markdownOutput.textContent)
                .then(() => {
                    const originalText = copyButton.textContent;
                    copyButton.textContent = 'Copied!';
                    setTimeout(() => {
                        copyButton.textContent = originalText;
                    }, 2000);
                })
                .catch(err => {
                    showAlert('Failed to copy: ' + err, 'danger');
                });
        });
    }
    
    // Download markdown
    if (downloadButton) {
        downloadButton.addEventListener('click', function() {
            const content = markdownOutput.textContent;
            const blob = new Blob([content], {type: 'text/markdown'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'converted_document.md';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
    }
    
    // Clear output
    if (clearButton) {
        clearButton.addEventListener('click', function() {
            markdownOutput.textContent = '';
            document.getElementById('output-section').classList.add('d-none');
            fileInput.value = '';
            fileName.textContent = '';
            fileName.parentElement.classList.add('d-none');
            copyButton.disabled = true;
            downloadButton.disabled = true;
        });
    }
    
    // Helper function to display alerts
    function showAlert(message, type = 'primary') {
        const alertsContainer = document.getElementById('alerts-container');
        
        if (!alertsContainer) return;
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.role = 'alert';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        alertsContainer.appendChild(alert);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => {
                alertsContainer.removeChild(alert);
            }, 150);
        }, 5000);
    }
});
