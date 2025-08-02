# Make sure you're in the extension directory
cd /Users/wenshyenchen/Calude/Martin/extension

# Create dist directory
mkdir -p dist/icons

# Copy manifest
cp manifest.json dist/

# Create all files at once
cat > dist/content.js << 'EOF'
console.log('Martin: Extension loaded on', window.location.hostname);

// Create indicator
const indicator = document.createElement('div');
indicator.id = 'martin-indicator';
indicator.style.cssText = `
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 48px;
  height: 48px;
  background: white;
  border-radius: 50%;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  color: #3B82F6;
  transition: transform 0.2s;
`;
indicator.innerHTML = 'M';
indicator.title = 'Martin - AI Prompt Optimizer';
document.body.appendChild(indicator);

// Add hover effect
indicator.addEventListener('mouseover', () => {
  indicator.style.transform = 'scale(1.1)';
});
indicator.addEventListener('mouseout', () => {
  indicator.style.transform = 'scale(1)';
});

// Monitor textarea
setTimeout(() => {
  const textarea = document.querySelector('textarea');
  if (textarea) {
    console.log('Martin: Monitoring prompts');
    let timeout;
    
    textarea.addEventListener('input', async (e) => {
      clearTimeout(timeout);
      timeout = setTimeout(async () => {
        const text = e.target.value;
        if (text.length > 10) {
          indicator.innerHTML = '...';
          try {
            const res = await fetch('http://localhost:8000/api/v1/analyze', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer demo'
              },
              body: JSON.stringify({
                prompt: text,
                target_model: 'gpt-4',
                context: { domain: 'technical' },
                options: {}
              })
            });
            const data = await res.json();
            const count = data.suggestions.length;
            indicator.innerHTML = count > 0 ? count : '✓';
            indicator.style.color = count > 0 ? '#3B82F6' : '#10B981';
          } catch (err) {
            console.error('Martin error:', err);
            indicator.innerHTML = '!';
            indicator.style.color = '#EF4444';
          }
        } else {
          indicator.innerHTML = 'M';
          indicator.style.color = '#3B82F6';
        }
      }, 500);
    });
  } else {
    console.log('Martin: No textarea found yet');
  }
}, 2000);
EOF

cat > dist/background.js << 'EOF'
console.log('Martin: Background service started');

chrome.runtime.onInstalled.addListener(() => {
  console.log('Martin: Extension installed successfully');
  chrome.storage.sync.set({
    enabled: true,
    apiEndpoint: 'http://localhost:8000'
  });
});
EOF

cat > dist/popup.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {
      width: 320px;
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    .header {
      background: #3B82F6;
      color: white;
      padding: 20px;
      text-align: center;
    }
    .header h1 {
      margin: 0;
      font-size: 24px;
      font-weight: 600;
    }
    .header p {
      margin: 4px 0 0 0;
      opacity: 0.9;
      font-size: 14px;
    }
    .content {
      padding: 20px;
    }
    .status {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px;
      background: #F3F4F6;
      border-radius: 8px;
      margin-bottom: 16px;
    }
    .status-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: #10B981;
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }
    .info {
      font-size: 14px;
      color: #374151;
      line-height: 1.5;
    }
    .api-info {
      margin-top: 16px;
      padding-top: 16px;
      border-top: 1px solid #E5E7EB;
      font-size: 12px;
      color: #6B7280;
    }
    .api-info code {
      background: #F3F4F6;
      padding: 2px 6px;
      border-radius: 4px;
      font-family: monospace;
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>Martin</h1>
    <p>AI Prompt Optimizer</p>
  </div>
  <div class="content">
    <div class="status">
      <div class="status-dot"></div>
      <div>
        <strong>Active</strong>
        <div style="font-size: 12px; color: #6B7280;">Monitoring your prompts</div>
      </div>
    </div>
    <div class="info">
      Martin analyzes your prompts in real-time and suggests improvements for better AI responses.
    </div>
    <div class="api-info">
      <div>API Endpoint: <code id="api-status">Checking...</code></div>
    </div>
  </div>
  <script>
    // Check API status
    fetch('http://localhost:8000/api/v1/health')
      .then(r => r.json())
      .then(data => {
        document.getElementById('api-status').textContent = 'Connected ✓';
        document.getElementById('api-status').style.color = '#10B981';
      })
      .catch(err => {
        document.getElementById('api-status').textContent = 'Offline ✗';
        document.getElementById('api-status').style.color = '#EF4444';
      });
  </script>
</body>
</html>
EOF

# Create empty CSS file
touch dist/styles.css

# Create a simple icon (blue square with M)
cat > dist/icon.html << 'EOF'
<html>
<body style="margin:0">
<div style="width:128px;height:128px;background:#3B82F6;display:flex;align-items:center;justify-content:center;font-family:Arial;font-size:72px;color:white;font-weight:bold">M</div>
</body>
</html>
EOF

echo "✅ Martin extension created successfully!"
echo ""
echo "📁 Files created in dist/:"
ls -la dist/