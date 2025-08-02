chrome.runtime.onInstalled.addListener(() => {
  console.log('Martin installed');
  
  // Set default settings
  chrome.storage.sync.set({
    enabled: true,
    apiEndpoint: 'http://localhost:8000',
    suggestionLevel: 'moderate',
    targetModels: ['gpt-4', 'claude-3', 'gemini-ultra', 'grok']
  });

  // Create context menu
  chrome.contextMenus.create({
    id: 'analyze-prompt',
    title: 'Analyze Prompt with Martin',
    contexts: ['selection']
  });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'analyze-prompt' && info.selectionText && tab?.id) {
    chrome.tabs.sendMessage(tab.id, {
      action: 'analyze-selection',
      text: info.selectionText
    });
  }
});
