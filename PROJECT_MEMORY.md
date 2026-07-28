# XAUUSD Quant & Machine Learning Trading System Memory

## Project Overview
- **Project Location**: `D:\vscode\XauQuantAnalyzer`
- **Asset**: XAUUSD (Gold / USD Spot) -> Broker Symbol: `XAUUSDm` (Exness)
- **Account Type**: Exness MT5 Trial Demo (`#433774184`)
- **Target Capital**: Micro Account ($50 - $70 USD)
- **Primary Model**: LightGBM Classifier (with Sklearn HistGradientBoosting fallback)
- **Risk Management**:
  - Lot Size: Fixed `0.01` micro-lot
  - Risk Per Trade: Max $4.00 - $6.00 Stop Loss (~8-10% of $60 balance)
  - Take Profit: 1:2 Risk-to-Reward ($8.00 - $12.00 TP target)
  - Break-Even: Stop Loss moves to Entry + Spread when profit reaches +$3.50
  - Single Position Limit: Only 1 active trade allowed for magic number `888111`
  - Equity Safety Halt: Auto-pause trading if equity drops below $35.00
- **Telegram Bot Integration**:
  - Bot Username: `@QuantXauAnalyzerBot`
  - Bot Token: `8999535099:AAF2rqk-ESRy4f3pmGdCmewtCiLh-yWGzFE`
  - User Chat ID: `1622957377` (User: AitchAre)


## Architecture Components
1. `xauusd_quant/data_loader.py`: Pulls 100% REAL broker market bars directly from MetaTrader 5 API (`XAUUSDm` feed).
2. `xauusd_quant/features.py`: Computes EMA Spread, RSI, ATR, Bollinger Band Width, Macro Momentum.
3. `xauusd_quant/ml_model.py`: LightGBM classifier with continuous online learning and weight persistence (`models/lightgbm_xauusd.pkl`).
4. `xauusd_quant/backtester.py`: Small-capital backtesting engine with realistic spread and slippage models.
5. `xauusd_quant/monte_carlo.py`: 2,000-run Trade Bootstrapping stress-test simulator.
6. `xauusd_quant/mt5_bridge.py`: Direct MT5 terminal connection with auto symbol detection (`XAUUSDm`), minimum stop level enforcement, and Magic Number filtering (`888111`).
7. `xauusd_quant/trailing_stop.py`: Break-Even & ATR Trailing Stop manager.
8. `xauusd_quant/telegram_notifier.py`: Real-time Telegram alert sender for `@QuantXauAnlyzerBot`.
9. `xauusd_quant/history_tracker.py`: Logs all trade events and account summaries to `output/trading_history.csv`.
10. `dashboard.py`: Streamlit / Web performance dashboard.
11. `run_all.py`: Unified Master Pipeline execution script.

## User Preferences & Rules
- Always save and recall all project context, architecture decisions, and settings from this memory file.
- All historical data MUST use 100% real broker price bars from MT5 (no dummy data fallback).
- Never place duplicate entries if a trade with magic number `888111` is already open.
