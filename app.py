```python
# app.py
# Flask backend for Creata Trading Assistant
# - Routes: / (frontend), /signal, /analyze, /ask
# - Uses trading.py (get_signal, get_analysis)
# - Uses OpenAI for chat (OPENAI_API_KEY from env)
# - Designed to run on Render (reads PORT env var)

import os
import traceback
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import openai

# load environment variables from .env (if present)
load_dotenv()

# import trading functions (from the trading.py you already installed)
from trading import get_signal, get_analysis

# Initialize Flask
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# OpenAI key (set in Render env vars or local .env)
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_KEY:
    openai.api_key = OPENAI_KEY

# ---- Helpers ----
def safe_json_error(message, code=500):
    return jsonify({"error": message}), code

# ---- Routes ----
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/signal", methods=["POST"])
def signal():
    """
    Request JSON:
      { "pair": "BTC/USDT", "timeframe": "1h" }
    Response:
      {
        "pair": "...",
        "timeframe": "...",
        "signal": "BUY/SELL/HOLD",
        "take_profit": <float or null>,
        "stop_loss": <float or null>
      }
    """
    try:
        data = request.get_json(force=True) or {}
        pair = data.get("pair") or data.get("symbol") or "BTC/USDT"
        timeframe = data.get("timeframe", "1h")

        # call trading logic
        result = get_signal(pair, timeframe)

        # Ensure response shape (defensive)
        if not isinstance(result, dict):
            return safe_json_error("Invalid signal response from trading module.")

        # Some trading modules may already return the final fields
        # Normalize keys if needed
        normalized = {
            "pair": result.get("pair", pair),
            "timeframe": result.get("timeframe", timeframe),
            "signal": result.get("signal", result.get("action", result.get("signal", "HOLD"))),
            "take_profit": result.get("take_profit", result.get("tp", None)),
            "stop_loss": result.get("stop_loss", result.get("sl", None)),
            "detail": result  # include full raw result for debugging / UI
        }
        return jsonify(normalized)
    except Exception as e:
        traceback.print_exc()
        return safe_json_error(f"Failed to generate signal: {str(e)}")


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Request JSON:
      { "pair": "BTC/USDT", "timeframe": "1h" }
    Response:
      { "pair": "...", "analysis": "human readable summary" }
    """
    try:
        data = request.get_json(force=True) or {}
        pair = data.get("pair") or data.get("symbol") or "BTC/USDT"
        timeframe = data.get("timeframe", "1h")

        summary = get_analysis(pair, timeframe)
        # If trading module returns dict, return as-is; else wrap
        if isinstance(summary, dict):
            return jsonify(summary)
        else:
            return jsonify({"pair": pair, "analysis": str(summary)})
    except Exception as e:
        traceback.print_exc()
        return safe_json_error(f"Failed to analyze pair: {str(e)}")


@app.route("/ask", methods=["POST"])
def ask():
    """
    Chat endpoint that uses OpenAI to answer user questions,
    optionally incorporating the latest signal/analysis for a given pair.
    Request JSON:
      {
        "message": "What are the chances of profit?",
        "pair": "BTC/USDT"   # optional
      }
    Response:
      { "response": "AI text..." }
    """
    try:
        data = request.get_json(force=True) or {}
        user_message = data.get("message") or data.get("question") or ""
        pair = data.get("pair") or data.get("symbol") or None
        timeframe = data.get("timeframe", "1h")

        if not user_message:
            return safe_json_error("No message provided", 400)

        # Optionally enrich the prompt with the latest signal for the requested pair
        enrichment = ""
        if pair:
            try:
                sig = get_signal(pair, timeframe)
                # pick friendly fields if available
                sig_action = sig.get("signal") or sig.get("action") or "HOLD"
                sig_tp = sig.get("take_profit") or sig.get("tp") or sig.get("TP")
                sig_sl = sig.get("stop_loss") or sig.get("sl") or sig.get("SL")
                enrichment = (
                    f"\n\nLatest technical snapshot for {pair} ({timeframe}):\n"
                    f"Signal: {sig_action}\n"
                    f"TP: {sig_tp}\n"
                    f"SL: {sig_sl}\n"
                )
            except Exception:
                # don't fail the whole request if enrichment fails
                enrichment = "\n\n(Unable to attach latest signal information.)"

        prompt = (
            "You are a polite, concise trading assistant. Give useful, practical trading guidance.\n"
            f"User question: {user_message}"
            f"{enrichment}\n\nAnswer clearly and include risk reminders."
        )

        # If OpenAI key is available, call ChatCompletion
        if not OPENAI_KEY:
            # No API key configured: return a helpful placeholder response
            return jsonify({
                "response": (
                    "OpenAI API key is not configured. You asked: "
                    f"'{user_message}'. {enrichment} "
                    "Install OPENAI_API_KEY in environment to enable AI responses."
                )
            })

        # Use ChatCompletion (Chat API)
        resp = openai.ChatCompletion.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "You are an expert trading assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.2,
        )

        ai_text = ""
        try:
            ai_text = resp["choices"][0]["message"]["content"]
        except Exception:
            ai_text = resp.get("choices", [{}])[0].get("text", "No reply from model.")

        return jsonify({"response": ai_text})
    except Exception as e:
        traceback.print_exc()
        return safe_json_error(f"Chat failed: {str(e)}")


# ---- Run app ----
if __name__ == "__main__":
    # Render provides PORT environment variable; fall back to 5000 locally
    port = int(os.environ.get("PORT", 5000))
    # Allow debug locally but not recommended in production
    debug_flag = os.getenv("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")
    app.run(host="0.0.0.0", port=port, debug=debug_flag)
```
