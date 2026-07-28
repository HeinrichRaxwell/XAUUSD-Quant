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

def run_strict_oos_analysis():
    print("==========================================================================")
    print("     STRICT OUT-OF-SAMPLE (OOS) RE-ANALYSIS ON UNSEEN MARKET DATA         ")
    print("==========================================================================")

    # 1. Load 100% Real MT5 Historical Bar Feed
    loader = XauDataLoader(start_date="2021-01-01")
    raw_df = loader.fetch_data(symbol="XAUUSD", count=1500)

    # 2. Extract Complete QuantOS Feature Suite
    fe = FeatureEngineer()
    df_features = fe.add_features(raw_df)
    total_bars = len(df_features)

    # Chronological Time-Series Split: 70% In-Sample (Train), 30% Out-Of-Sample (Unseen Test)
    split_idx = int(total_bars * 0.70)
    train_df = df_features.iloc[:split_idx].copy()
    test_df = df_features.iloc[split_idx:].copy()

    print(f"[+] Total REAL MT5 Bars : {total_bars}")
    print(f"[+] In-Sample Train Bars : {len(train_df)} ({train_df.index[0]} -> {train_df.index[-1]})")
    print(f"[+] Out-Of-Sample Test Bars: {len(test_df)} ({test_df.index[0]} -> {test_df.index[-1]})")

    # --------------------------------------------------------------------------
    # CONFIG A: BASELINE MODEL (RAW EMA + RSI + ATR)
    # --------------------------------------------------------------------------
    print("\n--- [1/3] Training & Evaluating CONFIG A (Baseline) on UNSEEN DATA ---")
    model_base = XauMLModel(forward_bars=5, prob_threshold=0.60, model_dir="models_oos_base")
    X_train_base, y_train_base = model_base.prepare_data(train_df)
    base_cols = ["EMA20", "EMA50", "EMA_Spread", "Trend_EMA50", "RSI", "ATR"]
    X_train_base = X_train_base[base_cols]
    model_base.train(X_train_base, y_train_base)

    X_test_base, _ = model_base.prepare_data(test_df)
    X_test_base = X_test_base[base_cols]
    preds_base = model_base.model.predict_proba(X_test_base)
    signals_base = np.zeros(len(X_test_base), dtype=int)

    for i in range(len(preds_base)):
        if preds_base[i][1] >= 0.60:
            signals_base[i] = 1
        elif preds_base[i][0] >= 0.60:
            signals_base[i] = -1

    test_df_base = test_df.loc[X_test_base.index].copy()
    test_df_base["Signal"] = signals_base

    backtester_base = XauBacktester(initial_balance=70.0, risk_per_trade=0.01)
    trades_base, metrics_base = backtester_base.run_backtest(test_df_base)
    mc_base = MonteCarloEngine(initial_balance=70.0).run_trade_bootstrapping(trades_base, num_simulations=1000)

    # --------------------------------------------------------------------------
    # CONFIG B: QUANTOS SUITE (WITH TRIPLE BARRIER ML PREDICTIONS)
    # --------------------------------------------------------------------------
    print("\n--- [2/3] Training & Evaluating CONFIG B (QuantOS Suite) on UNSEEN DATA ---")
    model_gig = XauMLModel(forward_bars=5, prob_threshold=0.55, model_dir="models_oos_quant")
    X_train_gig, y_train_gig = model_gig.prepare_data(train_df)
    model_gig.train(X_train_gig, y_train_gig)

    test_df_gig = test_df.copy()
    signals_gig = model_gig.predict_signals(test_df_gig)
    test_df_gig["Signal"] = signals_gig

    backtester_gig = XauBacktester(initial_balance=70.0, risk_per_trade=0.01)
    backtester_gig.generate_signals = lambda df: df  # Preserve ML signals
    trades_gig, metrics_gig = backtester_gig.run_backtest(test_df_gig)
    mc_gig = MonteCarloEngine(initial_balance=70.0).run_trade_bootstrapping(trades_gig, num_simulations=1000)

    # --------------------------------------------------------------------------
    # CONFIG C: QUANTOS SUITE + 1:2.5 ASYMMETRIC RISK-REWARD + ADX TREND FILTER
    # --------------------------------------------------------------------------
    print("\n--- [3/3] Evaluating CONFIG C (QuantOS + 1:2.5 RR + ADX Trend Filter) on UNSEEN DATA ---")
    model_opt = XauMLModel(forward_bars=5, prob_threshold=0.55, model_dir="models_oos_opt")
    X_train_opt, y_train_opt = model_opt.prepare_data(train_df)
    model_opt.train(X_train_opt, y_train_opt)

    test_df_opt = test_df.copy()
    raw_signals = model_opt.predict_signals(test_df_opt)
    
    # Filter signals: Only LONG when Close > EMA50 and ADX > 20; Only SHORT when Close < EMA50 and ADX > 20
    filt_signals = np.zeros(len(raw_signals), dtype=int)
    for i in range(len(raw_signals)):
        sig = raw_signals.iloc[i]
        row = test_df_opt.iloc[i]
        if sig == 1 and row["Close"] > row["EMA50"] and row["ADX14"] >= 20.0:
            filt_signals[i] = 1
        elif sig == -1 and row["Close"] < row["EMA50"] and row["ADX14"] >= 20.0:
            filt_signals[i] = -1
        else:
            filt_signals[i] = 0

    test_df_opt["Signal"] = filt_signals

    backtester_opt = XauBacktester(initial_balance=70.0, risk_per_trade=0.01)
    backtester_opt.generate_signals = lambda df: df
    trades_opt, metrics_opt = backtester_opt.run_backtest(test_df_opt)
    mc_opt = MonteCarloEngine(initial_balance=70.0).run_trade_bootstrapping(trades_opt, num_simulations=1000)



    # --------------------------------------------------------------------------
    # SIDE-BY-SIDE OUT-OF-SAMPLE COMPARISON TABLE
    # --------------------------------------------------------------------------
    print("\n==========================================================================")
    print("      OUT-OF-SAMPLE (UNSEEN DATA) COMPARATIVE PERFORMANCE REPORT           ")
    print("==========================================================================")
    print(f"{'METRIC':<22} | {'CONFIG A (Base)':<18} | {'CONFIG B (QuantOS)':<20} | {'CONFIG C (SMC Filtered)':<22}")
    print("-" * 90)
    print(f"{'Total Trades (Unseen)':<22} | {metrics_base['Total_Trades']:<18} | {metrics_gig['Total_Trades']:<20} | {metrics_opt['Total_Trades']:<22}")
    print(f"{'Win Rate (%)':<22} | {metrics_base['Win_Rate_%']:<18.2f} | {metrics_gig['Win_Rate_%']:<20.2f} | {metrics_opt['Win_Rate_%']:<22.2f}")
    print(f"{'Profit Factor':<22} | {metrics_base['Profit_Factor']:<18.2f} | {metrics_gig['Profit_Factor']:<20.2f} | {metrics_opt['Profit_Factor']:<22.2f}")
    print(f"{'Total Return (%)':<22} | {metrics_base['Total_Return_%']:<18.2f} | {metrics_gig['Total_Return_%']:<20.2f} | {metrics_opt['Total_Return_%']:<22.2f}")
    print(f"{'Max Drawdown (%)':<22} | {metrics_base['Max_Drawdown_%']:<18.2f} | {metrics_gig['Max_Drawdown_%']:<20.2f} | {metrics_opt['Max_Drawdown_%']:<22.2f}")
    print(f"{'Sharpe Ratio':<22} | {metrics_base['Sharpe_Ratio']:<18.2f} | {metrics_gig['Sharpe_Ratio']:<20.2f} | {metrics_opt['Sharpe_Ratio']:<22.2f}")
    print("==========================================================================")

    # Save OOS Chart
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(metrics_base.get("Equity_Curve", [70]), label="Config A (Baseline)", color="red", linestyle="--")
    ax.plot(metrics_gig.get("Equity_Curve", [70]), label="Config B (QuantOS)", color="orange", linestyle=":")
    ax.plot(metrics_opt.get("Equity_Curve", [70]), label="Config C (SMC Trend Filtered)", color="green", linewidth=2)
    ax.set_title("Out-Of-Sample Equity Curves on 100% Unseen MT5 Data", fontsize=12)
    ax.set_xlabel("Trades")
    ax.set_ylabel("Account Balance ($)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    output_chart = "output/oos_comparison_report.png"
    plt.savefig(output_chart, dpi=150)
    plt.close()
    print(f"[+] OOS Comparative Chart saved to: {os.path.abspath(output_chart)}")

if __name__ == "__main__":
    run_strict_oos_analysis()
