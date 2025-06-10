# --- Load environment and set API keys ---
from dotenv import load_dotenv
load_dotenv()

import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
print("✅ Loaded API key:", openai.api_key[:8] + "..." if openai.api_key else "❌ Not loaded")

from flask import Flask, request, jsonify, render_template, session
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from tools.price_fetcher import fetch_prices, is_valid_coin_name
from tools.portfolio_parser import parse_portfolio, autocorrect_transcript
from session_store import get_session_state
import json

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev")

llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    transcript = autocorrect_transcript(data.get("transcript", "")).lower()
    user_id = session.get("user_id", "default_user")
    state = get_session_state(user_id)

    def save_to_session():
        session[user_id] = state

    # Handle saving logic
    if state["mode"] == "saving":
        if "yes" in transcript or "correct" in transcript:
            if state["pending_coin"]:
                coin, qty = state["pending_coin"]
                state["portfolio"][coin] = qty
                state["pending_coin"] = None
                save_to_session()
                return jsonify({"summary": f"{coin.capitalize()} saved. Add another coin or say 'done' to finish."})
            else:
                return jsonify({"summary": "Sorry, I don't have a coin to confirm. Please say the coin and quantity again."})

        elif "done" in transcript:
            save_user_portfolio(state["portfolio"])
            summary = get_portfolio_summary(state["portfolio"])
            state["mode"] = None
            state["portfolio"] = {}
            save_to_session()
            return jsonify({"summary": summary})

        else:
            parsed = detect_intent_and_extract_info(transcript)
            portfolio = parsed.get("portfolio", {})

            if any(char.isdigit() for char in transcript) and portfolio:
                coin, qty = list(portfolio.items())[0]
                if is_valid_coin_name(coin):
                    state["pending_coin"] = (coin, qty)
                    save_to_session()
                    return jsonify({"summary": f"Did you say {qty} {coin.capitalize()}?"})
                else:
                    return jsonify({"summary": f"'{coin}' doesn’t look like a valid coin. Please try again with a known crypto."})
            else:
                return jsonify({"summary": "Sorry, I didn’t catch that. Try saying a coin and quantity again."})

    # Initial intent handling
    parsed = detect_intent_and_extract_info(transcript)
    intent = parsed.get("intent")
    portfolio = parsed.get("portfolio", {})
    print(f"🧠 Intent: {intent}, Portfolio: {portfolio}")

    if intent == "save_portfolio":
        state["mode"] = "saving"
        state["portfolio"] = {}
        state["pending_coin"] = None
        save_to_session()
        return jsonify({"summary": "Alright, let's save your portfolio. Say your first coin and amount."})

    elif intent == "check_value":
        portfolio = retrieve_user_portfolio()
        if isinstance(portfolio, dict) and portfolio:
            response = get_portfolio_summary(portfolio)
        else:
            response = "No saved portfolio found. Please save a new one first."
        return jsonify({"summary": response})

    else:
        return jsonify({"summary": "Sorry, I didn’t understand that. Try saying 'save my portfolio' or 'check my portfolio value'."})

def detect_intent_and_extract_info(transcript):
    keywords = ["bitcoin", "ethereum", "dogecoin", "check", "value", "save", "portfolio", "coin"]
    if not any(word in transcript.lower() for word in keywords):
        return {"intent": "unknown", "portfolio": {}}

    prompt = f"""
You are a crypto voice assistant. Classify the user's intent as one of:
- check_value
- save_portfolio
- update_portfolio
- coin_price_lookup

Also extract any mentioned coins and amounts (e.g. "2 ethereum"). Return only this JSON:
{{
  "intent": "check_value",
  "portfolio": {{"bitcoin": 1.0, "ethereum": 2.0}}
}}

User: "{transcript}"
""".strip()

    response = llm([HumanMessage(content=prompt)])
    try:
        return json.loads(response.content)
    except:
        return {"intent": "unknown", "portfolio": {}}

def get_portfolio_summary(portfolio):
    prices = fetch_prices(portfolio.keys())
    total_value = 0
    breakdown = []
    unfound_coins = []

    for coin, amount in portfolio.items():
        price = prices.get(coin.lower(), 0)
        value = round(amount * price, 2)
        if price == 0:
            unfound_coins.append(coin.capitalize())
            continue
        total_value += value

    for coin, amount in portfolio.items():
        price = prices.get(coin.lower(), 0)
        value = round(amount * price, 2)
        if price == 0:
            continue
        percent = round((value / total_value * 100)) if total_value > 0 else 0
        breakdown.append(f"{coin.capitalize()} is {percent} percent")

    summary = f"Your total portfolio value: ${total_value:,.2f}. " + ", ".join(breakdown) + " of your total portfolio."

    if unfound_coins:
        unfound_list = ", ".join(unfound_coins)
        summary += f" ⚠️ Prices not found for: {unfound_list}."

    return summary

def save_user_portfolio(portfolio):
    with open("user_portfolio.json", "w") as f:
        json.dump(portfolio, f)

def retrieve_user_portfolio():
    try:
        with open("user_portfolio.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

if __name__ == "__main__":
    app.run(debug=True)