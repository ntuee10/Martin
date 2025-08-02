// Martin Chrome Extension v2.0 - Grammarly-style UI
console.log('Martin v2.0: Developer prompt optimizer loaded');

// Configuration
const API_URL = 'http://localhost:8000/api/v2/analyze';
const DEBOUNCE_DELAY = 500;

// State management
let currentTextarea = null;
let martinUI = null;
let suggestions = [];
let isAnalyzing = false;
let optimizedPrompt = '';

// Detect current platform
function detectPlatform() {
  const hostname = window.location.hostname;
  const platforms = {
    'chat.openai.com': 'gpt-4',
    'claude.ai': 'claude-3',
    'cursor.sh': 'cursor',
    'gemini.google.com': 'gemini',
    'github.com': 'github-copilot'
  };
  return platforms[hostname] || 'gpt-4';
}

// Create Martin UI components
function createMartinUI() {
  // Remove existing UI if present
  const existing = document.getElementById('martin-ui-container');
  if (existing) existing.remove();

  // Main container
  const container = document.createElement('div');
  container.id = 'martin-ui-container';
  container.innerHTML = `
    <!-- Martin Button (Grammarly-style) -->
    <div id="martin-button" class="martin-button">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span class="martin-badge" id="martin-badge">0</span>
    </div>

    <!-- Suggestion Card (appears on hover/click) -->
    <div id="martin-suggestion-card" class="martin-suggestion-card">
      <div class="martin-card-header">
        <h3>Martin Suggestions</h3>
        <button class="martin-close-btn" onclick="closeMartinCard()">×</button>
      </div>
      <div class="martin-card-content" id="martin-suggestions-list">
        <!-- Suggestions will be inserted here -->
      </div>
      <div class="martin-card-footer">
        <button class="martin-btn martin-btn-primary" onclick="acceptAllSuggestions()">
          Accept All
        </button>
        <button class="martin-btn martin-btn-secondary" onclick="showOptimizedPrompt()">
          View Optimized
        </button>
      </div>
    </div>

    <!-- Optimized Prompt Modal -->
    <div id="martin-modal" class="martin-modal">
      <div class="martin-modal-content">
        <div class="martin-modal-header">
          <h2>Optimized Prompt</h2>
          <button class="martin-close-btn" onclick="closeMartinModal()">×</button>
        </div>
        <div class="martin-modal-body">
          <div class="martin-comparison">
            <div class="martin-original">
              <h4>Original</h4>
              <div id="martin-original-text"></div>
            </div>
            <div class="martin-optimized">
              <h4>Optimized</h4>
              <div id="martin-optimized-text"></div>
            </div>
          </div>
          <div class="martin-metrics" id="martin-metrics">
            <!-- Metrics will be inserted here -->
          </div>
        </div>
        <div class="martin-modal-footer">
          <button class="martin-btn martin-btn-primary" onclick="replaceWithOptimized()">
            Use Optimized
          </button>
          <button class="martin-btn martin-btn-secondary" onclick="copyOptimized()">
            Copy to Clipboard
          </button>
        </div>
      </div>
    </div>
  `;

  // Add styles
  const styles = document.createElement('style');
  styles.textContent = `
    /* Martin Button - Grammarly Style */
    .martin-button {
      position: fixed;
      bottom: 100px;
      right: 30px;
      width: 48px;
      height: 48px;
      background: white;
      border-radius: 50%;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      z-index: 10000;
      transition: all 0.2s ease;
      color: #3B82F6;
    }

    .martin-button:hover {
      transform: scale(1.05);
      box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);
    }

    .martin-button.analyzing {
      animation: pulse 1.5s infinite;
    }

    .martin-button.has-suggestions {
      color: #F59E0B;
    }

    .martin-button.optimized {
      color: #10B981;
    }

    @keyframes pulse {
      0% { opacity: 1; }
      50% { opacity: 0.6; }
      100% { opacity: 1; }
    }

    .martin-badge {
      position: absolute;
      top: -4px;
      right: -4px;
      background: #EF4444;
      color: white;
      border-radius: 10px;
      padding: 2px 6px;
      font-size: 11px;
      font-weight: bold;
      display: none;
    }

    .martin-badge.show {
      display: block;
    }

    /* Suggestion Card */
    .martin-suggestion-card {
      position: fixed;
      bottom: 160px;
      right: 30px;
      width: 380px;
      max-height: 400px;
      background: white;
      border-radius: 12px;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
      display: none;
      z-index: 10001;
      animation: slideIn 0.2s ease-out;
    }

    @keyframes slideIn {
      from {
        opacity: 0;
        transform: translateY(10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .martin-card-header {
      padding: 16px 20px;
      border-bottom: 1px solid #E5E7EB;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .martin-card-header h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: #1F2937;
    }

    .martin-close-btn {
      background: none;
      border: none;
      font-size: 24px;
      color: #6B7280;
      cursor: pointer;
      padding: 0;
      width: 28px;
      height: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .martin-close-btn:hover {
      color: #374151;
    }

    .martin-card-content {
      max-height: 260px;
      overflow-y: auto;
      padding: 12px 0;
    }

    /* Individual Suggestion */
    .martin-suggestion {
      padding: 12px 20px;
      border-bottom: 1px solid #F3F4F6;
      cursor: pointer;
      transition: background 0.2s;
    }

    .martin-suggestion:hover {
      background: #F9FAFB;
    }

    .martin-suggestion-type {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
      margin-bottom: 4px;
    }

    .martin-suggestion-type.clarity {
      background: #DBEAFE;
      color: #1E40AF;
    }

    .martin-suggestion-type.specificity {
      background: #FEF3C7;
      color: #92400E;
    }

    .martin-suggestion-type.token_optimization {
      background: #D1FAE5;
      color: #065F46;
    }

    .martin-suggestion-original {
      font-size: 13px;
      color: #6B7280;
      text-decoration: line-through;
      margin-bottom: 4px;
    }

    .martin-suggestion-new {
      font-size: 14px;
      color: #111827;
      font-weight: 500;
      margin-bottom: 4px;
    }

    .martin-suggestion-explanation {
      font-size: 12px;
      color: #6B7280;
    }

    .martin-card-footer {
      padding: 12px 20px;
      border-top: 1px solid #E5E7EB;
      display: flex;
      gap: 12px;
    }

    /* Buttons */
    .martin-btn {
      padding: 8px 16px;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      border: none;
      transition: all 0.2s;
      flex: 1;
    }

    .martin-btn-primary {
      background: #3B82F6;
      color: white;
    }

    .martin-btn-primary:hover {
      background: #2563EB;
    }

    .martin-btn-secondary {
      background: #F3F4F6;
      color: #374151;
    }

    .martin-btn-secondary:hover {
      background: #E5E7EB;
    }

    /* Modal */
    .martin-modal {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.5);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 10002;
    }

    .martin-modal.show {
      display: flex;
    }

    .martin-modal-content {
      width: 90%;
      max-width: 800px;
      background: white;
      border-radius: 12px;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
      animation: modalIn 0.3s ease-out;
    }

    @keyframes modalIn {
      from {
        opacity: 0;
        transform: scale(0.95);
      }
      to {
        opacity: 1;
        transform: scale(1);
      }
    }

    .martin-modal-header {
      padding: 24px;
      border-bottom: 1px solid #E5E7EB;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .martin-modal-header h2 {
      margin: 0;
      font-size: 20px;
      font-weight: 600;
      color: #111827;
    }

    .martin-modal-body {
      padding: 24px;
      max-height: 500px;
      overflow-y: auto;
    }

    .martin-comparison {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      margin-bottom: 24px;
    }

    .martin-original, .martin-optimized {
      background: #F9FAFB;
      padding: 16px;
      border-radius: 8px;
    }

    .martin-original h4, .martin-optimized h4 {
      margin: 0 0 12px 0;
      font-size: 14px;
      font-weight: 600;
      color: #6B7280;
    }

    .martin-optimized {
      background: #F0FDF4;
      border: 1px solid #86EFAC;
    }

    .martin-metrics {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      padding: 16px;
      background: #F3F4F6;
      border-radius: 8px;
    }

    .martin-metric {
      text-align: center;
    }

    .martin-metric-value {
      font-size: 24px;
      font-weight: 600;
      color: #111827;
    }

    .martin-metric-label {
      font-size: 12px;
      color: #6B7280;
    }

    .martin-modal-footer {
      padding: 16px 24px;
      border-top: 1px solid #E5E7EB;
      display: flex;
      gap: 12px;
      justify-content: flex-end;
    }

    /* Inline highlights */
    .martin-highlight {
      border-bottom: 2px dotted #F59E0B;
      cursor: pointer;
      position: relative;
    }

    .martin-highlight:hover {
      border-bottom-style: solid;
    }

    /* Loading state */
    .martin-loading {
      text-align: center;
      padding: 40px;
      color: #6B7280;
    }

    .martin-spinner {
      display: inline-block;
      width: 20px;
      height: 20px;
      border: 2px solid #E5E7EB;
      border-top-color: #3B82F6;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }
  `;

  document.head.appendChild(styles);
  document.body.appendChild(container);
  
  return container;
}

