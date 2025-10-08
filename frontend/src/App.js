import React, { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer
} from "recharts";

function App() {
  const [symbol, setSymbol] = useState("BTCUSDT");
  const [dataPoints, setDataPoints] = useState([]);
  const [signal, setSignal] = useState({});
  const [portfolio, setPortfolio] = useState({});
  const [amount, setAmount] = useState("0.001");
  const [tp, setTp] = useState("2"); // percent
  const [sl, setSl] = useState("1"); // percent

  async function fetchSignal(sym) {
    const url = sym.includes("/") ? `/forex/${sym.replace("/", "/")}` :
                (sym.endsWith("USDT") ? `/crypto/${sym}` : `/stock/${sym}`);
    try {
      const res = await fetch(`http://127.0.0.1:5000${url}`);
      const json = await res.json();
      setSignal(json);
      if (json.price) {
        setDataPoints(prev => [...prev, { time: new Date().toLocaleTimeString(), price: json.price }].slice(-30));
      }
    } catch (e) {
      console.error("signal error", e);
    }
  }

  async function fetchPortfolio() {
    try {
      const res = await fetch("http://127.0.0.1:5000/portfolio");
      const json = await res.json();
      setPortfolio(json);
    } catch (e) {
      console.error("portfolio error", e);
    }
  }

  useEffect(() => {
    setDataPoints([]);
    fetchSignal(symbol);
    fetchPortfolio();
    const t = setInterval(() => {
      fetchSignal(symbol);
      fetchPortfolio();
    }, 5000);
    return () => clearInterval(t);
  }, [symbol]);

  async function doTrade(action) {
    try {
      const body = {
        symbol,
        action,
        amount: parseFloat(amount),
        tp_pct: parseFloat(tp),
        sl_pct: parseFloat(sl)
      };
      const res = await fetch("http://127.0.0.1:5000/execute_trade", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      const json = await res.json();
      alert(JSON.stringify(json));
      fetchPortfolio();
    } catch (e) {
      console.error("trade error", e);
    }
  }

  return (
    <div style={{ padding: 20, fontFamily: "Arial, sans-serif" }}>
      <h1>Creata-Bot Dashboard</h1>

      <div style={{ marginBottom: 12 }}>
        <label>Symbol: </label>
        <select value={symbol} onChange={(e) => setSymbol(e.target.value)}>
          <option value="BTCUSDT">BTC/USDT</option>
          <option value="ETHUSDT">ETH/USDT</option>
          <option value="SOLUSDT">SOL/USDT</option>
          <option value="DOGEUSDT">DOGE/USDT</option>
          <option value="AAPL">AAPL (stock)</option>
          <option value="EUR/USD">EUR/USD (forex)</option>
        </select>
      </div>

      <h3>{signal.symbol || symbol} — {signal.source || ""}</h3>
      <h2 style={{ color: signal.signal === "BUY" ? "green" : signal.signal === "SELL" ? "red" : "gray" }}>
        {signal.price ? `$${Number(signal.price).toLocaleString()}` : "Loading..."} — {signal.signal || ""}
      </h2>

      <div style={{ height: 320 }}>
        <ResponsiveContainer>
          <LineChart data={dataPoints}>
            <CartesianGrid stroke="#eee" />
            <XAxis dataKey="time" />
            <YAxis domain={["auto","auto"]} />
            <Tooltip />
            <Line dataKey="price" stroke="#3b82f6" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <section style={{ marginTop: 16 }}>
        <h3>Manual Trade (simulation)</h3>
        <div>
          <label>Amount (units/shares): </label>
          <input value={amount} onChange={e => setAmount(e.target.value)} style={{ width: 120 }} />
          <label style={{ marginLeft: 12 }}>TP %</label>
          <input value={tp} onChange={e => setTp(e.target.value)} style={{ width: 80 }} />
          <label style={{ marginLeft: 12 }}>SL %</label>
          <input value={sl} onChange={e => setSl(e.target.value)} style={{ width: 80 }} />
        </div>
        <div style={{ marginTop: 8 }}>
          <button onClick={() => doTrade("BUY")} style={{ marginRight: 8, background: "green", color: "white", padding: "8px 12px", border: "none" }}>BUY</button>
          <button onClick={() => doTrade("SELL")} style={{ background: "red", color: "white", padding: "8px 12px", border: "none" }}>SELL</button>
        </div>
      </section>

      <section style={{ marginTop: 20 }}>
        <h3>Portfolio</h3>
        <pre style={{ textAlign: "left", background: "#f7f7f7", padding: 12 }}>{JSON.stringify(portfolio, null, 2)}</pre>
      </section>
    </div>
  );
}

export default App;
