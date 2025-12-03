import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_TOKEN = import.meta.env.VITE_API_TOKEN || 'dev-token-change-in-production';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Authorization': `Bearer ${API_TOKEN}`,
    'Content-Type': 'application/json',
  },
});

export const healthCheck = () => api.get('/health');

export const startIncident = (data) => api.post('/start_incident', data);

export const getIncidentStatus = (incidentId) => api.get(`/status/${incidentId}`);

export const getIncidentReport = (incidentId) => api.get(`/report/${incidentId}`);

export const stopIncident = (incidentId) => api.post(`/stop/${incidentId}`);

export const listIncidents = () => api.get('/incidents');

export const getArtifact = (incidentId, artifactName) => 
  api.get(`/incidents/${incidentId}/artifacts/${artifactName}`);

export default api;
