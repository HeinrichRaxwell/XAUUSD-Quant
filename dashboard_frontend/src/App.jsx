import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import MetricCard from './components/MetricCard';
import FinalRecommendationCard from './components/FinalRecommendationCard';
import InteractiveQuantChart from './components/InteractiveQuantChart';
import TradingViewHeatmap from './components/TradingViewHeatmap';
import TradingViewTechSummary from './components/TradingViewTechSummary';
import QuantSignalPanel from './components/QuantSignalPanel';
import ActivePositionsTable from './components/ActivePositionsTable';
import CorrelationMatrix from './components/CorrelationMatrix';
import PortfolioAnalyticsView from './components/PortfolioAnalyticsView';
import CorrelationLabView from './components/CorrelationLabView';
import MarketIntelligenceView from './components/MarketIntelligenceView';
import AlertManagementView from './components/AlertManagementView';

import { Terminal, PieChart, FlaskConical, Bell, Newspaper, Settings } from 'lucide-react';

const API_BASE = 'http://localhost:8000/api';

export default function App() {
  const [accountInfo, setAccountInfo] = useState(null);
  const [positions, setPositions] = useState([]);
  const [signalData, setSignalData] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [activeTab, setActiveTab] = useState('terminal');

  const fetchAllData = async () => {
    setIsRefreshing(true);
    try {
      const [accRes, posRes, sigRes] = await Promise.all([
        fetch(`${API_BASE}/account`),
        fetch(`${API_BASE}/positions`),
        fetch(`${API_BASE}/signal`)
      ]);

      if (accRes.ok) setAccountInfo(await accRes.json());
      if (posRes.ok) setPositions(await posRes.json());
      if (sigRes.ok) setSignalData(await sigRes.json());

      setErrorMsg(null);
    } catch (err) {
      console.error('Failed to sync API:', err);
      setErrorMsg('FastAPI backend offline or connecting... (http://localhost:8000)');
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleRunAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      const res = await fetch(`${API_BASE}/analyze`, { method: 'POST' });
      if (res.ok) {
        await fetchAllData();
      }
    } catch (e) {
      console.error('Error running inline analysis:', e);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleClosePosition = async (ticket) => {
    try {
      const res = await fetch(`${API_BASE}/close_position/${ticket}`, { method: 'POST' });
      if (res.ok) fetchAllData();
    } catch (e) {
      alert(`Error closing trade: ${e.message}`);
    }
  };

  const handleCloseAll = async () => {
    try {
      const res = await fetch(`${API_BASE}/close_all`, { method: 'POST' });
      if (res.ok) fetchAllData();
    } catch (e) {
      alert(`Error closing all trades: ${e.message}`);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', background: '#0e1511', color: '#dde4dd' }}>
      
      {/* Left Icon Rail Navigation Bar (QuantOS SideNavBar) */}
      <aside style={{
        width: '56px',
        background: '#161d19',
        borderRight: '1px solid #242c27',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: '16px 0',
        gap: '16px',
        flexShrink: 0,
        zIndex: 20
      }}>
        <button
          onClick={() => setActiveTab('terminal')}
          style={{
            width: '40px', height: '40px', borderRadius: '6px', border: 'none',
            background: activeTab === 'terminal' ? '#2f3632' : 'transparent',
            color: activeTab === 'terminal' ? '#4edea3' : '#86948a',
            display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer'
          }}
          title="Terminal (Main Dashboard)"
        >
          <Terminal size={20} />
        </button>

        <button
          onClick={() => setActiveTab('portfolio')}
          style={{
            width: '40px', height: '40px', borderRadius: '6px', border: 'none',
            background: activeTab === 'portfolio' ? '#2f3632' : 'transparent',
            color: activeTab === 'portfolio' ? '#4edea3' : '#86948a',
            display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer'
          }}
          title="Portfolio Analytics"
        >
          <PieChart size={20} />
        </button>

        <button
          onClick={() => setActiveTab('correlation')}
          style={{
            width: '40px', height: '40px', borderRadius: '6px', border: 'none',
            background: activeTab === 'correlation' ? '#2f3632' : 'transparent',
            color: activeTab === 'correlation' ? '#4edea3' : '#86948a',
            display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer'
          }}
          title="Correlation Lab (Macro Cross-Asset Heatmap)"
        >
          <FlaskConical size={20} />
        </button>

        <button
          onClick={() => setActiveTab('intelligence')}
          style={{
            width: '40px', height: '40px', borderRadius: '6px', border: 'none',
            background: activeTab === 'intelligence' ? '#2f3632' : 'transparent',
            color: activeTab === 'intelligence' ? '#4edea3' : '#86948a',
            display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer'
          }}
          title="Market Intelligence & Macro Feed"
        >
          <Newspaper size={20} />
        </button>

        <button
          onClick={() => setActiveTab('alerts')}
          style={{
            width: '40px', height: '40px', borderRadius: '6px', border: 'none',
            background: activeTab === 'alerts' ? '#2f3632' : 'transparent',
            color: activeTab === 'alerts' ? '#4edea3' : '#86948a',
            display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer'
          }}
          title="Alert Management & Telegram Triggers"
        >
          <Bell size={20} />
        </button>

        <div style={{ flexGrow: 1 }} />

        <button
          style={{
            width: '40px', height: '40px', borderRadius: '6px', border: 'none',
            background: 'transparent', color: '#86948a',
            display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer'
          }}
          title="Settings"
        >
          <Settings size={20} />
        </button>
      </aside>

      {/* Main Workspace Wrapper */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflowX: 'hidden' }}>
        
        {/* Header Bar */}
        <Header
          onRefresh={fetchAllData}
          isRefreshing={isRefreshing}
          accountInfo={accountInfo}
          onOpenAnalysis={handleRunAnalysis}
        />

        {/* Connection Warning */}
        {errorMsg && (
          <div style={{
            margin: '12px 20px 0 20px',
            padding: '10px 16px',
            borderRadius: '4px',
            background: 'rgba(255, 180, 171, 0.15)',
            border: '1px solid rgba(255, 180, 171, 0.3)',
            color: '#ffb4ab',
            fontSize: '0.82rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span>⚠️ {errorMsg}</span>
            <button onClick={fetchAllData} style={{ background: 'transparent', border: '1px solid #ffb4ab', color: '#ffb4ab', borderRadius: '4px', padding: '2px 8px', cursor: 'pointer' }}>Retry</button>
          </div>
        )}

        {/* Submenu Views Switcher */}
        {activeTab === 'terminal' && (
          <>
            {/* Top Telemetry Metric Cards */}
            <MetricCard accountInfo={accountInfo} signalData={signalData} />

            {/* Main Split Layout */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'minmax(0, 2.2fr) minmax(0, 1fr)',
              gap: '16px',
              margin: '16px 20px 40px 20px'
            }}>
              
              {/* Left Main Column (70% width) */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                
                <FinalRecommendationCard
                  signalData={signalData}
                  isAnalyzing={isAnalyzing}
                  onRunAnalysis={handleRunAnalysis}
                />

                <InteractiveQuantChart
                  isAnalyzing={isAnalyzing}
                  onRefreshChart={fetchAllData}
                />

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <ActivePositionsTable
                    positions={positions}
                    onClosePosition={handleClosePosition}
                    onCloseAll={handleCloseAll}
                  />
                  <CorrelationMatrix />
                </div>

                <TradingViewHeatmap />

              </div>

              {/* Right Column (30% width) */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                
                <QuantSignalPanel signalData={signalData} />

                <TradingViewTechSummary />

              </div>

            </div>
          </>
        )}

        {activeTab === 'portfolio' && (
          <PortfolioAnalyticsView accountInfo={accountInfo} />
        )}

        {activeTab === 'correlation' && (
          <CorrelationLabView />
        )}

        {activeTab === 'intelligence' && (
          <MarketIntelligenceView />
        )}

        {activeTab === 'alerts' && (
          <AlertManagementView />
        )}

        {/* Footer */}
        <footer className="font-mono" style={{ textAlign: 'center', padding: '16px', fontSize: '0.75rem', color: '#86948a', borderTop: '1px solid #242c27', marginTop: 'auto' }}>
          QuantOS XAUUSD Institutional Terminal &bull; Developed with LightGBM, Monte Carlo 10K GBM &amp; TradingView Live Canvas &bull; 2026
        </footer>

      </div>

    </div>
  );
}
