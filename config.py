# config.py

API_URL = "https://api.coingecko.com/api/v3/coins"
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
KEYPAIR_FILE = "phantom_keypair.json"

ASSETS = {
    "SOL": {
        "id": "solana",
        "mint": "So11111111111111111111111111111111111111112",
        "decimals": 9,
    },
    "SPX6900": {
        "id": "spx6900",
        "mint": "J3NKxxXZcnNiMjKw9hYb2K4LUxgwB6t1FtPtQVsv3KFr",
        "decimals": 8,  
    },
    "WBTC": {
        "id": "wrapped-bitcoin",
        "mint": "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh",
        "decimals": 8,
    },
    "PEPESOL": {
        "id": "pepesol",
        "mint": "F9CpWoyeBJfoRB8f2pBe2ZNPbPsEE76mWZWme3StsvHK",
        "decimals": 6,  
    },
    "USDC": {
        "id": "usd-coin",
        "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "decimals": 6,
    }
}
