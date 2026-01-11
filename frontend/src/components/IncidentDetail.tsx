import { useState } from 'react';
import type { Incident } from '../types';
import { formatTime, getStatusColor, getStatusLabel, getSeverityColor, getRiskColor } from '../utils/format';
import { api } from '../api/client';

interface Props {
  incident: Incident | null;
  loading: boolean;
  onActionComplete: () => void;
}

export function IncidentDetail({ incident, loading, onActionComplete }: Props) {
  const [actionLoading, setActionLoading] = useState(false);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectReason, setRejectReason] = useState('');

  if (loading) {
    return (
      <div className="bg-slate-800 rounded-lg border border-slate-700 p-8 text-center">
        <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
        <p className="text-slate-400 mt-4">Loading incident...</p>
      </div>
    );
  }

  if (!incident) {
    return (
      <div className="bg-slate-800 rounded-lg border border-slate-700 p-8 text-center text-slate-500">
        <svg className="w-16 h-16 mx-auto mb-4 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
        </svg>
        <p className="text-lg">Select an incident to view details</p>
        <p className="text-sm mt-1">Agent responses, diagnosis, and remediation plans will appear here</p>
      </div>
    );
  }

  const handleApprove = async () => {
    setActionLoading(true);
    try {
      await api.approveRemediation(incident.incident_id, {
        approved_by: 'dashboard-user',
      });
      onActionComplete();
    } catch (error) {
      console.error('Failed to approve:', error);
      alert('Failed to approve remediation');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    setActionLoading(true);
    try {
      await api.rejectRemediation(incident.incident_id, {
        rejected_by: 'dashboard-user',
        reason: rejectReason || undefined,
      });
      setShowRejectModal(false);
      setRejectReason('');
      onActionComplete();
    } catch (error) {
      console.error('Failed to reject:', error);
      alert('Failed to reject remediation');
    } finally {
      setActionLoading(false);
    }
  };

  const showApprovalButtons = incident.status === 'pending_approval';

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700">
      {/* Header */}
      <div className="p-4 border-b border-slate-700">
        <div className="flex items-center justify-between mb-2">
          <h2 className="font-mono text-lg text-white">{incident.incident_id}</h2>
          <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium text-white ${getStatusColor(incident.status)}`}>
            {getStatusLabel(incident.status)}
          </span>
        </div>
        <div className="flex items-center space-x-4 text-sm text-slate-400">
          <span>Target: {incident.target_instance || 'All'}</span>
          <span>Created: {formatTime(incident.created_at)}</span>
          {incident.severity && (
            <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium border ${getSeverityColor(incident.severity)}`}>
              {incident.severity.toUpperCase()}
            </span>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-6 max-h-[600px] overflow-y-auto">
        {/* Anomalies */}
        <Section title="Anomalies Detected">
          {!incident.anomalies || incident.anomalies.length === 0 ? (
            <p className="text-slate-500 text-sm">No anomalies detected yet</p>
          ) : (
            <div className="space-y-2">
              {incident.anomalies.map((anomaly, idx) => (
                <div key={idx} className="flex items-start space-x-3 p-2 rounded bg-slate-700/50">
                  <div className={`w-2 h-2 mt-1.5 rounded-full ${anomaly.severity === 'critical' ? 'bg-red-500' : 'bg-yellow-500'}`}></div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-white">{anomaly.metric || anomaly.type || 'Unknown'}</span>
                      <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium border ${getSeverityColor(anomaly.severity)}`}>
                        {anomaly.severity.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-sm text-slate-400 mt-1">{anomaly.description || anomaly.message || ''}</p>
                    {anomaly.value && <p className="text-xs text-slate-500 mt-1">Value: {anomaly.value}</p>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </Section>

        {/* Diagnosis */}
        <Section title="Diagnosis">
          {!incident.diagnosis ? (
            <p className="text-slate-500 text-sm">Diagnosis pending...</p>
          ) : (
            <pre className="whitespace-pre-wrap text-slate-300 text-sm bg-slate-700/50 p-3 rounded">
              {typeof incident.diagnosis === 'string' 
                ? incident.diagnosis 
                : JSON.stringify(incident.diagnosis, null, 2)}
            </pre>
          )}
        </Section>

        {/* Remediation Plan */}
        <Section title="Remediation Plan">
          {!incident.remediation_plan ? (
            <p className="text-slate-500 text-sm">No remediation plan yet</p>
          ) : (
            <>
              <div className="flex items-center justify-between mb-3">
                {incident.remediation_plan.risk && (
                  <span className={`text-xs px-2 py-1 rounded ${getRiskColor(incident.remediation_plan.risk)}`}>
                    Risk: {incident.remediation_plan.risk.toUpperCase()}
                  </span>
                )}
              </div>
              
              {incident.remediation_plan.explanation && (
                <p className="text-sm text-slate-300 mb-3">{incident.remediation_plan.explanation}</p>
              )}
              
              {incident.remediation_plan.commands && incident.remediation_plan.commands.length > 0 && (
                <div className="bg-slate-700/50 rounded p-3 mb-3">
                  <p className="text-xs text-slate-500 mb-2">Commands to execute:</p>
                  <pre className="text-sm text-green-400 font-mono">
                    {incident.remediation_plan.commands.join('\n')}
                  </pre>
                </div>
              )}

              {showApprovalButtons && (
                <div className="flex items-center space-x-3 mt-4 pt-4 border-t border-slate-700">
                  <button
                    onClick={handleApprove}
                    disabled={actionLoading}
                    className="flex-1 bg-green-600 hover:bg-green-700 disabled:opacity-50 px-4 py-2 rounded-lg text-sm font-medium text-white transition-colors"
                  >
                    {actionLoading ? 'Processing...' : 'Approve & Execute'}
                  </button>
                  <button
                    onClick={() => setShowRejectModal(true)}
                    disabled={actionLoading}
                    className="flex-1 bg-red-600 hover:bg-red-700 disabled:opacity-50 px-4 py-2 rounded-lg text-sm font-medium text-white transition-colors"
                  >
                    Reject
                  </button>
                </div>
              )}

              {incident.status === 'resolved' && (
                <div className="mt-4 pt-4 border-t border-slate-700">
                  <div className="flex items-center space-x-2 text-green-400">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <span className="font-medium">Remediation completed successfully</span>
                  </div>
                </div>
              )}

              {incident.status === 'rejected' && (
                <div className="mt-4 pt-4 border-t border-slate-700">
                  <div className="flex items-center space-x-2 text-slate-400">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <span className="font-medium">Remediation was rejected</span>
                  </div>
                </div>
              )}
            </>
          )}
        </Section>

        {/* Agent Activity */}
        <Section title="Agent Activity">
          {(!incident.agent_thoughts || incident.agent_thoughts.length === 0) && 
           (!incident.agent_messages || incident.agent_messages.length === 0) ? (
            <p className="text-slate-500 text-sm">No agent activity yet</p>
          ) : (
            <div className="space-y-3">
              {(incident.agent_thoughts || incident.agent_messages || []).map((msg, idx) => {
                const agentClass = msg.agent?.toLowerCase().includes('monitor') 
                  ? 'agent-monitor' 
                  : msg.agent?.toLowerCase().includes('diagnostic') 
                    ? 'agent-diagnostic' 
                    : 'agent-remediation';
                return (
                  <div key={idx} className={`border-l-2 ${agentClass} pl-3 py-2`}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-sm text-white">{msg.agent || 'System'}</span>
                      <span className="text-xs text-slate-500">{formatTime(msg.timestamp)}</span>
                    </div>
                    <p className="text-sm text-slate-300">{msg.content || msg.message || ''}</p>
                    {msg.tool_calls && (
                      <p className="text-xs text-slate-500 mt-1">Tools: {msg.tool_calls.join(', ')}</p>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </Section>
      </div>

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-lg border border-slate-700 w-full max-w-md mx-4">
            <div className="p-4 border-b border-slate-700">
              <h3 className="font-semibold text-white">Reject Remediation</h3>
            </div>
            <div className="p-4">
              <label className="block text-sm text-slate-400 mb-2">Reason (optional)</label>
              <textarea
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                rows={3}
                placeholder="Why are you rejecting this remediation?"
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
              />
            </div>
            <div className="p-4 border-t border-slate-700 flex justify-end space-x-3">
              <button
                onClick={() => setShowRejectModal(false)}
                className="px-4 py-2 text-sm text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={handleReject}
                disabled={actionLoading}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:opacity-50 rounded-lg text-sm font-medium text-white"
              >
                {actionLoading ? 'Processing...' : 'Reject'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
      <h3 className="text-sm font-semibold text-slate-400 mb-3">{title}</h3>
      {children}
    </div>
  );
}
