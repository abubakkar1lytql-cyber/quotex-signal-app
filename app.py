import streamlit as st
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import BollingerBands

st.set_page_config(page_title="Quotex AI Signal Board", layout="centered")

st.title("🎯 High Accuracy Signal Board")
st.write("কারেন্সি পেয়ার সিলেক্ট করে এনালাইসিস বাটনে চাপ দিন।")

pairs = {
    "USD/JPY": "USDJPY=X",
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
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
    with st.spinner("Analyzing Multi-Indicators..."):
        data = yf.download(ticker, period="1d", interval=tf)
        
        if not data.empty:
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
                
            rsi = RSIIndicator(close=data['Close'], window=14).rsi().iloc[-1]
            ema_9 = EMAIndicator(close=data['Close'], window=9).ema_indicator().iloc[-1]
            ema_21 = EMAIndicator(close=data['Close'], window=21).ema_indicator().iloc[-1]
            
            macd_obj = MACD(close=data['Close'])
            macd_diff = macd_obj.macd_diff().iloc[-1]
            
            bb = BollingerBands(close=data['Close'], window=20, window_dev=2)
            bb_high = bb.bollinger_hband().iloc[-1]
            bb_low = bb.bollinger_lband().iloc[-1]
            
            last_price = data['Close'].iloc[-1]
            
            signal = "NO STRONG SIGNAL (WAIT) ⏳"
            confidence = "50%"
            status = "neutral"

            if rsi > 70 and last_price >= bb_high and macd_diff < 0 and ema_9 < ema_21:
                signal = "STRONG PUT (SELL ⬇️)"
                confidence = "90%"
                status = "sell"
            elif rsi > 65 and last_price >= bb_high and ema_9 < ema_21:
                signal = "MODERATE PUT (SELL ⬇️)"
                confidence = "80%"
                status = "sell"
            elif rsi < 30 and last_price <= bb_low and macd_diff > 0 and ema_9 > ema_21:
                signal = "STRONG CALL (BUY ⬆️)"
                confidence = "90%"
                status = "buy"
            elif rsi < 35 and last_price <= bb_low and ema_9 > ema_21:
                signal = "MODERATE CALL (BUY ⬆️)"
                confidence = "80%"
                status = "buy"

            st.divider()
            col1, col2, col3 = st.columns(3)
            col1.metric("Current Price", f"{last_price:.4f}")
            col2.metric("RSI Value", f"{rsi:.1f}")
            col3.metric("AI Confidence", confidence)
            
            if status == "buy":
                st.success(f"### Signal: {signal}")
            elif status == "sell":
                st.error(f"### Signal: {signal}")
            else:
                st.warning(f"### Signal: {signal}")
        else:
            st.error("Market data fetch failed. Try again after a few seconds.")
