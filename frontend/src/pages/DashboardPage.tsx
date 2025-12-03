import { useEffect, useState } from 'react';
import type { Incident } from '@/types';
import { fetchIncidents } from '@/services/api';
import { DashboardStats } from '@/components/DashboardStats';
import { IncidentCard } from '@/components/IncidentCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RefreshCw, Plus } from 'lucide-react';

export default function DashboardPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadIncidents();
  }, []);

  const loadIncidents = async () => {
    setLoading(true);
    try {
      const data = await fetchIncidents();
      setIncidents(data);
    } catch (error) {
      console.error('Failed to load incidents:', error);
    } finally {
      setLoading(false);
    }
  };

  const stats = {
    totalIncidents: incidents.length,
    activeIncidents: incidents.filter(i => i.status === 'open' || i.status === 'investigating').length,
    resolvedIncidents: incidents.filter(i => i.status === 'resolved' || i.status === 'closed').length,
    avgResolutionTime: '15.2 min',
  };

  return (
    <div className="p-8 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-gray-400 mt-1">Monitor and manage your incidents in real-time</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={loadIncidents} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            New Incident
          </Button>
        </div>
      </div>

      <DashboardStats stats={stats} />

      <Card>
        <CardHeader>
          <CardTitle className="text-white">Recent Incidents</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="h-8 w-8 animate-spin text-gray-400" />
            </div>
          ) : incidents.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              No incidents found. Your system is running smoothly! 🎉
            </div>
          ) : (
            <div className="space-y-4">
              {incidents.slice(0, 5).map((incident) => (
                <IncidentCard key={incident.id} incident={incident} />
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
