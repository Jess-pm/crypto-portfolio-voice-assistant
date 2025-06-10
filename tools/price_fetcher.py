print("✅ price_fetcher loaded")

import requests
from fuzzywuzzy import process

# Call once to cache supported coin list
def get_coingecko_ids():
    try:
        url = 'https://api.coingecko.com/api/v3/coins/list'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return [coin['id'] for coin in data]
    except Exception as e:
        print(f"❌ Error fetching CoinGecko IDs: {e}")
        return []

# Cache coin IDs to avoid multiple API calls
KNOWN_IDS = get_coingecko_ids()

def match_coin_id(coin):
    if not KNOWN_IDS:
        print("❌ No CoinGecko IDs loaded.")
        return None, 0

    match, score = process.extractOne(coin.lower(), KNOWN_IDS)
    print(f"🔍 Matched '{coin}' to '{match}' (score {score})")
    return (match if score >= 85 else None), score

def fetch_prices(coins):
    matched_ids = {}
    warnings = []

    for coin in coins:
        matched, score = match_coin_id(coin)
        if matched:
            matched_ids[coin] = matched
            if score < 90:
                warnings.append(f"⚠️ Low confidence match: '{coin}' → '{matched}' ({score})")
        else:
            warnings.append(f"⚠️ Could not confidently match '{coin}' to any known token")

    if not matched_ids:
        print("❌ No valid coin IDs matched. Skipping price fetch.")
        return {}

    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(set(matched_ids.values()))}&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Error fetching prices: {e}")
        return {}

    prices = {}
    for coin, cg_id in matched_ids.items():
        prices[coin] = data.get(cg_id, {}).get('usd', 0)
    return prices

# New helper to verify coin name is valid against CoinGecko
def is_valid_coin_name(coin):
    return coin.lower() in KNOWN_IDS