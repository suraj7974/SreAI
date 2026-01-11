import type { IncidentStatus, Severity } from '../types';

export function formatTime(timestamp: string | undefined): string {
  if (!timestamp) return 'N/A';
  return new Date(timestamp).toLocaleString();
}

export function formatRelativeTime(timestamp: string | undefined): string {
  if (!timestamp) return '';
  const now = new Date();
  const date = new Date(timestamp);
  const diff = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

export function getStatusColor(status: IncidentStatus): string {
  const colors: Record<IncidentStatus, string> = {
    monitoring: 'bg-blue-500',
    diagnosing: 'bg-yellow-500',
    pending_approval: 'bg-orange-500',
    executing: 'bg-purple-500',
    resolved: 'bg-green-500',
    failed: 'bg-red-500',
    rejected: 'bg-gray-500',
  };
  return colors[status] || 'bg-gray-500';
}

export function getStatusLabel(status: IncidentStatus): string {
  return status.replace('_', ' ').toUpperCase();
}

export function getSeverityColor(severity: Severity | undefined): string {
  if (!severity) return 'bg-gray-500/20 text-gray-400 border-gray-500/50';
  
  const colors: Record<Severity, string> = {
    critical: 'bg-red-500/20 text-red-400 border-red-500/50',
    warning: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
    info: 'bg-blue-500/20 text-blue-400 border-blue-500/50',
  };
  return colors[severity];
}

export function getRiskColor(risk: string | undefined): string {
  if (!risk) return '';
  
  const colors: Record<string, string> = {
    high: 'bg-red-500/20 text-red-400',
    medium: 'bg-yellow-500/20 text-yellow-400',
    low: 'bg-green-500/20 text-green-400',
  };
  return colors[risk] || '';
}
