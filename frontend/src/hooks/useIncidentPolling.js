import { useState, useEffect, useRef } from 'react';
import { getIncidentStatus } from '../services/api';

export const useIncidentPolling = (incidentId, interval = 2000) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);

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
        setError(err.message);
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
