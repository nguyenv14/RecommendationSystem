// Chat Application JavaScript

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const statusIndicator = document.getElementById('statusIndicator');
const statusDot = statusIndicator.querySelector('.status-dot');
const statusText = statusIndicator.querySelector('.status-text');
const sourcesModal = document.getElementById('sourcesModal');
const closeModal = document.getElementById('closeModal');
const sourcesContent = document.getElementById('sourcesContent');
const loadingOverlay = document.getElementById('loadingOverlay');

// API Configuration
const API_BASE_URL = window.location.origin;
const API_ENDPOINTS = {
    chat: `${API_BASE_URL}/api/chat`,
    search: `${API_BASE_URL}/api/search`,
    health: `${API_BASE_URL}/api/health`,
    status: `${API_BASE_URL}/api/status`
};

// State
let isProcessing = false;
let chatHistory = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

// Initialize Application
async function initializeApp() {
    // Check health status
    await checkHealth();
    
    // Auto-resize textarea
    messageInput.addEventListener('input', autoResizeTextarea);
    messageInput.addEventListener('keydown', handleKeyDown);
    
    // Send button
    sendButton.addEventListener('click', handleSend);
    
    // Modal close
    closeModal.addEventListener('click', () => {
        sourcesModal.classList.remove('show');
    });
    
    sourcesModal.addEventListener('click', (e) => {
        if (e.target === sourcesModal) {
            sourcesModal.classList.remove('show');
        }
    });
    
    // Enable/disable send button based on input
    messageInput.addEventListener('input', () => {
        sendButton.disabled = !messageInput.value.trim() || isProcessing;
    });
    
    // Focus input
    messageInput.focus();
}

// Check Health Status
async function checkHealth() {
    try {
        const response = await fetch(API_ENDPOINTS.health);
        const data = await response.json();
        
        if (data.status === 'ok' && data.rag_initialized && data.qdrant_connected) {
            updateStatus('connected', 'Đã sẵn sàng');
        } else {
            updateStatus('error', 'Chưa khởi tạo');
        }
    } catch (error) {
        console.error('Health check error:', error);
        updateStatus('error', 'Kết nối lỗi');
    }
}

// Update Status Indicator
function updateStatus(status, text) {
    statusDot.className = 'status-dot';
    if (status === 'connected') {
        statusDot.classList.add('connected');
    } else if (status === 'error') {
        statusDot.classList.add('error');
    }
    statusText.textContent = text;
}

// Auto-resize Textarea
function autoResizeTextarea() {
    messageInput.style.height = 'auto';
    messageInput.style.height = `${Math.min(messageInput.scrollHeight, 120)}px`;
}

// Handle Key Down
function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (!sendButton.disabled) {
            handleSend();
        }
    }
}

// Handle Send
async function handleSend() {
    const question = messageInput.value.trim();
    
    if (!question || isProcessing) {
        return;
    }
    
    // Add user message
    addMessage('user', question);
    
    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';
    sendButton.disabled = true;
    
    // Show typing indicator
    const typingId = addTypingIndicator();
    
    // Set processing state
    isProcessing = true;
    showLoading(true);
    
    try {
        // Send to API
        const response = await fetch(API_ENDPOINTS.chat, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        if (data.success) {
            // Add bot response
            addMessage('bot', data.answer, data.sources);
            
            // Update chat history
            chatHistory.push({
                question: data.question,
                answer: data.answer,
                sources: data.sources,
                timestamp: new Date()
            });
        } else {
            addMessage('bot', `❌ Lỗi: ${data.error || 'Không thể xử lý câu hỏi'}`);
        }
    } catch (error) {
        console.error('Chat error:', error);
        removeTypingIndicator(typingId);
        addMessage('bot', `❌ Lỗi kết nối: ${error.message}`);
    } finally {
        isProcessing = false;
        showLoading(false);
        messageInput.focus();
    }
}

// Add Message
function addMessage(type, content, sources = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    
    if (type === 'user') {
        avatar.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z" fill="currentColor"/></svg>';
    } else {
        avatar.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor"/></svg>';
    }
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    const messageText = document.createElement('div');
    messageText.className = 'message-text';
    
    // Format content (preserve line breaks)
    const formattedContent = formatMessage(content);
    messageText.innerHTML = formattedContent;
    
    const messageTime = document.createElement('div');
    messageTime.className = 'message-time';
    messageTime.textContent = getCurrentTime();
    
    messageContent.appendChild(messageText);
    
    // Add sources button if sources exist
    if (sources && sources.length > 0) {
        const sourcesButton = document.createElement('button');
        sourcesButton.className = 'sources-button';
        sourcesButton.textContent = `📚 Xem ${sources.length} nguồn tham khảo`;
        sourcesButton.addEventListener('click', () => {
            showSources(sources);
        });
        messageContent.appendChild(sourcesButton);
    }
    
    messageContent.appendChild(messageTime);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    scrollToBottom();
}

// Format Message
function formatMessage(content) {
    // Convert line breaks to <br>
    let formatted = content.replace(/\n/g, '<br>');
    
    // Wrap paragraphs
    formatted = formatted.split('<br><br>').map(p => {
        if (p.trim()) {
            return `<p>${p.trim()}</p>`;
        }
        return '';
    }).join('');
    
    return formatted;
}

// Add Typing Indicator
function addTypingIndicator() {
    const typingId = `typing-${Date.now()}`;
    const messageDiv = document.createElement('div');
    messageDiv.id = typingId;
    messageDiv.className = 'message bot-message';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor"/></svg>';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
    
    messageContent.appendChild(typingIndicator);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
    
    return typingId;
}

// Remove Typing Indicator
function removeTypingIndicator(id) {
    const typingElement = document.getElementById(id);
    if (typingElement) {
        typingElement.remove();
    }
}

// Show Sources
function showSources(sources) {
    sourcesContent.innerHTML = '';
    
    sources.forEach((source, index) => {
        const sourceDiv = document.createElement('div');
        sourceDiv.className = 'source-item';
        
        sourceDiv.innerHTML = `
            <div class="source-name">${source.hotel_name || `Khách sạn #${source.hotel_id}`}</div>
            <div class="source-details">
                ${source.hotel_rank ? `<span>⭐ ${source.hotel_rank} sao</span>` : ''}
                ${source.hotel_price_average ? `<span>💰 ${formatPrice(source.hotel_price_average)}</span>` : ''}
                ${source.area_name ? `<span>📍 ${source.area_name}</span>` : ''}
            </div>
            ${source.text_preview ? `<div class="source-preview">${source.text_preview}</div>` : ''}
        `;
        
        sourcesContent.appendChild(sourceDiv);
    });
    
    sourcesModal.classList.add('show');
}

// Format Price
function formatPrice(price) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(price);
}

// Get Current Time
function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('vi-VN', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Scroll to Bottom
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show Loading
function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
}

