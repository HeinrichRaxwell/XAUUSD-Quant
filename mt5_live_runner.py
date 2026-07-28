import time
import argparse
import logging
import pandas as pd
import numpy as np
from datetime import datetime

from xauusd_quant.data_loader import XauDataLoader
from xauusd_quant.features import FeatureEngineer
from xauusd_quant.ml_model import XauMLModel
from xauusd_quant.mt5_bridge import MT5Bridge

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def run_live_trader(symbol: str = "XAUUSD", prob_threshold: float = 0.55, risk_pct: float = 0.01):
    logger.info("===============================================================")
    logger.info("      STARTING XAUUSD ML AUTO-TRADING ENGINE FOR MT5 DEMO      ")
    logger.info("===============================================================")

    # 1. Connect MT5 Bridge
    bridge = MT5Bridge(symbol=symbol)
    acc_info = bridge.get_account_summary()
    logger.info(f"Account Balance: ${acc_info['Balance']:,.2f} | Mode: {acc_info['Mode']}")

    # 2. Ingest Data & Train ML Model
    logger.info("Ingesting market data & training LightGBM Signal Model...")
    loader = XauDataLoader(start_date="2021-01-01")
    raw_df = loader.fetch_data(symbol="GC=F")

    fe = FeatureEngineer()
    df_features = fe.add_features(raw_df)

    ml_model = XauMLModel(forward_bars=5, prob_threshold=prob_threshold)
    X, y = ml_model.prepare_data(df_features)
    train_stats = ml_model.train(X, y)
    logger.info(f"ML Model Trained. Test Accuracy: {train_stats['Test_Accuracy']*100:.2f}%")

    # Display Feature Importance
    fi_df = ml_model.get_feature_importances()
    logger.info(f"Top Features:\n{fi_df.to_string(index=False)}")

    # 3. Generate Latest Signal
    latest_df = df_features.tail(50).copy()
    signals = ml_model.predict_signals(latest_df)
    latest_signal = signals.iloc[-1]
    latest_bar = latest_df.iloc[-1]
    current_close = latest_bar["Close"]
    current_atr = latest_bar["ATR"]

    logger.info(f"Latest Market Price: ${current_close:,.2f} | Current ATR: ${current_atr:.2f}")

    if latest_signal == 1:
        signal_type = "BUY"
    elif latest_signal == -1:
        signal_type = "SELL"
    else:
        signal_type = "HOLD"

    logger.info(f"[ML Prediction Result] Current Signal: >>> {signal_type} <<<")

    # 4. Execute Order on MT5 Demo Account if Signal Active
    if signal_type in ["BUY", "SELL"]:
        balance = acc_info["Balance"]
        risk_amount = balance * risk_pct
        sl_dist = max(current_atr * 1.5, 2.0)
        tp_dist = max(current_atr * 3.0, 4.0)

        if signal_type == "BUY":
            sl_price = current_close - sl_dist
            tp_price = current_close + tp_dist
        else:
            sl_price = current_close + sl_dist
            tp_price = current_close - tp_dist

        # Position Sizing: Lot = (Risk Amount) / (SL Distance * 100) for Gold
        lot_size = round(risk_amount / (sl_dist * 100), 2)
        lot_size = max(0.01, min(lot_size, 5.0))  # Risk bounds

        logger.info(f"Executing {signal_type} Order | Size: {lot_size} lots | SL: ${sl_price:.2f} | TP: ${tp_price:.2f}")
        order_res = bridge.execute_market_order(
            order_type=signal_type,
            volume=lot_size,
            sl_price=sl_price,
            tp_price=tp_price
        )
        logger.info(f"Order Result: {order_res}")
    else:
        logger.info("No high-confidence trade signal generated. Remaining in HOLD state.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MT5 XAUUSD ML Auto Trader")
    parser.add_argument("--symbol", type=str, default="XAUUSD", help="MT5 Symbol (default: XAUUSD)")
    parser.add_argument("--threshold", type=float, default=0.55, help="Probability threshold for ML signal")
    args = parser.parse_args()

    run_live_trader(symbol=args.symbol, prob_threshold=args.threshold)
