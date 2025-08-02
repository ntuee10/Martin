import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { Settings, HelpCircle, Zap } from 'lucide-react';

const Popup: React.FC = () => {
  const [settings, setSettings] = useState({
    enabled: true,
    apiEndpoint: 'http://localhost:8000',
    suggestionLevel: 'moderate'
  });

  useEffect(() => {
    chrome.storage.sync.get(['enabled', 'apiEndpoint', 'suggestionLevel'], (items) => {
      setSettings(items as any);
    });
  }, []);

  const toggleEnabled = () => {
    const newEnabled = !settings.enabled;
    setSettings({ ...settings, enabled: newEnabled });
    chrome.storage.sync.set({ enabled: newEnabled });
  };

  return (
    <div className="w-80 p-4">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-semibold">Martin</h1>
        <label className="relative inline-flex items-center cursor-pointer">
          <input 
            type="checkbox" 
            checked={settings.enabled}
            onChange={toggleEnabled}
            className="sr-only peer"
          />
          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
        </label>
      </div>

      <div className="space-y-2 text-sm text-gray-600">
        <p className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-amber-500" />
          AI-powered prompt optimization
        </p>
        <p>Endpoint: {settings.apiEndpoint}</p>
      </div>

      <div className="mt-4 pt-4 border-t flex gap-2">
        <button className="flex-1 flex items-center justify-center gap-1 py-2 text-sm text-gray-600 hover:text-gray-800">
          <Settings className="w-4 h-4" />
          Settings
        </button>
        <button className="flex-1 flex items-center justify-center gap-1 py-2 text-sm text-gray-600 hover:text-gray-800">
          <HelpCircle className="w-4 h-4" />
          Help
        </button>
      </div>
    </div>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root')!);
root.render(<Popup />);
