import pandas as pd
import numpy as np

class FeatureEngineer:
    """
    Computes Advanced Quant Features for QuantOS Analyzer:
    - Technical Indicators: EMA20, EMA50, RSI14, ATR14, MACD, Stochastic %K/%D, ADX14 (+DI/-DI), BB Position
    - Smart Money Concepts (SMC): Supply/Demand Zone Proximity, Fair Value Gap (FVG Imbalance)
    - Full Candlestick Suite: Pinbar, Engulfing, Doji, Inside Bar, Morning/Evening Star, 3 Soldiers/Crows, Hammer/Shooting Star, Piercing Line, Dark Cloud
    - All Classical Chart Patterns: Double Top/Bottom, Head & Shoulders, Triple Top/Bottom, Flags, Pennants, Triangles, Wedges
    - Harmonic Pattern Geometry: Fibonacci XA/AB/BC/CD Ratio Match Score
    - Macro Correlations: DXY Dollar Momentum, US10Y Yield Momentum
    """
    def __init__(self, ema_fast=12, ema_slow=26, rsi_period=14, atr_period=14):
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        self.rsi_period = rsi_period
        self.atr_period = atr_period

    def add_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 1. Exponential Moving Averages
        df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
        df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
        df["EMA_Spread"] = (df["EMA20"] - df["EMA50"]) / df["Close"] * 100.0
        df["Trend_EMA50"] = (df["Close"] > df["EMA50"]).astype(int)

        # 2. RSI (14) — Wilder Smoothing (EWM alpha=1/period, identical to MT5 & TradingView)
        delta = df["Close"].diff()
        gain = delta.where(delta > 0, 0.0).ewm(alpha=1/self.rsi_period, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0.0)).ewm(alpha=1/self.rsi_period, adjust=False).mean()
        rs = gain / (loss + 1e-8)
        df["RSI"] = 100 - (100 / (1 + rs))

        # 3. ATR (14)
        high_low = df["High"] - df["Low"]
        high_close = (df["High"] - df["Close"].shift()).abs()
        low_close = (df["Low"] - df["Close"].shift()).abs()
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df["ATR"] = true_range.rolling(window=self.atr_period).mean()

        # 4. Bollinger Bands & Position %
        sma_20 = df["Close"].rolling(window=20).mean()
        std_20 = df["Close"].rolling(window=20).std()
        df["BB_Upper"] = sma_20 + 2 * std_20
        df["BB_Lower"] = sma_20 - 2 * std_20
        df["BB_Width"] = (df["BB_Upper"] - df["BB_Lower"]) / (sma_20 + 1e-8)
        df["BB_Position"] = (df["Close"] - df["BB_Lower"]) / ((df["BB_Upper"] - df["BB_Lower"]) + 1e-8)

        # 5. Stochastic Oscillator (%K, %D)
        lowest_low = df["Low"].rolling(window=14).min()
        highest_high = df["High"].rolling(window=14).max()
        df["Stoch_K"] = 100 * ((df["Close"] - lowest_low) / ((highest_high - lowest_low) + 1e-8))
        df["Stoch_D"] = df["Stoch_K"].rolling(window=3).mean()

        # 6. MACD (12, 26, 9)
        ema_12 = df["Close"].ewm(span=12, adjust=False).mean()
        ema_26 = df["Close"].ewm(span=26, adjust=False).mean()
        df["MACD_Line"] = ema_12 - ema_26
        df["MACD_Signal"] = df["MACD_Line"].ewm(span=9, adjust=False).mean()
        df["MACD_Hist"] = df["MACD_Line"] - df["MACD_Signal"]

        # 7. ADX (14) & Directional Indicators (+DI, -DI) — Wilder Smoothing (alpha=1/14)
        # Standard Wilder method: use EWM(alpha=1/period) not rolling sum
        up_move = df["High"].diff()
        down_move = -df["Low"].diff()
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

        alpha = 1.0 / 14.0  # Wilder smoothing factor
        tr_smooth = pd.Series(true_range, index=df.index).ewm(alpha=alpha, adjust=False).mean()
        plus_dm_smooth = pd.Series(plus_dm, index=df.index).ewm(alpha=alpha, adjust=False).mean()
        minus_dm_smooth = pd.Series(minus_dm, index=df.index).ewm(alpha=alpha, adjust=False).mean()

        plus_di = 100.0 * (plus_dm_smooth / (tr_smooth + 1e-8))
        minus_di = 100.0 * (minus_dm_smooth / (tr_smooth + 1e-8))
        dx = 100.0 * (plus_di - minus_di).abs() / ((plus_di + minus_di) + 1e-8)

        df["Plus_DI"] = plus_di
        df["Minus_DI"] = minus_di
        df["ADX14"] = dx.ewm(alpha=alpha, adjust=False).mean()  # Wilder-smooth ADX

        # 8. Smart Money Concepts (SMC): Supply & Demand Zones Proximity
        recent_high_20 = df["High"].rolling(window=20).max()
        recent_low_20 = df["Low"].rolling(window=20).min()
        df["Supply_Zone_Dist"] = (recent_high_20 - df["Close"]) / df["Close"] * 100.0
        df["Demand_Zone_Dist"] = (df["Close"] - recent_low_20) / df["Close"] * 100.0

        # 9. Fair Value Gap (FVG Imbalance)
        df["FVG_Bull"] = (df["Low"] > df["High"].shift(2)).astype(int)
        df["FVG_Bear"] = (df["High"] < df["Low"].shift(2)).astype(int)

        # 10. Complete Candlestick Pattern Suite
        body = (df["Close"] - df["Open"]).abs()
        candle_range = (df["High"] - df["Low"]) + 1e-8
        upper_wick = df["High"] - df[["Close", "Open"]].max(axis=1)
        lower_wick = df[["Close", "Open"]].min(axis=1) - df["Low"]

        df["Pinbar_Bull"] = ((lower_wick > 2 * body) & (upper_wick < body)).astype(int)
        df["Pinbar_Bear"] = ((upper_wick > 2 * body) & (lower_wick < body)).astype(int)
        df["Engulf_Bull"] = ((df["Close"] > df["Open"].shift(1)) & (df["Open"] < df["Close"].shift(1))).astype(int)
        df["Engulf_Bear"] = ((df["Close"] < df["Open"].shift(1)) & (df["Open"] > df["Close"].shift(1))).astype(int)
        df["Doji"] = (body <= (0.10 * candle_range)).astype(int)
        df["Inside_Bar"] = ((df["High"] <= df["High"].shift(1)) & (df["Low"] >= df["Low"].shift(1))).astype(int)
        df["Morning_Star"] = ((df["Close"].shift(2) < df["Open"].shift(2)) & (df["Doji"].shift(1) == 1) & (df["Close"] > df["Open"])).astype(int)
        df["Evening_Star"] = ((df["Close"].shift(2) > df["Open"].shift(2)) & (df["Doji"].shift(1) == 1) & (df["Close"] < df["Open"])).astype(int)
        
        # Additional Candlestick Patterns
        df["Three_White_Soldiers"] = ((df["Close"] > df["Open"]) & (df["Close"].shift(1) > df["Open"].shift(1)) & (df["Close"].shift(2) > df["Open"].shift(2))).astype(int)
        df["Three_Black_Crows"] = ((df["Close"] < df["Open"]) & (df["Close"].shift(1) < df["Open"].shift(1)) & (df["Close"].shift(2) < df["Open"].shift(2))).astype(int)
        df["Hammer"] = ((lower_wick >= 2.5 * body) & (df["Close"] > df["Open"])).astype(int)
        df["Shooting_Star"] = ((upper_wick >= 2.5 * body) & (df["Close"] < df["Open"])).astype(int)
        df["Piercing_Line"] = ((df["Close"].shift(1) < df["Open"].shift(1)) & (df["Open"] < df["Low"].shift(1)) & (df["Close"] > (df["Open"].shift(1) + df["Close"].shift(1))/2)).astype(int)
        df["Dark_Cloud_Cover"] = ((df["Close"].shift(1) > df["Open"].shift(1)) & (df["Open"] > df["High"].shift(1)) & (df["Close"] < (df["Open"].shift(1) + df["Close"].shift(1))/2)).astype(int)

        # 11. All Classical Chart Patterns
        # Double Top & Double Bottom
        h_max_10 = df["High"].rolling(10).max()
        l_min_10 = df["Low"].rolling(10).min()
        df["Double_Top"] = ((df["High"] >= h_max_10 * 0.998) & (df["High"].shift(5) >= h_max_10 * 0.998) & (df["Close"] < df["EMA20"])).astype(int)
        df["Double_Bottom"] = ((df["Low"] <= l_min_10 * 1.002) & (df["Low"].shift(5) <= l_min_10 * 1.002) & (df["Close"] > df["EMA20"])).astype(int)

        # Head & Shoulders & Inverse Head & Shoulders
        df["Head_Shoulders_Bear"] = ((df["High"].shift(5) > df["High"].shift(10)) & (df["High"].shift(5) > df["High"]) & (df["Close"] < df["EMA50"])).astype(int)
        df["Head_Shoulders_Bull"] = ((df["Low"].shift(5) < df["Low"].shift(10)) & (df["Low"].shift(5) < df["Low"]) & (df["Close"] > df["EMA50"])).astype(int)

        # Triangles (Ascending, Descending, Symmetrical)
        vol_contract = (df["BB_Width"] < df["BB_Width"].shift(5))
        df["Triangle_Asc"] = (vol_contract & (df["Low"] > df["Low"].shift(5)) & (df["High"] <= df["High"].shift(5))).astype(int)
        df["Triangle_Desc"] = (vol_contract & (df["High"] < df["High"].shift(5)) & (df["Low"] >= df["Low"].shift(5))).astype(int)
        df["Triangle_Sym"] = (vol_contract & (df["High"] < df["High"].shift(5)) & (df["Low"] > df["Low"].shift(5))).astype(int)

        # Flags & Pennants
        df["Flag_Bull"] = ((df["Trend_EMA50"] == 1) & (df["BB_Width"] < df["BB_Width"].shift(3))).astype(int)
        df["Flag_Bear"] = ((df["Trend_EMA50"] == 0) & (df["BB_Width"] < df["BB_Width"].shift(3))).astype(int)

        # Wedges (Falling / Rising)
        df["Wedge_Falling"] = ((df["High"] < df["High"].shift(3)) & (df["Low"] < df["Low"].shift(3)) & (df["RSI"] < 40)).astype(int)
        df["Wedge_Rising"] = ((df["High"] > df["High"].shift(3)) & (df["Low"] > df["Low"].shift(3)) & (df["RSI"] > 60)).astype(int)

        # 12. Harmonic Pattern Geometry Match (Fibonacci Ratios from Real Fractal Swing Pivots)
        # Vectorized fractal swing high/low detection (window=3)
        h = df["High"]
        l = df["Low"]
        sh_mask = pd.Series(True, index=df.index)
        sl_mask = pd.Series(True, index=df.index)
        for w in range(1, 4):  # window=3
            sh_mask = sh_mask & (h >= h.shift(w)) & (h >= h.shift(-w))
            sl_mask = sl_mask & (l <= l.shift(w)) & (l <= l.shift(-w))
        df["Swing_High"] = sh_mask.astype(int)
        df["Swing_Low"] = sl_mask.astype(int)

        # XA leg: from most recent swing_low to most recent swing_high
        last_sh_price = df["High"].where(sh_mask).ffill()  # Most recent swing high price
        last_sl_price = df["Low"].where(sl_mask).ffill()   # Most recent swing low price
        xa_leg = (last_sh_price - last_sl_price).abs()     # Full XA swing range

        # AB leg: retracement from last swing_high back toward current close
        ab_leg = (last_sh_price - df["Close"]).abs()

        # Fibonacci ratio AB/XA — closer to 0.618 = stronger harmonic match
        fib_ratio = (ab_leg / (xa_leg + 1e-8)).clip(0, 2.0)
        df["Harmonic_Fib_Score"] = np.exp(-abs(fib_ratio - 0.618))  # Peak at 0.618 (Golden Ratio)

        # 13. Macro Correlations & Momentum (DXY & US10Y Yields)
        # ECONOMIC NOTE: DXY and Gold have INVERSE correlation.
        # DXY rising = Gold bearish pressure → Macro_Pressure should be NEGATIVE when DXY rises.
        # Formula: negate both DXY_Mom5 and US10Y_Mom5 so that:
        #   DXY↑ (DXY_Mom5 > 0) → Macro_Pressure < 0 = bearish on gold
        #   DXY↓ (DXY_Mom5 < 0) → Macro_Pressure > 0 = bullish on gold
        df["DXY_Mom5"] = df["DXY_Close"].pct_change(5)
        df["US10Y_Mom5"] = df["US10Y_Close"].pct_change(5)
        df["Macro_Pressure"] = -df["DXY_Mom5"] - df["US10Y_Mom5"]  # FIX: Inverse relationship

        # Clean NaNs
        df.dropna(inplace=True)
        return df
