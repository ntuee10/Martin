// Martin Popup Script
document.addEventListener('DOMContentLoaded', async () => {
  // Elements
  const statusIndicator = document.getElementById('status-indicator');
  const statusTitle = document.getElementById('status-title');
  const statusDescription = document.getElementById('status-description');
  const enableToggle = document.getElementById('enable-martin');
  const highlightsToggle = document.getElementById('show-highlights');
  const autoAnalyzeToggle = document.getElementById('auto-analyze');
  const promptsOptimized = document.getElementById('prompts-optimized');
  const tokensSaved = document.getElementById('tokens-saved');
  const clearStatsBtn = document.getElementById('clear-stats');
  const reportIssueLink = document.getElementById('report-issue');

  // Check API connection
  async function checkAPIConnection() {
    try {
      const response = await fetch('http://localhost:8000/api/v2/health');
      if (response.ok) {
        const data = await response.json();
        statusIndicator.className = 'status-indicator connected';
        statusTitle.textContent = 'Connected';
        statusDescription.textContent = `API ${data.mode} mode`;
      } else {
        throw new Error('API not responding');
      }
    } catch (error) {
      statusIndicator.className = 'status-indicator disconnected';
      statusTitle.textContent = 'Disconnected';
      statusDescription.textContent = 'Start the Martin backend';
    }
  }

  // Load settings
  async function loadSettings() {
    const settings = await chrome.storage.sync.get({
      enabled: true,
      showHighlights: true,
      autoAnalyze: true,
      stats: {
        promptsOptimized: 0,
        tokensSaved: 0
      }
    });

    enableToggle.checked = settings.enabled;
    highlightsToggle.checked = settings.showHighlights;
    autoAnalyzeToggle.checked = settings.autoAnalyze;
    promptsOptimized.textContent = settings.stats.promptsOptimized;
    tokensSaved.textContent = settings.stats.tokensSaved;
  }

  // Save settings
  async function saveSettings() {
    await chrome.storage.sync.set({
      enabled: enableToggle.checked,
      showHighlights: highlightsToggle.checked,
      autoAnalyze: autoAnalyzeToggle.checked
    });

    // Notify content script
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tabs[0]) {
      chrome.tabs.sendMessage(tabs[0].id, {
        type: 'settingsUpdated',
        settings: {
          enabled: enableToggle.checked,
          showHighlights: highlightsToggle.checked,
          autoAnalyze: autoAnalyzeToggle.checked
        }
      });
    }
  }

  // Event listeners
  enableToggle.addEventListener('change', saveSettings);
  highlightsToggle.addEventListener('change', saveSettings);
  autoAnalyzeToggle.addEventListener('change', saveSettings);

  clearStatsBtn.addEventListener('click', async () => {
    await chrome.storage.sync.set({
      stats: {
        promptsOptimized: 0,
        tokensSaved: 0
      }
    });
    promptsOptimized.textContent = '0';
    tokensSaved.textContent = '0';
  });

  reportIssueLink.addEventListener('click', (e) => {
    e.preventDefault();
    chrome.tabs.create({
      url: 'https://github.com/ntuee10/Martin/issues/new'
    });
  });

  // Initialize
  await checkAPIConnection();
  await loadSettings();
});
