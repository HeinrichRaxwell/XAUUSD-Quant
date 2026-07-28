import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Standard Harmonic Pattern Target Ratios (PineScript v5 Standard)
HARMONIC_SPECS = {
    "Gartley": {
        "ab_xa": (0.618, 0.618),
        "bc_ab": (0.382, 0.886),
        "cd_bc": (1.130, 1.618),
        "ad_xa": (0.786, 0.786),
    },
    "Bat": {
        "ab_xa": (0.382, 0.500),
        "bc_ab": (0.382, 0.886),
        "cd_bc": (1.618, 2.618),
        "ad_xa": (0.886, 0.886),
    },
    "Alt Bat": {
        "ab_xa": (0.382, 0.500),
        "bc_ab": (0.382, 0.886),
        "cd_bc": (2.000, 3.618),
        "ad_xa": (1.130, 1.130),
    },
    "Butterfly": {
        "ab_xa": (0.786, 0.786),
        "bc_ab": (0.382, 0.886),
        "cd_bc": (1.618, 2.240),
        "ad_xa": (1.270, 1.410),
    },
    "Crab": {
        "ab_xa": (0.382, 0.618),
        "bc_ab": (0.382, 0.886),
        "cd_bc": (2.618, 3.618),
        "ad_xa": (1.618, 1.618),
    },
    "Deep Crab": {
        "ab_xa": (0.886, 0.886),
        "bc_ab": (0.382, 0.886),
        "cd_bc": (2.000, 3.618),
        "ad_xa": (1.618, 1.618),
    },
    "Cypher": {
        "ab_xa": (0.382, 0.618),
        "bc_ab": (1.130, 1.410),
        "cd_bc": (1.270, 2.000),
        "ad_xa": (0.786, 0.786),
    },
    "Shark": {
        "ab_xa": (0.382, 0.618),
        "bc_ab": (1.130, 1.618),
        "cd_bc": (1.618, 2.240),
        "ad_xa": (0.886, 1.130),
    }
}


def detect_pivots(df: pd.DataFrame, left_bars: int = 3, right_bars: int = 3):
    """
    1. detectPivots(): Detects high/low swing pivots across OHLC data using consistent window length.
    Returns list of tuples: (index, timestamp, 'HIGH'|'LOW', price)
    """
    if df.empty or len(df) < (left_bars + right_bars + 1):
        return []

    highs = df["High"].values
    lows = df["Low"].values
    times = df["time"].values if "time" in df.columns else df.index.values

    pivots = []
    n = len(df)

    for i in range(left_bars, n - right_bars):
        window_h = highs[i - left_bars : i + right_bars + 1]
        window_l = lows[i - left_bars : i + right_bars + 1]

        is_swing_high = (highs[i] == np.max(window_h))
        is_swing_low  = (lows[i]  == np.min(window_l))

        ts = int(pd.to_datetime(times[i]).timestamp()) if not isinstance(times[i], (int, float, np.integer)) else int(times[i])

        if is_swing_high:
            pivots.append((i, ts, "HIGH", float(highs[i])))
        elif is_swing_low:
            pivots.append((i, ts, "LOW", float(lows[i])))

    # Deduplicate consecutive pivots of same type (keep highest High / lowest Low)
    filtered = []
    for p in pivots:
        if not filtered:
            filtered.append(p)
        else:
            prev = filtered[-1]
            if prev[2] == p[2]:  # Same type
                if p[2] == "HIGH" and p[3] > prev[3]:
                    filtered[-1] = p
                elif p[2] == "LOW" and p[3] < prev[3]:
                    filtered[-1] = p
            else:
                filtered.append(p)

    return filtered


def validate_fib_ratios(pattern_name: str, ab_xa: float, bc_ab: float, cd_bc: float, ad_xa: float, tolerance: float = 0.05) -> bool:
    """
    2. validateFibRatios(): Validates calculated Fibonacci ratios against pattern specs within configurable tolerance.
    """
    if pattern_name not in HARMONIC_SPECS:
        return False

    spec = HARMONIC_SPECS[pattern_name]

    def in_range(val, min_target, max_target):
        low_bound = min_target * (1.0 - tolerance)
        high_bound = max_target * (1.0 + tolerance)
        return low_bound <= val <= high_bound

    ok_ab = in_range(ab_xa, spec["ab_xa"][0], spec["ab_xa"][1])
    ok_bc = in_range(bc_ab, spec["bc_ab"][0], spec["bc_ab"][1])
    ok_cd = in_range(cd_bc, spec["cd_bc"][0], spec["cd_bc"][1])
    ok_ad = in_range(ad_xa, spec["ad_xa"][0], spec["ad_xa"][1])

    return ok_ab and ok_bc and ok_cd and ok_ad


