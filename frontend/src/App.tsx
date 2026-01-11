import { useState } from 'react';
import { Header } from './components/Header';
import { StatsOverview, calculateStats } from './components/StatsOverview';
import { IncidentsList } from './components/IncidentsList';
import { IncidentDetail } from './components/IncidentDetail';
import { StartMonitoringModal } from './components/StartMonitoringModal';
import { useIncidents, useIncident } from './hooks/useIncidents';

export default function App() {
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);
  const [showStartModal, setShowStartModal] = useState(false);

  const { incidents, loading: listLoading, refresh: refreshList } = useIncidents(5000);
  const { incident, loading: detailLoading, refresh: refreshDetail } = useIncident(selectedIncidentId, 3000);

  const stats = calculateStats(incidents);

  const handleStartMonitoring = () => {
    setShowStartModal(true);
  };

  const handleStartSuccess = (incidentId: string) => {
    refreshList();
    setSelectedIncidentId(incidentId);
  };

  const handleSelectIncident = (id: string) => {
    setSelectedIncidentId(id);
  };

  const handleActionComplete = () => {
    refreshDetail();
    refreshList();
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <Header onStartMonitoring={handleStartMonitoring} />

      <main className="max-w-7xl mx-auto px-4 py-6">
        <StatsOverview
          total={stats.total}
          active={stats.active}
          pending={stats.pending}
          resolved={stats.resolved}
        />

        {listLoading && incidents.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full"></div>
            <span className="ml-3 text-slate-400">Loading incidents...</span>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left sidebar - Incidents list */}
            <div className="lg:col-span-1">
              <IncidentsList
                incidents={incidents}
                selectedId={selectedIncidentId}
                onSelect={handleSelectIncident}
                onRefresh={refreshList}
              />
            </div>

            {/* Right content - Incident detail */}
            <div className="lg:col-span-2">
              <IncidentDetail
                incident={incident}
                loading={detailLoading}
                onActionComplete={handleActionComplete}
              />
            </div>
          </div>
        )}
      </main>

      <StartMonitoringModal
        isOpen={showStartModal}
        onClose={() => setShowStartModal(false)}
        onSuccess={handleStartSuccess}
      />
    </div>
  );
}
