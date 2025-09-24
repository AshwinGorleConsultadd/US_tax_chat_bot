/**
 * US Tax Chatbot - Frontend JavaScript
 * 
 * This file handles the frontend functionality and integrates with the Python backend
 * to provide a seamless chat experience for the US Tax Chatbot.
 */

class TaxChatbot {
    constructor() {
        this.chatHistory = [];
        this.isLoading = false;
        this.currentSessionId = this.generateSessionId();
        
        // DOM elements
        this.elements = {
            messageInput: document.getElementById('messageInput'),
            sendBtn: document.getElementById('sendBtn'),
            chatMessages: document.getElementById('chatMessages'),
            welcomeMessage: document.getElementById('welcomeMessage'),
            typingIndicator: document.getElementById('typingIndicator'),
            statusIndicator: document.getElementById('statusIndicator'),
            resetBtn: document.getElementById('resetBtn'),
            feedDataBtn: document.getElementById('feedDataBtn'),
            sidebar: document.getElementById('sidebar'),
            toggleSidebar: document.getElementById('toggleSidebar'),
            mobileMenuBtn: document.getElementById('mobileMenuBtn'),
            chatSessions: document.getElementById('chatSessions'),
            charCount: document.getElementById('charCount'),
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
        this.setupAutoResize();
        this.updateCharCount();
        this.loadChatSessions();
        this.updateStatus('ready');
    }
    
    setupEventListeners() {
        // Send message events
        this.elements.sendBtn.addEventListener('click', () => this.sendMessage());
        this.elements.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Input events
        this.elements.messageInput.addEventListener('input', () => {
            this.updateCharCount();
            this.toggleSendButton();
        });
        
        // Reset chat
        this.elements.resetBtn.addEventListener('click', () => this.resetChat());
        
        // Feed Data button
        this.elements.feedDataBtn.addEventListener('click', () => this.goToUpload());
        
        // Sidebar events
        this.elements.toggleSidebar.addEventListener('click', () => this.toggleSidebar());
        this.elements.mobileMenuBtn.addEventListener('click', () => this.toggleSidebar());
        
        // Modal events
        this.elements.closeErrorModal.addEventListener('click', () => this.hideErrorModal());
        this.elements.retryBtn.addEventListener('click', () => {
            this.hideErrorModal();
            this.sendMessage();
        });
        
        // Click outside sidebar to close
        document.addEventListener('click', (e) => {
            if (!this.elements.sidebar.contains(e.target) && 
                !this.elements.mobileMenuBtn.contains(e.target) && 
                this.elements.sidebar.classList.contains('open')) {
                this.toggleSidebar();
            }
        });
        
        // Example questions click
        document.querySelectorAll('.example-questions li').forEach(li => {
            li.addEventListener('click', () => {
                this.elements.messageInput.value = li.textContent.trim();
                this.updateCharCount();
                this.toggleSendButton();
                this.elements.messageInput.focus();
            });
        });
    }
    
    setupAutoResize() {
        this.elements.messageInput.addEventListener('input', () => {
            this.elements.messageInput.style.height = 'auto';
            this.elements.messageInput.style.height = Math.min(this.elements.messageInput.scrollHeight, 120) + 'px';
        });
    }
    
    updateCharCount() {
        const count = this.elements.messageInput.value.length;
        this.elements.charCount.textContent = `${count}/1000`;
        
        if (count > 900) {
            this.elements.charCount.style.color = 'var(--warning-color)';
        } else if (count > 800) {
            this.elements.charCount.style.color = 'var(--text-secondary)';
        } else {
            this.elements.charCount.style.color = 'var(--text-muted)';
        }
    }
    
    toggleSendButton() {
        const hasText = this.elements.messageInput.value.trim().length > 0;
        this.elements.sendBtn.disabled = !hasText || this.isLoading;
    }
    
    async sendMessage() {
        const message = this.elements.messageInput.value.trim();
        if (!message || this.isLoading) return;
        
        // Hide welcome message
        this.elements.welcomeMessage.style.display = 'none';
        
        // Add user message to chat
        this.addMessage('user', message);
        
        // Clear input
        this.elements.messageInput.value = '';
        this.elements.messageInput.style.height = 'auto';
        this.updateCharCount();
        this.toggleSendButton();
        
        // Show typing indicator
        this.showTypingIndicator();
        this.updateStatus('thinking');
        
        try {
            // Call Python backend
            const response = await this.callBackend('send_message', { message });
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            if (response.success) {
                this.addMessage('assistant', response.data.response);
                this.updateStatus('ready');
            } else {
                throw new Error(response.error || 'Failed to get response');
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.updateStatus('error');
            this.showError('Failed to send message. Please try again.');
        }
    }
    
    async resetChat() {
        if (this.isLoading) return;
        
        try {
            this.updateStatus('thinking');
            await this.callBackend('reset_chat', {});
            
            // Clear chat UI
            this.elements.chatMessages.innerHTML = '';
            this.elements.welcomeMessage.style.display = 'flex';
            this.chatHistory = [];
            this.currentSessionId = this.generateSessionId();
            
            this.updateStatus('ready');
            this.showSuccessMessage('Chat has been reset successfully!');
            
        } catch (error) {
            console.error('Error resetting chat:', error);
            this.updateStatus('error');
            this.showError('Failed to reset chat. Please try again.');
        }
    }
    
    async callBackend(endpoint, data) {
        const response = await fetch(`/api/${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    addMessage(type, content, timestamp = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const time = timestamp || new Date().toLocaleTimeString();
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-header">
                    <i class="fas ${type === 'user' ? 'fa-user' : 'fa-robot'}"></i>
                    <span>${type === 'user' ? 'You' : 'Tax Assistant'}</span>
                </div>
                <div class="message-text">${this.formatMessage(content)}</div>
                <div class="message-time">${time}</div>
            </div>
        `;
        
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Add to chat history
        this.chatHistory.push({
            type,
            content,
            timestamp: time,
            sessionId: this.currentSessionId
        });
    }
    
    formatMessage(content) {
        // Enhanced markdown formatting for better readability
        let formatted = content;
        
        // Handle markdown headers (must be processed first)
        formatted = formatted
            .replace(/^### (.*$)/gm, '<h3>$1</h3>')
            .replace(/^## (.*$)/gm, '<h2>$1</h2>')
            .replace(/^# (.*$)/gm, '<h1>$1</h1>');
        
        // Handle line breaks
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Handle bold text
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Handle italic text
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Handle inline code
        formatted = formatted.replace(/`(.*?)`/g, '<code>$1</code>');
        
        // Handle code blocks (triple backticks)
        formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        
        // Handle unordered lists
        formatted = formatted.replace(/^[\s]*[-*+] (.*$)/gm, '<li>$1</li>');
        
        // Handle ordered lists  
        formatted = formatted.replace(/^[\s]*\d+\. (.*$)/gm, '<li>$1</li>');
        
        // Wrap consecutive list items in appropriate list tags
        formatted = formatted.replace(/(<li>.*<\/li>)(\s*<li>.*<\/li>)*/gs, (match) => {
            // Check if it contains ordered list pattern (digits)
            if (/\d+\./.test(match)) {
                return '<ol>' + match + '</ol>';
            } else {
                return '<ul>' + match + '</ul>';
            }
        });
        
        // Handle links
        formatted = formatted.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
        
        return formatted;
    }
    
    showTypingIndicator() {
        this.elements.typingIndicator.classList.add('show');
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.elements.typingIndicator.classList.remove('show');
    }
    
    updateStatus(status) {
        const statusText = {
            'ready': 'Ready',
            'thinking': 'Thinking...',
            'error': 'Error'
        };
        
        this.elements.statusIndicator.innerHTML = `
            <i class="fas fa-circle"></i>
            <span>${statusText[status]}</span>
        `;
        
        this.elements.statusIndicator.className = `status-indicator ${status}`;
    }
    
    toggleSidebar() {
        this.elements.sidebar.classList.toggle('open');
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
        }, 100);
    }
    
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    loadChatSessions() {
        // Load chat sessions from localStorage
        const sessions = JSON.parse(localStorage.getItem('chatSessions') || '[]');
        
        this.elements.chatSessions.innerHTML = '';
        
        if (sessions.length === 0) {
            this.elements.chatSessions.innerHTML = '<p style="text-align: center; color: var(--text-muted); padding: var(--spacing-lg);">No chat sessions yet</p>';
            return;
        }
        
        sessions.forEach(session => {
            const sessionDiv = document.createElement('div');
            sessionDiv.className = 'chat-session';
            sessionDiv.innerHTML = `
                <div style="font-weight: 500;">${session.title}</div>
                <div style="font-size: 0.8rem; color: var(--text-muted);">${session.timestamp}</div>
            `;
            
            sessionDiv.addEventListener('click', () => {
                this.loadChatSession(session);
            });
            
            this.elements.chatSessions.appendChild(sessionDiv);
        });
    }
    
    loadChatSession(session) {
        // Implementation for loading a specific chat session
        console.log('Loading session:', session);
        // This would restore the chat history from the session
    }
    
    saveChatSession() {
        if (this.chatHistory.length === 0) return;
        
        const sessions = JSON.parse(localStorage.getItem('chatSessions') || '[]');
        const firstMessage = this.chatHistory.find(msg => msg.type === 'user');
        
        if (firstMessage) {
            const session = {
                id: this.currentSessionId,
                title: firstMessage.content.substring(0, 50) + (firstMessage.content.length > 50 ? '...' : ''),
                timestamp: new Date().toLocaleString(),
                chatHistory: this.chatHistory
            };
            
            sessions.unshift(session);
            
            // Keep only last 10 sessions
            if (sessions.length > 10) {
                sessions.splice(10);
            }
            
            localStorage.setItem('chatSessions', JSON.stringify(sessions));
        }
    }
    
    showError(message) {
        this.elements.errorMessage.textContent = message;
        this.elements.errorModal.classList.add('show');
    }
    
    hideErrorModal() {
        this.elements.errorModal.classList.remove('show');
    }
    
    showSuccessMessage(message) {
        // Create a temporary success message
        const successDiv = document.createElement('div');
        successDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--success-color);
            color: white;
            padding: var(--spacing-md) var(--spacing-lg);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-md);
            z-index: 1000;
            animation: slideInRight 0.3s ease-out;
        `;
        successDiv.textContent = message;
        
        document.body.appendChild(successDiv);
        
        setTimeout(() => {
            successDiv.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => {
                document.body.removeChild(successDiv);
            }, 300);
        }, 3000);
    }
    
    showLoading() {
        this.elements.loadingOverlay.classList.add('show');
    }
    
    hideLoading() {
        this.elements.loadingOverlay.classList.remove('show');
    }
    
    goToUpload() {
        window.location.href = '/upload.html';
    }
}

// Initialize the chatbot when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.taxChatbot = new TaxChatbot();
});

// Add CSS animations for success messages
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Save current session when page becomes hidden
        if (window.taxChatbot) {
            window.taxChatbot.saveChatSession();
        }
    }
});

// Handle beforeunload to save session
window.addEventListener('beforeunload', () => {
    if (window.taxChatbot) {
        window.taxChatbot.saveChatSession();
    }
});

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TaxChatbot;
}
