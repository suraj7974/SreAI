// Type definitions for the AI Chaos Handler frontend

export interface VMTarget {
  host: string;
  port: number;
  user: string;
  key_path: string;
}

export interface IncidentOptions {
  trigger_chaos?: boolean;
  duration?: number;
}

export interface IncidentRequest {
  scenario: string;
  target_vm: VMTarget;
  options?: IncidentOptions;
}

export interface AgentEvent {
  timestamp: string;
  agent: string;
  event: string;
  data?: Record<string, any>;
  success?: boolean;
  error?: string;
}

export interface IncidentStatus {
  incident_id: string;
  status: 'initializing' | 'running' | 'complete' | 'error';
  created_at: string;
  updated_at: string;
  trace: AgentEvent[];
  artifacts: string[];
  error?: string;
}

export interface Incident {
  id: string;
  incident_id: string;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'open' | 'investigating' | 'resolved' | 'closed';
  created_at: string;
  updated_at?: string;
  resolved_at?: string;
  assigned_to?: string;
  scenario?: string;
}

export interface IncidentReport {
  incident_id: string;
  created_at: string;
  status: string;
  summary: string;
  artifacts: string[];
}

export interface HealthStatus {
  status: string;
  version?: string;
  timestamp?: string;
}

export interface ArtifactData {
  [key: string]: any;
}

export interface UseIncidentPollingReturn {
  incidents: Incident[];
  loading: boolean;
  error: string | null;
}
