// src/content.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';

console.log('Martin content script loaded!');

// Simple component that adds Martin indicator
const MartinIndicator = () => {
  const [suggestions, setSuggestions] = React.useState(0);
  const [isAnalyzing, setIsAnalyzing] = React.useState(false);

  React.useEffect(() => {
    // Find textarea on the page
    const findTextarea = () => {
      const selectors = [
        'textarea[placeholder*="Send a message"]',
        'textarea[placeholder*="Talk to Claude"]',
        'textarea[placeholder*="Enter a prompt"]',
        'textarea'
      ];

      for (const selector of selectors) {
        const element = document.querySelector(selector);
        if (element) return element;
      }
      return null;
    };

    const textarea = findTextarea();
    if (!textarea) {
      console.log('Martin: No textarea found');
      return;
    }

    console.log('Martin: Textarea found, adding listener');

    // Simple input handler
    const handleInput = async (event) => {
      const text = event.target.value;
      if (text.length > 10) {
        setIsAnalyzing(true);
        
        try {
          const response = await fetch('http://localhost:8000/api/v1/analyze', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': 'Bearer demo-token'
            },
            body: JSON.stringify({
              prompt: text,
              target_model: 'gpt-4',
              context: {
                domain: 'technical'
              },
              options: {}
            })
          });

          if (response.ok) {
            const data = await response.json();
            setSuggestions(data.suggestions.length);
          }
        } catch (error) {
          console.error('Martin API error:', error);
        } finally {
          setIsAnalyzing(false);
        }
      }
    };

    textarea.addEventListener('input', handleInput);
    return () => textarea.removeEventListener('input', handleInput);
  }, []);

  return (
    <div style={{
      position: 'fixed',
      bottom: '24px',
      right: '24px',
      width: '48px',
      height: '48px',
      borderRadius: '50%',
      backgroundColor: '#fff',
      boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      cursor: 'pointer',
      zIndex: 10000,
      fontSize: '16px',
      fontWeight: 'bold',
      color: '#3B82F6'
    }}>
      {isAnalyzing ? '...' : suggestions > 0 ? suggestions : '✓'}
    </div>
  );
};

// Mount the component
const container = document.createElement('div');
container.id = 'martin-root';
document.body.appendChild(container);

const root = ReactDOM.createRoot(container);
root.render(<MartinIndicator />);

// src/background.ts
console.log('Martin background script loaded');

chrome.runtime.onInstalled.addListener(() => {
  console.log('Martin installed!');
  
  chrome.storage.sync.set({
    enabled: true,
    apiEndpoint: 'http://localhost:8000'
  });
});

// src/popup.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';

const Popup = () => {
  const [enabled, setEnabled] = React.useState(true);

  React.useEffect(() => {
    chrome.storage.sync.get(['enabled'], (result) => {
      setEnabled(result.enabled ?? true);
    });
  }, []);

  const toggle = () => {
    const newState = !enabled;
    setEnabled(newState);
    chrome.storage.sync.set({ enabled: newState });
  };

  return (
    <div style={{ width: '300px', padding: '16px', fontFamily: 'Arial, sans-serif' }}>
      <h2 style={{ margin: '0 0 16px 0', fontSize: '20px' }}>Martin</h2>
      <p style={{ margin: '0 0 16px 0', color: '#666', fontSize: '14px' }}>
        AI-powered prompt optimization
      </p>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span>Enabled</span>
        <button 
          onClick={toggle}
          style={{
            padding: '4px 12px',
            borderRadius: '4px',
            border: 'none',
            backgroundColor: enabled ? '#3B82F6' : '#ccc',
            color: 'white',
            cursor: 'pointer'
          }}
        >
          {enabled ? 'ON' : 'OFF'}
        </button>
      </div>
      <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid #eee' }}>
        <p style={{ margin: 0, fontSize: '12px', color: '#999' }}>
          API: http://localhost:8000
        </p>
      </div>
    </div>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root')!);
root.render(<Popup />);

// src/styles.css
/* Martin Extension Styles */
#martin-root {
  /* Container for our React app */
}

.martin-highlight {
  border-bottom: 2px dotted #3B82F6;
  cursor: pointer;
  transition: all 0.2s;
}

.martin-highlight:hover {
  border-bottom-style: solid;
}

/* src/types.ts (already created earlier) */