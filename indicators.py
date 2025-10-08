def calculate_rsi(prices, period=14):
    prices = list(prices)
    if len(prices) <= period:
        return None
    gains = 0.0
    losses = 0.0
    # Initial averages
    for i in range(1, period + 1):
        delta = prices[i] - prices[i - 1]
        if delta >= 0:
            gains += delta
        else:
            losses += -delta
    avg_gain = gains / period
    avg_loss = losses / period

    # Wilder’s smoothing
    for i in range(period + 1, len(prices)):
        delta = prices[i] - prices[i - 1]
        gain = max(delta, 0)
        loss = max(-delta, 0)
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period

    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)


def calculate_ema(prices, period=20):
    prices = list(prices)
    if len(prices) < period:
        return None
    k = 2 / (period + 1)
    ema = sum(prices[:period]) / period  # start from SMA
    for p in prices[period:]:
        ema = p * k + ema * (1 - k)
    return round(ema, 5)


def risk_management(price, rsi, ema, risk_percent=1.0, reward_ratio=2.0):
    """
    Returns signal + SL/TP given price, RSI, EMA.
    risk_percent is % from entry to stop.
    reward_ratio is RR (e.g., 2.0 = 1:2 risk:reward)
    """
    price = float(price)
    if rsi is None or ema is None:
        return {
            "signal": "WAIT",
            "buy_price": round(price, 5),
            "take_profit": None,
            "stop_loss": None,
            "risk_percent": risk_percent,
        }

    signal = "HOLD"
    stop = None
    tp = None

    # Long bias: oversold and above EMA
    if rsi < 30 and price > ema:
        signal = "LONG"
        stop = price * (1 - risk_percent / 100)
        tp = price + (price - stop) * reward_ratio

    # Short bias: overbought and below EMA
    elif rsi > 70 and price < ema:
        signal = "SHORT"
        stop = price * (1 + risk_percent / 100)
        tp = price - (stop - price) * reward_ratio

    return {
        "signal": signal,
        "buy_price": round(price, 5),
        "take_profit": (round(tp, 5) if tp else None),
        "stop_loss": (round(stop, 5) if stop else None),
        "risk_percent": risk_percent,
    }
