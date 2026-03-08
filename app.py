"""
app.py — Streamlit Community Cloud entry point
Main file path: app.py
"""
import sys, os, importlib.util
from pathlib import Path

# Absolute path to repo root — always correct on Streamlit Cloud
ROOT = Path(__file__).resolve().parent

# Insert into sys.path right now (main process)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import logging
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
import config

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="XAUUSD Quant Lab",
    page_icon="🥇",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .signal-buy  { color: #00ff88; font-size: 24px; font-weight: bold; }
    .signal-sell { color: #ff4444; font-size: 24px; font-weight: bold; }
    .signal-hold { color: #aaaaaa; font-size: 24px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


# ─── The ONE function that fixes everything ───────────────────────────────────
# st.cache_data serialises/deserialises the function and runs it in a worker.
# That worker does NOT inherit sys.path from the main process.
# Solution: derive ROOT from __file__ (always an absolute path) inside the
# function itself, and re-insert before any local import.
def _ensure_root_on_path():
    _r = str(Path(__file__).resolve().parent)
    if _r not in sys.path:
        sys.path.insert(0, _r)


@st.cache_data(ttl=config.DASHBOARD_REFRESH_SECONDS, show_spinner=False)
def load_and_process_data():
    _ensure_root_on_path()   # ← called first, before any local import

    from data.historical_loader import load_data
    from features.indicators import build_features
    from features.garch_model import compute_volatility
    from features.liquidity_sweep import detect_sweeps
    from features.stop_hunt import detect_stop_hunts
    from features.smart_money import detect_smart_money
    from features.volatility_regime import classify_volatility_regime, volatility_spike
    from features.market_maker_inventory import estimate_mm_inventory
    from features.liquidity_map import build_liquidity_map
    from features.liquidity_trap import build_full_trap_features
    from features.liquidity_heatmap import liquidity_levels, top_liquidity_levels
    from features.session_model import add_session_features
    from features.trend_exhaustion import detect_trend_exhaustion

    df = load_data(use_cache=True).tail(config.DASHBOARD_CANDLES_DISPLAY * 5)
    df = build_features(df)

    try:
        df = compute_volatility(df)
    except Exception:
        df["volatility"] = df["returns"].rolling(20).std() * 100
        df["vol_regime"] = "NORMAL"

    df = detect_sweeps(df)
    df = detect_stop_hunts(df)
    df = detect_smart_money(df)
    df = classify_volatility_regime(df)
    df = volatility_spike(df)
    df = estimate_mm_inventory(df)
    df = build_liquidity_map(df)
    df = detect_trend_exhaustion(df)
    df = add_session_features(df)

    liq_levels = top_liquidity_levels(df, top_n=20)
    df = build_full_trap_features(df, liq_levels)
    density = liquidity_levels(df)
    return df, density, liq_levels


@st.cache_data(ttl=300, show_spinner=False)
def get_regime_and_signal(df_tail):
    _ensure_root_on_path()   # ← called first

    from ai.market_regime_ai import train_regime_model, classify_regime
    from ai.ml_signal_model import train_model, predict_signal
    from strategy.master_engine import generate_master_signal

    try:
        regime_pipe = train_regime_model(df_tail)
        df_reg = classify_regime(df_tail, regime_pipe)
        regime = df_reg["regime"].iloc[-1]
    except Exception:
        regime = "RANGING"

    try:
        ml_pipe = train_model(df_tail)
        ml_result = predict_signal(df_tail, ml_pipe)
        ml_signal = ml_result["signal"]
    except Exception:
        ml_signal = "HOLD"

    signal = generate_master_signal(df_tail, regime=regime, ml_signal=ml_signal)
    return regime, ml_signal, signal


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ XAUUSD Quant Lab")
    st.markdown("---")
    n_candles    = st.slider("Chart candles", 50, 500, config.DASHBOARD_CANDLES_DISPLAY)
    show_sma     = st.checkbox("Show SMAs", value=True)
    show_bb      = st.checkbox("Show Bollinger Bands", value=False)
    show_traps   = st.checkbox("Show Liquidity Traps", value=True)
    show_sweeps  = st.checkbox("Show Sweeps / Stop Hunts", value=True)
    show_liq     = st.checkbox("Show Liquidity Levels", value=True)
    auto_refresh = st.checkbox("Auto-refresh (60s)", value=False)
    st.markdown("---")
    st.caption("Data: Yahoo Finance (delayed)")

if auto_refresh:
    st.rerun()

# ── Main ──────────────────────────────────────────────────────────────────────
st.title("🥇 XAUUSD Quant Research Dashboard")

with st.spinner("📥 Loading & processing XAUUSD data…"):
    try:
        df_full, density, liq_levels = load_and_process_data()
    except Exception as e:
        st.error(f"❌ Data load failed: {e}")
        st.exception(e)
        st.stop()

df = df_full.tail(n_candles).copy()

with st.spinner("🤖 Computing regime & signals…"):
    try:
        regime, ml_signal, signal_result = get_regime_and_signal(df_full.tail(500))
    except Exception as e:
        regime = "RANGING"
        ml_signal = "HOLD"
        signal_result = {"signal": "HOLD", "source": "ERROR", "confidence": 0.0,
                         "regime": regime, "timestamp": "", "details": {}}

# ── KPIs ──────────────────────────────────────────────────────────────────────
latest     = df.iloc[-1]
price      = latest["close"]
prev_price = df.iloc[-2]["close"] if len(df) > 1 else price
price_chg  = price - prev_price
price_pct  = (price_chg / prev_price) * 100

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("XAUUSD",       f"${price:,.2f}",  f"{price_chg:+.2f} ({price_pct:+.2f}%)")
c2.metric("Signal",       signal_result["signal"], signal_result.get("source", ""))
c3.metric("Regime",       regime)
c4.metric("GARCH Vol",    f"{latest.get('volatility', 0):.3f}%")
c5.metric("Vol Regime",   latest.get("vol_regime", "NORMAL"))
c6.metric("MM Inventory", latest.get("mm_inventory", "NEUTRAL"))

st.markdown("---")

# ── Price chart ───────────────────────────────────────────────────────────────
fig = make_subplots(
    rows=3, cols=1, row_heights=[0.6, 0.2, 0.2],
    shared_xaxes=True,
    subplot_titles=("XAUUSD Price", "RSI", "Order Flow"),
    vertical_spacing=0.05,
)
fig.add_trace(go.Candlestick(
    x=df.index, open=df["open"], high=df["high"], low=df["low"], close=df["close"],
    name="XAUUSD", increasing_line_color="#00c853", decreasing_line_color="#d32f2f",
), row=1, col=1)

if show_sma:
    for col_name, colour, label in [
        ("sma20","#2196F3","SMA20"),("sma50","#FF9800","SMA50"),("sma200","#9C27B0","SMA200")
    ]:
        if col_name in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[col_name],
                line=dict(color=colour, width=1), name=label, opacity=0.8), row=1, col=1)

if show_bb and "bb_upper" in df.columns:
    fig.add_trace(go.Scatter(x=df.index, y=df["bb_upper"],
        line=dict(color="rgba(128,128,128,0.5)", dash="dot"),
        name="BB Upper", showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["bb_lower"],
        line=dict(color="rgba(128,128,128,0.5)", dash="dot"),
        name="BB Lower", fill="tonexty",
        fillcolor="rgba(128,128,128,0.05)", showlegend=False), row=1, col=1)

if show_liq and len(liq_levels) > 0:
    for level in liq_levels:
        fig.add_hline(y=float(level), line_dash="dot",
            line_color="rgba(255,200,0,0.4)", line_width=1, row=1, col=1)

if show_traps and "trap_buy" in df.columns:
    buy_traps  = df[df["trap_buy"]  == True]
    sell_traps = df[df["trap_sell"] == True]
    if len(buy_traps):
        fig.add_trace(go.Scatter(x=buy_traps.index, y=buy_traps["low"] * 0.9995,
            mode="markers", marker=dict(symbol="triangle-up", size=10, color="#00c853"),
            name="Buy Trap"), row=1, col=1)
    if len(sell_traps):
        fig.add_trace(go.Scatter(x=sell_traps.index, y=sell_traps["high"] * 1.0005,
            mode="markers", marker=dict(symbol="triangle-down", size=10, color="#d32f2f"),
            name="Sell Trap"), row=1, col=1)

if show_sweeps and "sweep_low" in df.columns:
    mask = df["sweep_low"] | df["sweep_high"].fillna(False)
    sweeps = df[mask]
    if len(sweeps):
        fig.add_trace(go.Scatter(x=sweeps.index, y=sweeps["close"],
            mode="markers", marker=dict(symbol="x", size=8, color="#FF9800"),
            name="Sweep"), row=1, col=1)

if "rsi" in df.columns:
    fig.add_trace(go.Scatter(x=df.index, y=df["rsi"],
        line=dict(color="#2196F3", width=1.5), name="RSI"), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red",   opacity=0.5, row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)
    fig.add_hline(y=50, line_dash="dot",  line_color="gray",  opacity=0.3, row=2, col=1)

if "flow" in df.columns:
    flow = df["flow"]
    fig.add_trace(go.Bar(
        x=df.index, y=flow,
        marker_color=["#00c853" if v > 0 else "#d32f2f" for v in flow],
        name="Flow",
    ), row=3, col=1)

fig.update_layout(height=700, template="plotly_dark", showlegend=True,
    legend=dict(orientation="h", x=0, y=1.02),
    xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=40, b=0))
fig.update_yaxes(row=2, range=[0, 100])
st.plotly_chart(fig, use_container_width=True)

# ── Heatmap + Vol ─────────────────────────────────────────────────────────────
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("📊 Liquidity Heatmap")
    if not density.empty:
        liq_fig = px.bar(density, x="liquidity_density", y="price", orientation="h",
                         color="liquidity_density", color_continuous_scale="Viridis",
                         title="Volume Profile")
        liq_fig.add_hline(y=float(df["close"].iloc[-1]),
                          line_color="yellow", line_width=2, opacity=0.8)
        liq_fig.update_layout(template="plotly_dark", height=400, showlegend=False)
        st.plotly_chart(liq_fig, use_container_width=True)

with col_b:
    st.subheader("⚡ Volatility Regime")
    if "volatility" in df.columns:
        vol_fig = go.Figure()
        vol_fig.add_trace(go.Scatter(x=df.index, y=df["volatility"],
            fill="tozeroy", fillcolor="rgba(255,152,0,0.2)",
            line=dict(color="#FF9800", width=1.5), name="GARCH Vol"))
        vol_fig.update_layout(template="plotly_dark", height=400,
            yaxis_title="Volatility (%)", legend=dict(orientation="h"))
        st.plotly_chart(vol_fig, use_container_width=True)

# ── Signal breakdown ──────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🎯 Latest Signal Analysis")
s1, s2, s3 = st.columns(3)
with s1:
    st.markdown("**Master Signal**")
    sig_val   = signal_result["signal"]
    sig_color = {"BUY": "#00c853", "SELL": "#d32f2f", "HOLD": "#aaaaaa"}[sig_val]
    st.markdown(f"<div style='font-size:28px;color:{sig_color};font-weight:bold'>{sig_val}</div>",
                unsafe_allow_html=True)
    st.caption(f"Source: {signal_result.get('source','N/A')}")
    st.caption(f"Confidence: {signal_result.get('confidence',0):.0%}")
with s2:
    st.markdown("**Latest Bar**")
    for k, v in {
        "RSI":          f"{latest.get('rsi', 0):.1f}",
        "ATR":          f"${latest.get('atr', 0):.2f}",
        "Vol Spike":    "YES" if latest.get("vol_spike") else "NO",
        "Sweep":        "YES" if latest.get("sweep_high") or latest.get("sweep_low") else "NO",
        "Trap":         "BUY" if latest.get("trap_buy") else ("SELL" if latest.get("trap_sell") else "NONE"),
        "Killzone":     "YES" if latest.get("in_killzone") else "NO",
        "MM Inventory": latest.get("mm_inventory", "NEUTRAL"),
    }.items():
        st.text(f"{k}: {v}")
with s3:
    st.markdown("**AI / Regime**")
    st.text(f"Regime:   {regime}")
    st.text(f"ML:       {ml_signal}")
    st.text(f"BOS Bull: {'YES' if latest.get('bos_bullish') else 'NO'}")
    st.text(f"BOS Bear: {'YES' if latest.get('bos_bearish') else 'NO'}")
    st.text(f"Session:  {latest.get('session','UNKNOWN')}")

# ── Recent bars ───────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📋 Recent Bars")
show_cols = [c for c in ["open","high","low","close","rsi","volatility",
                          "vol_regime","session","trap_buy","trap_sell",
                          "sweep_high","sweep_low"] if c in df.columns]
st.dataframe(df[show_cols].tail(20).round(3), use_container_width=True)
st.caption(f"Last bar: {df.index[-1]} | Total bars: {len(df_full)}")
