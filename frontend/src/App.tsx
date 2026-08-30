import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { Dashboard } from './pages/Dashboard';
import { Benchmarks } from './pages/Benchmarks';
import { CreateBenchmark } from './pages/CreateBenchmark';
import { RunBenchmark } from './pages/RunBenchmark';
import { RunsHistory } from './pages/RunsHistory';
import { LiveExecution } from './pages/LiveExecution';
import { RunDetails } from './pages/RunDetails';
import { Leaderboard } from './pages/Leaderboard';
import { FailureAnalysis } from './pages/FailureAnalysis';
import { AgentsModels } from './pages/AgentsModels';
import { Compare } from './pages/Compare';
import { DoctorDocs } from './pages/DoctorDocs';

export const App: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-background text-primary-text flex">
        {/* Sidebar */}
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        {/* Backdrop for mobile */}
        {sidebarOpen && (
          <div
            onClick={() => setSidebarOpen(false)}
            className="fixed inset-0 z-30 bg-black/60 backdrop-blur-sm lg:hidden"
          />
        )}

        {/* Main Content Area */}
        <div className="flex-1 lg:pl-64 flex flex-col min-w-0">
          <Header onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
          
          <main className="flex-1 p-6 lg:p-10 max-w-7xl w-full mx-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/benchmarks" element={<Benchmarks />} />
              <Route path="/benchmarks/create" element={<CreateBenchmark />} />
              <Route path="/run" element={<RunBenchmark />} />
              <Route path="/runs" element={<RunsHistory />} />
              <Route path="/runs/:id/live" element={<LiveExecution />} />
              <Route path="/runs/:id" element={<RunDetails />} />
              <Route path="/leaderboard" element={<Leaderboard />} />
              <Route path="/failures" element={<FailureAnalysis />} />
              <Route path="/agents-models" element={<AgentsModels />} />
              <Route path="/compare" element={<Compare />} />
              <Route path="/doctor" element={<DoctorDocs />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
};

export default App;
