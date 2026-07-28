import React from 'react';
import { Bell, ShieldAlert, Send, Plus } from 'lucide-react';

export default function AlertManagementView() {
  const activeAlerts = [
    { id: 1, name: 'XAUUSD Breakout &gt; $4120.00', type: 'Price Cross', channel: 'Telegram Bot', status: 'ACTIVE' },
    { id: 2, name: 'LightGBM Signal = STRONG BUY (&ge;75%)', type: 'ML Confidence', channel: 'Telegram Bot &amp; MT5 Auto-Trade', status: 'ACTIVE' },
    { id: 3, name: 'Monte Carlo P50 Bearish Drift Shift', type: 'Stochastic Drift', channel: 'Dashboard Toast', status: 'ACTIVE' },
    { id: 4, name: 'Equity Drawdown &gt; 3.0%', type: 'Risk Ruin Guard', channel: 'Emergency Auto-Close', status: 'ARMED' },
  ];

  return (
    <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#ffffff' }}>
            Quant Alert &amp; Telegram Webhook Control Center
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--on-surface-variant)', marginTop: '4px' }}>
            Automated Risk Guards, Signal Notifications &amp; Webhook Triggers
          </p>
        </div>

        <button style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 14px', background: '#4edea3', color: '#002113', borderRadius: '4px', fontSize: '0.82rem', fontWeight: 700, border: 'none', cursor: 'pointer' }}>
          <Plus size={16} /> Create New Trigger
        </button>
      </div>

      <div className="quant-card" style={{ padding: '16px' }}>
        <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#ffffff', letterSpacing: '0.05em', display: 'block', marginBottom: '12px' }}>
          ACTIVE QUANT TRIGGERS ({activeAlerts.length})
        </span>

        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--outline-variant)', color: 'var(--on-surface-variant)', fontSize: '0.72rem', textTransform: 'uppercase', textAlign: 'left' }}>
              <th style={{ padding: '8px 12px' }}>RULE NAME</th>
              <th style={{ padding: '8px 12px' }}>TRIGGER TYPE</th>
              <th style={{ padding: '8px 12px' }}>DISPATCH CHANNEL</th>
              <th style={{ padding: '8px 12px' }}>STATUS</th>
            </tr>
          </thead>
          <tbody>
            {activeAlerts.map(rule => (
              <tr key={rule.id} style={{ borderBottom: '1px solid rgba(60, 74, 66, 0.4)' }}>
                <td style={{ padding: '10px 12px', fontWeight: 700, color: '#ffffff' }}>{rule.name}</td>
                <td style={{ padding: '10px 12px', color: '#ffca45' }}>{rule.type}</td>
                <td style={{ padding: '10px 12px', color: '#38bdf8' }}>{rule.channel}</td>
                <td style={{ padding: '10px 12px' }}>
                  <span style={{ padding: '2px 8px', borderRadius: '4px', background: 'rgba(78, 222, 163, 0.15)', color: '#4edea3', fontWeight: 700, fontSize: '0.72rem' }}>
                    {rule.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  );
}
