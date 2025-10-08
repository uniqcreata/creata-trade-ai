import os
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import BollingerBands
from dotenv import load_dotenv
from alpha_vantage.foreignexchange import ForeignExchange
from binance.client import Client

# === Load environment variables ===
load_dotenv()
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")

# Initialize clients
fx_client = ForeignExchange(key=ALPHA_VANTAGE_KEY, output_format='pandas')
binance_client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

# === Helper: Detect if it's a crypto or forex pair ===
def detect_market(pair):
    if "/" not in pair:
        pair = pair.upper()
    base, quote = pair.split("/")
    if quote in ["USDT", "BTC", "ETH", "BNB"]:
        return "crypto"
    else:
        return "forex"

# === Fetch Market Data ===
def fetch_data(pair, timeframe="1h", limit=200):
    market_type = detect_market(pair)
    if market_type == "crypto":
        symbol = pair.replace("/", "")
        klines = binance_client.get_klines(symbol=symbol, interval=timeframe, limit=limit)
        df = pd.DataFrame(klines, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "qav", "num_trades", "taker_base_vol", "taker_quote_vol", "ignore"
        ])
        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)
        df["time"] = pd.to_datetime(df["close_time"], unit='ms')
        return df[["time", "open", "high", "low", "close", "volume"]]

    else:
        try:
            data, _ = fx_client.get_currency_exchange_intraday(
                from_symbol=pair.split("/")[0],
                to_symbol=pair.split("/")[1],
                interval='60min',
                outputsize='compact'
            )
            df = data.rename(columns={
                '1. open': 'open',
                '2. high': 'high',
                '3. low': 'low',
                '4. close': 'close'
            })
            df = df.astype(float)
            df = df.sort_index()
            df["time"] = df.index
            return df
        except Exception as e:
            print(f"Error fetching forex data: {e}")
            return None

# === Generate Signal ===
def get_signal(pair, timeframe="1h"):
    df = fetch_data(pair, timeframe)
    if df is None or len(df) < 30:
        return {"pair": pair, "signal": "No data", "take_profit": None, "stop_loss": None}

    df["ema_fast"] = EMAIndicator(df["close"], window=9).ema_indicator()
    df["ema_slow"] = EMAIndicator(df["close"], window=26).ema_indicator()
    df["rsi"] = RSIIndicator(df["close"], window=14).rsi()
    macd = MACD(df["close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    bb = BollingerBands(df["close"], window=20, window_dev=2)
    df["bb_high"] = bb.bollinger_hband()
    df["bb_low"] = bb.bollinger_lband()

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    signal = "HOLD"
    if latest["ema_fast"] > latest["ema_slow"] and latest["rsi"] < 70 and latest["macd"] > latest["macd_signal"]:
        signal = "BUY"
    elif latest["ema_fast"] < latest["ema_slow"] and latest["rsi"] > 30 and latest["macd"] < latest["macd_signal"]:
        signal = "SELL"

    # === Calculate Take Profit & Stop Loss ===
    last_close = latest["close"]
    atr = (df["high"] - df["low"]).rolling(window=14).mean().iloc[-1]

    if signal == "BUY":
        take_profit = round(last_close + atr * 2, 5)
        stop_loss = round(last_close - atr * 1.5, 5)
    elif signal == "SELL":
        take_profit = round(last_close - atr * 2, 5)
        stop_loss = round(last_close + atr * 1.5, 5)
    else:
        take_profit = None
        stop_loss = None

    return {
        "pair": pair,
        "timeframe": timeframe,
        "signal": signal,
        "take_profit": take_profit,
        "stop_loss": stop_loss
    }

# === Get Analysis Summary ===
def get_analysis(pair, timeframe="1h"):
    df = fetch_data(pair, timeframe)
    if df is None or len(df) < 30:
        return {"pair": pair, "analysis": "Not enough data"}

    df["ema_fast"] = EMAIndicator(df["close"], window=9).ema_indicator()
    df["ema_slow"] = EMAIndicator(df["close"], window=26).ema_indicator()
    df["rsi"] = RSIIndicator(df["close"], window=14).rsi()
    macd = MACD(df["close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    latest = df.iloc[-1]
    trend = "Bullish" if latest["ema_fast"] > latest["ema_slow"] else "Bearish"
    rsi_status = "Overbought" if latest["rsi"] > 70 else "Oversold" if latest["rsi"] < 30 else "Neutral"
    macd_trend = "Positive" if latest["macd"] > latest["macd_signal"] else "Negative"

    summary = (
        f"Market: {trend}, RSI: {rsi_status}, MACD Trend: {macd_trend}. "
        f"Recent close price: {latest['close']:.4f}"
    )
    return {"pair": pair, "analysis": summary}
