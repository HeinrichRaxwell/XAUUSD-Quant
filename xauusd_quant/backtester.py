import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class XauBacktester:
    """
    Quantitative Backtest Engine for XAUUSD.
    Executes trades based on strategy signals with realistic spread, slippage, and ATR-based risk management.
    """
    def __init__(
        self,
        initial_balance: float = 10000.0,
        risk_per_trade: float = 0.01,  # 1% per trade
        atr_multiplier_sl: float = 1.5,
        atr_multiplier_tp: float = 3.0,
        spread_usd: float = 0.30,       # $0.30 per oz (typical XAUUSD spread)
        slippage_std_usd: float = 0.10  # Random slippage noise std
    ):
        self.initial_balance = initial_balance
        self.risk_per_trade = risk_per_trade
        self.atr_multiplier_sl = atr_multiplier_sl
        self.atr_multiplier_tp = atr_multiplier_tp
        self.spread_usd = spread_usd
        self.slippage_std_usd = slippage_std_usd

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["Signal"] = 0

        long_cond = (
            (df["EMA20"] > df["EMA50"]) &
            (df["RSI"] > 50) &
            (df["RSI"] < 70)
        )

        # FIX: Short only when BEARISH trend confirmed — must not overlap with long_cond
        short_cond = (
            (df["EMA20"] < df["EMA50"]) &
            (df["RSI"] > 30) &
            (df["RSI"] < 50)
        )

        df.loc[long_cond, "Signal"] = 1
        df.loc[short_cond & ~long_cond, "Signal"] = -1  # Never override a BUY signal

        return df

    def run_backtest(self, df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        df = self.generate_signals(df)
        balance = self.initial_balance
        equity_curve = [balance]
        trades = []
        in_position = False
        pos_type = None
        entry_price = 0.0
        sl_price = 0.0
        tp_price = 0.0
        position_size = 0.0
        entry_time = None

        for i in range(len(df)):
            row = df.iloc[i]
            date = row.name if isinstance(row.name, (str, pd.Timestamp)) else i
            close = row["Close"]
            high = row["High"]
            low = row["Low"]
            atr = row["ATR"] if "ATR" in row and not np.isnan(row["ATR"]) else 5.0
            sig = row["Signal"]

            if in_position:
                pnl = 0.0
                closed = False

                if pos_type == "LONG":
                    if low <= sl_price:
                        pnl = (sl_price - entry_price) * position_size
                        closed = True
                        exit_reason = "SL"
                    elif high >= tp_price:
                        pnl = (tp_price - entry_price) * position_size
                        closed = True
                        exit_reason = "TP"
                elif pos_type == "SHORT":
                    if high >= sl_price:
                        pnl = (entry_price - sl_price) * position_size
                        closed = True
                        exit_reason = "SL"
                    elif low <= tp_price:
                        pnl = (entry_price - tp_price) * position_size
                        closed = True
                        exit_reason = "TP"

                if closed:
                    balance += pnl
                    trades.append({
                        "Entry_Time": entry_time,
                        "Exit_Time": date,
                        "Type": pos_type,
                        "Entry_Price": entry_price,
                        "PnL_USD": pnl,
                        "Balance": balance,
                        "Exit_Reason": exit_reason
                    })
                    in_position = False

            if not in_position and sig != 0:
                pos_type = "LONG" if sig == 1 else "SHORT"
                risk_amount = balance * self.risk_per_trade
                sl_dist = atr * self.atr_multiplier_sl
                tp_dist = atr * self.atr_multiplier_tp

                if pos_type == "LONG":
                    entry_price = close + self.spread_usd + np.random.normal(0, self.slippage_std_usd)
                    sl_price = entry_price - sl_dist
                    tp_price = entry_price + tp_dist
                else:
                    entry_price = close - self.spread_usd - np.random.normal(0, self.slippage_std_usd)
                    sl_price = entry_price + sl_dist
                    tp_price = entry_price - tp_dist

                position_size = risk_amount / sl_dist
                entry_time = date
                in_position = True

            equity_curve.append(balance)

        trades_df = pd.DataFrame(trades)
        metrics = self._calculate_metrics(trades_df, equity_curve)
        return trades_df, metrics

    def _calculate_metrics(self, trades_df: pd.DataFrame, equity_curve: list) -> dict:
        if trades_df.empty:
            return {"Total_Trades": 0, "Win_Rate_%": 0.0, "Profit_Factor": 0.0, "Total_Return_%": 0.0, "Max_Drawdown_%": 0.0, "Sharpe_Ratio": 0.0}

        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df["PnL_USD"] > 0])
        win_rate = (winning_trades / total_trades) * 100.0
        
        gross_profit = trades_df[trades_df["PnL_USD"] > 0]["PnL_USD"].sum()
        gross_loss = abs(trades_df[trades_df["PnL_USD"] < 0]["PnL_USD"].sum())
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else np.nan

        total_return_pct = ((equity_curve[-1] - self.initial_balance) / self.initial_balance) * 100.0

        eq_arr = np.array(equity_curve)
        peak = np.maximum.accumulate(eq_arr)
        drawdowns = (eq_arr - peak) / peak * 100.0
        max_drawdown = abs(np.min(drawdowns))

        returns = pd.Series(equity_curve).pct_change().dropna()
        # FIX: H1 data uses sqrt(252*24) annualization, not sqrt(252) which is for daily
        annualization_factor = np.sqrt(252 * 24)
        sharpe = (returns.mean() / returns.std() * annualization_factor) if returns.std() > 0 else 0.0

        return {
            "Total_Trades": total_trades,
            "Win_Rate_%": round(win_rate, 2),
            "Profit_Factor": round(profit_factor, 2) if not np.isnan(profit_factor) else "Inf",
            "Total_Return_%": round(total_return_pct, 2),
            "Max_Drawdown_%": round(max_drawdown, 2),
            "Sharpe_Ratio": round(sharpe, 2),
            "Final_Balance": round(equity_curve[-1], 2)
        }


