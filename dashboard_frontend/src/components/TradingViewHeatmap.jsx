import React, { useEffect, useRef, useState } from 'react';
import { Globe, AlertTriangle } from 'lucide-react';

export default function TradingViewHeatmap() {
  const containerRef = useRef(null);
  const [hasError, setHasError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!containerRef.current) return;
    containerRef.current.innerHTML = '';
    setHasError(false);
    setIsLoading(true);

    try {
      const widgetContainer = document.createElement('div');
      widgetContainer.className = 'tradingview-widget-container__widget';
      widgetContainer.style.height = '100%';
      widgetContainer.style.width = '100%';
      widgetContainer.style.backgroundColor = '#131722';

      const script = document.createElement('script');
      script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-forex-cross-rates.js';
      script.type = 'text/javascript';
      script.async = true;

      // Assign configuration string directly to script.text (Official TradingView React Pattern)
      script.text = JSON.stringify({
        width: '100%',
        height: '100%',
        currencies: ['EUR', 'USD', 'JPY', 'GBP', 'CHF', 'AUD', 'CAD', 'NZD'],
        isTransparent: false,
        colorTheme: 'dark',
        locale: 'en'
      });

      script.onload = () => setIsLoading(false);
      script.onerror = () => {
        setIsLoading(false);
        setHasError(true);
      };

      containerRef.current.appendChild(widgetContainer);
      containerRef.current.appendChild(script);

      const timer = setTimeout(() => setIsLoading(false), 2000);
      return () => clearTimeout(timer);
    } catch (err) {
      console.error('TradingView Forex Cross-Rates widget mount error:', err);
      setHasError(true);
      setIsLoading(false);
    }
  }, []);

  return (
    <div style={{
      padding: '16px',
      display: 'flex',
      flexDirection: 'column',
      height: '440px',
      background: '#131722',
      border: '1px solid #242c27',
      borderRadius: '6px',
      overflow: 'hidden'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
        <Globe size={18} color="#4edea3" />
        <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#ffffff', letterSpacing: '0.05em' }}>
          TRADINGVIEW OFFICIAL GLOBAL FOREX CROSS-RATES MATRIX
        </h4>
      </div>
      
      <div style={{ flex: 1, position: 'relative', background: '#131722', borderRadius: '4px', overflow: 'hidden' }}>
        {isLoading && (
          <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#131722', color: '#4edea3', fontSize: '0.8rem', zIndex: 10 }}>
            ⚡ Loading Official TradingView Forex Cross-Rates Matrix...
          </div>
        )}

        {hasError ? (
          <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: '#131722', color: '#ffb4ab', gap: '8px', padding: '20px', textAlign: 'center' }}>
            <AlertTriangle size={24} color="#ffb4ab" />
            <span style={{ fontSize: '0.85rem', fontWeight: 700 }}>TradingView widget failed to load</span>
            <span style={{ fontSize: '0.72rem', color: '#86948a' }}>Check network connection or TradingView script availability</span>
          </div>
        ) : (
          <div className="tradingview-widget-container" ref={containerRef} style={{ width: '100%', height: '100%', background: '#131722' }} />
        )}
      </div>
    </div>
  );
}
