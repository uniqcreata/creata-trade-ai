from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from trading import generate_signal
import os
import requests

app = Flask(__name__)
CORS(app)

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")

# === Routes ===

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signal", methods=["POST"])
def signal():
    data = request.json
    symbol = data.get("symbol")
    market_type = data.get("market_type", "crypto")

    signal_data = generate_signal(symbol, market_type)

    return jsonify(signal_data)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    message = data.get("message")
    model = data.get("model", "ollama")  # Choose between 'ollama' or 'openai'

    response_text = "No response"

    if model.lower() == "ollama":
        headers = {"Authorization": f"Bearer {OLLAMA_API_KEY}"}
        payload = {"prompt": message, "model": "creata"}
        r = requests.post("https://api.ollama.com/v1/chat", headers=headers, json=payload)
        if r.status_code == 200:
            response_text = r.json().get("response", "No response")
        else:
            response_text = f"Ollama error: {r.text}"

    elif model.lower() == "openai":
        import openai
        openai.api_key = OPENAI_API_KEY
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": message}]
            )
            response_text = completion.choices[0].message.content
        except Exception as e:
            response_text = f"OpenAI error: {str(e)}"

    return jsonify({"response": response_text})

# === Run App ===
if __name__ == "__main__":
    import socket
    s = socket.socket()
    try:
        s.bind(("0.0.0.0", 5000))
    except OSError:
        import random
        port = random.randint(5001, 5999)
        app.run(host="0.0.0.0", port=port, debug=True)
    else:
        s.close()
        app.run(host="0.0.0.0", port=5000, debug=True)
