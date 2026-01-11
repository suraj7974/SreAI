import type { IncidentListItem } from '../types';

interface Props {
  total: number;
  active: number;
  pending: number;
  resolved: number;
}

export function StatsOverview({ total, active, pending, resolved }: Props) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <StatCard
        title="Total Incidents"
        value={total}
        icon={
          <svg className="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
        }
        iconBg="bg-blue-500/20"
      />
      <StatCard
        title="Active"
        value={active}
        valueColor="text-yellow-500"
        icon={
          <svg className="w-5 h-5 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        }
        iconBg="bg-yellow-500/20"
      />
      <StatCard
        title="Pending Approval"
        value={pending}
        valueColor="text-orange-500"
        icon={
          <svg className="w-5 h-5 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        }
        iconBg="bg-orange-500/20"
      />
      <StatCard
        title="Resolved"
        value={resolved}
        valueColor="text-green-500"
        icon={
          <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        }
        iconBg="bg-green-500/20"
      />
    </div>
  );
}

interface StatCardProps {
  title: string;
  value: number;
  valueColor?: string;
  icon: React.ReactNode;
  iconBg: string;
}

function StatCard({ title, value, valueColor = 'text-white', icon, iconBg }: StatCardProps) {
  return (
    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-slate-400 text-sm">{title}</p>
          <p className={`text-2xl font-bold ${valueColor}`}>{value}</p>
        </div>
        <div className={`w-10 h-10 ${iconBg} rounded-lg flex items-center justify-center`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

export function calculateStats(incidents: IncidentListItem[]) {
  const total = incidents.length;
  const active = incidents.filter(i => 
    ['monitoring', 'diagnosing', 'executing'].includes(i.status)
  ).length;
  const pending = incidents.filter(i => i.status === 'pending_approval').length;
  const resolved = incidents.filter(i => i.status === 'resolved').length;
  
  return { total, active, pending, resolved };
}
