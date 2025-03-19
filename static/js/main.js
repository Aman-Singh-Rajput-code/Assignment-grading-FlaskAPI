document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const fileInput = document.getElementById('file-input');
    const fileName = document.getElementById('file-name');
    const removeFile = document.getElementById('remove-file');
    const uploadButton = document.getElementById('upload-button');
    const uploadForm = document.getElementById('upload-form');
    const uploadContainer = document.getElementById('upload-container');
    const loaderDiv = document.querySelector('.loaderDiv');
    const loaderP1 = document.querySelector('.loaderP1');
    const loaderP2 = document.querySelector('.loaderP2');
    const fileLabel = document.querySelector('.file-label');
    
    // Handle file selection
    fileInput.addEventListener('change', function() {
        if (fileInput.files.length > 0) {
            // Display the selected file name
            fileName.textContent = fileInput.files[0].name;
            // Show the remove button
            removeFile.hidden = false;
            // Enable the upload button
            uploadButton.disabled = false;
            
            // Check file type and size
            const file = fileInput.files[0];
            const fileType = file.name.split('.').pop().toLowerCase();
            const validTypes = ['pdf', 'doc', 'docx'];
            const maxSize = 16 * 1024 * 1024; // 16MB
            
            if (!validTypes.includes(fileType)) {
                showError('Invalid file type. Please upload a PDF or Word document.');
                resetFileInput();
                return;
            }
            
            if (file.size > maxSize) {
                showError('File is too large. Maximum size is 16MB.');
                resetFileInput();
                return;
            }
        } else {
            resetFileInput();
        }
    });
    
    // Handle drag and drop functionality
    const dropArea = fileLabel.parentElement;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        dropArea.classList.add('highlight');
    }
    
    function unhighlight() {
        dropArea.classList.remove('highlight');
    }
    
    dropArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            fileInput.files = files;
            // Trigger change event
            const event = new Event('change');
            fileInput.dispatchEvent(event);
        }
    }
    
    // Remove file button
    removeFile.addEventListener('click', function() {
        resetFileInput();
    });
    
    // Form submission
    uploadForm.addEventListener('submit', function(e) {
        // Show loading animation
        uploadContainer.hidden = true;
        loaderDiv.removeAttribute('hidden');
        loaderP1.removeAttribute('hidden');
        loaderP2.removeAttribute('hidden');
    });
    
    // Helper functions
    function resetFileInput() {
        fileInput.value = '';
        fileName.textContent = 'No file selected';
        removeFile.hidden = true;
        uploadButton.disabled = true;
    }
    
    function showError(message) {
        // Create error message element
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        
        // Insert before the form
        uploadForm.parentNode.insertBefore(errorDiv, uploadForm);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
    
    // Add error message styling
    const style = document.createElement('style');
    style.textContent = `
        .error-message {
            color: #f44336;
            background-color: rgba(244, 67, 54, 0.1);
            padding: 0.75rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            text-align: center;
            border-left: 4px solid #f44336;
        }
        
        .highlight {
            background-color: var(--primary-light);
            border-color: var(--secondary-color);
        }
    `;
    document.head.appendChild(style);
});