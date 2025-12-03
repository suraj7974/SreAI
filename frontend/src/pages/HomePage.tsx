export default function HomePage() {
  return (
    <div className="text-center">
      <h1 className="text-4xl font-bold text-white mb-4">AI Chaos Handler</h1>
      <p className="text-gray-400 text-lg mb-8">Autonomous Multi-Agent Incident Response System</p>
      
      <div className="max-w-2xl mx-auto text-left bg-gray-800 p-6 rounded-lg">
        <h2 className="text-2xl font-semibold text-white mb-4">Quick Actions</h2>
        <ul className="space-y-2 text-gray-300">
          <li>✅ Frontend: React 19 + Vite + Tailwind v4</li>
          <li>✅ Backend: FastAPI with 5 AI agents</li>
          <li>✅ Real-time polling every 2 seconds</li>
          <li>✅ Complete setup guide created</li>
        </ul>
        
        <div className="mt-6">
          <p className="text-sm text-gray-400">
            Run <code className="bg-gray-700 px-2 py-1 rounded">python3 demo.py</code> to generate a demo incident,
            then navigate to the dashboard to see it in action.
          </p>
        </div>
      </div>
    </div>
  );
}
