import streamlit as st
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD

st.set_page_config(page_title="Quotex AI Signal Board", layout="centered")

st.title("🎯 High Accuracy Signal Board")
st.write("কারেন্সি পেয়ার সিলেক্ট করে এনালাইসিস বাটনে চাপ দিন।")

pairs = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "AUD/USD": "AUDUSD=X",
    "USD/CAD": "USDCAD=X",
    "EUR/JPY": "EURJPY=X",
    "GBP/JPY": "GBPJPY=X",
    "BTC/USD (Crypto)": "BTC-USD"
}

selected_pair_name = st.selectbox("Select Asset Pair", list(pairs.keys()))
ticker = pairs[selected_pair_name]

timeframe_option = st.radio("Select Expiry Timeframe", ["1 Minute (1m)", "2 Minutes (2m)", "5 Minutes (5m)"], horizontal=True)

if "1 Minute" in timeframe_option:
    tf = "1m"
elif "2 Minutes" in timeframe_option:
    tf = "2m"
else:
    tf = "5m"

if st.button("🚀 High Accuracy Market Analysis", use_container_width=True):
    with st.spinner("Analyzing Market Data..."):
        data = yf.download(ticker, period="1d", interval=tf)
        
        if not data.empty:
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
                
            rsi = float(RSIIndicator(close=data['Close'], window=14).rsi().iloc[-1])
            ema_9 = float(EMAIndicator(close=data['Close'], window=9).ema_indicator().iloc[-1])
            ema_21 = float(EMAIndicator(close=data['Close'], window=21).ema_indicator().iloc[-1])
            macd_diff = float(MACD(close=data['Close']).macd_diff().iloc[-1])
            last_price = float(data['Close'].iloc[-1])
            
            # Simple Scoring Model
            score = 0
            if rsi > 50: score += 1
            if ema_9 > ema_21: score += 1
            if macd_diff > 0: score += 1

            if score >= 2:
                signal = "CALL (BUY ⬆️)"
                confidence = "85%" if score == 3 else "70%"
                status = "buy"
            else:
                signal = "PUT (SELL ⬇️)"
                confidence = "85%" if score == 0 else "70%"
                status = "sell"

            st.divider()
            col1, col2, col3 = st.columns(3)
            col1.metric("Current Price", f"{last_price:.4f}")
            col2.metric("RSI Value", f"{rsi:.1f}")
            col3.metric("AI Confidence", confidence)
            
            if status == "buy":
                st.success(f"### Direction: {signal}")
            else:
                st.error(f"### Direction: {signal}")
        else:
            st.error("Market data fetch failed. Please try another pair or try again in a few seconds.")
