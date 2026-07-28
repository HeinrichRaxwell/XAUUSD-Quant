import os
import sys
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xauusd_quant.data_loader import XauDataLoader
from xauusd_quant.features import FeatureEngineer
from xauusd_quant.ml_model import XauMLModel
from xauusd_quant.backtester import XauBacktester
from xauusd_quant.monte_carlo import MonteCarloEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_enhanced_benchmark():
    print("==========================================================================")
    print(" HIGH-CONFIDENCE (>65%) MULTI-HORIZON BENCHMARK & 10,000 MONTE CARLO SIMS   ")
    print("==========================================================================")

    # 1. Ingest 100% REAL MT5 Market Data
    loader = XauDataLoader(start_date="2021-01-01")
    raw_df = loader.fetch_data(symbol="XAUUSD", count=1500)

    # 2. Extract Features
    fe = FeatureEngineer()
    df_features = fe.add_features(raw_df)
    total_bars = len(df_features)

    horizons = {
        "1 Month": 250,
        "2 Months": 500,
        "3 Months": 750,
        "6 Months": min(1500, total_bars)
    }

    results_table = []
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes_flat = axes.flatten()

    for idx, (h_name, bar_count) in enumerate(horizons.items()):
        print(f"\n--- Evaluating Horizon: {h_name} ({bar_count} Real MT5 Bars) ---")
        sub_df = df_features.tail(bar_count).copy()

        split_idx = int(len(sub_df) * 0.70)
        train_df = sub_df.iloc[:split_idx].copy()
        test_df = sub_df.iloc[split_idx:].copy()

        model_dir = f"models_enh_{bar_count}"
        if os.path.exists(model_dir):
            import shutil
            shutil.rmtree(model_dir)

        # High Confidence Threshold = 0.65 (65%)
        model = XauMLModel(forward_bars=5, prob_threshold=0.65, model_dir=model_dir)
        X_train, y_train = model.prepare_data(train_df)
        model.train(X_train, y_train)

        test_df_eval = test_df.copy()
        raw_signals = model.predict_signals(test_df_eval)
        
        # Confluence Filter: Only take signal when aligned with Trend_EMA50 and ADX >= 18
        filt_signals = np.zeros(len(raw_signals), dtype=int)
        for i in range(len(raw_signals)):
            sig = raw_signals.iloc[i]
            row = test_df_eval.iloc[i]
            if sig == 1 and row["Close"] > row["EMA50"]:
                filt_signals[i] = 1
            elif sig == -1 and row["Close"] < row["EMA50"]:
                filt_signals[i] = -1
            else:
                filt_signals[i] = 0

        test_df_eval["Signal"] = filt_signals

        backtester = XauBacktester(initial_balance=70.0, risk_per_trade=0.01)
        backtester.generate_signals = lambda df: df
        trades_df, metrics = backtester.run_backtest(test_df_eval)

        # Monte Carlo 10,000 Simulations
        mc_engine = MonteCarloEngine(initial_balance=70.0, ruin_threshold_pct=30.0)
        mc_res = mc_engine.run_trade_bootstrapping(trades_df, num_simulations=10000)
        mc_metrics = mc_res.get("Metrics", {})

        results_table.append({
            "Horizon": h_name,
            "Bars": bar_count,
            "Trades": metrics["Total_Trades"],
            "Win_Rate": metrics["Win_Rate_%"],
            "Profit_Factor": metrics["Profit_Factor"],
            "Return_%": metrics["Total_Return_%"],
            "Max_DD_%": metrics["Max_Drawdown_%"],
            "Sharpe": metrics["Sharpe_Ratio"],
            "Ruin_Risk_%": mc_metrics.get("Risk_of_Ruin_%", 0.0)
        })

        curves = mc_res.get("Equity_Curves", [])
        ax = axes_flat[idx]
        for c in curves[:100]:
            ax.plot(c, color="seagreen", alpha=0.08)
        
        if len(curves) > 0:
            median_curve = np.median(curves, axis=0)
            ax.plot(median_curve, color="darkgreen", linewidth=2, label="Median Path (P50)")

        ax.set_title(f"{h_name} Horizon - High Confidence 65% (10k Monte Carlo)", fontsize=11)
        ax.set_xlabel("Trades")
        ax.set_ylabel("Account Balance ($)")
        ax.legend()
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    chart_path = "output/multi_horizon_enhanced_report.png"
    plt.savefig(chart_path, dpi=150)
    plt.close()

    df_res = pd.DataFrame(results_table)
    print("\n==========================================================================")
    print("      ENHANCED HIGH-CONFIDENCE MULTI-HORIZON BENCHMARK (10,000 MC SIMS)     ")
    print("==========================================================================")
    print(df_res.to_string(index=False))
    print("==========================================================================")
    print(f"[+] Enhanced Multi-Horizon Chart saved to: {os.path.abspath(chart_path)}")

if __name__ == "__main__":
    run_enhanced_benchmark()
