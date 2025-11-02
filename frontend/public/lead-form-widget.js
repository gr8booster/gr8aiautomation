/**
 * GR8 Lead Capture Form Widget - Embeddable JavaScript
 * This script creates a functional lead capture form on any website
 */
(function() {
  'use strict';

  let config = {
    formId: null,
    apiUrl: null,
    theme: 'light',
    primaryColor: '#0c969b',
    position: 'inline', // 'inline' or 'popup'
    submitText: 'Submit',
    successMessage: 'Thank you! We\'ll be in touch soon.'
  };

  window.GR8LeadForm = {
    init: function(userConfig) {
      config = { ...config, ...userConfig };
      
      if (!config.formId || !config.apiUrl) {
        console.error('GR8 LeadForm: formId and apiUrl are required');
        return;
      }

      injectStyles();
      createForm();
      attachEventListeners();
      
      console.log('GR8 Lead Form initialized');
    }
  };

  function injectStyles() {
    const styles = `
      .gr8-form-container {
        max-width: 500px;
        margin: 0 auto;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }
      
      .gr8-form {
        background: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      }
      
      .gr8-form-title {
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 8px;
        color: #111827;
      }
      
      .gr8-form-description {
        font-size: 14px;
        color: #6b7280;
        margin-bottom: 20px;
      }
      
      .gr8-form-field {
        margin-bottom: 16px;
      }
      
      .gr8-form-label {
        display: block;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 6px;
        color: #374151;
      }
      
      .gr8-form-label .required {
        color: #ef4444;
        margin-left: 2px;
      }
      
      .gr8-form-input,
      .gr8-form-textarea {
        width: 100%;
        padding: 10px 12px;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        font-size: 14px;
        font-family: inherit;
        transition: border-color 0.2s;
      }
      
      .gr8-form-input:focus,
      .gr8-form-textarea:focus {
        outline: none;
        border-color: ${config.primaryColor};
        box-shadow: 0 0 0 3px ${config.primaryColor}20;
      }
      
      .gr8-form-textarea {
        resize: vertical;
        min-height: 100px;
      }
      
      .gr8-form-error {
        color: #ef4444;
        font-size: 12px;
        margin-top: 4px;
      }
      
      .gr8-form-submit {
        width: 100%;
        background: ${config.primaryColor};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: 500;
        cursor: pointer;
        transition: opacity 0.2s;
      }
      
      .gr8-form-submit:hover {
        opacity: 0.9;
      }
      
      .gr8-form-submit:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
      
      .gr8-form-success {
        background: #f0fdf4;
        border: 1px solid #86efac;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
      }
      
      .gr8-form-success-icon {
        width: 48px;
        height: 48px;
        margin: 0 auto 12px;
        background: #22c55e;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 24px;
      }
      
      .gr8-form-success-title {
        font-size: 18px;
        font-weight: 600;
        color: #166534;
        margin-bottom: 8px;
      }
      
      .gr8-form-success-message {
        font-size: 14px;
        color: #166534;
      }
      
      .gr8-form-loading {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
      }
      
      .gr8-form-spinner {
        width: 16px;
        height: 16px;
        border: 2px solid white;
        border-top-color: transparent;
        border-radius: 50%;
        animation: spin 0.6s linear infinite;
      }
      
      @keyframes spin {
        to { transform: rotate(360deg); }
      }
    `;
    
    const styleSheet = document.createElement('style');
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);
  }

  function createForm() {
    const container = document.getElementById('gr8-lead-form');
    if (!container) {
      console.error('GR8 LeadForm: Container element #gr8-lead-form not found');
      return;
    }
    
    container.innerHTML = `
      <div class="gr8-form-container">
        <div class="gr8-form" id="gr8-form-content">
          <h2 class="gr8-form-title">Get in Touch</h2>
          <p class="gr8-form-description">Fill out the form below and we'll get back to you soon.</p>
          
          <form id="gr8-form-element">
            <div class="gr8-form-field">
              <label class="gr8-form-label">
                Name <span class="required">*</span>
              </label>
              <input 
                type="text" 
                name="name" 
                class="gr8-form-input" 
                required
              />
              <div class="gr8-form-error" id="error-name"></div>
            </div>
            
            <div class="gr8-form-field">
              <label class="gr8-form-label">
                Email <span class="required">*</span>
              </label>
              <input 
                type="email" 
                name="email" 
                class="gr8-form-input" 
                required
              />
              <div class="gr8-form-error" id="error-email"></div>
            </div>
            
            <div class="gr8-form-field">
              <label class="gr8-form-label">
                Phone
              </label>
              <input 
                type="tel" 
                name="phone" 
                class="gr8-form-input"
              />
            </div>
            
            <div class="gr8-form-field">
              <label class="gr8-form-label">
                Message <span class="required">*</span>
              </label>
              <textarea 
                name="message" 
                class="gr8-form-textarea" 
                required
              ></textarea>
              <div class="gr8-form-error" id="error-message"></div>
            </div>
            
            <button type="submit" class="gr8-form-submit" id="gr8-form-submit-btn">
              ${config.submitText}
            </button>
          </form>
        </div>
      </div>
    `;
  }

  function attachEventListeners() {
    const form = document.getElementById('gr8-form-element');
    if (form) {
      form.addEventListener('submit', handleSubmit);
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const submitBtn = document.getElementById('gr8-form-submit-btn');
    const formData = new FormData(form);
    
    // Clear previous errors
    document.querySelectorAll('.gr8-form-error').forEach(el => el.textContent = '');
    
    // Get form data
    const data = {
      name: formData.get('name'),
      email: formData.get('email'),
      phone: formData.get('phone'),
      message: formData.get('message')
    };
    
    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<div class="gr8-form-loading"><div class="gr8-form-spinner"></div> Sending...</div>';
    
    try {
      const response = await fetch(`${config.apiUrl}/forms/${config.formId}/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data })
      });
      
      const result = await response.json();
      
      if (response.ok) {
        showSuccess(result.autoresponse);
      } else {
        throw new Error(result.detail || 'Submission failed');
      }
    } catch (error) {
      console.error('Form submission error:', error);
      submitBtn.disabled = false;
      submitBtn.textContent = config.submitText;
      alert('Sorry, there was an error submitting the form. Please try again.');
    }
  }

  function showSuccess(autoresponse) {
    const container = document.getElementById('gr8-form-content');
    container.innerHTML = `
      <div class="gr8-form-success">
        <div class="gr8-form-success-icon">✓</div>
        <h3 class="gr8-form-success-title">Thank You!</h3>
        <p class="gr8-form-success-message">${config.successMessage}</p>
        ${autoresponse ? `<p class="gr8-form-success-message" style="margin-top: 12px; font-style: italic; font-size: 13px;">${autoresponse}</p>` : ''}
      </div>
    `;
  }

})();
