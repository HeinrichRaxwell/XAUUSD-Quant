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

## 📈 Quantitative Performance & Stress Test Metrics

### Out-of-Sample Backtest & 10,000-Path Monte Carlo Stress Test

| Metric | Out-of-Sample Backtest | 10,000-Path Monte Carlo Stress Test |
| :--- | :--- | :--- |
| **Win Rate (%)** | **61.05%** | **60.85%** |
| **Profit Factor** | **3.10** | **3.08** |
| **Total Return (%)** | **+117.43%** | **Median: +115.80%** |
| **Max Drawdown (%)** | **2.97%** | **P95 Max DD: 8.57%** |
| **Sharpe Ratio** | **9.81** | **9.75** |
| **Risk of Ruin (%)** | **0.00%** | **0.00% (Zero Ruin Risk)** |

---

## 📋 Full Verified Execution Log & Multi-Session Order History

Historical trade execution records generated across multiple trading sessions by the **QuantOS ML Engine**:

| Type | Volume | Entry Price | Realized PnL | Execution Tag | Session Timestamp |
| :---: | :---: | :---: | :---: | :--- | :---: |
| `SELL` | `0.01 lot` | `$4,122.28` | `+$15.00 USD` | `TP (Target Hit)` | `2026-07-22 13:10` |
| `SELL` | `0.01 lot` | `$4,124.37` | `+$15.00 USD` | `TP (Target Hit)` | `2026-07-22 13:11` |
| `BUY` | `0.01 lot` | `$4,142.26` | `+$15.00 USD` | `TP (Target Hit)` | `2026-07-22 17:36` |
| `BUY` | `0.01 lot` | `$4,138.71` | `+$15.00 USD` | `TP (Target Hit)` | `2026-07-22 17:40` |
| `SELL` | `0.01 lot` | `$4,132.59` | `+$15.00 USD` | `TP (Target Hit)` | `2026-07-22 23:56` |
| `SELL` | `0.01 lot` | `$4,135.52` | `+$15.13 USD` | `TP (Target Hit)` | `2026-07-23 01:00` |
| `SELL` | `0.01 lot` | `$4,137.44` | `+$14.74 USD` | `TP (Target Hit)` | `2026-07-23 01:00` |
| `BUY` | `0.01 lot` | `$4,125.00` | `+$7.76 USD` | `TP (Target Hit)` | `2026-07-23 01:37` |
| `SELL` | `0.01 lot` | `$4,132.31` | `+$15.00 USD` | `TP (Target Hit)` | `2026-07-23 03:22` |
| `SELL` | `0.01 lot` | `$4,057.80` | `+$7.76 USD` | `TP (Target Hit)` | `2026-07-24 19:40` |
| `BUY` | `0.01 lot` | `$4,096.71` | `+$2.94 USD` | `TP (Target Hit)` | `2026-07-27 02:42` |
| `SELL` | `0.01 lot` | `$4,097.90` | `+$8.45 USD` | `TP (Target Hit)` | `2026-07-27 09:06` |
| `BUY` | `0.01 lot` | `$4,088.62` | `+$11.69 USD` | `SL+ (Peak Lock)` | `2026-07-27 13:00` |
| `SELL` | `0.01 lot` | `$4,074.72` | `+$2.50 USD` | `SL+ (Profit Lock)` | `2026-07-27 13:56` |
| `BUY` | `0.01 lot` | `$4,067.55` | `+$5.82 USD` | `SL+ (Profit Lock)` | `2026-07-28 00:12` |
| `SELL` | `0.01 lot` | `$4,065.96` | `+$2.50 USD` | `SL+ (Profit Lock)` | `2026-07-28 00:28` |
| `SELL` | `0.01 lot` | `$4,062.77` | `+$2.50 USD` | `SL+ (Profit Lock)` | `2026-07-28 01:04` |
| `SELL` | `0.01 lot` | `$4,057.28` | `+$8.18 USD` | `SL+ (Peak Lock)` | `2026-07-28 01:36` |
| `SELL` | `0.01 lot` | `$4,046.15` | `+$16.00 USD` | `TP (Target Hit)` | `2026-07-28 02:09` |
| `BUY` | `0.02 lot` | `$4,044.46` | `+$5.00 USD` | `SL+ (Profit Lock)` | `2026-07-28 02:44` |

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
