import React, { useState, useEffect } from 'react';
import { Activity, AlertTriangle } from 'lucide-react';

/**
 * Source Mapping:
 * equityCurveData <- /api/portfolio_analytics -> MT5 history_deals_get()
 * accountMetrics  <- /api/portfolio_analytics -> MT5 get_account_info()
 */

export default function PortfolioAnalyticsView({ accountInfo }) {
  const [analytics, setAnalytics] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);

  useEffect(() => {
    setIsLoading(true);
    setErrorMsg(null);

    // Fetch 100% real equity curve data from MT5 backend deals history
    fetch('http://localhost:8000/api/portfolio_analytics')
      .then(res => {
        if (!res.ok) throw new Error('API server status ' + res.status);
        return res.json();
      })
      .then(data => {
        if (data.error) {
          setErrorMsg(data.error);
        } else {
          setAnalytics(data);
        }
      })
      .catch(err => {
        console.error('Error fetching live analytics:', err);
        setErrorMsg('Equity curve unavailable: backend offline');
      })
      .finally(() => setIsLoading(false));
  }, []);

  const isConnected = analytics?.is_connected ?? false;
  const balance = accountInfo?.balance ?? analytics?.balance;
  const equity = accountInfo?.equity ?? analytics?.equity;
  const netPnl = analytics?.net_pnl;
  const winRate = analytics?.win_rate_pct;
  const profitFactor = analytics?.profit_factor;
  const sharpeRatio = analytics?.sharpe_ratio;
  const maxDrawdown = analytics?.max_drawdown_pct;
  const equityCurve = analytics?.equity_curve || [];

  // Plot ONLY confirmed real observations from backend deal timestamps
  const renderRealEquityCurveSVG = () => {
    if (!equityCurve || equityCurve.length < 2) return null;

    const width = 500;
    const height = 240;
    const pad = 20;

    const equities = equityCurve.map(p => p.equity);
    const minEq = Math.min(...equities);
    const maxEq = Math.max(...equities);
    const range = (maxEq - minEq) || 1;

    const points = equityCurve.map((p, idx) => {
      const x = pad + (idx / (equityCurve.length - 1)) * (width - 2 * pad);
      const y = height - pad - ((p.equity - minEq) / range) * (height - 2 * pad);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    });

    const linePath = `M ${points.join(' L ')}`;
    const areaPath = `M ${points[0]} L ${points.join(' L ')} L ${width - pad},${height - pad} L ${pad},${height - pad} Z`;

    return (
      <svg style={{ width: '100%', height: '100%' }} viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none">
        <defs>
          <linearGradient id="realEqGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#4edea3" stopOpacity="0.30" />
            <stop offset="100%" stopColor="#4edea3" stopOpacity="0.0" />
          </linearGradient>
        </defs>
        <path d={areaPath} fill="url(#realEqGradient)" />
        <path d={linePath} fill="none" stroke="#4edea3" strokeWidth="2.5" />
      </svg>
    );
  };

  return (
    <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px', background: '#0e1511', minHeight: '100vh', color: '#dde4dd' }}>
      
      {/* Page Title Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#ffffff' }}>
            Portfolio Performance Analytics
          </h2>
          <p style={{ fontSize: '0.8rem', color: '#86948a', marginTop: '4px' }}>
            Real MT5 Walk-Forward Account History &amp; Deals Performance (0% Dummy Data Policy)
          </p>
        </div>

        <div className="font-mono" style={{ display: 'flex', gap: '12px', fontSize: '0.78rem' }}>
          <span style={{ padding: '4px 10px', background: '#161d19', borderRadius: '4px', border: '1px solid #3c4a42' }}>
            AUM: <strong style={{ color: '#ffffff' }}>{equity !== undefined ? `$${equity.toLocaleString()}` : '--'}</strong>
          </span>
          <span style={{ padding: '4px 10px', background: isConnected ? 'rgba(78, 222, 163, 0.12)' : 'rgba(255, 180, 171, 0.12)', color: isConnected ? '#4edea3' : '#ffb4ab', borderRadius: '4px', border: `1px solid ${isConnected ? 'rgba(78, 222, 163, 0.3)' : 'rgba(255, 180, 171, 0.3)'}` }}>
            {isConnected ? 'LIVE MT5 FEED' : 'MT5 DISCONNECTED'}
          </span>
        </div>
      </div>

      {/* KPI Cards Strip */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
        <div style={{ background: '#1a211d', border: '1px solid #3c4a42', borderRadius: '6px', padding: '16px' }}>
          <span style={{ fontSize: '0.72rem', color: '#86948a', fontWeight: 700 }}>NET REALIZED P&amp;L</span>
          <h3 className="font-mono" style={{ fontSize: '1.5rem', color: netPnl !== undefined ? (netPnl >= 0 ? '#4edea3' : '#ffb4ab') : '#86948a', marginTop: '6px' }}>
            {netPnl !== undefined ? (netPnl >= 0 ? `+$${netPnl.toLocaleString()}` : `-$${Math.abs(netPnl).toLocaleString()}`) : '--'}
          </h3>
        </div>

        <div style={{ background: '#1a211d', border: '1px solid #3c4a42', borderRadius: '6px', padding: '16px' }}>
          <span style={{ fontSize: '0.72rem', color: '#86948a', fontWeight: 700 }}>SHARPE RATIO (ANN)</span>
          <h3 className="font-mono" style={{ fontSize: '1.5rem', color: '#ffffff', marginTop: '6px' }}>
            {sharpeRatio !== undefined ? sharpeRatio : '--'}
          </h3>
        </div>

        <div style={{ background: '#1a211d', border: '1px solid #3c4a42', borderRadius: '6px', padding: '16px' }}>
          <span style={{ fontSize: '0.72rem', color: '#86948a', fontWeight: 700 }}>MAX DRAWDOWN</span>
          <h3 className="font-mono" style={{ fontSize: '1.5rem', color: '#ffb4ab', marginTop: '6px' }}>
            {maxDrawdown !== undefined ? `-${maxDrawdown}%` : '--'}
          </h3>
        </div>

        <div style={{ background: '#1a211d', border: '1px solid #3c4a42', borderRadius: '6px', padding: '16px' }}>
          <span style={{ fontSize: '0.72rem', color: '#86948a', fontWeight: 700 }}>PROFIT FACTOR</span>
          <h3 className="font-mono" style={{ fontSize: '1.5rem', color: '#ffca45', marginTop: '6px' }}>
            {profitFactor !== undefined ? profitFactor : '--'}
          </h3>
        </div>
      </div>

      {/* Main Grid: Real Equity Curve + Account Metadata */}
      <div style={{ display: 'grid', gridTemplateColumns: '2.2fr 1fr', gap: '16px' }}>
        
        {/* Equity Curve Chart Box */}
        <div style={{ background: '#1a211d', border: '1px solid #3c4a42', borderRadius: '6px', padding: '16px', display: 'flex', flexDirection: 'column', height: '380px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#ffffff', letterSpacing: '0.05em' }}>
              EQUITY CURVE (1Y WALK-FORWARD DEALS HISTORY)
            </span>
            <span style={{ fontSize: '0.72rem', color: '#86948a', fontFamily: 'JetBrains Mono, monospace' }}>
              {equityCurve.length} Closed Deals
            </span>
          </div>

          <div style={{ flex: 1, position: 'relative', background: '#161d19', borderRadius: '4px', overflow: 'hidden', border: '1px solid #3c4a42', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {isLoading ? (
              <div style={{ color: '#4edea3', fontSize: '0.82rem' }}>
                ⚡ FETCHING REAL MT5 WALK-FORWARD DEALS HISTORY...
              </div>
            ) : errorMsg ? (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', color: '#ffb4ab', gap: '8px', padding: '20px', textAlign: 'center' }}>
                <AlertTriangle size={24} color="#ffb4ab" />
                <span style={{ fontSize: '0.85rem', fontWeight: 700 }}>{errorMsg}</span>
              </div>
            ) : equityCurve.length < 2 ? (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', color: '#86948a', gap: '8px', padding: '20px', textAlign: 'center' }}>
                <Activity size={24} color="#86948a" />
                <span style={{ fontSize: '0.85rem', fontWeight: 700 }}>No real 1Y walk-forward equity data available</span>
                <span style={{ fontSize: '0.74rem' }}>MT5 trade deal history required (0 closed trades recorded on account)</span>
              </div>
            ) : (
              renderRealEquityCurveSVG()
            )}
          </div>
        </div>

        {/* Account Details Box */}
        <div style={{ background: '#1a211d', border: '1px solid #3c4a42', borderRadius: '6px', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#ffffff', letterSpacing: '0.05em', marginBottom: '4px' }}>
            REAL ACCOUNT DETAILS
          </span>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1 }}>
            <div style={{ padding: '10px', background: '#161d19', border: '1px solid #3c4a42', borderRadius: '4px', display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.78rem', color: '#86948a' }}>ACCOUNT LOGIN</span>
              <span className="font-mono" style={{ fontSize: '0.85rem', color: '#ffffff', fontWeight: 700 }}>
                {analytics?.account_number ? `#${analytics.account_number}` : '--'}
              </span>
            </div>

            <div style={{ padding: '10px', background: '#161d19', border: '1px solid #3c4a42', borderRadius: '4px', display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.78rem', color: '#86948a' }}>SERVER</span>
              <span className="font-mono" style={{ fontSize: '0.85rem', color: '#ffffff', fontWeight: 700 }}>
                {analytics?.server || '--'}
              </span>
            </div>

            <div style={{ padding: '10px', background: '#161d19', border: '1px solid #3c4a42', borderRadius: '4px', display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.78rem', color: '#86948a' }}>BALANCE</span>
              <span className="font-mono" style={{ fontSize: '0.85rem', color: '#4edea3', fontWeight: 700 }}>
                {balance !== undefined ? `$${balance.toLocaleString()}` : '--'}
              </span>
            </div>

            <div style={{ padding: '10px', background: '#161d19', border: '1px solid #3c4a42', borderRadius: '4px', display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.78rem', color: '#86948a' }}>FREE MARGIN</span>
              <span className="font-mono" style={{ fontSize: '0.85rem', color: '#4edea3', fontWeight: 700 }}>
                {analytics?.free_margin !== undefined ? `$${analytics.free_margin.toLocaleString()}` : '--'}
              </span>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}
