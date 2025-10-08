from binance.client import Client
from binance.enums import *

# === CONFIG ===
API_KEY = "YOUR_BINANCE_API_KEY"
API_SECRET = "YOUR_BINANCE_API_SECRET"

client = Client(API_KEY, API_SECRET, testnet=True)  # testnet=True means DEMO

# === Example: Place Long Order ===
order = client.futures_create_order(
    symbol="BTCUSDT",
    side=SIDE_BUY,
    type=ORDER_TYPE_MARKET,
    quantity=0.001
)

print("Order executed:", order)
