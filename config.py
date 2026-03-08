"""
config.py
---------
Central configuration for the XAUUSD Quant Lab.
All tuneable parameters, API keys, and model settings live here.
"""

import os

# ─── Streamlit Cloud secrets support ─────────────────────────────────────────
# When running on Streamlit Community Cloud, secrets are injected via
# st.secrets. We try to import them here so the rest of config just uses
# the same os.getenv() pattern regardless of environment.
try:
    import streamlit as st
    if hasattr(st, "secrets"):
        for _key in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "NEWS_API_KEY"):
            if _key in st.secrets and not os.getenv(_key):
                os.environ[_key] = st.secrets[_key]
except Exception:
    pass  # Not running in Streamlit context — skip silently

# ─── Data Settings ────────────────────────────────────────────────────────────
SYMBOL = "XAUUSD=X"
INTERVAL = "1h"
LOOKBACK_YEARS = 4
DATA_START = "2020-01-01"

# ─── Feature Engineering ──────────────────────────────────────────────────────
SMA_FAST = 20
SMA_SLOW = 50
SMA_TREND = 200
ATR_PERIOD = 14
RSI_PERIOD = 14
BOLLINGER_PERIOD = 20
BOLLINGER_STD = 2.0
VOLUME_PROFILE_BINS = 50
ORDERFLOW_WINDOW = 10
LIQUIDITY_SWEEP_LOOKBACK = 20
STOP_HUNT_LOOKBACK = 10
WICK_RATIO_THRESHOLD = 2.0
EQUAL_HL_TOLERANCE = 0.001       # 0.1% tolerance for equal highs/lows
ROUND_NUMBER_STEP = 10           # Gold rounds to $10
ROUND_NUMBER_TOLERANCE = 1.0     # $1 proximity to round level
SESSION_LOOKBACK = 100
TREND_EXHAUSTION_WINDOW = 5
LIQUIDITY_VOID_MIN_MOVE = 0.005  # 0.5% gap minimum

# ─── GARCH Model ──────────────────────────────────────────────────────────────
GARCH_P = 1
GARCH_Q = 1
GARCH_DIST = "normal"
GARCH_VOL_WINDOW = 500           # Rows used to fit GARCH

# ─── ML Signal Model ──────────────────────────────────────────────────────────
ML_N_ESTIMATORS = 200
ML_MAX_DEPTH = 6
ML_MIN_SAMPLES_LEAF = 20
ML_TRAIN_RATIO = 0.75
ML_RANDOM_STATE = 42
ML_FEATURES = [
    "sma20", "sma50", "rsi", "atr", "volatility",
    "flow", "buy_pressure", "sell_pressure",
    "upper_wick_ratio", "lower_wick_ratio",
    "bb_width", "returns", "momentum",
]

# ─── Regime Detection ─────────────────────────────────────────────────────────
REGIME_LABELS = ["RANGING", "TRENDING", "HIGH_VOL", "MANIPULATION"]
REGIME_VOL_HIGH_THRESHOLD = 0.015   # 1.5% hourly vol = high vol
REGIME_TREND_THRESHOLD = 0.6        # ADX-proxy threshold
REGIME_MANIPULATION_WICK = 3.0      # Wick ratio for manipulation candles

# ─── Strategy Parameters ──────────────────────────────────────────────────────
TREND_STRATEGY_FAST = 20
TREND_STRATEGY_SLOW = 50
TREND_STRATEGY_ATR_MULT = 2.0

MEAN_REV_BOLLINGER_PERIOD = 20
MEAN_REV_BOLLINGER_STD = 2.0
MEAN_REV_RSI_UPPER = 70
MEAN_REV_RSI_LOWER = 30

BREAKOUT_LOOKBACK = 20
BREAKOUT_ATR_FILTER = 1.5

LIQUIDITY_REVERSAL_WICK = 2.0
LIQUIDITY_REVERSAL_VOL_WINDOW = 20

# ─── Risk Management ──────────────────────────────────────────────────────────
ACCOUNT_SIZE = 100_000.0
RISK_PER_TRADE = 0.01              # 1% per trade
MAX_OPEN_TRADES = 3
MAX_DRAWDOWN_LIMIT = 0.10          # 10% max drawdown halt
ATR_STOP_MULTIPLIER = 2.0
ATR_TP_MULTIPLIER = 3.0
POSITION_SIZE_UNIT = 1.0           # Lots (adjust for broker)

# ─── Backtesting ──────────────────────────────────────────────────────────────
BACKTEST_COMMISSION = 0.0002       # 2 bps per trade
BACKTEST_SLIPPAGE = 0.0001         # 1 bp slippage
WALK_FORWARD_FOLDS = 5
MONTE_CARLO_SIMULATIONS = 1000
MONTE_CARLO_CONFIDENCE = 0.05

# ─── Telegram Alerts ──────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE")
TELEGRAM_ENABLED = TELEGRAM_BOT_TOKEN != "YOUR_BOT_TOKEN_HERE"

# ─── News API ─────────────────────────────────────────────────────────────────
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "YOUR_NEWS_API_KEY_HERE")
NEWS_LOOKBACK_HOURS = 12

# ─── Dashboard ────────────────────────────────────────────────────────────────
DASHBOARD_REFRESH_SECONDS = 60
DASHBOARD_CANDLES_DISPLAY = 200

# ─── Logging ──────────────────────────────────────────────────────────────────
LOG_LEVEL = "INFO"
LOG_FILE = "xauusd_quant.log"
