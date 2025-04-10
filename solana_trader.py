import base58
import base64
import json
import asyncio

from solders import message
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

from solana.rpc.types import TxOpts
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed
from jupiter_python_sdk.jupiter import Jupiter
from config import ASSETS, SOLANA_RPC_URL
import json
from solana.keypair import Keypair


async def trade(source_asset: str, target_asset: str, amount: float):
    """
    Execute a swap between two specified assets.
    
    :param source_asset: Symbol of the source asset (e.g., 'SOL')
    :param target_asset: Symbol of the target asset (e.g., 'USDC')
    :param amount: Amount to exchange, expressed in the source asset
    """
    if source_asset not in ASSETS or target_asset not in ASSETS:
        print(f"❌ Invalid asset. Choose from: {list(ASSETS.keys())}")
        return

    # Retrieve asset information
    source_info = ASSETS[source_asset]
    target_info = ASSETS[target_asset]

    print(f"🔄 Starting trade: {amount} {source_asset} → {target_asset}")

    with open("phantom_keypair.json", "r") as f:
        secret = json.load(f)
        private_key = Keypair.from_secret_key(bytes(secret))

    
    async_client = AsyncClient(SOLANA_RPC_URL)
    jupiter = Jupiter(
        async_client=async_client,
        keypair=private_key,
        quote_api_url="https://quote-api.jup.ag/v6/quote?",
        swap_api_url="https://quote-api.jup.ag/v6/swap",
    )

    # Convert amount to smallest unit
    amount_in_smallest_unit = int(amount * (10 ** source_info['decimals']))
    
    try:
        print("📡 Fetching swap transaction from Jupiter API...")
        transaction_data = await jupiter.swap(
            input_mint=source_info['mint'],
            output_mint=target_info['mint'],
            amount=amount_in_smallest_unit,
            slippage_bps=10,  # 0.1% slippage tolerance
        )
        print("✅ Swap transaction received.")

        print("🔄 Signing transaction...")
        raw_transaction = VersionedTransaction.from_bytes(base64.b64decode(transaction_data))
        signature = private_key.sign_message(message.to_bytes_versioned(raw_transaction.message))
        signed_txn = VersionedTransaction.populate(raw_transaction.message, [signature])

        print("📡 Sending transaction to Solana blockchain...")
        opts = TxOpts(skip_preflight=False, preflight_commitment=Processed)
        result = await async_client.send_raw_transaction(txn=bytes(signed_txn), opts=opts)

        # Extract transaction ID
        transaction_json = json.loads(result.to_json())
        if 'result' in transaction_json and transaction_json['result']:
            transaction_id = transaction_json['result']
            print(f"✅ Trade successful: {source_asset} → {target_asset}")
            print(f"🔗 Transaction: https://explorer.solana.com/tx/{transaction_id}")
        else:
            print(f"❌ Transaction failed: {transaction_json}")

    except Exception as e:
        print(f"❌ Error during swap: {e}")

        # Better error handling
        if "insufficient lamports" in str(e):
            print("⚠️ Insufficient SOL for transaction fees.")

        elif "custom program error" in str(e):
            print("⚠️ Possible issue with Jupiter API or token account. Check the mint addresses and balances.")

    finally:
        await async_client.close()
        print("🔄 Trade process completed.")

# Example Usage
if __name__ == "__main__":
    source = "PEPESOL"
    target = "SPX6900"
    amount = 23000
    asyncio.run(trade(source, target, amount))
