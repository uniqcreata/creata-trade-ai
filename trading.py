import ccxt
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import datetime
import json
import os

# --- Signal journal file ---
SIGNAL_FILE = "signals.json"

# Ensure signal file exists
if not os.path.exists(SIGNAL_FILE):
    with open(SIGNAL_FILE, "w") as f:
        json.dump([], f)

# --- Binance exchange (crypto) ---
binance = ccxt.binance({
    'enableRateLimit': True
})

# --- Function to fetch market data ---
def fetch_market_data(symbol, market_type="crypto", timeframe="1h", limit=100):
    if market_type.lower() == "crypto":
        try:
            ohlcv = binance.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=["timestamp","open","high","low","close","volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            return df
        except Exception as e:
            print(f"Error fetching crypto data: {e}")
            return None
    elif market_type.lower() == "forex":
        try:
            data = yf.download(symbol, period="7d", interval="1h")
            data.reset_index(inplace=True)
            data.rename(columns={"Open":"open","High":"high","Low":"low","Close":"close","Volume":"volume"}, inplace=True)
            return data
        except Exception as e:
            print(f"Error fetching forex data: {e}")
            return None
    else:
        return None

# --- Technical Indicators ---
def add_indicators(df):
    df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()
    df["ema12"] = ta.trend.EMAIndicator(df["close"], window=12).ema_indicator()
    df["ema26"] = ta.trend.EMAIndicator(df["close"], window=26).ema_indicator()
    return df

# --- Generate signal ---
def generate_signal(symbol, market_type="crypto"):
    df = fetch_market_data(symbol, market_type)
    if df is None or df.empty:
        return {"symbol": symbol, "market_type": market_type, "signal": "Data unavailable", "take_profit": None, "stop_loss": None, "timestamp": str(datetime.datetime.now())}

    df = add_indicators(df)
    latest = df.iloc[-1]

    # --- Simple EMA + RSI strategy ---
    if latest["ema12"] > latest["ema26"] and latest["rsi"] < 70:
        signal = "BUY"
        tp = latest["close"] * 1.02  # Take profit +2%
        sl = latest["close"] * 0.99  # Stop loss -1%
    elif latest["ema12"] < latest["ema26"] and latest["rsi"] > 30:
        signal = "SELL"
        tp = latest["close"] * 0.98
        sl = latest["close"] * 1.01
    else:
        signal = "HOLD"
        tp = None
        sl = None

    signal_data = {
        "symbol": symbol,
        "market_type": market_type,
        "signal": signal,
        "take_profit": round(tp, 6) if tp else None,
        "stop_loss": round(sl, 6) if sl else None,
        "timestamp": str(datetime.datetime.now())
    }

    # --- Save to journal ---
    with open(SIGNAL_FILE, "r") as f:
        journal = json.load(f)
    journal.append(signal_data)
    with open(SIGNAL_FILE, "w") as f:
        json.dump(journal, f, indent=4)

    return signal_data
