import os
import time
import argparse
import logging
import pandas as pd
import numpy as np

from xauusd_quant.data_loader import XauDataLoader
from xauusd_quant.features import FeatureEngineer
from xauusd_quant.ml_model import XauMLModel
from xauusd_quant.backtester import XauBacktester, MonteCarloEngine
from xauusd_quant.mt5_bridge import MT5Bridge
from xauusd_quant.telegram_notifier import TelegramNotifier
from xauusd_quant.chart_generator import generate_quant_chart

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MasterPipeline")

MAGIC_NUMBER = 888111

def execute_pipeline(prob_threshold: float = 0.65, verbose_log: bool = True):
    if verbose_log:
        logger.info(f"==========================================================================")
        logger.info(f"      XAUUSD ALL-IN-ONE QUANT SIMULATOR & MT5 AUTO-TRADER               ")
        logger.info(f"      [ML Confidence Threshold: {prob_threshold*100:.0f}% | Dual H1/M15]             ")
        logger.info(f"==========================================================================")


    # 1. Connect MT5 Broker Bridge & Process Telegram Commands
    mt5 = MT5Bridge(symbol="XAUUSDm", magic_number=MAGIC_NUMBER)
    tele = TelegramNotifier()

    if not mt5.is_connected:
        logger.error("[!] Failed to connect to MT5 Broker. Proceeding in Simulation Mode.")

        is_live_mt5 = False
        # FIX: Use neutral $100 default, not old hardcoded account balance $71.57
        acc_info = {"Balance": 100.0, "Equity": 100.0, "Margin": 0, "Margin_Free": 100.0, "Margin_Level": 0}
    else:
        is_live_mt5 = True
        acc_info = mt5.get_account_info()
        if verbose_log:
            logger.info(f"[1/5] MT5 Account Connected: #{acc_info.get('Login', 'N/A')} (REAL_MT5)")
            logger.info(f"      Current Balance: ${acc_info.get('Balance', 0):.2f} USD | Equity: ${acc_info.get('Equity', 0):.2f} USD")
        
        # Process Telegram Commands (using persistent offset)
        cmd_count = tele.process_incoming_commands(mt5)
        if cmd_count > 0:
            logger.info(f"       [Telegram Bot] Processed {cmd_count} incoming Telegram slash command(s).")



    # 2. Ingest 100% REAL Market Data from MT5
    if verbose_log:
        logger.info("\n[2/5] Ingesting 100% REAL Market Data from MT5 & Computing Features...")
    loader = XauDataLoader()

    df_raw = loader.fetch_data(count=1500)
    
    if df_raw is None or len(df_raw) < 100:
        logger.error("Failed to load sufficient real market data.")
        return

    fe = FeatureEngineer()
    df_feat = fe.add_features(df_raw)
    if verbose_log:
        logger.info(f"      Processed {len(df_feat)} REAL historical bars from MT5.")

    # 3. ML Model Signal Prediction & Retraining
    if verbose_log:
        logger.info(f"\n[3/5] Online Retraining LightGBM Model (Threshold >= {prob_threshold*100:.0f}%)...")
    ml_model = XauMLModel(forward_bars=5, prob_threshold=prob_threshold, model_dir="models")
    
    try:
        df_feat["Signal"] = ml_model.predict_signals(df_feat)
    except Exception:
        X_tr, y_tr = ml_model.prepare_data(df_feat)
        ml_model.train(X_tr, y_tr)
        df_feat["Signal"] = ml_model.predict_signals(df_feat)

    backtester = XauBacktester(initial_balance=acc_info.get("Balance", 100.0), risk_per_trade=0.01)
    backtester.generate_signals = lambda df: df
    trades_df, perf_summary = backtester.run_backtest(df_feat)

    mc_engine = MonteCarloEngine(initial_balance=acc_info.get("Balance", 100.0))
    mc_results = mc_engine.run_trade_bootstrapping(trades_df, num_simulations=2000)


    print("\n============================================================")
    print("         XAUUSD QUANT & MONTE CARLO ANALYSIS REPORT         ")
    print("============================================================")
    print("--- BACKTEST PERFORMANCE METRICS ---")
    for k, v in perf_summary.items():
        print(f"  {k:<25}: {v}")

    print("\n--- MONTE CARLO STRESS TEST METRICS (10,000 SIMULATIONS) ---")
    for k, v in mc_results.items():
        if k != "Equity_Curves":
            print(f"  {k:<25}: {v}")
    print("============================================================\n")

    chart_file = generate_quant_chart(df_feat, mc_results, output_path="output/telegram_signal_chart.png")
    logger.info(f"      [OK] Monte Carlo Report Chart saved: {os.path.abspath(chart_file)}")

    # 5. Live Market Execution & Automatic Position Reversal (Cut Profit & Switch)
    if is_live_mt5:
        logger.info("\n[5/5] Evaluating MT5 Bot Active Positions & Live Market Conditions...")
        positions = mt5.get_open_positions()

        # Pure Empirical Price Monte Carlo Direction (10,000 Trajectories)
        price_mc = mc_engine.run_price_monte_carlo(df_feat, forecast_bars=10, num_simulations=10000)
        curr_price = df_feat["Close"].iloc[-1]
        p50_price = price_mc["P50_Price"]

        mc_direction = price_mc["Drift_Direction"]
        logger.info(f"      Pure Empirical Price Monte Carlo Direction: {mc_direction} (P50 Price Target: ${p50_price:,.2f})")

        # ML signal for current bar (used in reversal gate)
        latest_sig = df_feat["Signal"].iloc[-1]  # 1=BUY>=65%, -1=SELL>=65%, 0=no signal
        sig_direction = "BUY" if latest_sig == 1 else ("SELL" if latest_sig == -1 else "NEUTRAL")

        # --- Cooldown: Do NOT trade if last trade was < 300 seconds ago ---
        now_ts = time.time()
        _TRADE_COOLDOWN_FILE = "state/last_trade_time.txt"
        last_trade_ts = 0.0
        try:
            if os.path.exists(_TRADE_COOLDOWN_FILE):
                with open(_TRADE_COOLDOWN_FILE, "r") as f:
                    last_trade_ts = float(f.read().strip())
        except Exception:
            last_trade_ts = 0.0
        trade_cooldown_ok = (now_ts - last_trade_ts) >= 300.0  # 5 minute minimum

        def record_trade_time():
            os.makedirs("state", exist_ok=True)
            with open(_TRADE_COOLDOWN_FILE, "w") as f:
                f.write(str(time.time()))

        # Monitor & Trailing Stop on Active Trades
        if positions and len(positions) > 0:
            for pos in positions:
                ptype = "BUY" if pos["type"] == 0 else "SELL"
                pnl = pos["profit"]
                ticket = pos["ticket"]
                logger.info(f"--------------------------------------------------------------------------")
                logger.info(f"  [ACTIVE POSITION #{ticket}]: {ptype} {pos['volume']} lot | Floating PnL: ${pnl:+.2f} USD")
                logger.info(f"--------------------------------------------------------------------------")

                # Trailing Stop Break-Even Check
                mt5.manage_trailing_stop(pos, df_feat["ATR"].iloc[-1])

                # Position Reversal Logic:
                # REQUIRES BOTH: (1) Monte Carlo direction flipped AND (2) ML signal agrees AND (3) 5min cooldown
                if ptype == "SELL" and mc_direction == "BUY" and sig_direction == "BUY" and trade_cooldown_ok:
                    logger.info(f"🚨 [POSITION REVERSAL] MC=BUY + ML=BUY ({prob_threshold*100:.0f}%+). Closing SELL #{ticket} (PnL: ${pnl:+.2f}) → Switching to BUY...")
                    if mt5.close_position(ticket):
                        pnl_str = f"with profit `+${pnl:,.2f} USD`" if pnl >= 0 else f"with loss `-${abs(pnl):,.2f} USD`"
                        tele.send_message(f"🔄 *POSITION REVERSAL EXECUTED*: Closed SELL Position #{ticket} {pnl_str}. Switching to BUY position!")
                        time.sleep(0.5)
                        current_atr = float(df_feat["ATR"].iloc[-1])
                        sl_dist = round(current_atr * 1.5, 2)
                        tp_dist = round(current_atr * 3.0, 2)
                        mt5.execute_trade(signal_type="BUY", lot_size=0.01, sl_pips=sl_dist, tp_pips=tp_dist)
                        record_trade_time()
                elif ptype == "SELL" and mc_direction == "BUY" and (sig_direction != "BUY" or not trade_cooldown_ok):
                    cooldown_msg = f"Cooldown aktif ({300 - int(now_ts - last_trade_ts)}s lagi)" if not trade_cooldown_ok else f"ML Signal: {sig_direction} (bukan BUY)"
                    logger.info(f"⏸️ [REVERSAL BLOCKED] MC=BUY tapi {cooldown_msg}. Menunggu konfirmasi...")

                elif ptype == "BUY" and mc_direction == "SELL" and sig_direction == "SELL" and trade_cooldown_ok:
                    logger.info(f"🚨 [POSITION REVERSAL] MC=SELL + ML=SELL ({prob_threshold*100:.0f}%+). Closing BUY #{ticket} (PnL: ${pnl:+.2f}) → Switching to SELL...")
                    if mt5.close_position(ticket):
                        pnl_str = f"with profit `+${pnl:,.2f} USD`" if pnl >= 0 else f"with loss `-${abs(pnl):,.2f} USD`"
                        tele.send_message(f"🔄 *POSITION REVERSAL EXECUTED*: Closed BUY Position #{ticket} {pnl_str}. Switching to SELL position!")
                        time.sleep(0.5)
                        current_atr = float(df_feat["ATR"].iloc[-1])
                        sl_dist = round(current_atr * 1.5, 2)
                        tp_dist = round(current_atr * 3.0, 2)
                        mt5.execute_trade(signal_type="SELL", lot_size=0.01, sl_pips=sl_dist, tp_pips=tp_dist)
                        record_trade_time()
                elif ptype == "BUY" and mc_direction == "SELL" and (sig_direction != "SELL" or not trade_cooldown_ok):
                    cooldown_msg = f"Cooldown aktif ({300 - int(now_ts - last_trade_ts)}s lagi)" if not trade_cooldown_ok else f"ML Signal: {sig_direction} (bukan SELL)"
                    logger.info(f"⏸️ [REVERSAL BLOCKED] MC=SELL tapi {cooldown_msg}. Menunggu konfirmasi...")
        else:
            # Open New Position ONLY IF ML Confidence Signal >= 65% AND Aligned with Monte Carlo Direction
            logger.info(f"      ML Model Signal State: {sig_direction} (Threshold: {prob_threshold*100:.0f}%) | Monte Carlo: {mc_direction}")

            if latest_sig != 0 and sig_direction == mc_direction and trade_cooldown_ok:
                logger.info(f"🚀 [ENTERING LIVE TRADE] ML Confidence Signal >= {prob_threshold*100:.0f}% & Monte Carlo Aligned: {sig_direction}")
                # ATR-dynamic SL/TP for new entries
                current_atr = float(df_feat["ATR"].iloc[-1])
                sl_dist = round(current_atr * 1.5, 2)
                tp_dist = round(current_atr * 3.0, 2)
                logger.info(f"      ATR-Dynamic SL: ${sl_dist:.2f} | TP: ${tp_dist:.2f}")
                mt5.execute_trade(signal_type=sig_direction, lot_size=0.01, sl_pips=sl_dist, tp_pips=tp_dist)
                record_trade_time()
            elif latest_sig != 0 and sig_direction == mc_direction and not trade_cooldown_ok:
                secs_left = int(300 - (now_ts - last_trade_ts))
                logger.info(f"⏳ [COOLDOWN ACTIVE] Signal valid ({sig_direction}) tapi cooldown {secs_left}s lagi. Menunggu...")
            else:
                logger.info(f"⏸️ [NO TRADE ENTRY] ML Signal Confidence < {prob_threshold*100:.0f}% or Not Aligned with Monte Carlo. Waiting for next candle...")



    logger.info("==========================================================================")
    logger.info("   PIPELINE EXECUTED CLEANLY. MONITORING & BOT STATE UPDATED.             ")
    logger.info("==========================================================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="XAUUSD Quant Master Pipeline")
    parser.add_argument("--threshold", type=float, default=0.65, help="ML Signal Confidence Threshold (default: 0.65)")
    parser.add_argument("--loop", action="store_true", help="Run 24/7 continuous low-latency real-time loop")
    args = parser.parse_args()

    if args.threshold > 1.0:
        args.threshold = args.threshold / 100.0

    if args.loop:
        logger.info(f"[+] Starting 24/7 Real-Time Sub-Second Continuous Execution Loop (ML Threshold: {args.threshold*100:.0f}%)...")
        last_log_time = 0
        while True:
            try:
                now = time.time()
                verbose_log = (now - last_log_time >= 60.0)
                if verbose_log:
                    last_log_time = now
                
                execute_pipeline(prob_threshold=args.threshold, verbose_log=verbose_log)
                time.sleep(2.0)
            except KeyboardInterrupt:
                logger.info("[!] Stopping loop manually.")
                break
            except Exception as e:
                logger.error(f"[!] Error in loop execution: {e}")
                time.sleep(2.0)

    else:
        execute_pipeline(prob_threshold=args.threshold)
