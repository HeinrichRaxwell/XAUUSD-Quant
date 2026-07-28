import argparse
import sys
import os
import pandas as pd

from xauusd_quant.data_loader import XauDataLoader
from xauusd_quant.features import FeatureEngineer
from xauusd_quant.backtester import XauBacktester
from xauusd_quant.ml_model import XauMLModel
from xauusd_quant.monte_carlo import MonteCarloEngine
from xauusd_quant.reporter import QuantReporter

def main():
    parser = argparse.ArgumentParser(description="XAUUSD Quant Strategy & Monte Carlo Simulator")
    parser.add_argument("--symbol", type=str, default="GC=F", help="YFinance symbol for Gold (default: GC=F)")
    parser.add_argument("--strategy", type=str, choices=["rule", "ml"], default="ml", help="Strategy type: rule or ml")
    parser.add_argument("--balance", type=float, default=10000.0, help="Initial Account Balance")
    parser.add_argument("--simulations", type=int, default=2000, help="Number of Monte Carlo simulations")
    parser.add_argument("--ruin-threshold", type=float, default=30.0, help="Ruin drawdown threshold in percent")
    args = parser.parse_args()

    print("===============================================================")
    print("      INITIALIZING XAUUSD QUANT & MONTE CARLO PIPELINE         ")
    print("===============================================================")

    # 1. Ingest Data
    loader = XauDataLoader(start_date="2020-01-01")
    df_raw = loader.fetch_data(symbol=args.symbol)

    # 2. Compute Quant & Macro Features
    fe = FeatureEngineer()
    df_features = fe.add_features(df_raw)
    print(f"[+] Computed technical & macro features. Total bars: {len(df_features)}")

    # 3. Strategy Signal Generation (Rule-Based or Machine Learning)
    if args.strategy == "ml":
        print("[+] Training Machine Learning Classifier (LightGBM)...")
        ml_model = XauMLModel(forward_bars=5, prob_threshold=0.55)
        X, y = ml_model.prepare_data(df_features)
        train_stats = ml_model.train(X, y)
        print(f"[+] ML Training Accuracy - Train: {train_stats['Train_Accuracy']*100:.2f}%, Test: {train_stats['Test_Accuracy']*100:.2f}%")

        # Inject ML Signals into DataFrame
        df_features["Signal"] = ml_model.predict_signals(df_features)
    
    # 4. Execute Strategy Backtest
    backtester = XauBacktester(initial_balance=args.balance, risk_per_trade=0.01)
    
    # Override signal generation if ML strategy chosen
    if args.strategy == "ml":
        original_gen_signals = backtester.generate_signals
        backtester.generate_signals = lambda df: df  # Signals already attached

    trades_df, backtest_metrics = backtester.run_backtest(df_features)

    # 5. Run Dual Monte Carlo Simulations
    mc_engine = MonteCarloEngine(initial_balance=args.balance, ruin_threshold_pct=args.ruin_threshold)
    mc_results = mc_engine.run_trade_bootstrapping(trades_df, num_simulations=args.simulations)

    # 6. Generate Reports & Visualizations
    reporter = QuantReporter(output_dir="output")
    reporter.print_summary(backtest_metrics, mc_results.get("Metrics", {}))
    
    chart_path = reporter.plot_monte_carlo_results(mc_results)
    if chart_path:
        print(f"[OK] Analysis complete! Chart saved to: {os.path.abspath(chart_path)}")

if __name__ == "__main__":
    main()