// Initialize Martin UI
martinUI = createMartinUI();

// API Functions
async function analyzePrompt(text) {
  if (!text || text.length < 10) return null;
  
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer demo-token'
      },
      body: JSON.stringify({
        prompt: text,
        target_model: detectPlatform(),
        context: {
          domain: 'code_generation'
        },
        options: {
          aggressive_optimization: true
        }
      })
    });

    if (!response.ok) throw new Error('API error');
    
    return await response.json();
  } catch (error) {
    console.error('Martin API error:', error);
    return null;
  }
}

// UI Update Functions
function updateMartinButton(state) {
  const button = document.getElementById('martin-button');
  const badge = document.getElementById('martin-badge');
  
  button.className = 'martin-button';
  
  switch(state) {
    case 'analyzing':
      button.classList.add('analyzing');
      badge.classList.remove('show');
      break;
    case 'suggestions':
      button.classList.add('has-suggestions');
      badge.textContent = suggestions.length;
      badge.classList.add('show');
      break;
    case 'optimized':
      button.classList.add('optimized');
      badge.classList.remove('show');
      break;
    default:
      badge.classList.remove('show');
  }
}

function showSuggestions() {
  const card = document.getElementById('martin-suggestion-card');
  const list = document.getElementById('martin-suggestions-list');
  
  if (suggestions.length === 0) {
    list.innerHTML = '<div class="martin-loading">No suggestions available</div>';
  } else {
    list.innerHTML = suggestions.map((suggestion, index) => `
      <div class="martin-suggestion" onclick="applySuggestion(${index})">
        <span class="martin-suggestion-type ${suggestion.type}">${suggestion.type.replace('_', ' ')}</span>
        <div class="martin-suggestion-original">${suggestion.original}</div>
        <div class="martin-suggestion-new">${suggestion.suggested || 'Remove'}</div>
        <div class="martin-suggestion-explanation">${suggestion.explanation}</div>
      </div>
    `).join('');
  }
  
  card.style.display = 'block';
}

