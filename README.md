<div align="center">

  # ⚡ QuantOS Terminal & XAUUSD Auto-Trader

  **Institutional-Grade LightGBM AI & 10,000-Path Monte Carlo Stochastic Execution System for Gold (XAUUSD)**

  [![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
  [![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
  [![MetaTrader 5](https://img.shields.io/badge/Broker-MetaTrader_5-gold.svg)](https://www.metatrader5.com/)
  [![TradingView](https://img.shields.io/badge/Widgets-TradingView_Official_Dark-131722.svg)](https://www.tradingview.com/)
  [![0% Dummy Data](https://img.shields.io/badge/Data_Policy-100%25_Real_Data_Only-brightgreen.svg)]()

</div>

---

## 🌟 Executive Overview

**QuantOS** is an end-to-end, high-frequency quantitative trading terminal and automated execution engine tailored for Gold (**XAUUSD**). It combines:
1. **LightGBM 3-Class ML Classifier**: Online probability prediction (`BUY`, `SELL`, `NEUTRAL`) based on Wilder ATR swings, RSI, Bollinger Bands, and Volume Delta.
2. **10,000-Path Geometric Brownian Motion (GBM) Monte Carlo Simulator**: Pure empirical price path drift calculation with P10/P50/P90 targets.
3. **Harmonic Pattern Recognition Engine**: 8 PineScript v5-standard harmonic pattern specs (Gartley, Bat, Alt Bat, Butterfly, Crab, Deep Crab, Cypher, Shark) with vertex badges (`X, A, B, C, D`) and Fibonacci ratios.
4. **Smart Session Volatility Trailing Stop**: London/NY overlap session-aware breathing room engine (2.0x ATR buffer) with 50-pip continuous profit locking.
5. **TradingView Dark Dashboard**: React + Vite frontend powered by Lightweight Charts and official TradingView dark widgets.

---

## 📊 Core Architecture & Features

```
               ┌────────────────────────────────────────┐
               │    MetaTrader 5 Real-Time Tick Feed    │
               └───────────────────┬────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
       ┌────────────────────────┐    ┌────────────────────────┐
       │   LightGBM ML Engine   │    │  Monte Carlo (10K GBM) │
       │   (Probability > 60%)  │    │  (Stochastic Price P50)│
       └────────────┬───────────┘    └────────────┬───────────┘
                    │                             │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │    Dual-Confluence Filter     │
                   │  (Signal == MC Direction)     │
                   └───────────────┬───────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
       ┌────────────────────────┐    ┌────────────────────────┐
       │  Auto-Trader MT5 API   │    │  Telegram Bot Report   │
       │ (Smart Trailing Stop)  │    │  (/status & HD Chart)  │
       └────────────────────────┘    └────────────────────────┘
```

### 1. Zero Dummy Data Policy
- 100% of metrics, equity curves, position records, and candle charts are populated directly from live MT5 broker APIs.
- If data is unavailable, the UI renders an honest dark error state instead of synthetic filler.

### 2. Session-Aware Volatility Trailing Stop
- **London / New York Session (14:00 - 02:00 WIB)**: Applied **2.0x ATR** breathing room buffer to prevent premature stop-outs from session volatility.
- **50 Pips Fixed Breathing Space**:
  - At **50 pips (+$5.00)**: Locks in **+25 pips (+$2.50)**.
  - At **100 pips (+$10.00) onwards**: Trails SL exactly **50 pips ($5.00)** behind current market price for unlimited profit scaling ($20, $30, $40, $50+).

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10 or higher
- Node.js 18+ and npm
- MetaTrader 5 Terminal installed & logged into your broker (e.g. Exness, IC Markets)

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/HeinrichRaxwell/XAUUSD-Quant.git
cd XAUUSD-Quant

# Install Python dependencies
pip install -r requirements.txt

# Setup Environment Variables
cp .env.example .env
```

### 2. Launch FastAPI Backend Server

```bash
python -m uvicorn server:app --host 0.0.0.0 --port 8000
```

### 3. Launch React Dashboard Frontend

```bash
cd dashboard_frontend
npm install
npm run dev
```

Dashboard will be live at `http://localhost:5173`.

### 4. Run Automated Trading & Quant Loop

```bash
# Run with 60% confidence threshold in continuous loop
python run_all.py --threshold 0.60 --loop
```

---

## 📱 Telegram Bot Commands

- `/status` : Request live market status, active positions, ML confidence, and high-resolution TradingView-style chart report.
- `/balance`: Check real MT5 account balance, equity, and free margin.
- `/positions`: List active bot orders with floating PnL.
- `/closeall`: Close all open positions immediately.

---

## 📄 License & Disclaimer

Distributed under the **MIT License**. See `LICENSE` for details.

> **Risk Warning**: Quantitative trading on Gold (XAUUSD) carries significant financial risk due to market leverage. Past performance in backtesting or Monte Carlo simulations does not guarantee future results.
