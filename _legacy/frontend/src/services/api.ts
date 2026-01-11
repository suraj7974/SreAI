import axios from 'axios';
import type { 
  IncidentRequest, 
  IncidentStatus, 
  IncidentReport, 
  Incident, 
  HealthStatus,
  ArtifactData 
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_TOKEN = import.meta.env.VITE_API_TOKEN || 'dev-token-change-in-production';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Authorization': `Bearer ${API_TOKEN}`,
    'Content-Type': 'application/json',
  },
});

export const healthCheck = () => api.get<HealthStatus>('/health');

export const startIncident = (data: IncidentRequest) => api.post<IncidentStatus>('/start_incident', data);

export const getIncidentStatus = (incidentId: string) => api.get<IncidentStatus>(`/status/${incidentId}`);

export const getIncidentReport = (incidentId: string) => api.get<IncidentReport>(`/report/${incidentId}`);

export const stopIncident = (incidentId: string) => api.post(`/stop/${incidentId}`);

export const listIncidents = () => api.get<{ data: Incident[] }>('/incidents');

export const fetchIncidents = async (): Promise<Incident[]> => {
  const response = await api.get<{ data: Incident[] }>('/incidents');
  return response.data.data;
};

export const getArtifact = (incidentId: string, artifactName: string) => 
  api.get<ArtifactData>(`/incidents/${incidentId}/artifacts/${artifactName}`);

export default api;