function showOptimizedPrompt() {
  const modal = document.getElementById('martin-modal');
  const originalText = document.getElementById('martin-original-text');
  const optimizedText = document.getElementById('martin-optimized-text');
  
  originalText.textContent = currentTextarea.value;
  optimizedText.textContent = optimizedPrompt;
  
  modal.classList.add('show');
}

// Event Handlers
window.closeMartinCard = function() {
  document.getElementById('martin-suggestion-card').style.display = 'none';
};

window.closeMartinModal = function() {
  document.getElementById('martin-modal').classList.remove('show');
};

window.applySuggestion = function(index) {
  const suggestion = suggestions[index];
  if (currentTextarea && suggestion) {
    let text = currentTextarea.value;
    text = text.replace(suggestion.original, suggestion.suggested);
    currentTextarea.value = text;
    currentTextarea.dispatchEvent(new Event('input', { bubbles: true }));
    
    // Remove applied suggestion
    suggestions.splice(index, 1);
    updateMartinButton(suggestions.length > 0 ? 'suggestions' : 'default');
    
    if (suggestions.length > 0) {
      showSuggestions();
    } else {
      closeMartinCard();
    }
  }
};

window.acceptAllSuggestions = function() {
  if (currentTextarea && optimizedPrompt) {
    currentTextarea.value = optimizedPrompt;
    currentTextarea.dispatchEvent(new Event('input', { bubbles: true }));
    closeMartinCard();
    updateMartinButton('optimized');
    
    // Reset after 2 seconds
    setTimeout(() => {
      updateMartinButton('default');
    }, 2000);
  }
};

