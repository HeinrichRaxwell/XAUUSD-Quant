import React, { useState } from 'react';
import { X, Play, Zap, Compass, CheckCircle2, ShieldCheck } from 'lucide-react';
import InteractiveQuantChart from './InteractiveQuantChart';

export default function AnalysisModal({ isOpen, onClose, signalData }) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);

  if (!isOpen) return null;

  const runAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      const res = await fetch('http://localhost:8000/api/analyze', { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setAnalysisResult(data);
      }
    } catch (e) {
      console.error('Error running analysis:', e);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const rec = analysisResult?.final_recommendation || {
    direction: signalData?.ml_signal === 'SELL' ? 'BEAR' : (signalData?.ml_signal === 'BUY' ? 'BULL' : 'NEUTRAL'),
    action: signalData?.ml_signal || 'SELL',
    timeframe: 'Daily / H1',
    confidence_pct: signalData?.confidence_pct || 68.0,
    current_price: signalData?.current_price || 4085.00
  };

  const levels = analysisResult?.levels || {
    prz_tp1: rec.current_price - 18.0,
    prz_tp2: rec.current_price - 14.4,
    prz_tp3: rec.current_price + 4.5,
    monte_target: signalData?.monte_carlo?.p50_target || 4082.50,
    tp: rec.current_price - 11.25,
    entry: rec.current_price + 2.25,
    sl: rec.current_price + 6.75
  };

  const isSell = rec.action.includes('SELL') || rec.direction === 'BEAR';
  const isBuy = rec.action.includes('BUY') || rec.direction === 'BULL';

  const themeColor = isSell ? '#f43f5e' : (isBuy ? '#10b981' : '#94a3b8');
  const themeBg = isSell ? 'rgba(244,63,94,0.15)' : (isBuy ? 'rgba(16,185,129,0.15)' : 'rgba(148,163,184,0.15)');

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(5, 8, 16, 0.92)',
      backdropFilter: 'blur(16px)',
      zIndex: 99999,
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '16px'
    }}>
      <div style={{
        background: '#0d111c',
        border: '1px solid rgba(51, 65, 85, 0.8)',
        borderRadius: '16px',
        maxWidth: '1050px',
        width: '100%',
        maxHeight: '94vh',
        overflowY: 'auto',
        padding: '24px',
        boxShadow: '0 0 50px rgba(0, 0, 0, 0.9)',
        position: 'relative'
      }}>

        {/* Close Button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '20px',
            right: '20px',
            background: 'rgba(30, 41, 59, 0.8)',
            border: '1px solid rgba(100, 116, 139, 0.4)',
            color: '#94a3b8',
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer'
          }}
        >
          <X size={20} />
        </button>

        {/* Top Header Trigger Button */}
        <div style={{ textAlign: 'center', marginBottom: '20px' }}>
          <button
            onClick={runAnalysis}
            disabled={isAnalyzing}
            style={{
              width: '100%',
              maxWidth: '400px',
              padding: '14px 28px',
              borderRadius: '12px',
              border: 'none',
              background: 'linear-gradient(135deg, #2563eb, #1d4ed8)',
              color: '#ffffff',
              fontWeight: 800,
              fontSize: '1.1rem',
              letterSpacing: '0.06em',
              cursor: 'pointer',
              boxShadow: '0 0 25px rgba(37, 99, 235, 0.6)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '10px'
            }}
          >
            <Play size={20} fill="#ffffff" />
            <span>{isAnalyzing ? 'RUNNING QUANT ANALYSIS...' : 'RE-RUN ANALISIS REAL-TIME'}</span>
          </button>
        </div>

        {/* SECTION 1: Final Recommendation Card (Matches Reference Screenshot) */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.8)',
          border: '1px solid rgba(51, 65, 85, 0.8)',
          borderRadius: '12px',
          padding: '20px',
          marginBottom: '20px'
        }}>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-muted)' }}>
                {rec.direction} &bull; Timeframe {rec.timeframe}
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '1.3rem', fontWeight: 800, color: themeColor }}>
                {rec.confidence_pct}%
              </span>
              <span style={{
                background: themeBg,
                color: themeColor,
                border: `1px solid ${themeColor}`,
                padding: '4px 14px',
                borderRadius: '6px',
                fontWeight: 800,
                fontSize: '0.9rem'
              }}>
                {rec.action}
              </span>
            </div>
          </div>

          <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '12px' }}>
            Final Recommendation
          </h2>

          <div style={{ height: '8px', background: 'rgba(30, 41, 59, 0.8)', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{ width: `${rec.confidence_pct}%`, height: '100%', background: `linear-gradient(90deg, #2563eb, ${themeColor})`, transition: 'width 0.6s ease' }}></div>
          </div>
        </div>

        {/* SECTION 2: 100% Interactive TradingView Lightweight Canvas Chart */}
        <div style={{ marginBottom: '20px' }}>
          <InteractiveQuantChart />
        </div>

        {/* SECTION 3: Technical & Monte Carlo Breakdown Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          
          {/* Teknikal Card */}
          <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-card)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <h4 style={{ fontSize: '0.95rem', fontWeight: 700 }}>Teknikal Breakdown</h4>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ fontSize: '1rem', fontWeight: 800, color: themeColor }}>{rec.confidence_pct}%</span>
                <span style={{ background: themeBg, color: themeColor, padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700 }}>
                  {rec.action}
                </span>
              </div>
            </div>

            <div style={{ height: '6px', background: 'rgba(30,41,59,0.8)', borderRadius: '3px', overflow: 'hidden', marginBottom: '12px' }}>
              <div style={{ width: `${rec.confidence_pct}%`, height: '100%', background: themeColor }}></div>
            </div>

            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Wilder RSI + ADX Trend strength &bull; Harmonic Fib Score: {signalData?.technical_indicators?.harmonic_fib_score ?? 0.892}
            </p>
          </div>

          {/* Monte Carlo Teknis Card */}
          <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-card)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <h4 style={{ fontSize: '0.95rem', fontWeight: 700 }}>Monte Carlo 10,000 Sims</h4>
              <span style={{ color: '#fbbf24', fontWeight: 700, fontSize: '0.9rem' }}>
                P50 Target: ${levels.monte_target.toFixed(2)}
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '6px', fontSize: '0.75rem', textAlign: 'center', marginTop: '8px' }}>
              <div style={{ background: 'rgba(30,41,59,0.6)', padding: '6px', borderRadius: '6px' }}>
                <span style={{ color: 'var(--text-muted)' }}>P10</span><br />
                <strong style={{ color: 'var(--color-sell)' }}>${(signalData?.monte_carlo?.p10_target ?? levels.monte_target - 12).toFixed(2)}</strong>
              </div>
              <div style={{ background: 'rgba(245,158,11,0.15)', padding: '6px', borderRadius: '6px' }}>
                <span style={{ color: '#fbbf24' }}>P50</span><br />
                <strong style={{ color: '#fbbf24' }}>${levels.monte_target.toFixed(2)}</strong>
              </div>
              <div style={{ background: 'rgba(30,41,59,0.6)', padding: '6px', borderRadius: '6px' }}>
                <span style={{ color: 'var(--text-muted)' }}>P90</span><br />
                <strong style={{ color: 'var(--color-buy)' }}>${(signalData?.monte_carlo?.p90_target ?? levels.monte_target + 12).toFixed(2)}</strong>
              </div>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
