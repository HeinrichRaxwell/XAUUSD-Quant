<div align="center">

  # QuantOS Quantitative Execution System

  **Institutional-Grade LightGBM Machine Learning & 10,000-Path Stochastic Monte Carlo Framework for Gold (XAUUSD)**

  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
  [![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
  [![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
  [![React](https://img.shields.io/badge/Frontend-React_18-61DAFB.svg?logo=react&logoColor=black)](https://reactjs.org/)
  [![MetaTrader 5](https://img.shields.io/badge/Execution-MetaTrader_5-0052FF.svg)](https://www.metatrader5.com/)

</div>

---

## 🏛️ Executive Overview

**QuantOS** is an institutional quantitative trading terminal and automated trade execution system engineered specifically for spot Gold (**XAUUSD**). The system integrates supervised machine learning classification, stochastic Monte Carlo drift modeling, automated harmonic pattern identification, and dynamic session-aware risk management into a unified execution framework.

---

## ⚙️ Core Technical Modules

### 1. Machine Learning Signal Engine (LightGBM)
- **Classifier**: Multi-class LightGBM gradient boosting model configured for 3-class probability estimation (`BUY`, `SELL`, `NEUTRAL`).
- **Feature Space**: 40+ quantitative indicators including Wilder ATR swings, RSI momentum vectors, Bollinger Band percentile channels, Volume Delta, and macro yield differentials (DXY & US10Y correlations).
- **Confluence Thresholding**: Trades execute when directional confidence meets or exceeds configurable probability gates ($\ge 60\%$).

### 2. Stochastic Monte Carlo Drift Engine
- **Model**: Geometric Brownian Motion (GBM) running 10,000 empirical price path simulations per evaluation cycle.
- **Metrics**: Computes drift direction alongside non-parametric target boundaries ($P_{10}$, $P_{50}$, $P_{90}$) and Value-at-Risk ($VaR_{95}$) stress metrics.

### 3. Session-Aware Risk & Trailing Stop Engine
- **Session Liquidity Protection**: Dynamically expands volatility buffers ($2.0\times\text{ATR}$) during high-liquidity London/New York session overlaps (14:00 - 02:00 WIB) to mitigate market noise.
- **Continuous Scaling Ratchet**: 
  - **Tier 1 ($50\text{ pips}$ / $+\$5.00$)**: Locks $+\$2.50$ ($+25\text{ pips}$) profit buffer.
  - **Tier 2 ($100+\text{ pips}$ / $+\$10.00+$)**: Maintains a fixed $50\text{ pips}$ ($+\$5.00$) trailing buffer behind running price for continuous profit scaling.

### 4. Geometric Harmonic Pattern Recognition
- **Engine**: Automated detection for 8 PineScript v5-standard harmonic structures (Gartley, Bat, Alt Bat, Butterfly, Crab, Deep Crab, Cypher, Shark).
- **Geometry Matching**: Evaluates exact vertex ratios ($X, A, B, C, D$) across primary Fibonacci retracement levels ($0.618$, $0.786$, $0.886$, $1.618$).

---

## 📐 System Architecture

```
                               ┌───────────────────────────────────┐
                               │  MetaTrader 5 Real-Time Market    │
                               │      Tick & OHLC Data Feed        │
                               └─────────────────┬─────────────────┘
                                                 │
                        ┌────────────────────────┴────────────────────────┐
                        ▼                                                 ▼
          ┌───────────────────────────┐                     ┌───────────────────────────┐
          │  LightGBM Feature Engine  │                     │ Stochastic Monte Carlo    │
          │  (Wilder Swings, RSI, FVG)│                     │ (10,000 GBM Path Model)   │
          └─────────────┬─────────────┘                     └─────────────┬─────────────┘
                        │                                                 │
                        └────────────────────────┬────────────────────────┘
                                                 │
                                                 ▼
                                ┌───────────────────────────────────┐
                                │      Confluence Filter Gate       │
                                │   (Probability >= 60% & P50 Sync) │
                                └────────────────┬──────────────────┘
                                                 │
                        ┌────────────────────────┴────────────────────────┐
                        ▼                                                 ▼
          ┌───────────────────────────┐                     ┌───────────────────────────┐
          │    MT5 Auto-Execution     │                     │   Telegram Signal Daemon  │
          │  (Dynamic Trailing Stop)  │                     │   (/status & Chart Report)│
          └───────────────────────────┘                     └───────────────────────────┘
```

---

## 📁 Repository Structure

```
XAUUSD-Quant/
├── server.py                       # FastAPI Microservice Backend & REST API
├── run_all.py                      # Main Quant Execution & Monitoring Loop
├── mt5_live_runner.py              # MT5 Terminal Direct Interface
├── test_telegram.py                # Telemetry Verification Suite
├── requirements.txt                # Python Dependencies Specification
├── LICENSE                         # MIT License
├── .env.example                    # Environment Variables Blueprint
│
├── xauusd_quant/                   # Core Quantitative Library
│   ├── features.py                 # Feature Engineering Suite
│   ├── ml_model.py                 # LightGBM Model Architecture & Training
│   ├── monte_carlo.py              # Stochastic Monte Carlo Engine
│   ├── mt5_bridge.py               # Order Management & Trailing Stop Engine
│   ├── harmonic_quant_engine.py    # Harmonic Geometry Classifier
│   ├── chart_generator.py          # High-Resolution Signal Chart Renderer
│   └── telegram_notifier.py        # Telegram Notification Daemon
│
└── dashboard_frontend/             # Institutional React Web Dashboard
    ├── src/components/             # UI Components & TradingView Widgets
    └── vite.config.js              # Vite Build Configuration
```

---

## 🛠️ Installation & Setup

### Prerequisites
- **Python**: 3.10 or higher
- **Node.js**: 18.0 or higher
- **Broker**: MetaTrader 5 Terminal connected to a valid broker account

### 1. Environment Configuration

```bash
# Clone repository
git clone https://github.com/HeinrichRaxwell/XAUUSD-Quant.git
cd XAUUSD-Quant

# Install Python requirements
pip install -r requirements.txt

# Create environment configuration
cp .env.example .env
```

### 2. Launch Backend REST API

```bash
python -m uvicorn server:app --host 0.0.0.0 --port 8000
```

### 3. Launch Frontend Web Dashboard

```bash
cd dashboard_frontend
npm install
npm run dev
```

Dashboard interface accessible at `http://localhost:5173`.

### 4. Execute Continuous Quant Loop

```bash
python run_all.py --threshold 0.60 --loop
```

---

## 📱 Telegram Command Suite

- `/status` : Generates live Monte Carlo distribution, ML confidence score, and signal chart.
- `/balance`: Displays account balance, equity, margin utilization, and floating drawdown.
- `/positions`: Lists active orders with current PnL and Stop Loss thresholds.
- `/closeall`: Emergency order termination across all active positions.

---

## 📄 License & Disclaimer

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for complete terms.

> **Risk Disclaimer**: Trading financial instruments such as spot Gold (XAUUSD) involves substantial risk of capital loss. Empirical backtest performance and stochastic simulations do not guarantee future performance.
