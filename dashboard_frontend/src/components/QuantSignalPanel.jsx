import React from 'react';
import { Zap, Activity } from 'lucide-react';

export default function QuantSignalPanel({ signalData }) {
  if (!signalData) {
    return (
      <div className="quant-card" style={{ padding: '24px', textAlign: 'center', color: 'var(--on-surface-variant)' }}>
        Loading Live Quant AI Engine...
      </div>
    );
  }

  const {
    current_price,
    ml_signal = 'NEUTRAL',
    confidence_pct,
    probabilities = { sell: 0, neutral: 0, buy: 0 },
    monte_carlo = {},
    technical_indicators = {}
  } = signalData;

  const isSell = ml_signal === 'SELL';
  const isBuy = ml_signal === 'BUY';
  const isNeutral = ml_signal === 'NEUTRAL';

  const badgeColor = isSell ? '#ffb4ab' : (isBuy ? '#4edea3' : '#ffca45');
  const strokeColor = isSell ? '#ffb4ab' : (isBuy ? '#4edea3' : '#4edea3');

  // Radial Gauge Math (Circle circumference 2 * pi * 40 = ~251)
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (confidence_pct / 100) * circumference;

  return (
    <div className="quant-card" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Zap size={16} color="#4edea3" />
          <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--on-surface)', letterSpacing: '0.05em' }}>
            AI SIGNAL ENGINE
          </h4>
        </div>
        <span style={{ fontSize: '0.7rem', color: '#4edea3', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#4edea3' }} />
          ACTIVE
        </span>
      </div>

      {/* Radial AI Signal Circle Gauge */}
      <div className="quant-card-low" style={{ padding: '20px 16px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ position: 'relative', width: '120px', height: '120px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <svg width="120" height="120" viewBox="0 0 100 100">
            <circle
              cx="50"
              cy="50"
              r={radius}
              fill="none"
              stroke="var(--outline-variant)"
              strokeWidth="8"
            />
            <circle
              cx="50"
              cy="50"
              r={radius}
              fill="none"
              stroke={strokeColor}
              strokeWidth="8"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              transform="rotate(-90 50 50)"
              style={{ transition: 'stroke-dashoffset 0.8s ease' }}
            />
          </svg>

          <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
            <span className="font-mono" style={{ fontSize: '1.4rem', fontWeight: 800, color: '#ffffff', letterSpacing: '-0.02em', lineHeight: '1' }}>
              {confidence_pct.toFixed(1)}%
            </span>
          </div>
        </div>

        <div style={{ marginTop: '12px', textAlign: 'center' }}>
          <span
            style={{
              padding: '4px 14px',
              borderRadius: '4px',
              fontSize: '0.78rem',
              fontWeight: 800,
              letterSpacing: '0.05em',
              background: 'rgba(78, 222, 163, 0.15)',
              color: badgeColor,
              border: `1px solid ${badgeColor}40`,
            }}
          >
            {ml_signal === 'NEUTRAL' ? 'HOLD / NEUTRAL' : `STRONG ${ml_signal}`}
          </span>
          <p style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', marginTop: '8px', maxWidth: '220px', lineHeight: '1.3' }}>
            Confluence of bullish harmonic structure and positive macro USD divergence.
          </p>
        </div>
      </div>

      {/* Directional Probability (4H) */}
      <div>
        <p style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--on-surface-variant)', marginBottom: '8px', letterSpacing: '0.05em' }}>
          DIRECTIONAL PROBABILITY (4H)
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '2px' }}>
              <span style={{ color: '#4edea3', fontWeight: 600 }}>&uarr; UP</span>
              <span className="font-mono" style={{ color: '#4edea3', fontWeight: 700 }}>{probabilities.buy}%</span>
            </div>
            <div style={{ height: '6px', background: 'var(--surface-container-high)', borderRadius: '3px', overflow: 'hidden' }}>
              <div style={{ width: `${probabilities.buy}%`, height: '100%', background: '#4edea3', transition: 'width 0.5s ease' }} />
            </div>
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '2px' }}>
              <span style={{ color: '#ffca45', fontWeight: 600 }}>&rarr; SIDE</span>
              <span className="font-mono" style={{ color: '#ffca45', fontWeight: 700 }}>{probabilities.neutral}%</span>
            </div>
            <div style={{ height: '6px', background: 'var(--surface-container-high)', borderRadius: '3px', overflow: 'hidden' }}>
              <div style={{ width: `${probabilities.neutral}%`, height: '100%', background: '#ffca45', transition: 'width 0.5s ease' }} />
            </div>
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '2px' }}>
              <span style={{ color: '#ffb4ab', fontWeight: 600 }}>&darr; DOWN</span>
              <span className="font-mono" style={{ color: '#ffb4ab', fontWeight: 700 }}>{probabilities.sell}%</span>
            </div>
            <div style={{ height: '6px', background: 'var(--surface-container-high)', borderRadius: '3px', overflow: 'hidden' }}>
              <div style={{ width: `${probabilities.sell}%`, height: '100%', background: '#ffb4ab', transition: 'width 0.5s ease' }} />
            </div>
          </div>
        </div>
      </div>

      {/* Monte Carlo Projections (EOD) */}
      <div>
        <p style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--on-surface-variant)', marginBottom: '8px', letterSpacing: '0.05em' }}>
          MONTE CARLO PROJECTIONS (EOD)
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 12px', background: 'var(--surface-container-low)', borderRadius: '4px', border: '1px solid var(--outline-variant)' }}>
            <span style={{ fontSize: '0.75rem', color: '#4edea3', fontWeight: 600 }}>P90 (Bull)</span>
            <span className="font-mono" style={{ fontSize: '0.85rem', fontWeight: 700, color: '#4edea3' }}>
              ${monte_carlo.p90_target.toFixed(2)}
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 12px', background: 'var(--surface-container-low)', borderRadius: '4px', border: '1px solid var(--outline-variant)' }}>
            <span style={{ fontSize: '0.75rem', color: '#ffca45', fontWeight: 600 }}>P50 (Median)</span>
            <span className="font-mono" style={{ fontSize: '0.85rem', fontWeight: 700, color: '#ffca45' }}>
              ${monte_carlo.p50_target.toFixed(2)}
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 12px', background: 'var(--surface-container-low)', borderRadius: '4px', border: '1px solid var(--outline-variant)' }}>
            <span style={{ fontSize: '0.75rem', color: '#ffb4ab', fontWeight: 600 }}>P10 (Bear)</span>
            <span className="font-mono" style={{ fontSize: '0.85rem', fontWeight: 700, color: '#ffb4ab' }}>
              ${monte_carlo.p10_target.toFixed(2)}
            </span>
          </div>
        </div>
      </div>

      {/* Technical Pressure */}
      <div>
        <p style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--on-surface-variant)', marginBottom: '8px', letterSpacing: '0.05em' }}>
          TECHNICAL PRESSURE
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
          <div style={{ background: 'var(--surface-container-low)', padding: '8px 10px', borderRadius: '4px', border: '1px solid var(--outline-variant)' }}>
            <span style={{ fontSize: '0.68rem', color: 'var(--on-surface-variant)' }}>RSI (14)</span>
            <div className="font-mono" style={{ fontSize: '0.85rem', fontWeight: 700, color: '#ffffff' }}>
              {technical_indicators.rsi_wilder.toFixed(1)}
            </div>
          </div>

          <div style={{ background: 'var(--surface-container-low)', padding: '8px 10px', borderRadius: '4px', border: '1px solid var(--outline-variant)' }}>
            <span style={{ fontSize: '0.68rem', color: 'var(--on-surface-variant)' }}>ADX (14)</span>
            <div className="font-mono" style={{ fontSize: '0.85rem', fontWeight: 700, color: '#4edea3' }}>
              {technical_indicators.adx_14.toFixed(1)} <span style={{ fontSize: '0.65rem', color: '#86948a' }}>STRONG</span>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}
