import React, { useState } from "react";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ComposedChart, Bar } from "recharts";

function App() {
  const [symbol, setSymbol] = useState("BTCUSDT");
  const [data, setData] = useState([]);
  const [signal, setSignal] = useState(null);
  const [loading, setLoading] = useState(false);

  const getSignal = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://127.0.0.1:5000/trade/${symbol}`);
      const json = await res.json();
      if (json.error) throw new Error(json.error);
      setData(json.chartData);
      setSignal(json.signal);
    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ fontFamily: "Arial", padding: 20 }}>
      <h1>📊 Creata-Bot Trading Dashboard</h1>

      <div style={{ marginBottom: 20 }}>
        <input
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          placeholder="BTCUSDT"
          style={{ padding: 8, borderRadius: 6, border: "1px solid #ccc" }}
        />
        <button
          onClick={getSignal}
          disabled={loading}
          style={{ marginLeft: 10, padding: "8px 16px", background: "#22c55e", border: 0, borderRadius: 6, color: "#fff" }}
        >
          {loading ? "Loading..." : "Get Signal"}
        </button>
      </div>

      {signal && (
        <div style={{ marginBottom: 20, padding: 15, border: "1px solid #ddd", borderRadius: 8 }}>
          <h2>Signal for {symbol}</h2>
          <p><b>Action:</b> {signal.signal}</p>
          <p><b>Reason:</b> {signal.reason}</p>
          <p><b>Price:</b> {signal.price}</p>
          <p><b>Stop Loss:</b> {signal.stop_loss}</p>
          <p><b>Take Profit:</b> {signal.take_profit}</p>
          <p><b>Risk/Reward:</b> {signal.risk_reward}</p>
          <p><b>RSI:</b> {signal.rsi}</p>
        </div>
      )}

      {data.length > 0 && (
        <>
          <h3>Price with EMA</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <XAxis dataKey="time" tickFormatter={(t) => new Date(t * 1000).toLocaleDateString()} />
              <YAxis domain={["auto", "auto"]} />
              <Tooltip labelFormatter={(t) => new Date(t * 1000).toLocaleString()} />
              <CartesianGrid stroke="#eee" />
              <Line type="monotone" dataKey="close" stroke="#000" dot={false} name="Close" />
              <Line type="monotone" dataKey="ema50" stroke="#22c55e" dot={false} name="EMA50" />
              <Line type="monotone" dataKey="ema200" stroke="#ef4444" dot={false} name="EMA200" />
            </LineChart>
          </ResponsiveContainer>

          <h3>RSI</h3>
          <ResponsiveContainer width="100%" height={200}>
            <ComposedChart data={data}>
              <XAxis dataKey="time" tickFormatter={(t) => new Date(t * 1000).toLocaleDateString()} />
              <YAxis domain={[0, 100]} />
              <Tooltip labelFormatter={(t) => new Date(t * 1000).toLocaleString()} />
              <Line type="monotone" dataKey="rsi" stroke="#3b82f6" dot={false} />
              <CartesianGrid stroke="#eee" />
              <Bar dataKey="volume" fill="#cbd5e1" opacity={0.3} />
            </ComposedChart>
          </ResponsiveContainer>
        </>
      )}
    </div>
  );
}

export default App;