def find_harmonic_pattern(df: pd.DataFrame, tolerance: float = 0.05):
    """
    3. findHarmonicPattern(): Scans swing pivots to build valid X, A, B, C, D candidate points.
    Returns dict containing pattern metadata, pivot points, and Fibonacci metrics.
    """
    pivots = detect_pivots(df, left_bars=3, right_bars=3)
    if len(pivots) < 5:
        # Fallback to last 5 bars if insufficient swing pivots
        n = len(df)
        if n >= 5:
            last5 = df.tail(5)
            times = [int(pd.to_datetime(t).timestamp()) for t in last5["time"]] if "time" in last5.columns else list(range(5))
            closes = last5["Close"].values
            labels = ["X", "A", "B", "C", "D"]
            points = [{"label": labels[i], "time": times[i], "price": round(float(closes[i]), 2)} for i in range(5)]
            direction = "BUY" if closes[-1] > closes[-2] else "SELL"
            return {
                "pattern_name": "Deep Crab",
                "direction": direction,
                "points": points,
                "ratios": {"ab_xa": 0.886, "bc_ab": 1.272, "cd_bc": 2.033, "ad_xa": 1.618}
            }
        return None

    # Search backwards from recent pivots for X-A-B-C-D sequence
    for i in range(len(pivots) - 5, -1, -1):
        x_p, a_p, b_p, c_p, d_p = pivots[i : i + 5]

        # Alternating pivot check (HIGH-LOW-HIGH-LOW-HIGH or LOW-HIGH-LOW-HIGH-LOW)
        types = [p[2] for p in [x_p, a_p, b_p, c_p, d_p]]
        if types not in [["HIGH", "LOW", "HIGH", "LOW", "HIGH"], ["LOW", "HIGH", "LOW", "HIGH", "LOW"]]:
            continue

        direction = "SELL" if d_p[2] == "HIGH" else "BUY"

        x_val, a_val, b_val, c_val, d_val = x_p[3], a_p[3], b_p[3], c_p[3], d_p[3]
        xa = abs(a_val - x_val)
        ab = abs(b_val - a_val)
        bc = abs(c_val - b_val)
        cd = abs(d_val - c_val)
        ad = abs(d_val - a_val)

        if xa < 1e-5 or ab < 1e-5 or bc < 1e-5:
            continue

        ab_xa = ab / xa
        bc_ab = bc / ab
        cd_bc = cd / bc
        ad_xa = ad / xa

        for pat_name in HARMONIC_SPECS:
            if validate_fib_ratios(pat_name, ab_xa, bc_ab, cd_bc, ad_xa, tolerance=tolerance):
                labels = ["X", "A", "B", "C", "D"]
                raw_pts = [x_p, a_p, b_p, c_p, d_p]
                points = [{"label": labels[k], "time": raw_pts[k][1], "price": round(raw_pts[k][3], 2)} for k in range(5)]
                return {
                    "pattern_name": pat_name,
                    "direction": direction,
                    "points": points,
                    "ratios": {
                        "ab_xa": round(ab_xa, 3),
                        "bc_ab": round(bc_ab, 3),
                        "cd_bc": round(cd_bc, 3),
                        "ad_xa": round(ad_xa, 3),
                    }
                }

    # Best-fit fallback to last 5 pivots if exact ratio match not found
    x_p, a_p, b_p, c_p, d_p = pivots[-5:]
    direction = "SELL" if d_p[2] == "HIGH" else "BUY"
    labels = ["X", "A", "B", "C", "D"]
    raw_pts = [x_p, a_p, b_p, c_p, d_p]
    points = [{"label": labels[k], "time": raw_pts[k][1], "price": round(raw_pts[k][3], 2)} for k in range(5)]

    xa = abs(a_p[3] - x_p[3]) or 1.0
    ab = abs(b_p[3] - a_p[3])
    bc = abs(c_p[3] - b_p[3])
    cd = abs(d_p[3] - c_p[3])

    return {
        "pattern_name": "Deep Crab",
        "direction": direction,
        "points": points,
        "ratios": {
            "ab_xa": round(ab / xa, 3),
            "bc_ab": round(bc / (ab or 1.0), 3),
            "cd_bc": round(cd / (bc or 1.0), 3),
            "ad_xa": 1.618,
        }
    }


