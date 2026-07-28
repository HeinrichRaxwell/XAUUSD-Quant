import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def _detect_swing_pivots(highs: np.ndarray, lows: np.ndarray, window: int = 3):
    """
    Detect fractal swing highs and lows using a vectorized window comparison.
    A swing high at index i means highs[i] >= all highs in [i-window, i+window].
    A swing low  at index i means lows[i]  <= all lows  in [i-window, i+window].
    Returns (swing_high_indices, swing_low_indices).
    """
    n = len(highs)
    sh_idx, sl_idx = [], []
    for i in range(window, n - window):
        is_sh = all(highs[i] >= highs[i - j] for j in range(1, window + 1)) and \
                all(highs[i] >= highs[i + j] for j in range(1, window + 1))
        is_sl = all(lows[i]  <= lows[i  - j] for j in range(1, window + 1)) and \
                all(lows[i]  <= lows[i  + j] for j in range(1, window + 1))
        if is_sh:
            sh_idx.append(i)
        if is_sl:
            sl_idx.append(i)
    return sh_idx, sl_idx


def _pick_xabcd_pivots(sh_idx, sl_idx, highs, lows, n_bars):
    """
    From detected swing highs and lows, pick 5 alternating pivots (X, A, B, C, D)
    for XABCD harmonic pattern overlay. Returns (indices, prices) for X,A,B,C,D.
    Falls back to fixed positions if insufficient swing points are detected.
    """
    # Build combined list of (bar_index, type, price), sorted by bar index
    all_pivots = sorted(
        [(i, "H", highs[i]) for i in sh_idx] +
        [(i, "L", lows[i])  for i in sl_idx],
        key=lambda x: x[0]
    )

    # Select 5 alternating pivots from the most recent end
    pivot_seq = []
    last_type = None
    for idx, ptype, val in reversed(all_pivots):
        if ptype != last_type:
            pivot_seq.insert(0, (idx, ptype, val))
            last_type = ptype
        if len(pivot_seq) >= 5:
            break

    if len(pivot_seq) >= 5:
        return pivot_seq[-5:]  # Return the last 5 alternating pivots

    # Fallback: use evenly-spaced indices if not enough swing points
    fallback = [
        (4,          "L", lows[4]),
        (12,         "H", highs[12]),
        (20,         "L", lows[20]),
        (28,         "H", highs[28]),
        (n_bars - 5, "L", lows[n_bars - 5]),
    ]
    return fallback


def _identify_harmonic_pattern(xa, ab, bc, cd, direction_is_bull: bool) -> tuple[str, str]:
    """
    Identify harmonic pattern type from Fibonacci ratios of swing legs.
    Returns (pattern_name, direction_label).
    """
    if xa < 1e-8:
        return "ABCD Structure", "Bullish" if direction_is_bull else "Bearish"

    ab_xa = ab / (xa + 1e-8)
    cd_bc = cd / (bc + 1e-8)

    if 0.50  <= ab_xa <= 0.618 and 1.27  <= cd_bc <= 1.618:
        name = "Gartley"
    elif 0.382 <= ab_xa <= 0.50  and 1.618 <= cd_bc <= 2.618:
        name = "Bat"
    elif 0.382 <= ab_xa <= 0.618 and 2.24  <= cd_bc <= 3.618:
        name = "Deep Crab"
    elif 0.382 <= ab_xa <= 0.618 and 1.618 <= cd_bc <= 2.618:
        name = "Butterfly"
    elif 0.618 <= ab_xa <= 0.786 and 1.272 <= cd_bc <= 1.618:
        name = "Shark"
    else:
        name = "ABCD Structure"

    direction = "Bullish" if direction_is_bull else "Bearish"
    return name, direction


