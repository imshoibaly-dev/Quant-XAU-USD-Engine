# 🥇 XAUUSD Quant Lab

A professional-grade quantitative research and live trading platform for XAUUSD (Gold).  
Deploys in one click to **Streamlit Community Cloud** (free).

---

## What it does

| Layer | What's inside |
|---|---|
| **Data** | yfinance historical + live feed with parquet cache |
| **Features** | GARCH volatility, liquidity sweeps, stop hunts, SMC (BOS/CHoCH/OB/FVG), order flow, session model, market maker inventory, liquidity traps |
| **AI** | RandomForest signal model + KMeans regime classifier (TRENDING / RANGING / HIGH_VOL / MANIPULATION) |
| **Strategy** | Trend, Mean Reversion, Breakout, Liquidity Reversal — switched dynamically by regime |
| **Backtesting** | Vectorised backtester, walk-forward validation, Monte Carlo simulation |
| **Execution** | Telegram alerts for signals and regime changes |
| **Dashboard** | Streamlit + Plotly live dashboard |

---

## 🚀 Deploy to Streamlit Community Cloud (free)

### Step 1 — Push to GitHub

```bash
# From inside the xauusd_quant_lab/ folder:
git init
git add .
git commit -m "Initial commit — XAUUSD Quant Lab"

# Create a new repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/xauusd-quant-lab.git
git branch -M main
git push -u origin main
```

### Step 2 — Deploy on Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub
2. Click **"New app"**
3. Fill in:
   - **Repository:** `YOUR_USERNAME/xauusd-quant-lab`
   - **Branch:** `main`
   - **Main file path:** `app.py`  ← just `app.py`, NOT `dashboard/app.py`
4. Click **"Deploy"** — it will install dependencies and boot up automatically

### Step 3 — Add your API secrets (optional)

If you want Telegram alerts or news sentiment, add secrets **before** deploying:

1. In your Streamlit Cloud app page → click **"⋮" → Settings → Secrets**
2. Paste:

```toml
TELEGRAM_BOT_TOKEN = "your_bot_token"
TELEGRAM_CHAT_ID   = "your_chat_id"
NEWS_API_KEY       = "your_newsapi_key"
```

The app works fine without these — it just skips alerts and uses neutral sentiment.

---

## 🖥️ Run locally

```bash
# Install dependencies
pip install -r requirements.txt

# Launch dashboard
streamlit run app.py

# Full research pipeline (backtest + signal)
python runner/xauusd_quant_runner.py

# Backtest only
python runner/xauusd_quant_runner.py --mode backtest

# Quick live signal
python runner/xauusd_quant_runner.py --mode signal

# Live trading loop (hourly, sends Telegram alerts)
python runner/xauusd_quant_runner.py --mode live
```

---

## ⚙️ Configuration

All parameters are in `config.py`:

```python
RISK_PER_TRADE      = 0.01      # 1% risk per trade
ACCOUNT_SIZE        = 100_000   # USD
ATR_STOP_MULTIPLIER = 2.0       # Stop = 2× ATR from entry
ATR_TP_MULTIPLIER   = 3.0       # TP = 3× ATR (1:3 R/R)
GARCH_P, GARCH_Q    = 1, 1      # GARCH order
ML_N_ESTIMATORS     = 200       # RandomForest trees
WALK_FORWARD_FOLDS  = 5
MONTE_CARLO_SIMULATIONS = 1000
```

---

## 📁 Project structure

```
xauusd_quant_lab/
├── config.py
├── requirements.txt
├── .streamlit/
│   ├── config.toml        ← dark theme + server settings
│   └── secrets.toml       ← API keys (gitignored, add via Streamlit Cloud UI)
├── data/
│   ├── historical_loader.py
│   └── live_feed.py
├── features/              ← 14 feature modules
├── ai/                    ← ML signal model + regime AI + sentiment
├── strategy/              ← 4 strategies + regime switcher + master engine
├── backtesting/           ← backtester, performance, walk-forward, monte carlo
├── execution/             ← Telegram notifier
├── dashboard/
│   └── app.py             ← Streamlit entry point
└── runner/
    ├── live_trader.py
    └── xauusd_quant_runner.py
```

---

## ⚠️ Disclaimer

This is a **research and educational platform**. It is not financial advice.  
Past backtest performance does not guarantee future results.  
Always paper-trade before risking real capital.
