import { BrowserRouter as Router, Routes, Route, useLocation, useNavigate } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import IncidentsPage from './pages/IncidentsPage';

function AppContent() {
  const location = useLocation();
  const navigate = useNavigate();

  const getCurrentPage = () => {
    if (location.pathname === '/') return 'home';
    if (location.pathname.startsWith('/dashboard')) return 'dashboard';
    if (location.pathname.startsWith('/incidents')) return 'incidents';
    if (location.pathname.startsWith('/settings')) return 'settings';
    return 'home';
  };

  const handleNavigate = (page: string) => {
    switch (page) {
      case 'home':
        navigate('/');
        break;
      case 'dashboard':
        navigate('/dashboard');
        break;
      case 'incidents':
        navigate('/incidents');
        break;
      case 'settings':
        navigate('/settings');
        break;
    }
  };

  return (
    <div className="flex h-screen bg-gray-900 overflow-hidden">
      <Sidebar currentPage={getCurrentPage()} onNavigate={handleNavigate} />
      <main className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/incidents" element={<IncidentsPage />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
