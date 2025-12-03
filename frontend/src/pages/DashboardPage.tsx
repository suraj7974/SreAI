import { useParams } from 'react-router-dom';
import { useIncidentPolling } from '../hooks/useIncidentPolling';
import { formatDate, getStatusColor, getAgentColor } from '../utils/helpers';

export default function DashboardPage() {
  const { incidentId } = useParams<{ incidentId: string }>();
  const { data, loading, error } = useIncidentPolling(incidentId);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading incident data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-800 rounded-lg p-4">
        <p className="text-red-400">Error: {error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-yellow-900/20 border border-yellow-800 rounded-lg p-4">
        <p className="text-yellow-400">No incident data found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold text-white">
            Incident Dashboard: {data.incident_id}
          </h1>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(data.status)}`}>
            {data.status}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-400">Created:</span>
            <span className="text-white ml-2">{formatDate(data.created_at)}</span>
          </div>
          <div>
            <span className="text-gray-400">Updated:</span>
            <span className="text-white ml-2">{formatDate(data.updated_at)}</span>
          </div>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold text-white mb-4">Agent Trace</h2>
        <div className="space-y-3">
          {data.trace.map((event, idx) => (
            <div
              key={idx}
              className={`border-l-4 ${getAgentColor(event.agent as any)} bg-gray-900 p-4 rounded-r-lg`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-blue-400 font-medium">{event.agent}</span>
                <span className="text-gray-500 text-sm">{formatDate(event.timestamp)}</span>
              </div>
              <p className="text-white">{event.event}</p>
              {event.data && (
                <pre className="mt-2 text-xs text-gray-400 bg-gray-950 p-2 rounded overflow-auto">
                  {JSON.stringify(event.data, null, 2)}
                </pre>
              )}
            </div>
          ))}
        </div>
      </div>

      {data.artifacts.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4">Artifacts</h2>
          <ul className="space-y-2">
            {data.artifacts.map((artifact, idx) => (
              <li key={idx} className="text-gray-300">
                📄 {artifact}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
