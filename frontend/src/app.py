from flask import Flask, jsonify
import requests
import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# ====================
# Indicators
# ====================

def calculate_rsi(data, period=14):
    delta = data["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]


def calculate_ema(data, period=20):
    return data["close"].ewm(span=period, adjust=False).mean().iloc[-1]


def calculate_atr(data, period=14):
    high = data["high"]
    low = data["low"]
    close = data["close"]

    data["H-L"] = high - low
    data["H-C"] = abs(high - close.shift())
    data["L-C"] = abs(low - close.shift())
    tr = data[["H-L", "H-C", "L-C"]].max(axis=1)

    atr = tr.rolling(period).mean()
    return atr.iloc[-1]


# ====================
# Signal Logic
# ====================

def generate_trade_signal(data):
    last_price = data["close"].iloc[-1]
    rsi = calculate_rsi(data)
    ema20 = calculate_ema(data, 20)
    ema50 = calculate_ema(data, 50)
    atr = calculate_atr(data)

    # Stop loss = 1.5 × ATR below price
    stop_loss = round(last_price - (1.5 * atr), 2)
    # Take profits: conservative (2× ATR), ambitious (4× ATR)
    tp1 = round(last_price + (2 * atr), 2)
    tp2 = round(last_price + (4 * atr), 2)

    # Dynamic risk/greed
    risk_pct = round((atr / last_price) * 100, 2)  # ATR as % of price
    greed_pct = round(((tp2 - last_price) / last_price) * 100, 2)

    # Decision logic
    if rsi < 30 and ema20 > ema50:
        recommendation = "STRONG BUY"
    elif rsi > 70 and ema20 < ema50:
        recommendation = "STRONG SELL"
    elif ema20 > ema50 and rsi < 50:
        recommendation = "BUY"
    elif ema20 < ema50 and rsi > 50:
        recommendation = "SELL"
    else:
        recommendation = "HOLD"

    return {
        "recommendation": recommendation,
        "current_price": round(last_price, 2),
        "stop_loss": stop_loss,
        "take_profit_1": tp1,
        "take_profit_2": tp2,
        "rsi": round(rsi, 2),
        "ema20": round(ema20, 2),
        "ema50": round(ema50, 2),
        "atr": round(atr, 2),
        "risk_pct": f"{risk_pct}%",
        "greed_pct": f"{greed_pct}%"
    }


# ====================
# Routes
# ====================

@app.route("/crypto/<symbol>")
def get_crypto_signal(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol.upper()}&interval=1h&limit=200"
        response = requests.get(url)
        response.raise_for_status()

        raw = response.json()
        if not isinstance(raw, list):
            return jsonify({"error": "Invalid data from Binance"}), 400

        df = pd.DataFrame(raw, columns=[
            "time", "open", "high", "low", "close", "volume",
            "close_time", "qav", "trades", "tbbav", "tbqav", "ignore"
        ])
        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)

        signal = generate_trade_signal(df)
        return jsonify(signal)

    except Exception as e:
        return jsonify({"error": f"Crypto API error: {str(e)}"}), 500


@app.route("/forex/<base>/<quote>")
def get_forex_signal(base, quote):
    try:
        api_key = os.getenv("ALPHA_VANTAGE_KEY")
        if not api_key:
            return jsonify({"error": "Alpha Vantage API key missing"}), 400

        url = (
            f"https://www.alphavantage.co/query?function=FX_INTRADAY"
            f"&from_symbol={base.upper()}&to_symbol={quote.upper()}"
            f"&interval=60min&apikey={api_key}&datatype=json"
        )
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        timeseries = data.get("Time Series FX (60min)")
        if not timeseries:
            return jsonify({"error": "Invalid data from Alpha Vantage"}), 400

        df = pd.DataFrame(timeseries).T
        df = df.rename(columns={
            "1. open": "open",
            "2. high": "high",
            "3. low": "low",
            "4. close": "close"
        })
        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)

        signal = generate_trade_signal(df)
        return jsonify(signal)

    except Exception as e:
        return jsonify({"error": f"Forex API error: {str(e)}"}), 500


# ====================
# Run
# ====================
if __name__ == "__main__":
    app.run(debug=True, port=5000)
