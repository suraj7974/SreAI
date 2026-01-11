import { useIncidentPolling } from '@/hooks/useIncidentPolling';
import { IncidentCard } from '@/components/IncidentCard';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RefreshCw, Filter } from 'lucide-react';
import { useState } from 'react';

export default function IncidentsPage() {
  const { incidents, loading, error } = useIncidentPolling();
  const [filter, setFilter] = useState<string>('all');

  const filteredIncidents = filter === 'all' ? incidents : incidents.filter(i => i.status === filter);

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">All Incidents</h1>
          <p className="text-gray-400 mt-1">View and manage all system incidents</p>
        </div>
        <Button variant="outline">
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Auto-refresh: ON
        </Button>
      </div>

      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-gray-400" />
            <span className="text-sm text-gray-400 mr-2">Filter:</span>
            <div className="flex gap-2">
              {['all', 'open', 'investigating', 'resolved', 'closed'].map((status) => (
                <Button
                  key={status}
                  variant={filter === status ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilter(status)}
                >
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                  {status === 'all' && ` (${incidents.length})`}
                  {status !== 'all' && ` (${incidents.filter(i => i.status === status).length})`}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {error && (
        <Card className="border-red-500">
          <CardContent className="p-6 text-red-500">Error loading incidents: {error}</CardContent>
        </Card>
      )}

      {loading && incidents.length === 0 ? (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="h-8 w-8 animate-spin text-gray-400" />
        </div>
      ) : filteredIncidents.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center text-gray-400">
            No incidents found with status: {filter}
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredIncidents.map((incident) => (
            <IncidentCard key={incident.id} incident={incident} />
          ))}
        </div>
      )}
    </div>
  );
}
