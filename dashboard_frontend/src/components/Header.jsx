import React, { useState, useEffect } from 'react';
import { Play, RefreshCw, Plus, Activity } from 'lucide-react';

export default function Header({ onRefresh, isRefreshing, accountInfo, onOpenAnalysis }) {
  const [timeStr, setTimeStr] = useState('');

  useEffect(() => {
    const updateClock = () => {
      const now = new Date();
      setTimeStr(now.toLocaleTimeString('id-ID', { timeZone: 'Asia/Jakarta', hour12: false }) + ' WIB');
    };
    updateClock();
    const interval = setInterval(updateClock, 1000);
    return () => clearInterval(interval);
  }, []);

  const isConnected = accountInfo && accountInfo.account;

  return (
    <header style={{ display: 'flex', flexDirection: 'column', width: '100%', background: '#0e1511', borderBottom: '1px solid #242c27' }}>
      
      {/* Top Main Navigation Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: '52px', padding: '0 20px', borderBottom: '1px solid #242c27' }}>
        
        {/* Brand & Status Tabs */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Activity size={22} color="#4edea3" />
            <span className="font-mono" style={{ fontSize: '1.25rem', fontWeight: 800, color: '#4edea3', letterSpacing: '-0.02em' }}>
              QuantOS
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '0.85rem' }}>
            <span style={{ color: '#4edea3', borderBottom: '2px solid #4edea3', paddingBottom: '12px', paddingTop: '12px', fontWeight: 600 }}>
              Live
            </span>
            <span style={{ color: '#bbcabf', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: isRefreshing ? '#ffca45' : '#4edea3' }} />
              {isRefreshing ? 'Syncing...' : 'Syncing'}
            </span>
            <span className="font-mono" style={{ color: '#86948a', fontSize: '0.78rem' }}>
              12ms
            </span>
            <span className="font-mono" style={{ color: '#86948a', fontSize: '0.78rem' }}>
              {timeStr}
            </span>
          </div>
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          
          {/* Prominent Run Analysis Button */}
          <button
            onClick={onOpenAnalysis}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 16px',
              borderRadius: '4px',
              border: 'none',
              background: '#4edea3',
              color: '#002113',
              fontWeight: 700,
              fontSize: '0.85rem',
              cursor: 'pointer',
              transition: 'background 0.2s ease'
            }}
          >
            <Play size={14} fill="#002113" />
            <span>ANALYSIS</span>
          </button>

          {/* Sync Button */}
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 14px',
              borderRadius: '4px',
              border: '1px solid #3c4a42',
              background: '#1a211d',
              color: '#dde4dd',
              fontWeight: 600,
              fontSize: '0.82rem',
              cursor: 'pointer'
            }}
          >
            <RefreshCw size={14} style={{ animation: isRefreshing ? 'spin 1s linear infinite' : 'none' }} />
            <span>Sync</span>
          </button>

          {/* Account Status Badge */}
          {isConnected && (
            <span className="font-mono" style={{ padding: '4px 10px', borderRadius: '4px', background: 'rgba(78, 222, 163, 0.12)', color: '#4edea3', border: '1px solid rgba(78, 222, 163, 0.3)', fontSize: '0.78rem' }}>
              MT5 #{accountInfo.account} ({accountInfo.company || 'Exness'})
            </span>
          )}
        </div>

      </div>

      {/* Subheader Ticker Bar */}
      <div className="font-mono" style={{ display: 'flex', alignItems: 'center', height: '34px', padding: '0 20px', background: '#161d19', fontSize: '0.78rem', gap: '20px', borderBottom: '1px solid #242c27' }}>
        <span style={{ color: '#ffffff', fontWeight: 700, borderRight: '1px solid #3c4a42', paddingRight: '16px' }}>
          XAUUSD
        </span>
        <span style={{ color: '#86948a' }}>Spread: <span style={{ color: '#dde4dd' }}>0.2</span></span>
        <span style={{ color: '#86948a' }}>Vol: <span style={{ color: '#dde4dd' }}>1.2M</span></span>
        <span style={{ color: '#4edea3', fontWeight: 600 }}>Change: +0.45%</span>
        <span style={{ color: '#ffca45', marginLeft: 'auto', fontSize: '0.75rem' }}>
          LightGBM AI &amp; 10,000 Monte Carlo Engine
        </span>
      </div>

    </header>
  );
}
