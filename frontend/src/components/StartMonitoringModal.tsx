import { useState } from 'react';
import { api } from '../api/client';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (incidentId: string) => void;
}

export function StartMonitoringModal({ isOpen, onClose, onSuccess }: Props) {
  const [target, setTarget] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const result = await api.startIncident({
        target_instance: target || 'node-exporter:9100',
        trigger_source: 'dashboard',
      });
      setTarget('');
      onSuccess(result.incident_id);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start monitoring');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-slate-800 rounded-lg border border-slate-700 w-full max-w-md mx-4">
        <div className="p-4 border-b border-slate-700">
          <h3 className="font-semibold text-white">Start Monitoring</h3>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="p-4">
            <label className="block text-sm text-slate-400 mb-2">Target Instance</label>
            <input
              type="text"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              placeholder="e.g., 192.168.1.10:9100"
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
            />
            <p className="text-xs text-slate-500 mt-2">
              Enter the Node Exporter endpoint (host:port). Leave empty to use default.
            </p>
            {error && (
              <p className="text-xs text-red-400 mt-2">{error}</p>
            )}
          </div>
          <div className="p-4 border-t border-slate-700 flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm text-slate-400 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-lg text-sm font-medium text-white"
            >
              {loading ? 'Starting...' : 'Start Monitoring'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
