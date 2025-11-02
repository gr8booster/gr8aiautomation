/**
 * GR8 AI Chatbot Widget - Embeddable JavaScript
 * This script creates a functional chatbot widget on any website
 */
(function() {
  'use strict';

  // Widget Configuration
  let config = {
    websiteId: null,
    apiUrl: null,
    position: 'bottom-right',
    theme: 'light',
    primaryColor: '#0c969b',
    greeting: 'Hi! How can I help you today?'
  };

  // Session Management
  let sessionId = null;
  let isOpen = false;
  let messageHistory = [];

  // Initialize Widget
  window.GR8Chatbot = {
    init: function(userConfig) {
      config = { ...config, ...userConfig };
      
      if (!config.websiteId || !config.apiUrl) {
        console.error('GR8 Chatbot: websiteId and apiUrl are required');
        return;
      }

      // Generate or retrieve session ID
      sessionId = getSessionId();
      
      // Inject styles
      injectStyles();
      
      // Create widget HTML
      createWidget();
      
      // Add event listeners
      attachEventListeners();
      
      console.log('GR8 Chatbot initialized');
    }
  };

  function getSessionId() {
    let sid = localStorage.getItem('gr8_chatbot_session_' + config.websiteId);
    if (!sid) {
      sid = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('gr8_chatbot_session_' + config.websiteId, sid);
    }
    return sid;
  }

  function injectStyles() {
    const styles = `
      #gr8-chatbot-container {
        position: fixed;
        ${config.position.includes('right') ? 'right: 20px;' : 'left: 20px;'}
        ${config.position.includes('bottom') ? 'bottom: 20px;' : 'top: 20px;'}
        z-index: 999999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }
      
      #gr8-chatbot-button {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: ${config.primaryColor};
        border: none;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.2s;
      }
      
      #gr8-chatbot-button:hover {
        transform: scale(1.1);
      }
      
      #gr8-chatbot-button svg {
        width: 28px;
        height: 28px;
        fill: white;
      }
      
      #gr8-chatbot-window {
        position: absolute;
        ${config.position.includes('right') ? 'right: 0;' : 'left: 0;'}
        ${config.position.includes('bottom') ? 'bottom: 70px;' : 'top: 70px;'}
        width: 380px;
        height: 500px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        display: none;
        flex-direction: column;
        overflow: hidden;
      }
      
      #gr8-chatbot-window.open {
        display: flex;
        animation: slideUp 0.3s ease-out;
      }
      
      @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
      }
      
      #gr8-chatbot-header {
        background: ${config.primaryColor};
        color: white;
        padding: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      
      #gr8-chatbot-header h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
      }
      
      #gr8-chatbot-close {
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        font-size: 24px;
        line-height: 1;
        padding: 0;
        width: 24px;
        height: 24px;
      }
      
      #gr8-chatbot-messages {
        flex: 1;
        overflow-y: auto;
        padding: 16px;
        background: #f9fafb;
      }
      
      .gr8-message {
        margin-bottom: 12px;
        display: flex;
        gap: 8px;
      }
      
      .gr8-message.user {
        flex-direction: row-reverse;
      }
      
      .gr8-message-bubble {
        max-width: 70%;
        padding: 10px 14px;
        border-radius: 12px;
        font-size: 14px;
        line-height: 1.4;
      }
      
      .gr8-message.bot .gr8-message-bubble {
        background: white;
        border: 1px solid #e5e7eb;
        color: #374151;
      }
      
      .gr8-message.user .gr8-message-bubble {
        background: ${config.primaryColor};
        color: white;
      }
      
      .gr8-typing {
        display: flex;
        gap: 4px;
        padding: 10px 14px;
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        width: fit-content;
      }
      
      .gr8-typing span {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #9ca3af;
        animation: typing 1.4s infinite;
      }
      
      .gr8-typing span:nth-child(2) { animation-delay: 0.2s; }
      .gr8-typing span:nth-child(3) { animation-delay: 0.4s; }
      
      @keyframes typing {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-10px); }
      }
      
      #gr8-chatbot-input-area {
        padding: 12px;
        border-top: 1px solid #e5e7eb;
        background: white;
        display: flex;
        gap: 8px;
      }
      
      #gr8-chatbot-input {
        flex: 1;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 10px 12px;
        font-size: 14px;
        outline: none;
        resize: none;
        font-family: inherit;
      }
      
      #gr8-chatbot-input:focus {
        border-color: ${config.primaryColor};
      }
      
      #gr8-chatbot-send {
        background: ${config.primaryColor};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 16px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
      }
      
      #gr8-chatbot-send:hover {
        opacity: 0.9;
      }
      
      #gr8-chatbot-send:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
      
      @media (max-width: 480px) {
        #gr8-chatbot-window {
          width: calc(100vw - 40px);
          height: calc(100vh - 100px);
        }
      }
    `;
    
    const styleSheet = document.createElement('style');
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);
  }

  function createWidget() {
    const container = document.createElement('div');
    container.id = 'gr8-chatbot-container';
    container.innerHTML = `
      <button id="gr8-chatbot-button" aria-label="Open chat">
        <svg viewBox="0 0 24 24">
          <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
        </svg>
      </button>
      
      <div id="gr8-chatbot-window">
        <div id="gr8-chatbot-header">
          <h3>Chat with us</h3>
          <button id="gr8-chatbot-close" aria-label="Close chat">&times;</button>
        </div>
        
        <div id="gr8-chatbot-messages">
          <div class="gr8-message bot">
            <div class="gr8-message-bubble">${config.greeting}</div>
          </div>
        </div>
        
        <div id="gr8-chatbot-input-area">
          <textarea 
            id="gr8-chatbot-input" 
            placeholder="Type your message..." 
            rows="1"
          ></textarea>
          <button id="gr8-chatbot-send">Send</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(container);
  }

  function attachEventListeners() {
    const button = document.getElementById('gr8-chatbot-button');
    const closeBtn = document.getElementById('gr8-chatbot-close');
    const input = document.getElementById('gr8-chatbot-input');
    const sendBtn = document.getElementById('gr8-chatbot-send');
    
    button.addEventListener('click', toggleChat);
    closeBtn.addEventListener('click', toggleChat);
    sendBtn.addEventListener('click', sendMessage);
    
    input.addEventListener('keypress', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  }

  function toggleChat() {
    isOpen = !isOpen;
    const window = document.getElementById('gr8-chatbot-window');
    
    if (isOpen) {
      window.classList.add('open');
      document.getElementById('gr8-chatbot-input').focus();
    } else {
      window.classList.remove('open');
    }
  }

  function sendMessage() {
    const input = document.getElementById('gr8-chatbot-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to UI
    addMessage(message, 'user');
    input.value = '';
    
    // Show typing indicator
    showTyping();
    
    // Send to API
    fetch(config.apiUrl + '/chatbot/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        website_id: config.websiteId,
        session_id: sessionId,
        message: message
      })
    })
    .then(res => res.json())
    .then(data => {
      hideTyping();
      if (data.response) {
        addMessage(data.response, 'bot');
      } else {
        addMessage('Sorry, I encountered an error. Please try again.', 'bot');
      }
    })
    .catch(error => {
      console.error('Chat error:', error);
      hideTyping();
      addMessage('Sorry, I couldn\'t process your message. Please try again.', 'bot');
    });
  }

  function addMessage(text, role) {
    const messagesContainer = document.getElementById('gr8-chatbot-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `gr8-message ${role}`;
    messageDiv.innerHTML = `<div class="gr8-message-bubble">${escapeHtml(text)}</div>`;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    messageHistory.push({ role, text });
  }

  function showTyping() {
    const messagesContainer = document.getElementById('gr8-chatbot-messages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'gr8-typing-indicator';
    typingDiv.className = 'gr8-message bot';
    typingDiv.innerHTML = `
      <div class="gr8-typing">
        <span></span><span></span><span></span>
      </div>
    `;
    
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function hideTyping() {
    const typingDiv = document.getElementById('gr8-typing-indicator');
    if (typingDiv) typingDiv.remove();
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

})();
