import type { IncidentListItem } from '../types';
import { formatRelativeTime, getStatusColor, getStatusLabel, getSeverityColor } from '../utils/format';

interface Props {
  incidents: IncidentListItem[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onRefresh: () => void;
}

export function IncidentsList({ incidents, selectedId, onSelect, onRefresh }: Props) {
  // Sort by created_at descending
  const sortedIncidents = [...incidents].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700">
      <div className="p-4 border-b border-slate-700 flex items-center justify-between">
        <h2 className="font-semibold text-white">Incidents</h2>
        <button 
          onClick={onRefresh}
          className="text-slate-400 hover:text-white transition-colors"
          title="Refresh"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
        </button>
      </div>
      <div className="divide-y divide-slate-700 max-h-[600px] overflow-y-auto">
        {sortedIncidents.length === 0 ? (
          <div className="p-8 text-center text-slate-500">
            <p>No incidents yet</p>
            <p className="text-sm mt-1">Click "Start Monitoring" to begin</p>
          </div>
        ) : (
          sortedIncidents.map((incident) => (
            <div
              key={incident.incident_id}
              onClick={() => onSelect(incident.incident_id)}
              className={`p-4 cursor-pointer transition-colors hover:bg-slate-700/50 ${
                selectedId === incident.incident_id ? 'bg-slate-700/70' : ''
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <span className="font-mono text-sm text-blue-400">
                  {incident.incident_id}
                </span>
                <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium text-white ${getStatusColor(incident.status)}`}>
                  {getStatusLabel(incident.status)}
                </span>
              </div>
              <div className="flex items-center justify-between text-xs text-slate-500">
                <span>{incident.target_instance || 'All targets'}</span>
                <span>{formatRelativeTime(incident.created_at)}</span>
              </div>
              {incident.severity && (
                <div className="mt-2">
                  <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium border ${getSeverityColor(incident.severity)}`}>
                    {incident.severity.toUpperCase()}
                  </span>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
