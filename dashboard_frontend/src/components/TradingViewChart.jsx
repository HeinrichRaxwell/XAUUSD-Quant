import React, { useEffect, useRef, useState } from 'react';
import { BarChart2, Layers } from 'lucide-react';

export default function TradingViewChart() {
  const containerRef = useRef(null);
  const [interval, setIntervalVal] = useState('60');

  useEffect(() => {
    if (!containerRef.current) return;
    containerRef.current.innerHTML = '';

    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/tv.js';
    script.async = true;
    script.onload = () => {
      if (window.TradingView && containerRef.current) {
        new window.TradingView.widget({
          autosize: true,
          symbol: 'OANDA:XAUUSD',
          interval: interval,
          timezone: 'Asia/Jakarta',
          theme: 'dark',
          style: '1',
          locale: 'en',
          toolbar_bg: '#0f172a',
          enable_publishing: false,
          allow_symbol_change: true,
          save_image: true,
          hide_side_toolbar: false,
          studies: [
            'RSI@tv-basicstudies',
            'MASimple@tv-basicstudies'
          ],
          container_id: containerRef.current.id
        });
      }
    };

    document.head.appendChild(script);

    return () => {
      if (script.parentNode) script.parentNode.removeChild(script);
    };
  }, [interval]);

  return (
    <div className="glass-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', height: '680px' }}>
      
      {/* Chart Toolbar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <BarChart2 size={20} color="#f59e0b" />
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700 }}>
            TradingView Live Chart &bull; <span style={{ color: 'var(--color-gold-bright)' }}>XAU/USD Gold</span>
          </h3>
          <span style={{ fontSize: '0.75rem', background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24', padding: '2px 8px', borderRadius: '4px', border: '1px solid rgba(245,158,11,0.3)' }}>
            OANDA Feed &bull; Asia/Jakarta
          </span>
        </div>

        {/* Timeframe selector buttons */}
        <div style={{ display: 'flex', gap: '6px', background: 'rgba(30, 41, 59, 0.6)', padding: '4px', borderRadius: '8px', border: '1px solid var(--border-card)' }}>
          {[
            { label: 'M15', val: '15' },
            { label: 'H1 (Quant)', val: '60' },
            { label: 'H4', val: '240' },
            { label: 'Daily', val: 'D' }
          ].map((item) => (
            <button
              key={item.val}
              onClick={() => setIntervalVal(item.val)}
              style={{
                background: interval === item.val ? 'var(--color-gold)' : 'transparent',
                color: interval === item.val ? '#070a12' : 'var(--text-muted)',
                fontWeight: interval === item.val ? 700 : 500,
                border: 'none',
                padding: '4px 10px',
                borderRadius: '6px',
                fontSize: '0.78rem',
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {/* Embedded Chart Iframe Container */}
      <div
        id="tradingview_xauusd_chart"
        ref={containerRef}
        style={{ width: '100%', flex: 1, borderRadius: '8px', overflow: 'hidden', border: '1px solid var(--border-card)' }}
      >
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: 'var(--text-muted)' }}>
          Loading TradingView Advanced Real-Time Chart...
        </div>
      </div>

    </div>
  );
}
