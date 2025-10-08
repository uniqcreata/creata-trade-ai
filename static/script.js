let currentChart = null;

async function getSignal() {
  const symbol = document.getElementById("symbol").value.toUpperCase();
  if(!symbol) return alert("Enter symbol");
  
  const res = await fetch("/signal", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({symbol})
  });
  const data = await res.json();
  if(data.error){
    document.getElementById("signal-result").innerText = data.error;
    return;
  }

  document.getElementById("signal-result").innerHTML =
    `Symbol: ${data.symbol} | Signal: ${data.signal} | Price: ${data.last_price} | TP: ${data.tp} | SL: ${data.sl} | Confidence: ${data.confidence}%<br>
     Indicators: RSI:${data.indicators.RSI} EMA20:${data.indicators.EMA20} EMA50:${data.indicators.EMA50}`;

  loadChart(symbol);
}

function loadChart(symbol){
  if(currentChart) currentChart.remove();
  new TradingView.widget({
    container_id: "tradingview_chart",
    width: "100%",
    height: 500,
    symbol: symbol,
    interval: "60",
    timezone: "Etc/UTC",
    theme: "dark",
    style: "1",
    locale: "en",
    toolbar_bg: "#1e293b",
    enable_publishing: false,
    allow_symbol_change: true,
    hideideas: true
  });
  currentChart = true;
}

async function askBot(){
  const input = document.getElementById("chat-input");
  if(!input.value.trim()) return;
  const res = await fetch("/ask", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({message: input.value})
  });
  const data = await res.json();
  const chatBox = document.getElementById("chat-box");
  chatBox.innerHTML += `<p><b>You:</b> ${input.value}</p><p><b>Bot:</b> ${data.response}</p>`;
  input.value="";
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function loadJournal(){
  const res = await fetch("/journal");
  const data = await res.json();
  const journalBox = document.getElementById("journal-box");
  if(data.length===0){journalBox.innerHTML="<p>No trades yet.</p>"; return;}
  let html="<ul>";
  data.reverse().forEach(trade=>{
    html += `<li>[${trade.timestamp}] ${trade.symbol} - ${trade.signal} | Price: ${trade.last_price} | TP: ${trade.tp} | SL: ${trade.sl} | Confidence: ${trade.confidence}%</li>`;
  });
  html += "</ul>";
  journalBox.innerHTML = html;
}

window.onload = loadJournal;