window.replaceWithOptimized = function() {
  acceptAllSuggestions();
  closeMartinModal();
};

window.copyOptimized = function() {
  navigator.clipboard.writeText(optimizedPrompt).then(() => {
    const btn = event.target;
    const originalText = btn.textContent;
    btn.textContent = 'Copied!';
    btn.style.background = '#10B981';
    
    setTimeout(() => {
      btn.textContent = originalText;
      btn.style.background = '';
    }, 2000);
  });
};

// Debounce function
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Analyze text with debounce
const analyzeText = debounce(async (text) => {
  if (isAnalyzing || !text || text.length < 10) return;
  
  isAnalyzing = true;
  updateMartinButton('analyzing');
  
  const result = await analyzePrompt(text);
  
  if (result) {
    suggestions = result.suggestions;
    optimizedPrompt = result.optimized_prompt;
    
    // Update metrics display
    if (result.metrics) {
      const metricsDiv = document.getElementById('martin-metrics');
      metricsDiv.innerHTML = `
        <div class="martin-metric">
          <div class="martin-metric-value">${Math.round(result.metrics.clarity_score)}%</div>
          <div class="martin-metric-label">Clarity</div>
        </div>
        <div class="martin-metric">
          <div class="martin-metric-value">${Math.round(result.metrics.specificity_score)}%</div>
          <div class="martin-metric-label">Specificity</div>
        </div>
        <div class="martin-metric">
          <div class="martin-metric-value">${result.metrics.token_reduction}</div>
          <div class="martin-metric-label">Tokens Saved</div>
        </div>
        <div class="martin-metric">
          <div class="martin-metric-value">$${result.metrics.estimated_cost_savings.toFixed(3)}</div>
          <div class="martin-metric-label">Cost Saved</div>
        </div>
      `;
    }
    
    updateMartinButton(suggestions.length > 0 ? 'suggestions' : 'optimized');
  } else {
    updateMartinButton('default');
  }
  
  isAnalyzing = false;
}, DEBOUNCE_DELAY);

// Find and monitor textarea
function findAndMonitorTextarea() {
  const selectors = [
    'textarea[placeholder*="Send a message"]',
    'textarea[placeholder*="Talk to Claude"]',
    'textarea[placeholder*="Enter a prompt"]',
    'textarea[placeholder*="Type a message"]',
    'textarea[data-id="root"]',
    '[contenteditable="true"]',
    'textarea'
  ];
  
  for (const selector of selectors) {
    const element = document.querySelector(selector);
    if (element) {
      currentTextarea = element;
      
      // Add input listener
      element.addEventListener('input', (e) => {
        analyzeText(e.target.value || e.target.textContent);
      });
      
      // Add focus listener
      element.addEventListener('focus', () => {
        const text = element.value || element.textContent;
        if (text && text.length > 10) {
          analyzeText(text);
        }
      });
      
      console.log('Martin: Monitoring textarea for prompts');
      return true;
    }
  }
  
  return false;
}

// Martin button click handler
document.getElementById('martin-button').addEventListener('click', () => {
  if (suggestions.length > 0 || optimizedPrompt) {
    showSuggestions();
  } else if (currentTextarea) {
    const text = currentTextarea.value || currentTextarea.textContent;
    if (text && text.length > 10) {
      analyzeText(text);
    }
  }
});

// Initialize monitoring
let retryCount = 0;
const maxRetries = 20;

function initializeMonitoring() {
  if (findAndMonitorTextarea()) {
    console.log('Martin v2.0: Ready to optimize your prompts!');
  } else if (retryCount < maxRetries) {
    retryCount++;
    setTimeout(initializeMonitoring, 1000);
  } else {
    console.log('Martin: Could not find textarea after multiple attempts');
  }
}

// Start monitoring after page loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeMonitoring);
} else {
  setTimeout(initializeMonitoring, 1000);
}

// Listen for dynamic content changes
const observer = new MutationObserver((mutations) => {
  if (!currentTextarea || !document.body.contains(currentTextarea)) {
    findAndMonitorTextarea();
  }
});

observer.observe(document.body, {
  childList: true,
  subtree: true
});

console.log('Martin v2.0: Extension initialized successfully');
