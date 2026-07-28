# 🧠 XAUQUANT AGENT MEMORY — Persistent System & Context State File
# Dibuat: 2026-07-27 14:26 WIB
# Tujuan: Agent AI/Developer manapun dapat melanjutkan project ini tanpa kehilangan konteks.

---

## 🎯 Identitas & Environment Sistem

| Parameter | Nilai / Konfirmasi |
|-----------|-------------------|
| **Project Root Path** | `D:/vscode/XauQuantAnalyzer/` |
| **Active 24/7 Loop Task** | `task-1004` (`python run_all.py --threshold 0.65 --loop`) |
| **Active FastAPI Backend** | `task-1287` (`python -m uvicorn server:app --host 0.0.0.0 --port 8000`) |
| **Active React Web Dashboard**| `task-1134` (`http://localhost:5173`) |
| **MT5 Account** | `#433774184` — Server: `Exness-MT5Trial7` (Trial Account) |
| **Symbol** | `XAUUSDm` (Gold USD Micro Exness) |
| **Current Account State** | Balance: **$75.12 USD** \| Equity: **$75.12 USD** (0 active trades) |
| **Telegram Bot Token** | `8999535099:AAF2rqk-ESRy4f3pmGdCmewtCiLh-yWGzFE` |
| **Telegram Chat ID** | `1622957377` |
| **ML Threshold** | `65%` (0.65) confidence minimum untuk entry |
| **Magic Number MT5** | `888111` |

---

## 💻 100% MATCH TARGET SCREENSHOT 141036 DESIGN

```
URL Frontend : http://localhost:5173
URL API      : http://localhost:8000
```

### Complete Visual Features (100% Identical to Target Screenshot 141036):
1. **Harmonic XABCD Overlay Lines & Labels**: Line zigzag warna Amber dengan circular badges `X`, `A`, `B`, `C`, `D`, line diagonal Fibonacci biru putus-putus, serta teks rasio Fibonacci presisi (`2.708`, `1.697`, `0.321`, `PRZ ABCD STRUCTURE`).
2. **Demand / Supply Zone Shaded Box**: Box shaded biru/amber transparan (`DEMAND ZONE` / `SUPPLY ZONE`).
3. **Monte Carlo P50 Projection Curve**: Kurva garis putus-putus kuning memproyeksikan estimasi jalur harga P50.
4. **Risk / Reward Shaded Profit/Loss Boxes**: Box transparan hijau (Profit Area) & merah (Stop Loss Area) yang memanjang ke candle masa depan.
5. **Right Price Scale Level Badges**: Badges warna-warni presisi (`PRZ TP1`, `PRZ TP2`, `PRZ TP3`, `Monte`, `TP`, `Entry`, `SL`).
6. **Zoom-In Inspection Modal**: Fitur perbesar tampilan gambar (High-DPI 150 DPI) saat mengklik chart.

---

## 🔄 Cara Menjalankan Layanan (Services Command)

```powershell
# 1. 24/7 Quant Loop Engine
python run_all.py --threshold 0.65 --loop

# 2. FastAPI Backend Service (Port 8000)
python -m uvicorn server:app --host 0.0.0.0 --port 8000

# 3. React Frontend Dev Server (Port 5173)
cd dashboard_frontend
npm run dev -- --host 0.0.0.0
```
