import re
from difflib import get_close_matches

# Known coin name mappings for fuzzy matching and multi-word names
COIN_ALIASES = {
    "btc": "bitcoin",
    "bit coin": "bitcoin",
    "bitcon": "bitcoin",
    "eth": "ethereum",
    "ether": "ethereum",
    "doge": "dogecoin",
    "doge coin": "dogecoin",
    "dodge coin": "dogecoin",
    "bnb": "binancecoin",
    "binance": "binancecoin",
    "usdt": "tether",
    "tether": "tether",
    "pepe": "pepe"
}

KNOWN_COINS = set(COIN_ALIASES.values())


def fuzzy_match_coin(name):
    name = name.lower().strip().rstrip('s')
    if name in COIN_ALIASES:
        return COIN_ALIASES[name]
    close = get_close_matches(name, KNOWN_COINS, n=1, cutoff=0.8)
    return close[0] if close else name


def autocorrect_transcript(text):
    corrections = {
        " to ": " 2 ", " too ": " 2 ", " two ": " 2 ",
        " one ": " 1 ", " three ": " 3 ", " four ": " 4 ",
        " five ": " 5 ", " six ": " 6 ", " seven ": " 7 ",
        " eight ": " 8 ", " nine ": " 9 ", " zero ": " 0 ",
        " douchecoin": " dogecoin", " pipi": "pepe"
    }
    text = " " + text.lower() + " "
    for wrong, right in corrections.items():
        text = text.replace(wrong, right)
    return text.strip()


def parse_portfolio(transcript):
    pattern = r'(\d+(?:,\d{3})*(?:\.\d+)?)\s+([\w\s]+)'
    matches = re.findall(pattern, transcript)
    portfolio = {}
    for amount_str, coin in matches:
        try:
            amount = float(amount_str.replace(",", ""))
            coin_name = fuzzy_match_coin(coin.strip())
            portfolio[coin_name] = portfolio.get(coin_name, 0) + amount
        except ValueError:
            continue
    return portfolio


def parse_coin_quantity(text):
    match = re.search(r'(\d+(?:\.\d+)?)\s+([\w\s]+)', text)
    if match:
        quantity = float(match.group(1))
        coin = fuzzy_match_coin(match.group(2))
        return coin, quantity
    return None