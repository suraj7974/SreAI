import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/common/Layout';
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import IncidentsPage from './pages/IncidentsPage';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard/:incidentId" element={<DashboardPage />} />
          <Route path="/incidents" element={<IncidentsPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
