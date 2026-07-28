import React, { useState } from 'react';
import { List, XCircle, CheckCircle2 } from 'lucide-react';

export default function ActivePositionsTable({ positions, onClosePosition, onCloseAll }) {
  const [closingTicket, setClosingTicket] = useState(null);
  const [isClosingAll, setIsClosingAll] = useState(false);

  const handleClose = async (ticket) => {
    setClosingTicket(ticket);
    await onClosePosition(ticket);
    setClosingTicket(null);
  };

  const handleCloseAll = async () => {
    if (!window.confirm("Are you sure you want to close ALL active MT5 positions?")) return;
    setIsClosingAll(true);
    await onCloseAll();
    setIsClosingAll(false);
  };

  return (
    <div className="quant-card" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <List size={16} color="#4edea3" />
          <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--on-surface)', letterSpacing: '0.05em' }}>
            ACTIVE ORDERS ({positions ? positions.length : 0})
          </h4>
        </div>

        {positions && positions.length > 0 && (
          <button
            onClick={handleCloseAll}
            disabled={isClosingAll}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              background: 'rgba(255, 180, 171, 0.12)',
              color: '#ffb4ab',
              border: '1px solid rgba(255, 180, 171, 0.3)',
              padding: '4px 10px',
              borderRadius: '4px',
              fontSize: '0.75rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            <XCircle size={14} />
            <span>{isClosingAll ? 'Closing All...' : 'Close All Positions'}</span>
          </button>
        )}
      </div>

      {/* Table */}
      {!positions || positions.length === 0 ? (
        <div style={{ padding: '24px', textAlign: 'center', background: 'var(--surface-container-low)', borderRadius: '4px', border: '1px border-dashed var(--outline-variant)' }}>
          <CheckCircle2 size={24} color="#4edea3" style={{ margin: '0 auto 6px auto', opacity: 0.8 }} />
          <p style={{ fontSize: '0.82rem', color: '#ffffff', fontWeight: 600 }}>No Active Orders</p>
          <p style={{ fontSize: '0.75rem', color: 'var(--on-surface-variant)', marginTop: '4px' }}>
            The bot is in Standby mode waiting for ML Confidence &ge; 65% + Monte Carlo alignment.
          </p>
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--outline-variant)', color: 'var(--on-surface-variant)', fontSize: '0.72rem', textTransform: 'uppercase' }}>
                <th style={{ padding: '8px 12px' }}>SIDE</th>
                <th style={{ padding: '8px 12px' }}>TICKET</th>
                <th style={{ padding: '8px 12px' }}>SYMBOL</th>
                <th style={{ padding: '8px 12px' }}>SIZE</th>
                <th style={{ padding: '8px 12px' }}>OPEN PRICE</th>
                <th style={{ padding: '8px 12px' }}>CURRENT</th>
                <th style={{ padding: '8px 12px' }}>PNL</th>
                <th style={{ padding: '8px 12px', textAlign: 'right' }}>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {positions.map((pos) => {
                const isBuy = pos.type === 'BUY';
                const isProf = pos.profit >= 0;
                return (
                  <tr key={pos.ticket} style={{ borderBottom: '1px solid rgba(60, 74, 66, 0.4)' }}>
                    <td style={{ padding: '8px 12px' }}>
                      <span
                        style={{
                          padding: '2px 8px',
                          borderRadius: '4px',
                          fontWeight: 700,
                          fontSize: '0.72rem',
                          background: isBuy ? 'rgba(78, 222, 163, 0.15)' : 'rgba(255, 180, 171, 0.15)',
                          color: isBuy ? '#4edea3' : '#ffb4ab',
                          border: `1px solid ${isBuy ? 'rgba(78, 222, 163, 0.3)' : 'rgba(255, 180, 171, 0.3)'}`,
                        }}
                      >
                        {pos.type}
                      </span>
                    </td>
                    <td className="font-mono" style={{ padding: '8px 12px', color: 'var(--on-surface-variant)' }}>
                      #{pos.ticket}
                    </td>
                    <td className="font-mono" style={{ padding: '8px 12px', color: '#ffffff', fontWeight: 700 }}>
                      {pos.symbol}
                    </td>
                    <td className="font-mono" style={{ padding: '8px 12px', color: 'var(--on-surface)' }}>
                      {pos.volume}
                    </td>
                    <td className="font-mono" style={{ padding: '8px 12px', color: 'var(--on-surface)' }}>
                      ${pos.open_price.toFixed(2)}
                    </td>
                    <td className="font-mono" style={{ padding: '8px 12px', color: 'var(--on-surface)' }}>
                      ${pos.current_price.toFixed(2)}
                    </td>
                    <td className="font-mono" style={{ padding: '8px 12px', fontWeight: 700, color: isProf ? '#4edea3' : '#ffb4ab' }}>
                      {isProf ? `+$${pos.profit.toFixed(2)}` : `$${pos.profit.toFixed(2)}`}
                    </td>
                    <td style={{ padding: '8px 12px', textAlign: 'right' }}>
                      <button
                        onClick={() => handleClose(pos.ticket)}
                        disabled={closingTicket === pos.ticket}
                        style={{
                          background: 'rgba(255, 180, 171, 0.15)',
                          border: '1px solid rgba(255, 180, 171, 0.3)',
                          color: '#ffb4ab',
                          padding: '3px 8px',
                          borderRadius: '4px',
                          fontSize: '0.72rem',
                          fontWeight: 600,
                          cursor: 'pointer',
                        }}
                      >
                        {closingTicket === pos.ticket ? 'Closing...' : 'Close'}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

    </div>
  );
}