def generate_quant_chart(df: pd.DataFrame, mc_results: dict, output_path: str = "output/telegram_signal_chart.png") -> str:
    """
    Generates an authentic XAUUSD Quant TradingView-Style Candlestick Chart:
    - Real Candlestick OHLC bars (Green = Bullish, Red = Bearish)
    - Direction-aware TP/SL/PRZ/Entry levels (SELL: TP below, SL above; BUY: TP above, SL below)
    - Real XABCD harmonic pattern overlay from fractal swing pivot detection
    - Fibonacci ratio-based pattern identification (Gartley/Bat/Deep Crab/Butterfly/Shark)
    - Direction-aware Supply/Demand Zone shading
    - Monte Carlo P50 future projection curve
    - Right-side price badges for all key levels
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 1. Dark Theme Configuration
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor('#0d0e12')
    ax.set_facecolor('#131722')

    plot_df = df.tail(45).copy().reset_index(drop=True)
    n_bars = len(plot_df)

    opens  = plot_df["Open"].values
    highs  = plot_df["High"].values
    lows   = plot_df["Low"].values
    closes = plot_df["Close"].values

    # 2. Draw Candlesticks (OHLC)
    width  = 0.55
    for i in range(n_bars):
        c_open, c_high, c_low, c_close = opens[i], highs[i], lows[i], closes[i]
        color = '#26a69a' if c_close >= c_open else '#ef5350'
        ax.plot([i, i], [c_low, c_high], color=color, linewidth=1.2)
        rect_bottom = min(c_open, c_close)
        rect_height = max(abs(c_close - c_open), 0.05)
        rect = patches.Rectangle((i - width / 2, rect_bottom), width, rect_height,
                                  facecolor=color, edgecolor=color)
        ax.add_patch(rect)

    # 3. Direction-aware Key Price Levels
    curr_close = closes[-1]
    atr_val    = plot_df["ATR"].iloc[-1] if "ATR" in plot_df.columns else 4.50
    direction  = mc_results.get("Drift_Direction", "BUY")

    if direction == "SELL":
        tp_level    = curr_close - (2.5 * atr_val)   # TP below price for SELL
        sl_level    = curr_close + (1.5 * atr_val)   # SL above price for SELL
        prz_tp1     = curr_close - (4.0 * atr_val)
        prz_tp2     = curr_close - (3.2 * atr_val)
        entry_level = curr_close + (0.5 * atr_val)   # Ideal short entry zone above
        prz_tp3     = curr_close + (1.0 * atr_val)   # Resistance / PRZ for SELL
        zone_label  = "SUPPLY ZONE"
        zone_bottom = max(highs) - (max(highs) - min(lows)) * 0.22
        zone_top    = max(highs)
        zone_color  = '#2d1b1b'
        zone_text_color = '#f87171'
    else:  # BUY
        tp_level    = curr_close + (2.5 * atr_val)
        sl_level    = curr_close - (1.5 * atr_val)
        prz_tp1     = curr_close + (4.0 * atr_val)
        prz_tp2     = curr_close + (3.2 * atr_val)
        entry_level = curr_close - (0.5 * atr_val)
        prz_tp3     = curr_close - (1.0 * atr_val)
        zone_label  = "DEMAND ZONE"
        zone_bottom = min(lows)
        zone_top    = min(lows) + (max(highs) - min(lows)) * 0.20
        zone_color  = '#1e293b'
        zone_text_color = '#94a3b8'

    # Monte Carlo P50 Target
    monte_target = float(mc_results["P50_Price"]) if "P50_Price" in mc_results else (
        curr_close - (1.8 * atr_val) if direction == "SELL" else curr_close + (1.8 * atr_val)
    )

    # 4. Draw Direction-aware Zone Box
    ax.axhspan(zone_bottom, zone_top, color=zone_color, alpha=0.6)
    ax.text(n_bars * 0.45, (zone_bottom + zone_top) / 2,
            f"{zone_label} (${zone_bottom:,.2f} - ${zone_top:,.2f})",
            color=zone_text_color, fontsize=9, fontweight='bold', ha='center', va='center')

    # 5. Real XABCD Harmonic Overlay from Fractal Swing Pivots
    sh_idx, sl_idx = _detect_swing_pivots(highs, lows, window=3)
    pivots = _pick_xabcd_pivots(sh_idx, sl_idx, highs, lows, n_bars)

    (x_idx, _, x_p), (a_idx, _, a_p), (b_idx, _, b_p), (c_idx, _, c_p), (d_idx, _, d_p) = pivots

    ax.plot([x_idx, a_idx, b_idx, c_idx, d_idx], [x_p, a_p, b_p, c_p, d_p],
            color='#f59e0b', linewidth=2.2, linestyle='-', marker='o', markersize=5, label="Harmonic XABCD")

    # Diagonal Fibonacci Projection Lines matching Target Screenshot 141036
    ax.plot([x_idx, c_idx], [x_p, c_p], color='#38bdf8', linestyle=':', linewidth=1.2, alpha=0.85)
    ax.plot([a_idx, d_idx], [a_p, d_p], color='#38bdf8', linestyle=':', linewidth=1.2, alpha=0.85)
    ax.plot([x_idx, d_idx], [x_p, d_p], color='#eab308', linestyle='--', linewidth=1.4, alpha=0.9)

    # Annotate XABCD pivot labels
    for lbl, xi, xp in [("X", x_idx, x_p), ("A", a_idx, a_p), ("B", b_idx, b_p),
                         ("C", c_idx, c_p), ("D", d_idx, d_p)]:
        ax.text(xi, xp, f" {lbl} ", color='#ffffff', fontsize=8.5, fontweight='bold', ha='center',
                bbox=dict(boxstyle="circle,pad=0.2", facecolor="#f59e0b", edgecolor="none", alpha=0.85))

    # Fibonacci ratio identification & annotations
    xa = abs(a_p - x_p)
    ab = abs(b_p - a_p)
    bc = abs(c_p - b_p)
    cd = abs(d_p - c_p)
    direction_is_bull = (d_p < c_p)
    pattern_name, dir_label = _identify_harmonic_pattern(xa, ab, bc, cd, direction_is_bull)

    fib_score  = plot_df["Harmonic_Fib_Score"].iloc[-1] if "Harmonic_Fib_Score" in plot_df.columns else 0.618
    ab_xa_val = ab / (xa + 1e-8) if xa > 1e-8 else 0.618
    bc_ab_val = bc / (ab + 1e-8) if ab > 1e-8 else 1.272
    cd_bc_val = cd / (bc + 1e-8) if bc > 1e-8 else 1.618

    # Fib ratio labels on diagonal lines
    ax.text((x_idx + b_idx) / 2, (x_p + b_p) / 2, f"{ab_xa_val:.3f}", color='#f59e0b', fontsize=7.5, fontweight='bold', ha='center')
    ax.text((a_idx + c_idx) / 2, (a_p + c_p) / 2, f"{bc_ab_val:.3f}", color='#38bdf8', fontsize=7.5, fontweight='bold', ha='center')
    ax.text((b_idx + d_idx) / 2, (b_p + d_p) / 2, f"{cd_bc_val:.3f}", color='#38bdf8', fontsize=7.5, fontweight='bold', ha='center')

    pattern_lbl = f"PRZ {pattern_name.upper()} {dir_label} ({'W' if direction_is_bull else 'M'})"
    ax.text((c_idx + d_idx) / 2, (c_p + d_p) / 2 + (atr_val * 0.2), pattern_lbl,
            color='#f59e0b', fontsize=8, fontweight='bold', ha='center',
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#1e293b", edgecolor="#f59e0b", alpha=0.85))

    # 6. Monte Carlo Future Projection Curve
    future_x   = np.linspace(n_bars - 1, n_bars + 12, 20)
    curve_bend = np.sin(np.linspace(0, np.pi, 20)) * (atr_val * 0.3)
    if monte_target < curr_close:
        curve_bend = -curve_bend
    future_y = np.linspace(curr_close, monte_target, 20) + curve_bend
    ax.plot(future_x, future_y, color='#38bdf8', linestyle='--', linewidth=2.5,
            label="Monte Carlo P50 Projection")

    # 6.5 Draw Risk/Reward Shaded Profit/Loss Boxes (Matching Target Screenshot 141036)
    if direction == "SELL":
        ax.axhspan(tp_level, entry_level, xmin=0.75, xmax=0.96, color='#065f46', alpha=0.30)
        ax.axhspan(entry_level, sl_level, xmin=0.75, xmax=0.96, color='#991b1b', alpha=0.30)
    else:
        ax.axhspan(entry_level, tp_level, xmin=0.75, xmax=0.96, color='#065f46', alpha=0.30)
        ax.axhspan(sl_level, entry_level, xmin=0.75, xmax=0.96, color='#991b1b', alpha=0.30)

    # 7. Horizontal Level Dashed Lines
    ax.axhline(tp_level,    color='#26a69a', linestyle='--', linewidth=1.2)
    ax.axhline(monte_target, color='#3b82f6', linestyle='--', linewidth=1.2)
    ax.axhline(curr_close,  color='#ef5350', linestyle=':',  linewidth=1.2)
    ax.axhline(entry_level, color='#eab308', linestyle='--', linewidth=1.2)
    ax.axhline(sl_level,    color='#ef5350', linestyle='--', linewidth=1.2)

    # 8. Right-Side Level Badges
    badge_x = n_bars + 0.5
    badges = [
        ("PRZ TP1", prz_tp1,     "#ef4444"),
        ("PRZ TP2", prz_tp2,     "#ef4444"),
        ("Monte",   monte_target, "#3b82f6"),
        ("TP",      tp_level,    "#26a69a"),
        ("Close",   curr_close,  "#ef5350"),
        ("Entry",   entry_level, "#eab308"),
        ("PRZ TP3", prz_tp3,     "#a855f7"),
        ("SL",      sl_level,    "#ef4444"),
    ]

    for label, val, bg_color in badges:
        ax.text(badge_x, val, f"{label:<7} {val:>8.2f}",
                color='#ffffff', fontsize=8, fontweight='bold', va='center',
                bbox=dict(boxstyle="round,pad=0.35", facecolor=bg_color, edgecolor="none", alpha=0.9))

    # 9. Formatting
    ax.set_xlim(-1, n_bars + 11)
    ax.set_ylim(min(lows) * 0.995, max(highs) * 1.008)
    dir_tag = "[SELL BIAS]" if direction == "SELL" else "[BUY BIAS]"
    ax.set_title(f"XAUUSD QUANT ANALYZER | {dir_tag}", fontsize=11,
                 fontweight='bold', color="#ffffff", pad=12)
    ax.set_ylabel("Gold Price USD ($)", fontsize=10, color="#94a3b8")
    ax.grid(True, alpha=0.12, color='#334155')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    return output_path

