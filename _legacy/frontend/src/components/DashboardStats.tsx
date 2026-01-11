import { Activity, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: string;
  trendUp?: boolean;
}

function StatsCard({ title, value, icon, trend, trendUp }: StatsCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-gray-400">
          {title}
        </CardTitle>
        <div className="text-gray-400">{icon}</div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-white">{value}</div>
        {trend && (
          <p className={`text-xs ${trendUp ? 'text-green-500' : 'text-red-500'} mt-1`}>
            {trend}
          </p>
        )}
      </CardContent>
    </Card>
  );
}

interface DashboardStatsProps {
  stats: {
    totalIncidents: number;
    activeIncidents: number;
    resolvedIncidents: number;
    avgResolutionTime: string;
  };
}

export function DashboardStats({ stats }: DashboardStatsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <StatsCard
        title="Total Incidents"
        value={stats.totalIncidents}
        icon={<Activity className="h-4 w-4" />}
        trend="+12% from last month"
        trendUp={false}
      />
      <StatsCard
        title="Active Incidents"
        value={stats.activeIncidents}
        icon={<AlertCircle className="h-4 w-4" />}
        trend="3 critical"
        trendUp={false}
      />
      <StatsCard
        title="Resolved"
        value={stats.resolvedIncidents}
        icon={<CheckCircle className="h-4 w-4" />}
        trend="+8% from last month"
        trendUp={true}
      />
      <StatsCard
        title="Avg Resolution Time"
        value={stats.avgResolutionTime}
        icon={<Clock className="h-4 w-4" />}
        trend="-2.5 min faster"
        trendUp={true}
      />
    </div>
  );
}
