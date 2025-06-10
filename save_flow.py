from tools.portfolio_parser import autocorrect_transcript, parse_portfolio
from tools.price_fetcher import fetch_prices
import json

# Simulated memory for single user; in production use sessions or DB
save_memory = {
    "mode": None,
    "pending_coin": None,
    "portfolio": {}
}

def handle_save_flow(user_id, transcript):
    transcript = autocorrect_transcript(transcript).lower()

    if save_memory["mode"] != "saving":
        save_memory["mode"] = "saving"
        save_memory["portfolio"] = {}
        return "Got it. Let's save your portfolio. Tell me your first coin and how much you have."

    if "done" in transcript:
        save_user_portfolio(save_memory["portfolio"])
        response = get_portfolio_summary(save_memory["portfolio"])
        save_memory["mode"] = None
        save_memory["pending_coin"] = None
        save_memory["portfolio"] = {}
        return f"✅ Portfolio saved.\n{response}"

    if save_memory["pending_coin"] and ("yes" in transcript or "correct" in transcript):
        coin, qty = save_memory["pending_coin"]
        save_memory["portfolio"][coin] = qty
        save_memory["pending_coin"] = None
        return f"{coin.capitalize()} saved. Add another coin or say 'done' to finish."

    parsed = parse_portfolio(transcript)
    if parsed:
        coin, qty = list(parsed.items())[0]
        save_memory["pending_coin"] = (coin, qty)
        return f"Did you say {qty} {coin.capitalize()}?"
    else:
        return "Sorry, I didn't catch that. Please say the coin and quantity again."

def save_user_portfolio(portfolio):
    with open("user_portfolio.json", "w") as f:
        json.dump(portfolio, f)

def get_portfolio_summary(portfolio):
    prices = fetch_prices(portfolio.keys())
    total_value = 0
    breakdown = []
    unfound = []

    for coin, amount in portfolio.items():
        price = prices.get(coin.lower(), 0)
        value = round(amount * price, 2)
        if price == 0:
            unfound.append(coin.capitalize())
            continue
        total_value += value

    for coin, amount in portfolio.items():
        price = prices.get(coin.lower(), 0)
        value = round(amount * price, 2)
        if price == 0:
            continue
        percent = (value / total_value * 100) if total_value > 0 else 0
        breakdown.append(f"{coin.capitalize()}: ${value:,.2f} ({percent:.2f}%)")

    summary = f"Total Portfolio Value: ${total_value:,.2f}\nBreakdown:\n" + "\n".join(breakdown)

    if unfound:
        summary += f"\n\n⚠️ Prices not found for: {', '.join(unfound)}."

    return summary