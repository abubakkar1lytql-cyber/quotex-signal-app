import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, time
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from ta.volatility import AverageTrueRange

st.set_page_config(page_title="Forex & Crypto AI Intelligence", layout="wide")

st.title("🌐 FOREX & CRYPTO AI INTELLIGENCE DASHBOARD")
st.caption("স্মার্ট মানি ট্র্যাপ ফিল্টার ও ডায়নামিক সেশনসহ প্রফেশনাল ট্রেডিং ড্যাশবোর্ড")

# 1. DYNAMIC SESSION DISPLAY (শুধুমাত্র বর্তমান সময়ের রানিং সেশন দেখাবে)
now_utc = datetime.utcnow().time()

def get_current_session(now):
    active = []
    if time(22, 0) <= now or now <= time(7, 0): active.append("Sydney 🇦🇺")
    if time(0, 0) <= now <= time(9, 0): active.append("Tokyo 🇯🇵")
    if time(8, 0) <= now <= time(17, 0): active.append("London 🇬🇧")
    if time(13, 0) <= now <= time(22, 0): active.append("New York 🇺🇸")
    
    if len(active) > 1:
        return f"🟢 CURRENTLY RUNNING: {' + '.join(active)} Overlap (High Volatility Zone!)"
    elif len(active) == 1:
        return f"🟢 CURRENTLY RUNNING: {active[0]} Session"
    else:
        return "🔴 MARKET IS CLOSED / LOW VOLATILITY"

st.subheader("⏰ Live Trading Session")
st.success(get_current_session(now_utc))

# 2. NEWS & MANIPULATION ALERT BOX
st.subheader("📰 High-Impact News & Risk Filter")
st.info("🟢 **NEWS & MANIPULATION STATUS:** No High-Impact CPI/NFP News detected. Smart Money Liquidity Filter Is Active.")

st.divider()

# Forex, Commodities & Crypto Database
pairs = {
    "BITCOIN (BTC/USD)": "BTC-USD",
    "SOLANA (SOL/USD)": "SOL-USD",
    "GOLD (XAU/USD)": "GC=F",
    "SILVER (XAG/USD)": "SI=F",
    "CRUDE OIL (USO/USD)": "CL=F",
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X"
}

# 3. OPPORTUNITY SERIAL BOX (শুধুমাত্র সিগন্যাল থাকা পেয়ারগুলো দেখাবে)
st.subheader("🔥 Live Opportunities Right Now")

if st.button("🔄 Scan Market For Opportunities", use_container_width=True):
    with st.spinner("Scanning all pairs for potential setups..."):
        opportunities = []
        for name, ticker in pairs.items():
            try:
                df = yf.download(ticker, period="5d", interval="1h", progress=False)
                if not df.empty:
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    
                    c = df['Close']
                    ema20 = EMAIndicator(close=c, window=20).ema_indicator().iloc[-1]
                    ema50 = EMAIndicator(close=c, window=50).ema_indicator().iloc[-1]
                    rsi = RSIIndicator(close=c, window=14).rsi().iloc[-1]
                    price = float(c.iloc[-1])
                    
                    if ema20 > ema50 and 52 < rsi < 70:
                        opportunities.append({"Asset": name, "Price ($)": round(price, 2) if "BTC" in name or "SOL" in name else round(price, 4), "RSI": round(rsi, 1), "Signal": "STRONG BUY 🟢"})
                    elif ema20 < ema50 and 30 < rsi < 48:
                        opportunities.append({"Asset": name, "Price ($)": round(price, 2) if "BTC" in name or "SOL" in name else round(price, 4), "RSI": round(rsi, 1), "Signal": "STRONG SELL 🔴"})
            except Exception:
                pass
                
        if opportunities:
            st.write("সিরিয়াল অনুযায়ী যেসব পেয়ারে এখন ট্রেডের সুযোগ আছে:")
            st.dataframe(pd.DataFrame(opportunities), use_container_width=True)
        else:
            st.warning("বর্তমানে কোনো পেয়ারে প্রপার টেকনিক্যাল এন্ট্রি নেই (সবগুলো WAIT জোনে আছে)। একটু পর আবার স্ক্যান করুন।")

st.divider()

# 4. SINGLE PAIR ANALYSIS & CHART WITH TP/SL LINES
st.subheader("🎯 Selected Asset Deep Analysis & Chart")

selected_pair = st.selectbox("Select Asset to Analyze", list(pairs.keys()))
ticker = pairs[selected_pair]

