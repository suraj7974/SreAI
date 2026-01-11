import { useEffect, useRef, useState, useCallback } from 'react';
import { api } from '../api/client';
import type { Incident, IncidentListItem } from '../types';

export function useIncidents(pollInterval = 5000) {
  const [incidents, setIncidents] = useState<IncidentListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<number | null>(null);

  const fetchIncidents = useCallback(async () => {
    try {
      const response = await api.listIncidents();
      setIncidents(response.incidents);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch incidents');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchIncidents();
    
    intervalRef.current = window.setInterval(fetchIncidents, pollInterval);
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [fetchIncidents, pollInterval]);

  return { incidents, loading, error, refresh: fetchIncidents };
}

export function useIncident(incidentId: string | null, pollInterval = 3000) {
  const [incident, setIncident] = useState<Incident | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<number | null>(null);

  const fetchIncident = useCallback(async () => {
    if (!incidentId) {
      setIncident(null);
      return;
    }

    try {
      const data = await api.getIncident(incidentId);
      setIncident(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch incident');
    } finally {
      setLoading(false);
    }
  }, [incidentId]);

  useEffect(() => {
    if (!incidentId) {
      setIncident(null);
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      return;
    }

    setLoading(true);
    fetchIncident();
    
    intervalRef.current = window.setInterval(fetchIncident, pollInterval);
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [incidentId, fetchIncident, pollInterval]);

  return { incident, loading, error, refresh: fetchIncident };
}
