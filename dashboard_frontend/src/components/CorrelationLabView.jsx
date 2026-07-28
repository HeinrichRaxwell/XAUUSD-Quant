import React, { useState, useEffect, useRef } from 'react';
import { Activity, Globe, AlertTriangle } from 'lucide-react';

export default function CorrelationLabView() {
  const [selectedCell, setSelectedCell] = useState(null);
  const [timeframe, setTimeframe] = useState('30D');
  const [liveMatrix, setLiveMatrix] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [matrixError, setMatrixError] = useState(null);
  const [widgetError, setWidgetError] = useState(false);

  const tvHeatmapRef = useRef(null);

  // Fetch 100% computed Pearson correlation matrix from live MT5 backend
  useEffect(() => {
    setIsLoading(true);
    setMatrixError(null);
    fetch('http://localhost:8000/api/correlation')
      .then(res => {
        if (!res.ok) throw new Error('API server returned status ' + res.status);
        return res.json();
      })
      .then(data => {
        if (data && data.matrix) {
          setLiveMatrix(data.matrix);
          if (data.matrix.XAU && data.matrix.XAU.DXY !== undefined) {
            setSelectedCell({
              pair: 'XAU vs DXY',
              val: data.matrix.XAU.DXY,
              status: data.matrix.XAU.DXY < 0 ? 'INVERSE CORRELATION' : 'POSITIVE CORRELATION'
            });
          }
        } else {
          throw new Error('Correlation matrix empty or unavailable');
        }
      })
      .catch(err => {
        console.error('Error fetching live correlation:', err);
        setMatrixError('Live MT5 correlation matrix backend unavailable');
      })
      .finally(() => setIsLoading(false));
  }, []);

  // Embed TradingView Official Forex Cross-Rates Widget using official script.text execution
  useEffect(() => {
    if (!tvHeatmapRef.current) return;
    tvHeatmapRef.current.innerHTML = '';
    setWidgetError(false);

    try {
      const widgetDiv = document.createElement('div');
      widgetDiv.className = 'tradingview-widget-container__widget';
      widgetDiv.style.height = '100%';
      widgetDiv.style.width = '100%';

      const script = document.createElement('script');
      script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-forex-cross-rates.js';
      script.type = 'text/javascript';
      script.async = true;
      script.text = JSON.stringify({
        width: '100%',
        height: '100%',
        currencies: ['EUR', 'USD', 'JPY', 'GBP', 'CHF', 'AUD', 'CAD', 'NZD'],
        isTransparent: false,
        colorTheme: 'dark',
        locale: 'en'
      });

      script.onerror = () => setWidgetError(true);

      tvHeatmapRef.current.appendChild(widgetDiv);
      tvHeatmapRef.current.appendChild(script);
    } catch (e) {
      setWidgetError(true);
    }
  }, []);

  const assets = ['XAU', 'DXY', 'US10Y', 'SPX', 'EUR', 'JPY'];

  const getCellBg = (val) => {
    if (val === 1.00) return '#242c27';
    if (val < 0) {
      const alpha = Math.min(Math.abs(val) * 0.35, 0.35);
      return `rgba(255, 180, 171, ${alpha})`;
    }
    const alpha = Math.min(val * 0.35, 0.35);
    return `rgba(78, 222, 163, ${alpha})`;
  };

  const getCellColor = (val) => {
    if (val === 1.00) return '#86948a';
    if (val < 0) return '#ffb4ab';
    return '#4edea3';
  };

  return (
    <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px', background: '#0e1511', minHeight: '100vh', color: '#dde4dd' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#ffffff' }}>
            Cross-Asset Correlation Matrix &amp; Macro Lab
          </h2>
          <p style={{ fontSize: '0.8rem', color: '#86948a', marginTop: '4px' }}>
            Real-time Pearson correlation calculated live from MT5 market price series (0% Mock / Dummy Data)
          </p>
        </div>
      </div>

      {/* Main Grid: Live Computed Matrix + Pair Detail */}
      <div style={{ display: 'grid', gridTemplateColumns: '2.2fr 1fr', gap: '16px' }}>
        
        {/* Pearson Heatmap Box */}
        <div style={{ background: '#1a211d', border: '1px solid #3c4a42', borderRadius: '6px', padding: '16px', display: 'flex', flexDirection: 'column', minHeight: '380px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid #3c4a42', paddingBottom: '10px' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#ffffff', letterSpacing: '0.05em' }}>
              REAL-TIME PEARSON CORRELATION (MT5 LIVE DATA)
            </span>
            <div className="font-mono" style={{ display: 'flex', gap: '4px', fontSize: '0.72rem' }}>
              {['30D', '90D', '1Y'].map(tf => (
                <button
                  key={tf}
                  onClick={() => setTimeframe(tf)}
                  style={{
                    padding: '2px 8px',
                    borderRadius: '3px',
                    border: '1px solid #3c4a42',
                    background: timeframe === tf ? 'var(--on-primary-container)' : '#161d19',
                    color: timeframe === tf ? '#4edea3' : '#86948a',
                    fontWeight: timeframe === tf ? 700 : 400,
                    cursor: 'pointer'
                  }}
                >
                  {tf}
                </button>
              ))}
            </div>
          </div>

          {/* Render Loading, Honest Error State, or Live Calculated Matrix */}
          {isLoading ? (
            <div style={{ height: '260px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#4edea3', fontSize: '0.85rem' }}>
              ⚡ COMPUTING LIVE PEARSON COVARIANCE MATRIX FROM MT5 DATA...
            </div>
          ) : matrixError ? (
            <div style={{ height: '260px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#ffb4ab', gap: '8px', padding: '20px', textAlign: 'center' }}>
              <AlertTriangle size={24} color="#ffb4ab" />
              <span style={{ fontSize: '0.85rem', fontWeight: 700 }}>{matrixError}</span>
            </div>
          ) : (
            <div style={{ overflowX: 'auto', flex: 1 }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr>
                    <th style={{ width: '60px', padding: '8px' }} />
                    {assets.map(a => (
                      <th key={a} style={{ padding: '8px', textAlign: 'center', color: '#86948a', fontSize: '0.75rem', fontWeight: 700 }}>
                        {a}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {assets.map(rAsset => (
                    <tr key={rAsset}>
                      <td style={{ padding: '8px', fontWeight: 700, color: '#86948a', fontSize: '0.75rem', textAlign: 'right' }}>
                        {rAsset}
                      </td>
                      {assets.map(cAsset => {
                        const val = liveMatrix[rAsset]?.[cAsset] ?? (rAsset === cAsset ? 1.0 : 0.0);
                        return (
                          <td key={cAsset} style={{ padding: '3px' }}>
                            <div
                              onClick={() => setSelectedCell({ pair: `${rAsset} vs ${cAsset}`, val, status: val < 0 ? 'INVERSE CORRELATION' : 'POSITIVE CORRELATION' })}
                              className="font-mono"
                              style={{
                                height: '42px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                borderRadius: '4px',
                                background: getCellBg(val),
                                color: getCellColor(val),
                                fontWeight: 700,
                                fontSize: '0.85rem',
                                cursor: 'pointer',
                                border: '1px solid #3c4a42',
                                transition: 'all 0.15s ease'
                              }}
                              onMouseOver={(e) => e.currentTarget.style.borderColor = '#4edea3'}
                              onMouseOut={(e) => e.currentTarget.style.borderColor = '#3c4a42'}
                            >
                              {val > 0 ? `+${val.toFixed(2)}` : val.toFixed(2)}
                            </div>
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Color Scale Legend */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '16px', borderTop: '1px solid #3c4a42', paddingTop: '10px', fontSize: '0.72rem', color: '#86948a' }}>
            <span>-1.0 (Strong Inverse)</span>
            <div style={{ width: '120px', height: '6px', borderRadius: '3px', background: 'linear-gradient(90deg, #ffb4ab, #242c27, #4edea3)' }} />
            <span>+1.0 (Strong Positive)</span>
          </div>

        </div>

        {/* Selected Pair Detail Card */}
        <div style={{ background: '#1a211d', border: '1px solid #3c4a42', borderRadius: '6px', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#86948a', letterSpacing: '0.05em' }}>
            SELECTED COVARIANCE PAIR
          </span>

          {selectedCell ? (
            <div style={{ padding: '16px', background: '#161d19', borderRadius: '4px', border: '1px solid #3c4a42', textAlign: 'center' }}>
              <span style={{ fontSize: '0.8rem', color: '#86948a' }}>LIVE MT5 CORRELATION</span>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#ffffff', marginTop: '4px' }}>
                {selectedCell.pair}
              </h3>
              <h2 className="font-mono" style={{ fontSize: '2.2rem', fontWeight: 800, color: selectedCell.val < 0 ? '#ffb4ab' : '#4edea3', marginTop: '8px' }}>
                {selectedCell.val > 0 ? `+${selectedCell.val.toFixed(2)}` : selectedCell.val.toFixed(2)}
              </h2>
              <span style={{ fontSize: '0.72rem', padding: '2px 8px', borderRadius: '4px', background: 'rgba(78,222,163,0.1)', color: selectedCell.val < 0 ? '#ffb4ab' : '#4edea3' }}>
                {selectedCell.status}
              </span>
            </div>
          ) : (
            <div style={{ padding: '16px', color: '#86948a', textAlign: 'center', fontSize: '0.8rem' }}>
              Select a cell in the heatmap to view covariance details
            </div>
          )}
        </div>

      </div>

      {/* Official TradingView Forex Cross-Rates Embed Widget - Dark & Fitted */}
      <div style={{ background: '#131722', border: '1px solid #242c27', borderRadius: '6px', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px', height: '440px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Globe size={18} color="#4edea3" />
          <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#ffffff', letterSpacing: '0.05em' }}>
            TRADINGVIEW OFFICIAL GLOBAL FOREX CROSS-RATES MATRIX
          </span>
        </div>

        <div style={{ flex: 1, position: 'relative', background: '#131722', borderRadius: '4px', overflow: 'hidden' }}>
          {widgetError ? (
            <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#ffb4ab', gap: '8px', padding: '20px', textAlign: 'center' }}>
              <AlertTriangle size={24} color="#ffb4ab" />
              <span style={{ fontSize: '0.85rem', fontWeight: 700 }}>TradingView Forex Cross-Rates widget failed to load</span>
            </div>
          ) : (
            <div ref={tvHeatmapRef} className="tradingview-widget-container" style={{ width: '100%', height: '100%', background: '#131722' }} />
          )}
        </div>
      </div>

    </div>
  );
}
