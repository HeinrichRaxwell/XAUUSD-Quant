import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class QuantReporter:
    """
    Generates terminal summary reports and visual plots for XAUUSD Monte Carlo & Backtest results.
    """
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        plt.style.use("ggplot")

    def print_summary(self, backtest_metrics: dict, mc_metrics: dict):
        """
        Prints clean formatted terminal summary table.
        """
        print("\n" + "="*60)
        print("         XAUUSD QUANT & MONTE CARLO ANALYSIS REPORT         ")
        print("="*60)
        print("--- BACKTEST PERFORMANCE METRICS ---")
        for key, val in backtest_metrics.items():
            print(f"  {key:<25}: {val}")

        print("\n--- MONTE CARLO STRESS TEST METRICS (10,000 SIMULATIONS) ---")
        if mc_metrics:
            for key, val in mc_metrics.items():
                print(f"  {key:<25}: {val}")
        else:
            print("  No Monte Carlo metrics generated.")
        print("="*60 + "\n")

    def plot_monte_carlo_results(self, mc_results: dict, save_filename: str = "monte_carlo_xauusd.png") -> str:
        """
        Generates and saves a multi-panel visual report of Monte Carlo simulations.
        """
        if not mc_results or "Equity_Paths" not in mc_results:
            logger.warning("No Monte Carlo results available to plot.")
            return ""

        equity_paths = mc_results["Equity_Paths"]
        percentiles = mc_results["Percentiles"]
        metrics = mc_results["Metrics"]
        save_path = os.path.join(self.output_dir, save_filename)

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("XAUUSD Quantitative Strategy - Monte Carlo Stress Analysis", fontsize=16, fontweight="bold")

        # 1. Equity Fan Chart
        ax1 = axes[0, 0]
        # Plot subset of individual paths (first 50)
        for i in range(min(50, len(equity_paths))):
            ax1.plot(equity_paths[i], color="gray", alpha=0.15, linewidth=0.8)

        ax1.plot(percentiles["P95"], label="95th Percentile (Best 5%)", color="#2ecc71", linewidth=2.0)
        ax1.plot(percentiles["P50"], label="50th Percentile (Median)", color="#3498db", linewidth=2.5)
        ax1.plot(percentiles["P5"], label="5th Percentile (Worst 5%)", color="#e74c3c", linewidth=2.0)
        ax1.set_title("Simulated Equity Curves (Fan Chart)")
        ax1.set_xlabel("Trade Sequence")
        ax1.set_ylabel("Account Balance ($)")
        ax1.legend(loc="upper left")

        # 2. Final Equity Distribution
        ax2 = axes[0, 1]
        final_balances = equity_paths[:, -1]
        ax2.hist(final_balances, bins=30, color="#3498db", edgecolor="black", alpha=0.7)
        ax2.axvline(metrics["Median_Final_Balance"], color="black", linestyle="--", label=f"Median: ${metrics['Median_Final_Balance']:,.2f}")
        ax2.set_title("Terminal Equity Distribution")
        ax2.set_xlabel("Final Balance ($)")
        ax2.set_ylabel("Frequency")
        ax2.legend()

        # 3. Risk of Ruin & Drawdown PDF
        ax3 = axes[1, 0]
        # Calculate max drawdown array across simulations
        peak = np.maximum.accumulate(equity_paths, axis=1)
        drawdowns = (peak - equity_paths) / peak * 100.0
        max_dds = np.max(drawdowns, axis=1)

        ax3.hist(max_dds, bins=30, color="#e74c3c", edgecolor="black", alpha=0.7)
        ax3.axvline(metrics["Max_Drawdown_P95_%"], color="darkred", linestyle="--", label=f"95% Max DD: {metrics['Max_Drawdown_P95_%']}%")
        ax3.set_title("Maximum Drawdown Distribution (%)")
        ax3.set_xlabel("Max Drawdown (%)")
        ax3.set_ylabel("Frequency")
        ax3.legend()

        # 4. Metric Dashboard Summary Card
        ax4 = axes[1, 1]
        ax4.axis("off")
        summary_text = (
            f"SUMMARY RISK ASSESSMENT\n"
            f"----------------------------------------\n"
            f"Simulations Run       : {metrics['Simulations_Run']:,}\n"
            f"Risk of Ruin (<30% DD): {metrics['Risk_of_Ruin_%']}%\n"
            f"95% Value at Risk     : {metrics['VaR_95_%']}%\n"
            f"Median Final Equity   : ${metrics['Median_Final_Balance']:,.2f}\n"
            f"Worst 5% Drawdown     : {metrics['Max_Drawdown_P95_%']}%\n"
            f"Median Drawdown       : {metrics['Max_Drawdown_Median_%']}%\n"
            f"----------------------------------------\n"
            f"Status: {'PASSED (Robust)' if metrics['Risk_of_Ruin_%'] < 1.0 else 'WARNING (High Risk)'}"
        )
        ax4.text(0.1, 0.5, summary_text, fontsize=12, family="monospace", verticalalignment="center",
                 bbox=dict(boxstyle="round,pad=1", facecolor="#ecf0f1", alpha=0.8))

        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()

        logger.info(f"Saved Monte Carlo report chart to: {save_path}")
        return save_path

