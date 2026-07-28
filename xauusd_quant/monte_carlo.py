import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class MonteCarloEngine:
    """
    Dual-Engine Monte Carlo Simulator for XAUUSD Trading Strategies.
    1. Trade Bootstrapping: Resamples backtest trade logs with execution noise.
    2. Price Path Simulation: Generates stochastic GBM & Merton Jump-Diffusion price paths.
    """
    def __init__(self, initial_balance: float = 10000.0, ruin_threshold_pct: float = 30.0):
        self.initial_balance = initial_balance
        self.ruin_threshold_pct = ruin_threshold_pct
        self.ruin_balance = initial_balance * (1.0 - ruin_threshold_pct / 100.0)

    def run_trade_bootstrapping(
        self,
        trades_df: pd.DataFrame,
        num_simulations: int = 2000,
        noise_std_pct: float = 0.15
    ) -> dict:
        """
        Resamples trade returns randomly N times with added execution noise.
        Returns simulation metrics and equity paths matrix.
        """
        if trades_df.empty or "PnL_Pct" not in trades_df.columns:
            logger.warning("No trade log available for Monte Carlo resampling.")
            return {}

        returns = trades_df["PnL_Pct"].values / 100.0  # Convert to fraction
        num_trades = len(returns)

        equity_paths = np.zeros((num_simulations, num_trades + 1))
        equity_paths[:, 0] = self.initial_balance

        ruin_count = 0
        max_drawdowns = np.zeros(num_simulations)
        final_balances = np.zeros(num_simulations)

        for i in range(num_simulations):
            # Bootstrap sample (with replacement) + Gaussian execution noise
            shuffled_indices = np.random.choice(num_trades, size=num_trades, replace=True)
            noise = np.random.normal(0, noise_std_pct / 100.0, size=num_trades)
            sim_returns = returns[shuffled_indices] + noise

            # Calculate equity path
            path = self.initial_balance * np.cumprod(1.0 + sim_returns)
            equity_paths[i, 1:] = path

            # Check for ruin
            min_bal = np.min(path)
            if min_bal <= self.ruin_balance:
                ruin_count += 1

            # Max Drawdown calculation
            peak = np.maximum.accumulate(path)
            dd = (peak - path) / peak * 100.0
            max_drawdowns[i] = np.max(dd)
            final_balances[i] = path[-1]

        # Calculate Percentiles across simulations
        p5 = np.percentile(equity_paths, 5, axis=0)
        p25 = np.percentile(equity_paths, 25, axis=0)
        p50 = np.percentile(equity_paths, 50, axis=0)
        p75 = np.percentile(equity_paths, 75, axis=0)
        p95 = np.percentile(equity_paths, 95, axis=0)

        ruin_probability_pct = (ruin_count / num_simulations) * 100.0
        var_95_pct = abs(np.percentile((final_balances - self.initial_balance) / self.initial_balance * 100.0, 5))

        return {
            "Equity_Paths": equity_paths,
            "Percentiles": {
                "P5": p5,
                "P25": p25,
                "P50": p50,
                "P75": p75,
                "P95": p95,
            },
            "Metrics": {
                "Simulations_Run": num_simulations,
                "Risk_of_Ruin_%": round(ruin_probability_pct, 2),
                "VaR_95_%": round(var_95_pct, 2),
                "Median_Final_Balance": round(np.median(final_balances), 2),
                "Max_Drawdown_P95_%": round(np.percentile(max_drawdowns, 95), 2),
                "Max_Drawdown_Median_%": round(np.median(max_drawdowns), 2)
            }
        }

    def generate_stochastic_price_paths(
        self,
        initial_price: float = 2000.0,
        num_days: int = 252,
        num_paths: int = 100,
        annual_drift: float = 0.06,
        annual_volatility: float = 0.18,
        jump_lambda: float = 12,  # Expected jumps per year
        jump_std: float = 0.02
    ) -> np.ndarray:
        """
        Generates Merton Jump-Diffusion synthetic XAUUSD price paths.
        S_t = S_0 * exp((mu - 0.5*sigma^2)*t + sigma*W_t + sum(J_i))
        """
        dt = 1.0 / 252.0
        paths = np.zeros((num_paths, num_days + 1))
        paths[:, 0] = initial_price

        for i in range(num_paths):
            # Diffusion component
            z = np.random.normal(0, 1, num_days)
            diffusion = (annual_drift - 0.5 * annual_volatility**2) * dt + annual_volatility * np.sqrt(dt) * z
            
            # Jump component (Merton Model)
            jumps_occurred = np.random.poisson(jump_lambda * dt, num_days)
            jump_sizes = np.random.normal(0, jump_std, num_days) * jumps_occurred
            
            total_log_returns = diffusion + jump_sizes
            paths[i, 1:] = initial_price * np.exp(np.cumsum(total_log_returns))

        return paths

    def run_price_monte_carlo(
        self,
        df: pd.DataFrame,
        forecast_bars: int = 10,
        num_simulations: int = 10000
    ) -> dict:
        """
        Runs Geometric Brownian Motion Monte Carlo price simulation on recent dataframe.
        Deterministic random seed per bar to prevent flipping on browser refresh.
        """
        if df.empty or "Close" not in df.columns:
            return {"Drift_Direction": "NEUTRAL", "P10_Price": 4085.0, "P50_Price": 4085.0, "P90_Price": 4085.0}

        # Set deterministic seed based on latest bar timestamp
        if "time" in df.columns and len(df) > 0:
            last_ts = int(pd.to_datetime(df["time"].iloc[-1]).timestamp())
            np.random.seed(last_ts % 1000000)
        else:
            np.random.seed(42)

        closes = df["Close"].values
        current_price = float(closes[-1])
        log_returns = np.diff(np.log(closes[-100:] if len(closes) >= 100 else closes))
        mu = np.mean(log_returns)
        sigma = np.std(log_returns)

        simulated_finals = []
        for _ in range(num_simulations):
            shocks = np.random.normal(mu, sigma, forecast_bars)
            price_path = current_price * np.exp(np.cumsum(shocks))
            simulated_finals.append(price_path[-1])

        p10 = float(np.percentile(simulated_finals, 10))
        p50 = float(np.percentile(simulated_finals, 50))
        p90 = float(np.percentile(simulated_finals, 90))
        direction = "SELL" if p50 < current_price else "BUY"

        return {
            "Drift_Direction": direction,
            "P10_Price": round(p10, 2),
            "P50_Price": round(p50, 2),
            "P90_Price": round(p90, 2)
        }
