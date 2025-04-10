from solana.rpc.api import Client
from solders.pubkey import Pubkey
from solana.rpc.types import TokenAccountOpts

# Configuration
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
WALLET_ADDRESS = "9Ca3mGaQzJdw52aGywzfP3KuwcrDv41SX6efCgtj5vZ6"

# Connexion to cluster Solana
client = Client(SOLANA_RPC_URL)

mint_to_symbol = {
    "F9CpWoyeBJfoRB8f2pBe2ZNPbPsEE76mWZWme3StsvHK": "PEPESOL",
    "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh": "WBTC",
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "USDC",
    "J3NKxxXZcnNiMjKw9hYb2K4LUxgwB6t1FtPtQVsv3KFr": "SPX6900", 
}


def get_wallet_info(wallet_address):
    pubkey = Pubkey.from_string(wallet_address)
    return_dict = {}

    try:
        balance_response = client.get_balance(pubkey)
        sol_balance = balance_response.value / 1e9
        return_dict["SOL"] = sol_balance
    except Exception as e:
        print(f"⚠️ Error fetching SOL balance: {e}")

    # Tokens SPL
    opts = TokenAccountOpts(program_id=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"))
    try:
        token_accounts_response = client.get_token_accounts_by_owner(pubkey, opts)
        tokens = token_accounts_response.value
    except Exception as e:
        print(f"⚠️ Error fetching token accounts: {e}")
        return return_dict

    for token in tokens:
        account_pubkey = token.pubkey

        try:
            token_info = client.get_token_account_balance(account_pubkey)
            account_data = client.get_account_info(account_pubkey)
        except Exception as e:
            print(f"⚠️ Error accessing token info or account data for {account_pubkey}: {e}")
            continue

        if account_data.value is None:
            continue

        try:
            data = account_data.value.data
            mint = str(Pubkey.from_bytes(data[:32]))
        except Exception as e:
            print(f"⚠️ Error decoding mint for {account_pubkey}: {e}")
            continue

        if mint in mint_to_symbol:
            symbol = mint_to_symbol[mint]
            try:
                ui_amount = float(token_info.value.ui_amount_string)
                if ui_amount:
                    return_dict[symbol] = ui_amount
            except Exception as e:
                print(f"⚠️ Error reading balance for {symbol}: {e}")
                continue

    return return_dict


if __name__ == "__main__":
    print(f"Check Wallet: {WALLET_ADDRESS}")
    wallet_info = get_wallet_info(WALLET_ADDRESS)
    print(wallet_info)
