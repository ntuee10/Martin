// Martin Background Service Worker
console.log('Martin background service worker started');

// Install handler
chrome.runtime.onInstalled.addListener(() => {
  console.log('Martin installed successfully');
  
  // Set default settings
  chrome.storage.sync.set({
    enabled: true,
    showHighlights: true,
    autoAnalyze: true,
    apiEndpoint: 'http://localhost:8000',
    stats: {
      promptsOptimized: 0,
      tokensSaved: 0,
      lastUpdated: new Date().toISOString()
    }
  });

  // Open welcome page on first install
  chrome.runtime.openOptionsPage();
});

// Message handler
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  switch (request.type) {
    case 'updateStats':
      updateStatistics(request.data);
      break;
    
    case 'getSettings':
      chrome.storage.sync.get(null, (settings) => {
        sendResponse(settings);
      });
      return true; // Keep channel open for async response
    
    case 'apiRequest':
      // Proxy API requests if needed
      handleAPIRequest(request.data).then(sendResponse);
      return true;
  }
});

// Update statistics
async function updateStatistics(data) {
  const { stats } = await chrome.storage.sync.get('stats');
  const updated = {
    promptsOptimized: (stats.promptsOptimized || 0) + (data.promptsOptimized || 0),
    tokensSaved: (stats.tokensSaved || 0) + (data.tokensSaved || 0),
    lastUpdated: new Date().toISOString()
  };
  
  await chrome.storage.sync.set({ stats: updated });
  
  // Update badge
  if (updated.promptsOptimized > 0) {
    chrome.action.setBadgeText({ text: updated.promptsOptimized.toString() });
    chrome.action.setBadgeBackgroundColor({ color: '#3B82F6' });
  }
}

// Handle API requests (if needed for CORS bypass)
async function handleAPIRequest(data) {
  try {
    const response = await fetch(data.url, {
      method: data.method || 'GET',
      headers: data.headers || {},
      body: data.body ? JSON.stringify(data.body) : undefined
    });
    
    const result = await response.json();
    return { success: true, data: result };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

// Periodic cleanup (reset daily stats)
chrome.alarms.create('dailyReset', { periodInMinutes: 1440 }); // 24 hours

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'dailyReset') {
    chrome.storage.sync.set({
      stats: {
        promptsOptimized: 0,
        tokensSaved: 0,
        lastUpdated: new Date().toISOString()
      }
    });
  }
});
