import { useState, useEffect, useRef } from 'react';
import { getIncidentStatus } from '../services/api';
import type { IncidentStatus } from '../types';

interface UseIncidentPollingReturn {
  data: IncidentStatus | null;
  loading: boolean;
  error: string | null;
}

export const useIncidentPolling = (incidentId: string | undefined, interval: number = 2000): UseIncidentPollingReturn => {
  const [data, setData] = useState<IncidentStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!incidentId) return;

    const fetchData = async () => {
      try {
        const response = await getIncidentStatus(incidentId);
        setData(response.data);
        setError(null);
        
        // Stop polling if complete or error
        if (response.data.status === 'complete' || response.data.status === 'error') {
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    // Initial fetch
    fetchData();

    // Start polling
    intervalRef.current = setInterval(fetchData, interval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [incidentId, interval]);

  return { data, loading, error };
};
