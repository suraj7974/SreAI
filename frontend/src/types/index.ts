export type IncidentStatus = 
  | 'monitoring' 
  | 'diagnosing' 
  | 'pending_approval' 
  | 'executing' 
  | 'resolved' 
  | 'failed' 
  | 'rejected';

export type Severity = 'critical' | 'warning' | 'info';

export interface Anomaly {
  metric: string;
  type?: string;
  severity: Severity;
  description?: string;
  message?: string;
  value?: number | string;
  threshold?: number;
  timestamp?: string;
}

export interface RemediationPlan {
  commands: string[];
  risk: 'low' | 'medium' | 'high';
  explanation: string;
  estimated_duration?: string;
}

export interface AgentMessage {
  agent: string;
  content: string;
  message?: string;
  timestamp: string;
  tool_calls?: string[];
  type?: string;
}

export interface Incident {
  incident_id: string;
  status: IncidentStatus;
  severity?: Severity;
  target_instance: string;
  created_at: string;
  updated_at?: string;
  anomalies?: Anomaly[];
  diagnosis?: string | Record<string, unknown>;
  remediation_plan?: RemediationPlan;
  awaiting_approval?: boolean;
  agent_messages?: AgentMessage[];
  agent_thoughts?: AgentMessage[];
}

export interface IncidentListItem {
  incident_id: string;
  status: IncidentStatus;
  severity?: Severity;
  target_instance: string;
  created_at: string;
  awaiting_approval?: boolean;
}

export interface StartIncidentRequest {
  target_instance: string;
  trigger_source?: string;
}

export interface ApprovalRequest {
  approved_by: string;
  feedback?: string;
}

export interface RejectionRequest {
  rejected_by: string;
  reason?: string;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
}

export interface IncidentsListResponse {
  incidents: IncidentListItem[];
  total: number;
}

export interface HealthResponse {
  status: string;
  version: string;
  prometheus_url: string;
  active_incidents: number;
}
