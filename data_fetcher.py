import requests
import time
from datetime import datetime, timedelta
from config import ASSETS  

API_URL_SIMPLE_PRICE = 'https://pro-api.coingecko.com/api/v3/simple/price'
API_URL_MARKET_CHART_RANGE = 'https://pro-api.coingecko.com/api/v3/coins/{id}/market_chart/range'
API_KEY = 'XX-YYYYYYYYY'

def get_current_prices(assets):

    ids = ','.join([info['id'] for info in assets.values()])
    params = {
        'ids': ids,
        'vs_currencies': 'usd'
    }
    headers = {
        'accept': 'application/json',
        'x-cg-pro-api-key': API_KEY
    }
    try:
        response = requests.get(API_URL_SIMPLE_PRICE, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"⚠️ Erreur lors de la récupération des prix actuels: {e}")
        return {}

def get_historical_data(token_id, start_timestamp, end_timestamp):

    url = API_URL_MARKET_CHART_RANGE.format(id=token_id)
    params = {
        'vs_currency': 'usd',
        'from': start_timestamp,
        'to': end_timestamp
    }
    headers = {
        'accept': 'application/json',
        'x-cg-pro-api-key': API_KEY
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("prices", [])
    except requests.RequestException as e:
        print(f"⚠️ Erreur lors de la récupération des données historiques pour {token_id}: {e}")
        return None

def calculate_percentage_change(prices):

    if not prices or len(prices) < 2:
        return None
    start_price = prices[0][1]
    end_price = prices[-1][1]
    percent_change = ((end_price - start_price) / start_price) * 100
    return round(percent_change, 2)  

def get_crypto_trends():

    trends = {}
    current_prices = get_current_prices(ASSETS)

    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)
    end_timestamp = int(end_time.timestamp())
    start_timestamp = int(start_time.timestamp())

    for asset, info in ASSETS.items():
        token_id = info["id"]

        last_hour_prices = get_historical_data(token_id, start_timestamp, end_timestamp)
        last_hour_change = calculate_percentage_change(last_hour_prices)

        current_price = current_prices.get(token_id, {}).get('usd', None)

        trends[asset] = {
            "current_price": current_price,
            "1h": last_hour_change
        }

        time.sleep(0.25)

    return trends

if __name__ == "__main__":
    trends = get_crypto_trends()
    print("\n📊 **Cryptos trends:**")
    for asset, trend in trends.items():
        trend_value = trend['1h']
        trend_str = f"{trend_value}%" if trend_value is not None else "Données indisponibles"
        print(f"🔹 {asset.upper()} | Current price: {trend['current_price']} | Variation 1h: {trend_str}")
    