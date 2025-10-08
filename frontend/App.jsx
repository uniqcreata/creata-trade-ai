import React, { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

function App() {
  const [mode, setMode] = useState("stocks"); // stocks | crypto | forex
  const [symbol, setSymbol] = useState("");
  const [base, setBase] = useState("");
  const [quote, setQuote] = useState("");
  const [signal, setSignal] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(false);

  const getSignal = async () => {
    setLoading(true);
    setSignal(null);
    setChartData([]);

    let url = "";
    if (mode === "stocks") {
      url = `http://127.0.0.1:5000/stocks/${symbol}`;
    } else if (mode === "crypto") {
      url = `http://127.0.0.1:5000/crypto/${symbol}`;
    } else if (mode === "forex") {
      url = `http://127.0.0.1:5000/forex/${base}/${quote}`;
    }

    try {
      const res = await fetch(url);
      const data = await res.json();
      setSignal(data);

      if (data.chart) {
        // Normalize chart data for Recharts
        const formatted = data.chart.map((candle, i) => ({
          time: i,
          price: candle.close,
          rsi: candle.rsi,
        }));
        setChartData(formatted);
      }
    } catch (err) {
      console.error(err);
      setSignal({ error: "Failed to fetch signal" });
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: 20, fontFamily: "Arial" }}>
      <h1>📈 Creata-Bot Trading Assistant</h1>

      {/* Mode Selection */}
      <div style={{ marginBottom: 20 }}>
        <label>
          <input
            type="radio"
            value="stocks"
            checked={mode === "stocks"}
            onChange={() => setMode("stocks")}
          />
          Stocks
        </label>
        <label style={{ marginLeft: 10 }}>
          <input
            type="radio"
            value="crypto"
            checked={mode === "crypto"}
            onChange={() => setMode("crypto")}
          />
          Crypto
        </label>
        <label style={{ marginLeft: 10 }}>
          <input
            type="radio"
            value="forex"
            checked={mode === "forex"}
            onChange={() => setMode("forex")}
          />
          Forex
        </label>
      </div>

      {/* Input fields */}
      {mode === "stocks" && (
        <div>
          <input
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            style={{ padding: 8, borderRadius: 8, width: 150 }}
            placeholder="AAPL"
          />
        </div>
      )}

      {mode === "crypto" && (
        <div>
          <input
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            style={{ padding: 8, borderRadius: 8, width: 150 }}
            placeholder="BTC/USD"
          />
        </div>
      )}

      {mode === "forex" && (
        <div>
          <input
            value={base}
            onChange={(e) => setBase(e.target.value.toUpperCase())}
            style={{ padding: 8, borderRadius: 8, width: 100, marginRight: 5 }}
            placeholder="EUR"
          />
          <input
            value={quote}
            onChange={(e) => setQuote(e.target.value.toUpperCase())}
            style={{ padding: 8, borderRadius: 8, width: 100 }}
            placeholder="USD"
          />
        </div>
      )}

      {/* Button */}
      <button
        onClick={getSignal}
        disabled={loading}
        style={{
          marginTop: 15,
          padding: "10px 16px",
          background: "#22c55e",
          border: 0,
          borderRadius: 8,
          color: "white",
          cursor: "pointer",
        }}
      >
        {loading ? "Loading..." : "Get Signal"}
      </button>

      {/* Trading Signal Output */}
      {signal && (
        <div
          style={{
            marginTop: 20,
            padding: 20,
            background: "#f3f4f6",
            borderRadius: 8,
          }}
        >
          {signal.error ? (
            <p style={{ color: "red" }}>{signal.error}</p>
          ) : (
            <>
              <h2>📊 Trading Signal</h2>
              <p>
                <strong>Signal:</strong> {signal.signal}
              </p>
              <p>
                <strong>Price:</strong> {signal.price}
              </p>
              <p>
                <strong>Stop Loss:</strong> {signal.stop_loss}
              </p>
              <p>
                <strong>Take Profit:</strong> {signal.take_profit}
              </p>
              <p>
                <strong>Risk %:</strong> {signal.risk_percent}
              </p>
              <p>
                <strong>Greed %:</strong> {signal.greed_percent}
              </p>
            </>
          )}
        </div>
      )}

      {/* Chart Section */}
      {chartData.length > 0 && (
        <div style={{ marginTop: 30 }}>
          <h2>📉 Price & RSI Chart</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="price" stroke="#2563eb" />
              <Line type="monotone" dataKey="rsi" stroke="#f59e0b" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

export default App;
