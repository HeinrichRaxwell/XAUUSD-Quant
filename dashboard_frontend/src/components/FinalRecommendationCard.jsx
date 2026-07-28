import React from 'react';
import { Play, RefreshCw } from 'lucide-react';

export default function FinalRecommendationCard({ signalData, isAnalyzing, onRunAnalysis }) {
  if (!signalData) {
    return (
      <div className="quant-card" style={{ padding: '16px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: '0.8rem', color: 'var(--on-surface-variant)', fontWeight: 600 }}>
          ⚡ CALCULATING LIVE QUANT MODEL CONFLUENCE &amp; CONFIDENCE...
        </span>
        <button disabled style={{ padding: '6px 14px', borderRadius: '4px', border: 'none', background: 'var(--surface-container-high)', color: '#86948a', fontSize: '0.82rem' }}>
          Syncing...
        </button>
      </div>
    );
  }

  const signal = signalData.ml_signal || 'NEUTRAL';
  const confidence = signalData.confidence_pct;
  const timeframe = 'Daily / H1';

  const isSell = signal === 'SELL';
  const isBuy = signal === 'BUY';

  const dirBadge = isSell ? 'BEAR' : (isBuy ? 'BULL' : 'NEUTRAL');
  const actionText = isSell ? 'SELL NOW' : (isBuy ? 'BUY NOW' : 'HOLD / WATCH');
  
  const themeColor = isSell ? '#ffb4ab' : (isBuy ? '#4edea3' : '#ffca45');

  return (
    <div className="quant-card" style={{ padding: '16px 20px', position: 'relative', overflow: 'hidden' }}>
      
      {/* Header Row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--on-surface-variant)', letterSpacing: '0.05em' }}>
            {dirBadge} &bull; TIMEFRAME {timeframe}
          </span>

          <span className="font-mono" style={{
            background: 'rgba(78, 222, 163, 0.12)',
            color: themeColor,
            border: `1px solid ${themeColor}40`,
            padding: '2px 8px',
            borderRadius: '4px',
            fontWeight: 700,
            fontSize: '0.75rem'
          }}>
            {actionText}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="font-mono" style={{ fontSize: '1.4rem', fontWeight: 800, color: themeColor }}>
            {confidence != null ? `${confidence.toFixed(1)}%` : '--%'}
          </span>
          <button
            onClick={onRunAnalysis}
            disabled={isAnalyzing}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 14px',
              borderRadius: '4px',
              border: 'none',
              background: '#4edea3',
              color: '#002113',
              fontWeight: 700,
              fontSize: '0.82rem',
              cursor: 'pointer'
            }}
          >
            {isAnalyzing ? <RefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} /> : <Play size={14} fill="#002113" />}
            <span>{isAnalyzing ? 'ANALYZING...' : 'RUN ANALYSIS'}</span>
          </button>
        </div>

      </div>

      <h3 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '8px', color: '#ffffff' }}>
        Final Quant Recommendation &amp; Model Confluence
      </h3>

      {/* Progress Bar */}
      <div style={{ height: '6px', background: 'var(--surface-container-high)', borderRadius: '3px', overflow: 'hidden' }}>
        <div style={{
          width: `${confidence}%`,
          height: '100%',
          background: themeColor,
          transition: 'width 0.6s ease'
        }} />
      </div>

    </div>
  );
}
