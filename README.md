# 🧠💸 dapp-capstone-quantum-buying-bot

This capstone project is a quantum-enhanced decentralized application (DApp) that optimizes crypto token swaps on the **Solana** blockchain using **Qiskit's Variational Quantum Eigensolver (VQE)**. The application interacts with the **Jupiter Aggregator SDK** (an automated market maker aggregator) and securely signs transactions via **Phantom Wallet**. Real-time token prices and variation data are fetched through the **CoinGecko API**.

---

## 🚀 How it works

The bot continuously runs in a loop (`bot.py`) that performs the following steps:

1. **Fetches the wallet status** for a predefined set of tradable tokens:  
   `["USDC", "PEPESOL", "SPX6900", "WBTC"]`  
   The native token `SOL` is used **only to pay transaction fees**.

2. **Retrieves recent price variations** for the listed tokens via the CoinGecko API.

3. **Applies a Variational Quantum Eigensolver (VQE)** to determine the most promising asset allocation based on market dynamics.

4. **Executes the token swap** using the **Jupiter Aggregator SDK** (Solana AMM).

5. Repeats the process to maintain an optimized portfolio.

---

## ⚙️ Setup Instructions

1. **Clone the repository**:

```bash
git clone https://github.com/your-username/dapp-capstone-quantum-buying-bot.git
cd dapp-capstone-quantum-buying-bot
```

2. **(Optional but recommended) Create a virtual environment**:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Python dependencies**:

```bash
pip install -r requirements.txt
```

4. **Configure Phantom Wallet credentials**:  
   Export your Phantom wallet's keypair and save it as:

```
phantom-pair.json
```

Place this file in the root directory of the project.

5. **Set your CoinGecko API key**:  
   Open the file `data_fetcher.py` and locate the line:

```python
COINGECKO_API_KEY = "your-api-key-here"
```

Replace `"your-api-key-here"` with your actual CoinGecko API key.

---

## 🧠 Run the Bot

Launch the bot using:

```bash
python3 bot.py
```

The bot will begin analyzing your wallet and market data, and execute swaps based on quantum optimization.

---

## 🛠 Tech Stack

- 🧪 Qiskit (VQE) — quantum optimization algorithm  
- 🔗 Solana Blockchain  
- 🔄 Jupiter Aggregator SDK — token swap routing  
- 👛 Phantom Wallet — transaction signing  
- 📊 CoinGecko API — real-time crypto pricing  
- 🐍 Python  

---

## 📄 License

This project is released under the MIT License.
