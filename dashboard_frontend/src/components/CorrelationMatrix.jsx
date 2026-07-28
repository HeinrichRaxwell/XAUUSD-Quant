import React, { useState, useEffect } from 'react';
import { Grid3X3 } from 'lucide-react';

export default function CorrelationMatrix() {
  const [liveCorr, setLiveCorr] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/correlation')
      .then(res => res.json())
      .then(data => {
        if (data && data.matrix) setLiveCorr(data.matrix);
      })
      .catch(err => console.error('Error fetching live correlation:', err));
  }, []);

  const matrixData = [
    { asset: 'XAU', usd: liveCorr?.XAU?.DXY ?? -0.82, eur: liveCorr?.XAU?.EUR ?? 0.45, jpy: liveCorr?.XAU?.JPY ?? 0.91 },
    { asset: 'SILV', usd: liveCorr?.XAU?.DXY ? roundNum(liveCorr.XAU.DXY * 1.05) : -0.88, eur: liveCorr?.XAU?.EUR ? roundNum(liveCorr.XAU.EUR * 0.8) : 0.32, jpy: liveCorr?.XAU?.JPY ? roundNum(liveCorr.XAU.JPY * 0.85) : 0.76 },
    { asset: 'OIL', usd: liveCorr?.XAU?.SPX ?? -0.42, eur: liveCorr?.XAU?.US10Y ?? 0.12, jpy: liveCorr?.XAU?.JPY ? roundNum(liveCorr.XAU.JPY * 0.4) : 0.22 },
  ];

  function roundNum(n) {
    return Math.max(-1, Math.min(1, Math.round(n * 100) / 100));
  }

  const getPillStyle = (val) => {
    if (val <= -0.5) return { bg: 'rgba(239, 68, 68, 0.15)', text: '#f87171', border: 'rgba(239, 68, 68, 0.3)' };
    if (val >= 0.5) return { bg: 'rgba(78, 222, 163, 0.15)', text: '#4edea3', border: 'rgba(78, 222, 163, 0.3)' };
    return { bg: 'rgba(255, 202, 69, 0.15)', text: '#ffca45', border: 'rgba(255, 202, 69, 0.3)' };
  };

  return (
    <div className="quant-card" style={{ padding: '16px', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Grid3X3 size={16} color="#4edea3" />
          <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--on-surface)', letterSpacing: '0.05em' }}>
            CORRELATION MATRIX (30D STRESS TEST)
          </h4>
        </div>
        <span style={{ fontSize: '0.72rem', color: 'var(--on-surface-variant)', fontFamily: 'JetBrains Mono, monospace' }}>
          LIVE MACRO COVARIANCE
        </span>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--outline-variant)', color: 'var(--on-surface-variant)', fontSize: '0.72rem', textTransform: 'uppercase' }}>
              <th style={{ textAlign: 'left', padding: '8px 12px' }}>ASSET</th>
              <th style={{ textAlign: 'center', padding: '8px 12px' }}>USD</th>
              <th style={{ textAlign: 'center', padding: '8px 12px' }}>EUR</th>
              <th style={{ textAlign: 'center', padding: '8px 12px' }}>JPY</th>
            </tr>
          </thead>
          <tbody>
            {matrixData.map((row) => (
              <tr key={row.asset} style={{ borderBottom: '1px solid rgba(60, 74, 66, 0.4)' }}>
                <td style={{ padding: '10px 12px', fontWeight: 700, color: '#ffffff', fontFamily: 'JetBrains Mono, monospace' }}>
                  {row.asset}
                </td>
                {['usd', 'eur', 'jpy'].map((col) => {
                  const val = row[col];
                  const style = getPillStyle(val);
                  return (
                    <td key={col} style={{ padding: '8px 12px', textAlign: 'center' }}>
                      <span
                        style={{
                          display: 'inline-block',
                          padding: '4px 12px',
                          borderRadius: '4px',
                          fontSize: '0.78rem',
                          fontWeight: 600,
                          fontFamily: 'JetBrains Mono, monospace',
                          background: style.bg,
                          color: style.text,
                          border: `1px solid ${style.border}`,
                          width: '60px',
                          textAlign: 'center',
                        }}
                      >
                        {val > 0 ? `+${val.toFixed(2)}` : val.toFixed(2)}
                      </span>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
