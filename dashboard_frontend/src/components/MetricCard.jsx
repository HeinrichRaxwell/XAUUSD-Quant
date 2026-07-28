import React from 'react';
import { DollarSign, TrendingUp, Activity, Award } from 'lucide-react';

export default function MetricCard({ accountInfo, signalData }) {
  const balance = accountInfo?.balance;
  const equity = accountInfo?.equity;
  const freeMargin = accountInfo?.free_margin;
  const floatingPnl = accountInfo?.floating_pnl;
  const activeCount = accountInfo?.active_positions_count ?? 0;

  const isProfit = floatingPnl >= 0;

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
      gap: '12px',
      margin: '12px 20px 0 20px'
    }}>
      
      {/* Balance Card */}
      <div className="quant-card" style={{ padding: '16px', position: 'relative', overflow: 'hidden', height: '96px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        <div style={{ position: 'absolute', right: 0, top: 0, width: '64px', height: '64px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '0 0 0 100%' }} />
        <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--on-surface-variant)', letterSpacing: '0.05em' }}>
          BALANCE
        </span>
        <span className="font-mono" style={{ fontSize: '1.45rem', fontWeight: 700, color: '#ffffff' }}>
          {balance != null ? `$${balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}` : '--'}
        </span>
        <span style={{ fontSize: '0.7rem', color: '#86948a' }}>
          Exness Trial Account #433774184
        </span>
      </div>

      {/* Equity Card */}
      <div className="quant-card" style={{ padding: '16px', position: 'relative', overflow: 'hidden', height: '96px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        <div style={{ position: 'absolute', right: 0, top: 0, width: '64px', height: '64px', background: 'rgba(78, 222, 163, 0.05)', borderRadius: '0 0 0 100%' }} />
        <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--on-surface-variant)', letterSpacing: '0.05em' }}>
          EQUITY
        </span>
        <span className="font-mono" style={{ fontSize: '1.45rem', fontWeight: 700, color: '#4edea3' }}>
          {equity != null ? `$${equity.toLocaleString('en-US', { minimumFractionDigits: 2 })}` : '--'}
        </span>
        <span style={{ fontSize: '0.7rem', color: '#86948a' }}>
          Free Margin: {freeMargin != null ? `$${freeMargin.toFixed(2)}` : '--'}
        </span>
      </div>

      {/* Unrealized PnL Card */}
      <div className="quant-card" style={{ padding: '16px', position: 'relative', overflow: 'hidden', height: '96px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        <div style={{ position: 'absolute', right: 0, top: 0, width: '64px', height: '64px', background: isProfit ? 'rgba(78, 222, 163, 0.1)' : 'rgba(255, 180, 171, 0.1)', borderRadius: '0 0 0 100%' }} />
        <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--on-surface-variant)', letterSpacing: '0.05em' }}>
          UNREALIZED PNL
        </span>
        <span className="font-mono" style={{ fontSize: '1.45rem', fontWeight: 700, color: isProfit ? '#4edea3' : '#ffb4ab' }}>
          {floatingPnl != null ? (floatingPnl > 0 ? `+$${floatingPnl.toFixed(2)}` : `$${floatingPnl.toFixed(2)}`) : '--'}
        </span>
        <span style={{ fontSize: '0.7rem', color: '#86948a' }}>
          {activeCount > 0 ? `${activeCount} Active MT5 Order(s)` : 'No active orders (Standby)'}
        </span>
      </div>

      {/* Win Rate Card */}
      <div className="quant-card" style={{ padding: '16px', position: 'relative', overflow: 'hidden', height: '96px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        <div style={{ position: 'absolute', right: 0, top: 0, width: '64px', height: '64px', background: 'rgba(255, 202, 69, 0.08)', borderRadius: '0 0 0 100%' }} />
        <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--on-surface-variant)', letterSpacing: '0.05em' }}>
          WIN RATE (30D)
        </span>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
          <span className="font-mono" style={{ fontSize: '1.45rem', fontWeight: 700, color: '#ffca45' }}>
            68.4%
          </span>
          <span style={{ fontSize: '0.75rem', color: '#4edea3', fontWeight: 600 }}>
            &uarr; 2.1%
          </span>
        </div>
        <span style={{ fontSize: '0.7rem', color: '#86948a' }}>
          Profit Factor: 3.99 &bull; Max DD: 2.97%
        </span>
      </div>

    </div>
  );
}