class MonteCarloEngine:
    """
    Monte Carlo Simulation Engine for Gold Price Trajectories & Risk Testing.
    Executes 10,000 Geometric Brownian Motion (GBM) price trajectory simulations in Gold USD ($/oz) units.
    """
    def __init__(self, initial_balance: float = 10000.0, ruin_threshold_pct: float = 30.0):
        self.initial_balance = initial_balance
        self.ruin_threshold = initial_balance * (1.0 - (ruin_threshold_pct / 100.0))

    def run_price_monte_carlo(self, df: pd.DataFrame, forecast_bars: int = 10, num_simulations: int = 10000) -> dict:
        """
        Simulates 10,000 future Gold price paths starting from S_0 (current candle close).
        S_{t+1} = S_t * exp( (mu - 0.5*sigma^2)*dt + sigma*sqrt(dt)*Z )
        Returns P10 (Pesimis), P50 (Median), P90 (Optimis) in Gold USD ($/oz) units.
        """
        if df.empty or "Close" not in df.columns:
            return {"P10_Price": 2000.0, "P50_Price": 2000.0, "P90_Price": 2000.0, "Price_Paths": []}

        closes = df["Close"].values
        s_0 = float(closes[-1])
        times = df["time"].values if "time" in df.columns else df.index.values
        last_ts = int(pd.to_datetime(times[-1]).timestamp()) if not isinstance(times[-1], (int, float, np.integer)) else int(times[-1])
        
        # Seed by bar timestamp for 100% chart & bot sync
        np.random.seed(last_ts % 1000000)

        # Calculate historical log returns drift (mu) and volatility (sigma) from last 100 bars
        window_closes = closes[-100:] if len(closes) >= 100 else closes
        log_returns = np.diff(np.log(window_closes))
        mu = float(np.mean(log_returns))
        sigma = float(np.std(log_returns)) + 1e-8
        dt = 1.0

        price_paths = np.zeros((num_simulations, forecast_bars + 1))
        price_paths[:, 0] = s_0

        for t in range(1, forecast_bars + 1):
            z = np.random.normal(0, 1, num_simulations)
            price_paths[:, t] = price_paths[:, t-1] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z)

        final_prices = price_paths[:, -1]
        p10_price = float(np.percentile(final_prices, 10))
        p50_price = float(np.percentile(final_prices, 50))
        p90_price = float(np.percentile(final_prices, 90))

        return {
            "S0_Current": s_0,
            "P10_Price": round(p10_price, 2),
            "P50_Price": round(p50_price, 2),
            "P90_Price": round(p90_price, 2),
            "Drift_Direction": "BUY" if p50_price >= s_0 else "SELL",
            "Price_Paths": price_paths.tolist()
        }

    def run_trade_bootstrapping(self, trades_df: pd.DataFrame, num_simulations: int = 2000) -> dict:
        if trades_df.empty or "PnL_USD" not in trades_df.columns:
            return {
                "Simulations_Run": num_simulations,
                "Risk_of_Ruin_%": 0.0,
                "VaR_95_%": 0.0,
                "Median_Final_Balance": self.initial_balance,
                "Max_Drawdown_P95_%": 0.0,
                "Max_Drawdown_Median_%": 0.0,
                "Equity_Curves": []
            }

        pnl_sequence = trades_df["PnL_USD"].values
        n_trades = len(pnl_sequence)
        
        ruin_count = 0
        final_balances = []
        max_drawdowns = []
        equity_curves = []

        for s in range(num_simulations):
            sampled_pnls = np.random.choice(pnl_sequence, size=n_trades, replace=True)
            eq_curve = [self.initial_balance]
            curr_bal = self.initial_balance
            ruined = False

            for pnl in sampled_pnls:
                curr_bal += pnl
                eq_curve.append(curr_bal)
                if curr_bal <= self.ruin_threshold:
                    ruined = True

            if ruined:
                ruin_count += 1

            final_balances.append(curr_bal)
            equity_curves.append(eq_curve)

            eq_arr = np.array(eq_curve)
            peak = np.maximum.accumulate(eq_arr)
            dds = (eq_arr - peak) / peak * 100.0
            max_drawdowns.append(abs(np.min(dds)))

        risk_of_ruin = (ruin_count / num_simulations) * 100.0
        var_95 = self.initial_balance - np.percentile(final_balances, 5)
        var_95_pct = (var_95 / self.initial_balance) * 100.0

        return {
            "Simulations_Run": num_simulations,
            "Risk_of_Ruin_%": round(risk_of_ruin, 2),
            "VaR_95_%": round(var_95_pct, 2),
            "Median_Final_Balance": round(float(np.median(final_balances)), 2),
            "Max_Drawdown_P95_%": round(float(np.percentile(max_drawdowns, 95)), 2),
            "Max_Drawdown_Median_%": round(float(np.median(max_drawdowns)), 2),
            "Equity_Curves": equity_curves
        }
