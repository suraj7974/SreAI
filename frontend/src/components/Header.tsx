interface Props {
  onStartMonitoring: () => void;
}

export function Header({ onStartMonitoring }: Props) {
  return (
    <header className="bg-slate-800 border-b border-slate-700 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
            </svg>
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">SRE Agent</h1>
            <p className="text-xs text-slate-400">Autonomous Incident Response</p>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <button 
            onClick={onStartMonitoring}
            className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-sm font-medium text-white transition-colors"
          >
            Start Monitoring
          </button>
          <a 
            href="http://localhost:3001" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-slate-400 hover:text-white text-sm"
          >
            Grafana
          </a>
          <a 
            href="http://localhost:8000/docs" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-slate-400 hover:text-white text-sm"
          >
            API Docs
          </a>
          <div className="flex items-center space-x-2">
            <span className="status-dot w-2 h-2 rounded-full bg-green-500"></span>
            <span className="text-xs text-slate-400">Connected</span>
          </div>
        </div>
      </div>
    </header>
  );
}
