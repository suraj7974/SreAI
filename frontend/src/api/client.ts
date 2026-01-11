import type {
  Incident,
  IncidentsListResponse,
  StartIncidentRequest,
  ApprovalRequest,
  RejectionRequest,
  HealthResponse,
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  status: number;
  
  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ApiError(response.status, error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Health
  getHealth: () => request<HealthResponse>('/health'),

  // Incidents
  listIncidents: () => request<IncidentsListResponse>('/incidents'),
  
  getIncident: (id: string) => request<Incident>(`/incidents/${id}`),
  
  startIncident: (data: StartIncidentRequest) =>
    request<{ incident_id: string; status: string; message: string }>('/incidents', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Approvals
  approveRemediation: (incidentId: string, data: ApprovalRequest) =>
    request<{ incident_id: string; status: string; message: string }>(
      `/incidents/${incidentId}/approve`,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    ),

  rejectRemediation: (incidentId: string, data: RejectionRequest) =>
    request<{ incident_id: string; status: string; message: string }>(
      `/incidents/${incidentId}/reject`,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    ),

  // Prometheus
  getAlerts: () => request<unknown>('/prometheus/alerts'),
  getTargets: () => request<unknown>('/prometheus/targets'),
};

export { ApiError };
