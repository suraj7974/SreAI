import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { listIncidents } from '../services/api';
import { formatDate, getStatusColor } from '../utils/helpers';
import type { Incident } from '../types';

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchIncidents = async () => {
      try {
        const response = await listIncidents();
        setIncidents(response.data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load incidents');
      } finally {
        setLoading(false);
      }
    };

    fetchIncidents();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading incidents...</div>
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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">All Incidents</h1>
        <span className="text-gray-400">{incidents.length} total</span>
      </div>

      {incidents.length === 0 ? (
        <div className="bg-gray-800 rounded-lg p-8 text-center">
          <p className="text-gray-400">No incidents found</p>
          <p className="text-sm text-gray-500 mt-2">
            Run <code className="bg-gray-700 px-2 py-1 rounded">python3 demo.py</code> to create a demo incident
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {incidents.map((incident) => (
            <Link
              key={incident.incident_id}
              to={`/dashboard/${incident.incident_id}`}
              className="bg-gray-800 hover:bg-gray-700 rounded-lg p-6 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-white mb-2">
                    {incident.incident_id}
                  </h3>
                  <p className="text-sm text-gray-400">
                    {formatDate(incident.created_at)}
                  </p>
                  {incident.scenario && (
                    <p className="text-sm text-gray-500 mt-1">
                      Scenario: {incident.scenario}
                    </p>
                  )}
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(incident.status as any)}`}>
                  {incident.status}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