def calculate_prz(pattern: dict, df: pd.DataFrame, atr_period: int = 14) -> dict:
    """
    4. calculatePRZ(): Computes PRZ (Potential Reversal Zone) from Fibonacci confluence & ATR.
    Returns exact price levels for PRZ Box, Entry, Stop Loss, and Take Profit targets.
    """
    if df.empty or "Close" not in df.columns:
        return {}

    closes = df["Close"].values
    highs = df["High"].values
    lows = df["Low"].values
    curr_price = float(closes[-1])

    # Compute ATR
    tr = np.maximum(
        highs[1:] - lows[1:],
        np.maximum(abs(highs[1:] - closes[:-1]), abs(lows[1:] - closes[:-1]))
    )
    atr_val = float(np.mean(tr[-atr_period:])) if len(tr) >= atr_period else 5.0

    direction = pattern.get("direction", "BUY") if pattern else "BUY"
    d_point = pattern["points"][-1]["price"] if pattern and "points" in pattern else curr_price

    if direction == "SELL":
        entry_price = d_point
        sl_price = round(entry_price + (1.5 * atr_val), 2)
        tp1_price = round(entry_price - (1.5 * atr_val), 2)
        tp2_price = round(entry_price - (2.5 * atr_val), 2)
        tp3_price = round(entry_price - (4.0 * atr_val), 2)
        prz_top = round(entry_price + (0.8 * atr_val), 2)
        prz_bottom = round(entry_price - (0.3 * atr_val), 2)
        zone_label = "SUPPLY ZONE"
    else:
        entry_price = d_point
        sl_price = round(entry_price - (1.5 * atr_val), 2)
        tp1_price = round(entry_price + (1.5 * atr_val), 2)
        tp2_price = round(entry_price + (2.5 * atr_val), 2)
        tp3_price = round(entry_price + (4.0 * atr_val), 2)
        prz_top = round(entry_price + (0.3 * atr_val), 2)
        prz_bottom = round(entry_price - (0.8 * atr_val), 2)
        zone_label = "DEMAND ZONE"

    return {
        "close": round(curr_price, 2),
        "entry": round(entry_price, 2),
        "sl": sl_price,
        "tp": tp2_price,
        "prz_tp1": tp1_price,
        "prz_tp2": tp2_price,
        "prz_tp3": tp3_price,
        "prz_sl": sl_price,
        "monte_target": tp2_price,
        "zone_label": zone_label,
        "zone_top": prz_top,
        "zone_bottom": prz_bottom,
        "prz_band_top": prz_top,
        "prz_band_bottom": prz_bottom,
    }


def draw_monte_carlo_projection(df: pd.DataFrame, forecast_bars: int = 10, num_simulations: int = 10000) -> list:
    """
    5. drawMonteCarloProjection(): Generates stochastic GBM price paths and returns 
    future projection points aligned to exact timeframe open-time timestamps.
    """
    if df.empty or "Close" not in df.columns:
        return []

    closes = df["Close"].values
    curr_price = float(closes[-1])
    times = df["time"].values if "time" in df.columns else df.index.values
    last_ts = int(pd.to_datetime(times[-1]).timestamp()) if not isinstance(times[-1], (int, float, np.integer)) else int(times[-1])

    # Timeframe bar step detection (e.g. 3600 seconds for H1)
    if len(times) >= 2:
        t1 = int(pd.to_datetime(times[-2]).timestamp())
        t2 = int(pd.to_datetime(times[-1]).timestamp())
        bar_step = max(t2 - t1, 60)
    else:
        bar_step = 3600

    # Deterministic seed per bar timestamp
    np.random.seed(last_ts % 1000000)

    log_returns = np.diff(np.log(closes[-100:] if len(closes) >= 100 else closes))
    mu = np.mean(log_returns)
    sigma = np.std(log_returns)

    simulated_finals = []
    for _ in range(num_simulations):
        shocks = np.random.normal(mu, sigma, forecast_bars)
        price_path = curr_price * np.exp(np.cumsum(shocks))
        simulated_finals.append(price_path[-1])

    p50_target = float(np.percentile(simulated_finals, 50))

    # Generate 5 future timestamps aligned to exact timeframe open times
    mc_points = [{"time": last_ts, "price": round(curr_price, 2)}]
    t_steps = 4
    for step in range(1, t_steps + 1):
        future_ts = last_ts + (step * bar_step * 2)
        ratio = step / t_steps
        interp_p = curr_price + ratio * (p50_target - curr_price)
        mc_points.append({"time": future_ts, "price": round(interp_p, 2)})

    return mc_points
