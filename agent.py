from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from tools.price_fetcher import fetch_prices
from tools.portfolio_parser import parse_portfolio, autocorrect_transcript
import json
import os

# Initialize LLM once
llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

def detect_intent_and_extract_info(transcript: str) -> dict:
    """Extracts intent and coin/quantity info from user transcript."""
    cleaned_input = autocorrect_transcript(transcript).lower()
    prompt = (
        "You are a crypto voice assistant.\n"
        "Possible intents: check_value, save_portfolio, update_portfolio, coin_price_lookup.\n\n"
        f"User said: \"{cleaned_input}\"\n\n"
        "Respond ONLY in compact JSON format like:\n"
        '{"intent": "save_portfolio", "portfolio": {"bitcoin": 1.0, "ethereum": 2.0}}'
    )

    try:
        response = llm([HumanMessage(content=prompt)])
        return json.loads(response.content)
    except Exception as e:
        print(f"❌ LLM parse failed: {e}")
        return {"intent": "unknown", "portfolio": {}}

def get_portfolio_summary(portfolio: dict) -> str:
    """Generates a human-readable summary of portfolio value and breakdown."""
    prices = fetch_prices(portfolio.keys())
    total_value = 0
    breakdown = []
    unfound_coins = []

    for coin, amount in portfolio.items():
        price = prices.get(coin.lower(), 0)
        if price == 0:
            unfound_coins.append(coin.capitalize())
            continue
        value = round(amount * price, 2)
        total_value += value

    for coin, amount in portfolio.items():
        price = prices.get(coin.lower(), 0)
        if price == 0:
            continue
        value = round(amount * price, 2)
        percent = (value / total_value * 100) if total_value > 0 else 0
        breakdown.append(f"{coin.capitalize()}: ${value:,.2f} ({percent:.2f}%)")

    summary = f"Total Portfolio Value: ${total_value:,.2f}\nBreakdown:\n" + "\n".join(breakdown)

    if unfound_coins:
        summary += (
            f"\n\n⚠️ Prices not found for: {', '.join(unfound_coins)}."
            " Please check spelling or try again."
        )

    return summary

def save_user_portfolio(portfolio: dict, user_id="default_user"):
    """Save user portfolio to disk (basic implementation)."""
    try:
        with open(f"user_portfolio_{user_id}.json", "w") as f:
            json.dump(portfolio, f)
    except Exception as e:
        print(f"❌ Failed to save portfolio: {e}")

def retrieve_user_portfolio(user_id="default_user") -> dict:
    """Retrieve user's saved portfolio from disk."""
    try:
        with open(f"user_portfolio_{user_id}.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"❌ Failed to load portfolio: {e}")
        return {}