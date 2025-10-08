async function getSignal() {
    const symbol = document.getElementById("symbol").value;
    const market_type = document.getElementById("market_type").value;

    if (!symbol) {
        alert("Please enter a symbol");
        return;
    }

    const response = await fetch("/signal", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({symbol, market_type})
    });

    const data = await response.json();

    document.getElementById("signal-text").innerText = `Signal: ${data.signal}`;
    document.getElementById("tp-sl").innerText = `TP: ${data.take_profit || "-"} | SL: ${data.stop_loss || "-"}`;
    document.getElementById("timestamp").innerText = `Timestamp: ${data.timestamp}`;
}

async function askAI() {
    const message = document.getElementById("ai-message").value;
    const model = document.getElementById("ai-model").value;

    if (!message) {
        alert("Please enter a message");
        return;
    }

    const response = await fetch("/ask", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message, model})
    });

    const data = await response.json();
    document.getElementById("ai-response").innerText = data.response;
}
