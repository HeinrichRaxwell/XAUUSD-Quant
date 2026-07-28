import React, { useState } from 'react';
import { Image, Maximize2, X, RefreshCw } from 'lucide-react';

export default function SignalChartViewer({ chartUrl, onRefreshChart }) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [imgTimestamp, setImgTimestamp] = useState(Date.now());

  const handleRefresh = () => {
    setImgTimestamp(Date.now());
    if (onRefreshChart) onRefreshChart();
  };

  const srcWithCacheBust = `http://localhost:8000/api/chart?t=${imgTimestamp}`;

  return (
    <div className="glass-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', height: '480px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Image size={18} color="#f59e0b" />
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700 }}>
            QuantOS AI Candlestick Chart (Python Engine)
          </h4>
        </div>
        
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={handleRefresh}
            style={{
              background: 'rgba(30, 41, 59, 0.6)',
              border: '1px solid var(--border-card)',
              color: 'var(--text-muted)',
              padding: '4px 8px',
              borderRadius: '6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '0.75rem'
            }}
          >
            <RefreshCw size={12} /> Reload
          </button>
          
          <button
            onClick={() => setIsModalOpen(true)}
            style={{
              background: 'rgba(245, 158, 11, 0.15)',
              border: '1px solid var(--border-gold)',
              color: '#fbbf24',
              padding: '4px 8px',
              borderRadius: '6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '0.75rem',
              fontWeight: 600
            }}
          >
            <Maximize2 size={12} /> Expand
          </button>
        </div>
      </div>

      {/* Image Preview Container */}
      <div style={{ flex: 1, overflow: 'hidden', borderRadius: '8px', border: '1px solid var(--border-card)', background: '#000', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <img
          src={srcWithCacheBust}
          alt="XAUUSD QuantOS Signal Chart"
          style={{ width: '100%', height: '100%', objectFit: 'contain', cursor: 'pointer' }}
          onClick={() => setIsModalOpen(true)}
          onError={(e) => {
            e.target.style.display = 'none';
          }}
        />
      </div>

      {/* Full Resolution Modal */}
      {isModalOpen && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.88)',
          backdropFilter: 'blur(12px)',
          zIndex: 9999,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          padding: '24px'
        }}>
          <div style={{ position: 'relative', maxWidth: '95vw', maxHeight: '95vh', width: '100%', height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <button
              onClick={() => setIsModalOpen(false)}
              style={{
                position: 'absolute',
                top: '-16px',
                right: '-16px',
                background: '#f43f5e',
                color: '#fff',
                border: 'none',
                borderRadius: '50%',
                width: '36px',
                height: '36px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                boxShadow: '0 0 15px rgba(244,63,94,0.5)'
              }}
            >
              <X size={20} />
            </button>
            <img
              src={srcWithCacheBust}
              alt="QuantOS Chart Full Resolution"
              style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', borderRadius: '8px', boxShadow: '0 0 40px rgba(0,0,0,0.8)' }}
            />
          </div>
        </div>
      )}

    </div>
  );
}
