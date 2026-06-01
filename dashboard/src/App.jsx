import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import DashboardPage from './pages/DashboardPage';
import AnalyzerPage from './pages/AnalyzerPage';
import { AppProvider } from './components/AppContext';

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<DashboardPage />} />
            <Route path="analyzer" element={<AnalyzerPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AppProvider>
  );
}
