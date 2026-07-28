import React, { useEffect, useRef, useState } from 'react';
import { Newspaper, Calendar, MapPin, Zap, AlertTriangle } from 'lucide-react';

export default function MarketIntelligenceView() {
  const tvEconomicMapRef = useRef(null);
  const tvTopStoriesRef = useRef(null);
  const tvCalendarRef = useRef(null);

  const [mapError, setMapError] = useState(false);
  const [storiesError, setStoriesError] = useState(false);
  const [calendarError, setCalendarError] = useState(false);

  // 1. TradingView Official Economic Map Widget
  useEffect(() => {
    if (!tvEconomicMapRef.current) return;
    tvEconomicMapRef.current.innerHTML = '';
    setMapError(false);

    try {
      const widgetDiv = document.createElement('div');
      widgetDiv.className = 'tradingview-widget-container__widget';
      widgetDiv.style.height = '100%';
      widgetDiv.style.width = '100%';

      const script = document.createElement('script');
      script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-forex-heat-map.js';
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

      script.onerror = () => setMapError(true);

      tvEconomicMapRef.current.appendChild(widgetDiv);
      tvEconomicMapRef.current.appendChild(script);
    } catch (e) {
      setMapError(true);
    }
  }, []);

  // 2. TradingView Official Top Stories Widget (20s Daily News Briefs)
  useEffect(() => {
    if (!tvTopStoriesRef.current) return;
    tvTopStoriesRef.current.innerHTML = '';
    setStoriesError(false);

    try {
      const widgetDiv = document.createElement('div');
      widgetDiv.className = 'tradingview-widget-container__widget';
      widgetDiv.style.height = '100%';
      widgetDiv.style.width = '100%';

      const script = document.createElement('script');
      script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-timeline.js';
      script.type = 'text/javascript';
      script.async = true;
      script.text = JSON.stringify({
        width: '100%',
        height: '100%',
        colorTheme: 'dark',
        isTransparent: false,
        locale: 'en',
        feedMode: 'market',
        market: 'stock'
      });

      script.onerror = () => setStoriesError(true);

      tvTopStoriesRef.current.appendChild(widgetDiv);
      tvTopStoriesRef.current.appendChild(script);
    } catch (e) {
      setStoriesError(true);
    }
  }, []);

  // 3. TradingView Official High-Impact Economic Calendar Widget
  useEffect(() => {
    if (!tvCalendarRef.current) return;
    tvCalendarRef.current.innerHTML = '';
    setCalendarError(false);

    try {
      const widgetDiv = document.createElement('div');
      widgetDiv.className = 'tradingview-widget-container__widget';
      widgetDiv.style.height = '100%';
      widgetDiv.style.width = '100%';

      const script = document.createElement('script');
      script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-events.js';
      script.type = 'text/javascript';
      script.async = true;
      script.text = JSON.stringify({
        width: '100%',
        height: '100%',
        colorTheme: 'dark',
        isTransparent: false,
        locale: 'en',
        importanceFilter: '-1,0,1',
        countryFilter: 'us,eu,gb,jp,cn'
      });

      script.onerror = () => setCalendarError(true);

      tvCalendarRef.current.appendChild(widgetDiv);
      tvCalendarRef.current.appendChild(script);
    } catch (e) {
      setCalendarError(true);
    }
  }, []);

  return (
    <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px', background: '#0e1511', minHeight: '100vh', color: '#dde4dd' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#ffffff' }}>
            Market Intelligence &amp; TradingView Live Fundamental Radar
          </h2>
          <p style={{ fontSize: '0.8rem', color: '#86948a', marginTop: '4px' }}>
            Official TradingView Live Widgets Only (0% Mock / Dummy Data)
          </p>
        </div>
      </div>

      {/* Grid Row 1: Economic Map + Top Stories */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        
        {/* TradingView Economic Map Widget */}
        <div style={{ background: '#131722', border: '1px solid #242c27', borderRadius: '6px', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px', height: '440px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <MapPin size={18} color="#4edea3" />
            <div>
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#ffffff', letterSpacing: '0.05em' }}>
                TRADINGVIEW OFFICIAL ECONOMIC MAP
              </span>
              <p style={{ fontSize: '0.72rem', color: '#86948a' }}>Geographical macroeconomics &amp; regional currency heat-map</p>
            </div>
          </div>

          <div style={{ flex: 1, position: 'relative', background: '#131722', borderRadius: '4px', overflow: 'hidden' }}>
            {mapError ? (
              <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#ffb4ab', gap: '8px', padding: '20px', textAlign: 'center' }}>
                <AlertTriangle size={24} color="#ffb4ab" />
                <span style={{ fontSize: '0.85rem', fontWeight: 700 }}>TradingView Economic Map widget failed to load</span>
              </div>
            ) : (
              <div ref={tvEconomicMapRef} className="tradingview-widget-container" style={{ width: '100%', height: '100%', background: '#131722' }} />
            )}
          </div>
        </div>

        {/* TradingView Top Stories Widget (20s Daily News Briefs) */}
        <div style={{ background: '#131722', border: '1px solid #242c27', borderRadius: '6px', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px', height: '440px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Zap size={18} color="#ffca45" />
            <div>
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#ffffff', letterSpacing: '0.05em' }}>
                TRADINGVIEW TOP STORIES (DAILY NEWS BRIEFS)
              </span>
              <p style={{ fontSize: '0.72rem', color: '#86948a' }}>20-second daily briefs for stocks, crypto &amp; macro markets</p>
            </div>
          </div>

          <div style={{ flex: 1, position: 'relative', background: '#131722', borderRadius: '4px', overflow: 'hidden' }}>
            {storiesError ? (
              <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#ffb4ab', gap: '8px', padding: '20px', textAlign: 'center' }}>
                <AlertTriangle size={24} color="#ffb4ab" />
                <span style={{ fontSize: '0.85rem', fontWeight: 700 }}>TradingView Top Stories widget failed to load</span>
              </div>
            ) : (
              <div ref={tvTopStoriesRef} className="tradingview-widget-container" style={{ width: '100%', height: '100%', background: '#131722' }} />
            )}
          </div>
        </div>

      </div>

      {/* Grid Row 2: Live Economic Calendar */}
      <div style={{ background: '#131722', border: '1px solid #242c27', borderRadius: '6px', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px', height: '440px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Calendar size={18} color="#38bdf8" />
          <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#ffffff', letterSpacing: '0.05em' }}>
            TRADINGVIEW OFFICIAL LIVE HIGH-IMPACT ECONOMIC CALENDAR
          </span>
        </div>

        <div style={{ flex: 1, position: 'relative', background: '#131722', borderRadius: '4px', overflow: 'hidden' }}>
          {calendarError ? (
            <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#ffb4ab', gap: '8px', padding: '20px', textAlign: 'center' }}>
              <AlertTriangle size={24} color="#ffb4ab" />
              <span style={{ fontSize: '0.85rem', fontWeight: 700 }}>TradingView Economic Calendar widget failed to load</span>
            </div>
          ) : (
            <div ref={tvCalendarRef} className="tradingview-widget-container" style={{ width: '100%', height: '100%', background: '#131722' }} />
          )}
        </div>
      </div>

    </div>
  );
}
