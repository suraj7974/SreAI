import { useState, useEffect, useRef } from 'react';
import { fetchIncidents } from '../services/api';
import type { Incident, UseIncidentPollingReturn } from '../types';

export const useIncidentPolling = (interval: number = 2000): UseIncidentPollingReturn => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await fetchIncidents();
        setIncidents(data);
        setError(null);
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
  }, [interval]);

  return { incidents, loading, error };
};
