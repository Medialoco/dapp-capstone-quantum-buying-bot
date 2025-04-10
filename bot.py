import time
import asyncio
import datetime
from flask import Flask, render_template
from quantum_trader import analyze_and_trade
from wallet_content import get_wallet_info, WALLET_ADDRESS
from data_fetcher import get_crypto_trends

app = Flask(__name__)

def get_wallet_summary():
    wallet = get_wallet_info(WALLET_ADDRESS)
    trends = get_crypto_trends()
    wallet_amount = sum(wallet.get(asset, 0) * trends.get(asset, {}).get('current_price', 0) for asset in wallet)
    
    composition = {}
    for asset in ["USDC", "PEPESOL", "SPX6900", "SOL", "WBTC"]:
        balance = wallet.get(asset, 0.0)
        price = trends.get(asset, {}).get('current_price', 0.0)
        variation = trends.get(asset, {}).get("1h", 0.0)
        usd_value = balance * price
        composition[asset] = {
            "balance": balance,
            "variation": variation,
            "usd_value": usd_value
        }

    return wallet_amount, composition


@app.route('/')
def index():
    wallet_amount, composition = get_wallet_summary()
    return render_template('index.html', wallet_amount=wallet_amount, composition=composition)

if __name__ == "__main__":
    print("Starting...")
    
    # Lancer Flask en mode asynchrone
    from threading import Thread
    flask_thread = Thread(target=lambda: app.run(debug=True, use_reloader=False))
    flask_thread.start()
    
    while True:
        print("***********************")
        now = datetime.datetime.now()
        print(now.strftime("%Y-%m-%d %H:%M:%S"))
        analyze_and_trade()
        time.sleep(120)