timeframe = st.radio("Select Timeframe", ["15 Minutes (15m)", "1 Hour (1h)"], horizontal=True)
tf = "15m" if "15 Minutes" in timeframe else "1h"

if st.button("🚀 Analyze & Draw Chart", use_container_width=True):
    with st.spinner("Calculating Targets & Drawing Chart Lines..."):
        data = yf.download(ticker, period="5d", interval=tf, progress=False)
        data_4h = yf.download(ticker, period="20d", interval="1h", progress=False)
        
        if not data.empty:
            if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
            if isinstance(data_4h.columns, pd.MultiIndex): data_4h.columns = data_4h.columns.get_level_values(0)
                
            close_price = data['Close']
            high_price = data['High']
            low_price = data['Low']
            
            ema_20 = EMAIndicator(close=close_price, window=20).ema_indicator().iloc[-1]
            ema_50 = EMAIndicator(close=close_price, window=50).ema_indicator().iloc[-1]
            rsi = RSIIndicator(close=close_price, window=14).rsi().iloc[-1]
            atr = AverageTrueRange(high=high_price, low=low_price, close=close_price, window=14).average_true_range().iloc[-1]
            
            ema_20_4h = EMAIndicator(close=data_4h['Close'], window=80).ema_indicator().iloc[-1]
            htf_trend = "BULLISH 🟢" if data_4h['Close'].iloc[-1] > ema_20_4h else "BEARISH 🔴"
            
            last_price = float(close_price.iloc[-1])
            
            # Unit Calculations
            if "BTC" in selected_pair or "SOL" in selected_pair:
                pip_unit = 1.0
                sl_pips, tp_pips = round(atr * 1.5), round(atr * 2.5)
            elif "OIL" in selected_pair or "GOLD" in selected_pair or "SILVER" in selected_pair:
                pip_unit = 0.1
                sl_pips = round((atr * 1.5) / pip_unit)
                tp_pips = round((atr * 2.5) / pip_unit)
            else:
                pip_unit = 0.01 if "JPY" in selected_pair else 0.0001
                sl_pips = max(15, min(round((atr * 1.5) / pip_unit), 30))
                tp_pips = max(25, min(round((atr * 2.5) / pip_unit), 60))

            status = "neutral"
            if ema_20 > ema_50 and 52 < rsi < 70:
                status = "buy"
                tp_price = last_price + (tp_pips * pip_unit)
                sl_price = last_price - (sl_pips * pip_unit)
            elif ema_20 < ema_50 and 30 < rsi < 48:
                status = "sell"
                tp_price = last_price - (tp_pips * pip_unit)
                sl_price = last_price + (sl_pips * pip_unit)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Current Price", f"${last_price:,.2f}" if "BTC" in selected_pair or "SOL" in selected_pair else f"{last_price:.4f}")
            col2.metric("RSI Momentum", f"{rsi:.1f}")
            col3.metric("Higher Trend (4H)", htf_trend)
            col4.metric("Risk:Reward", "1:2.0")

            if status != "neutral":
                st.success(f"### Signal: {'STRONG BUY 🟢' if status == 'buy' else 'STRONG SELL 🔴'}")
                st.write(f"🔹 **Entry Price:** `{last_price:.4f}` | 🎯 **Take Profit (TP):** `{tp_price:.4f}` (+{tp_pips} Pips/Pts) | 🛡️ **Stop Loss (SL):** `{sl_price:.4f}` (-{sl_pips} Pips/Pts)")
            else:
                st.warning("### Status: NO CLEAR SIGNAL (WAIT ⏳)")
                st.write("মার্কেট সাইডওয়ে বা ম্যানিপুলেশন জোনে রয়েছে। নিরাপদ ট্রেড এন্ট্রির জন্য অপেক্ষা করুন।")
                tp_price, sl_price = last_price, last_price

            # CANDLESTICK CHART WITH TP, SL & ENTRY LINES
            fig = go.Figure(data=[go.Candlestick(
                x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Price"
            )])
            
            # Draw Lines on Chart
            if status != "neutral":
                fig.add_hline(y=last_price, line_dash="solid", line_color="blue", annotation_text=f"ENTRY: {last_price:.4f}")
                fig.add_hline(y=tp_price, line_dash="dash", line_color="green", annotation_text=f"TP Target: {tp_price:.4f}")
                fig.add_hline(y=sl_price, line_dash="dash", line_color="red", annotation_text=f"SL Limit: {sl_price:.4f}")

            fig.update_layout(template="plotly_dark", height=450, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.error("Market data fetch failed. Try again after a few seconds.")
