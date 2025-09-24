/**
 * Document Upload Page - Frontend JavaScript
 * 
 * This file handles the document upload functionality for the US Tax Chatbot.
 */

class DocumentUploader {
    constructor() {
        this.selectedFiles = [];
        this.isUploading = false;

        this.currentSessionId = null;
        this.pollingInterval = null;
        
        // DOM elements
        this.elements = {
            uploadArea: document.getElementById('uploadArea'),
            fileInput: document.getElementById('fileInput'),
            browseBtn: document.getElementById('browseBtn'),
            selectedFiles: document.getElementById('selectedFiles'),
            filesList: document.getElementById('filesList'),
            uploadBtn: document.getElementById('uploadBtn'),
            clearBtn: document.getElementById('clearBtn'),
            uploadProgress: document.getElementById('uploadProgress'),
            progressText: document.getElementById('progressText'),
            progressFill: document.getElementById('progressFill'),
            progressDetails: document.getElementById('progressDetails'),
            uploadResults: document.getElementById('uploadResults'),
            resultsContent: document.getElementById('resultsContent'),
            backToChatBtn: document.getElementById('backToChatBtn'),
            backToChatBtn2: document.getElementById('backToChatBtn2'),
            uploadMoreBtn: document.getElementById('uploadMoreBtn'),
            loadingOverlay: document.getElementById('loadingOverlay'),
            errorModal: document.getElementById('errorModal'),
            errorMessage: document.getElementById('errorMessage'),
            closeErrorModal: document.getElementById('closeErrorModal'),
            retryBtn: document.getElementById('retryBtn')
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
    }
    
    setupEventListeners() {
        // File input events
        this.elements.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        this.elements.browseBtn.addEventListener('click', () => this.elements.fileInput.click());
        
        // Upload area events
        this.elements.uploadArea.addEventListener('click', () => this.elements.fileInput.click());
        
        // Button events
        this.elements.uploadBtn.addEventListener('click', () => this.uploadFiles());
        this.elements.clearBtn.addEventListener('click', () => this.clearFiles());
        this.elements.backToChatBtn.addEventListener('click', () => this.goBackToChat());
        this.elements.backToChatBtn2.addEventListener('click', () => this.goBackToChat());
        this.elements.uploadMoreBtn.addEventListener('click', () => this.resetUpload());
        
        // Modal events
        this.elements.closeErrorModal.addEventListener('click', () => this.hideErrorModal());
        this.elements.retryBtn.addEventListener('click', () => {
            this.hideErrorModal();
            this.uploadFiles();
        });
    }
    
    setupDragAndDrop() {
        const uploadArea = this.elements.uploadArea;
        
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });
        
        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => this.highlight(uploadArea), false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => this.unhighlight(uploadArea), false);
        });
        
        // Handle dropped files
        uploadArea.addEventListener('drop', (e) => this.handleDrop(e), false);
    }
    
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    highlight(element) {
        element.classList.add('drag-over');
    }
    
    unhighlight(element) {
        element.classList.remove('drag-over');
    }
    
    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        this.handleFiles(files);
    }
    
    handleFileSelect(e) {
        const files = e.target.files;
        this.handleFiles(files);
    }
    
    handleFiles(files) {
        const validFiles = [];
        
        for (let file of files) {
            if (this.validateFile(file)) {
                validFiles.push(file);
            }
        }
        
        if (validFiles.length > 0) {
            this.selectedFiles = [...this.selectedFiles, ...validFiles];
            this.updateFileList();
            this.showSelectedFiles();
        }
    }
    
    validateFile(file) {
        // Check file type
        if (file.type !== 'application/pdf') {
            this.showError(`File "${file.name}" is not a PDF file. Only PDF files are allowed.`);
            return false;
        }
        
        // Check file size (16MB limit)
        const maxSize = 16 * 1024 * 1024; // 16MB
        if (file.size > maxSize) {
            this.showError(`File "${file.name}" is too large. Maximum file size is 16MB.`);
            return false;
        }
        
        // Check if file already selected
        if (this.selectedFiles.some(f => f.name === file.name && f.size === file.size)) {
            this.showError(`File "${file.name}" is already selected.`);
            return false;
        }
        
        return true;
    }
    
    updateFileList() {
        this.elements.filesList.innerHTML = '';
        
        this.selectedFiles.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <div class="file-info">
                    <i class="fas fa-file-pdf"></i>
                    <div class="file-details">
                        <span class="file-name">${file.name}</span>
                        <span class="file-size">${this.formatFileSize(file.size)}</span>
                    </div>
                </div>
                <button class="btn btn-icon remove-file" data-index="${index}">
                    <i class="fas fa-times"></i>
                </button>
            `;
            
            // Add remove file event listener
            const removeBtn = fileItem.querySelector('.remove-file');
            removeBtn.addEventListener('click', () => this.removeFile(index));
            
            this.elements.filesList.appendChild(fileItem);
        });
        
        this.elements.uploadBtn.disabled = this.selectedFiles.length === 0;
    }
    
    removeFile(index) {
        this.selectedFiles.splice(index, 1);
        this.updateFileList();
        
        if (this.selectedFiles.length === 0) {
            this.hideSelectedFiles();
        }
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    showSelectedFiles() {
        this.elements.selectedFiles.style.display = 'block';
        this.elements.uploadArea.style.display = 'none';
    }
    
    hideSelectedFiles() {
        this.elements.selectedFiles.style.display = 'none';
        this.elements.uploadArea.style.display = 'block';
    }
    
    clearFiles() {
        this.selectedFiles = [];
        this.elements.fileInput.value = '';
        this.stopPolling();
        this.hideSelectedFiles();
        this.hideProgress();
        this.hideResults();
    }
    
    async uploadFiles() {
        if (this.selectedFiles.length === 0 || this.isUploading) return;
        
        this.isUploading = true;
        this.showProgress();
        this.updateProgress(0, 'Preparing upload...');
        
        try {
            const formData = new FormData();
            this.selectedFiles.forEach(file => {
                formData.append('files', file);
            });
            
            this.updateProgress(10, 'Uploading files...');
            
            const response = await fetch('/api/upload_documents', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                // Start polling for progress
                this.currentSessionId = result.data.session_id;
                this.startPolling();
            } else {
                throw new Error(result.error || 'Upload failed');
            }
            
        } catch (error) {
            console.error('Upload error:', error);
            this.showError(`Upload failed: ${error.message}`);
            this.hideProgress();
        } finally {
            this.isUploading = false;
        }
    }
    
    showProgress() {
        this.elements.uploadProgress.style.display = 'block';
        this.elements.selectedFiles.style.display = 'none';
    }
    
    hideProgress() {
        this.elements.uploadProgress.style.display = 'none';
    }
    
    updateProgress(percentage, text) {
        this.elements.progressFill.style.width = `${percentage}%`;
        this.elements.progressText.textContent = text;
        
        // Add progress details
        if (percentage === 10) {
            this.elements.progressDetails.innerHTML = `
                <div class="progress-step">
                    <i class="fas fa-check"></i>
                    <span>Files uploaded successfully</span>
                </div>
            `;
        } else if (percentage === 50) {
            this.elements.progressDetails.innerHTML = `
                <div class="progress-step">
                    <i class="fas fa-check"></i>
                    <span>Files uploaded successfully</span>
                </div>
                <div class="progress-step">
                    <i class="fas fa-spinner fa-spin"></i>
                    <span>Extracting text from PDFs</span>
                </div>
            `;
        } else if (percentage === 80) {
            this.elements.progressDetails.innerHTML = `
                <div class="progress-step">
                    <i class="fas fa-check"></i>
                    <span>Files uploaded successfully</span>
                </div>
                <div class="progress-step">
                    <i class="fas fa-check"></i>
                    <span>Text extracted from PDFs</span>
                </div>
                <div class="progress-step">
                    <i class="fas fa-spinner fa-spin"></i>
                    <span>Generating embeddings</span>
                </div>
            `;
        } else if (percentage === 100) {
            this.elements.progressDetails.innerHTML = `
                <div class="progress-step">
                    <i class="fas fa-check"></i>
                    <span>Files uploaded successfully</span>
                </div>
                <div class="progress-step">
                    <i class="fas fa-check"></i>
                    <span>Text extracted from PDFs</span>
                </div>
                <div class="progress-step">
                    <i class="fas fa-check"></i>
                    <span>Embeddings generated</span>
                </div>
                <div class="progress-step">
                    <i class="fas fa-check"></i>
                    <span>Documents added to database</span>
                </div>
            `;
        }
    }
    
    showResults(data) {
        this.elements.resultsContent.innerHTML = `
            <div class="result-summary">
                <p><strong>${data.message}</strong></p>
                <p>Your documents are now available for the chatbot to reference.</p>
            </div>
            <div class="result-files">
                <h4>Successfully processed files:</h4>
                <ul>
                    ${data.uploaded_files.map(file => `<li><i class="fas fa-file-pdf"></i> ${file}</li>`).join('')}
                </ul>
                ${data.failed_files && data.failed_files.length > 0 ? `
                    <h4>Failed files:</h4>
                    <ul>
                        ${data.failed_files.map(file => `<li><i class="fas fa-exclamation-triangle"></i> ${file}</li>`).join('')}
                    </ul>
                ` : ''}
            </div>
        `;
        
        this.elements.uploadResults.style.display = 'block';
        this.hideProgress();
    }
    
    hideResults() {
        this.elements.uploadResults.style.display = 'none';
    }
    
    resetUpload() {
        this.clearFiles();
        this.hideResults();
    }
    
    goBackToChat() {
        window.location.href = '/';
    }
    
    startPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }
        
        // Poll every 2 seconds
        this.pollingInterval = setInterval(() => {
            this.checkProgress();
        }, 2000);
    }
    
    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }
    
    async checkProgress() {
        if (!this.currentSessionId) return;
        
        try {
            const response = await fetch(`/api/upload_progress/${this.currentSessionId}`);
            const result = await response.json();
            
            if (result.success) {
                const progressData = result.data;
                this.updateRealProgress(progressData);
                
                // Stop polling if completed or failed
                if (progressData.status === 'completed') {
                    this.stopPolling();
                    setTimeout(() => {
                        this.showResults({
                            message: progressData.message,
                            uploaded_files: this.selectedFiles.map(f => f.name),
                            failed_files: []
                        });
                    }, 1000);
                } else if (progressData.status === 'error') {
                    this.stopPolling();
                    this.showError('Upload processing failed');
                }
            } else {
                console.error('Progress check failed:', result.error);
            }
        } catch (error) {
            console.error('Error checking progress:', error);
        }
    }
    
    updateRealProgress(data) {
        this.elements.progressFill.style.width = `${data.percentage}%`;
        this.elements.progressText.textContent = data.message;
        
        // Update progress details based on stage
        let details = '';
        if (data.currentStage === 'extracting') {
            details = `
                <div class="progress-step">
                    <i class="fas fa-spinner fa-spin"></i>
                    <span>Extracting text from ${data.currentFile}</span>
                </div>
            `;
        } else if (data.currentStage === 'chunking') {
            details = `
                <div class="progress-step">
                    <i class="fas fa-check"></i>
                    <span>Text extracted from ${data.currentFile}</span>
                </div>
                <div class="progress-step">
                    <i class="fas fa-spinner fa-spin"></i>
                    <span>Chunking text from ${data.currentFile}</span>
                </div>
            `;
        } else if (data.currentStage === 'embedding') {
            details = `
                <div class="progress-step">
                    <i class="fas fa-check"></i>
                    <span>All files processed</span>
                </div>
                <div class="progress-step">
                    <i class="fas fa-spinner fa-spin"></i>
                    <span>Generating embeddings</span>
                </div>
            `;
        } else if (data.currentStage === 'storing') {
            details = `
                <div class="progress-step">
                    <i class="fas fa-check"></i>
                    <span>All files processed</span>
                </div>
                <div class="progress-step">
                    <i class="fas fa-check"></i>
                    <span>Embeddings generated</span>
                </div>
                <div class="progress-step">
                    <i class="fas fa-spinner fa-spin"></i>
                    <span>Storing in database</span>
                </div>
            `;
        } else if (data.currentStage === 'completed') {
            details = `
                <div class="progress-step">
                    <i class="fas fa-check"></i>
                    <span>All files processed</span>
                </div>
                <div class="progress-step">
                    <i class="fas fa-check"></i>
                    <span>Embeddings generated</span>
                </div>
                <div class="progress-step">
                    <i class="fas fa-check"></i>
                    <span>Stored in database</span>
                </div>
            `;
        }
        
        this.elements.progressDetails.innerHTML = details;
    }
    
    showError(message) {
        this.elements.errorMessage.textContent = message;
        this.elements.errorModal.classList.add('show');
    }
    
    hideErrorModal() {
        this.elements.errorModal.classList.remove('show');
    }
}

// Initialize the uploader when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.documentUploader = new DocumentUploader();
});

// Add CSS for drag and drop
const style = document.createElement('style');
style.textContent = `
    .upload-area.drag-over {
        border-color: var(--primary-color);
        background-color: var(--primary-light);
        transform: scale(1.02);
    }
    
    .file-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: var(--spacing-md);
        background: var(--surface-color);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        margin-bottom: var(--spacing-sm);
    }
    
    .file-info {
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
    }
    
    .file-details {
        display: flex;
        flex-direction: column;
    }
    
    .file-name {
        font-weight: 500;
        color: var(--text-primary);
    }
    
    .file-size {
        font-size: 0.875rem;
        color: var(--text-muted);
    }
    
    .remove-file {
        color: var(--error-color);
    }
    
    .remove-file:hover {
        background: var(--error-light);
    }
    
    .upload-actions {
        display: flex;
        gap: var(--spacing-sm);
        margin-top: var(--spacing-md);
    }
    
    .progress-bar {
        width: 100%;
        height: 8px;
        background: var(--border-light);
        border-radius: 4px;
        overflow: hidden;
        margin: var(--spacing-md) 0;
    }
    
    .progress-fill {
        height: 100%;
        background: var(--primary-color);
        transition: width 0.3s ease;
        width: 0%;
    }
    
    .progress-step {
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
        margin: var(--spacing-xs) 0;
        font-size: 0.875rem;
    }
    
    .progress-step i {
        width: 16px;
        text-align: center;
    }
    
    .result-summary {
        margin-bottom: var(--spacing-lg);
        padding: var(--spacing-md);
        background: var(--success-light);
        border-radius: var(--radius-md);
        border-left: 4px solid var(--success-color);
    }
    
    .result-files h4 {
        margin: var(--spacing-md) 0 var(--spacing-sm) 0;
        color: var(--text-primary);
    }
    
    .result-files ul {
        list-style: none;
        padding: 0;
    }
    
    .result-files li {
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
        padding: var(--spacing-xs) 0;
        color: var(--text-secondary);
    }
    
    .results-actions {
        display: flex;
        gap: var(--spacing-sm);
        margin-top: var(--spacing-lg);
    }
`;
document.head.appendChild(style);
