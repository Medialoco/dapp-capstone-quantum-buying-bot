import numpy as np
import asyncio
from wallet_content import get_wallet_info, WALLET_ADDRESS
from data_fetcher import get_crypto_trends
from solana_trader import trade

from qiskit_aer import AerSimulator
from qiskit.circuit.library import RealAmplitudes
from qiskit.quantum_info import SparsePauliOp
from qiskit_algorithms import VQE
from qiskit_algorithms.optimizers import COBYLA
from qiskit.primitives import BackendEstimator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

MIN_USD_THRESHOLD = 1

THRESHOLDS = {
    "WBTC": {"up": 0.5, "down": -0.2},
    "PEPESOL": {"up": 1, "down": -0.4},
    "SPX6900": {"up": 0.9, "down": -0.14},
    "USDC": {"up": 0.05, "down": -0.05},
}

USE_QUANTUM = False  
THEORETICAL_WALLET = ["USDC", "WBTC", "PEPESOL", "SPX6900"]

def analyze_and_trade():
    wallet = get_wallet_info(WALLET_ADDRESS)
    trends = get_crypto_trends()

    print("\n. . . . . . . . . . . . ")
    print("Wallet status:", wallet)
    print("Crypto trends:", trends)
    print(". . . . . . . . . . . . ")

    wallet_amount = sum(wallet.get(asset, 0) * trends[asset]['current_price'] for asset in THEORETICAL_WALLET if asset in trends)

    print("\n* * * * * * * * * * * * * * * * * * * * * * * *")
    print("Wallet in US dollars (without SOL):", wallet_amount)
    print("* * * * * * * * * * * * * * * * * * * * * * * *\n")

    obvious_swap = detect_obvious_swap(wallet, trends)

    if obvious_swap:
        source, target, amount = obvious_swap
        if "SOL" in (source, target):
            print(f"⛔ Swap involving SOL is not allowed: {source} → {target}")
            return
        source_value_usd = amount * trends[source]['current_price']
        if source_value_usd < MIN_USD_THRESHOLD:
            print(f"⚠️ Swap cancelled: {source} value too low (${source_value_usd:.6f} USD).")
        else:
            print(f"✅ Executing obvious swap: {source} → {target} ({amount:.4f})")
            asyncio.run(trade(source, target, amount))
    else:
        print("🔍 No obvious swap found, proceeding with analysis...")
        if USE_QUANTUM:
            quantum_swap(wallet, trends)
        else:
            classical_swap(wallet, trends)

def detect_variation(asset, trends):
    return trends.get(asset, {}).get('1h', 0.0)

def detect_obvious_swap(wallet, trends):
    for asset in THEORETICAL_WALLET:
        if asset == "SOL" or asset not in wallet:
            continue
        balance = wallet[asset]
        variation = detect_variation(asset, trends)
        if asset in THRESHOLDS and variation <= THRESHOLDS[asset]["down"]:
            print(f"🚨 Obvious swap detected: {asset} dropping significantly ({variation:.2f}%).")
            return asset, "USDC", balance
    return None



def quantum_swap(wallet, trends):
    print("⚛️ Performing quantum-based trading decision (with VQE)...")

    SELECTED_ASSETS = THEORETICAL_WALLET
    TOP_VARIATION_THRESHOLD = 2.0

    valid_assets = []
    for asset in SELECTED_ASSETS:
        if asset == "SOL":
            continue
        if asset in trends:
            usd_value = wallet.get(asset, 0) * trends[asset]['current_price']
            variation = trends[asset].get('1h', 0.0)
            if usd_value > MIN_USD_THRESHOLD or variation >= TOP_VARIATION_THRESHOLD:
                valid_assets.append(asset)

    print(f"✅ Valid assets for quantum analysis: {valid_assets}")

    if len(valid_assets) < 2:
        print("⚠️ Not enough assets for a quantum swap.")
        return

    variations = np.array([trends[asset].get('1h', 0.0) for asset in valid_assets])
    print(f"📊 1h Variations: {dict(zip(valid_assets, variations))}")

    num_assets = len(valid_assets)
    pauli_terms = [("".join(["Z" if i == j else "I" for i in range(num_assets)]), -variations[j]) for j in range(num_assets)]
    print(f"🧮 Pauli terms for cost operator: {pauli_terms}")

    cost_operator = SparsePauliOp.from_list(pauli_terms)
    ansatz = RealAmplitudes(num_qubits=num_assets, reps=1)

    backend = AerSimulator()
    estimator = BackendEstimator(backend=backend)
    vqe = VQE(ansatz=ansatz, optimizer=COBYLA(), estimator=estimator)

    try:
        print("🚀 Starting VQE computation...")
        result = vqe.compute_minimum_eigenvalue(cost_operator)
        print("✅ VQE computation completed successfully!")
    except Exception as e:
        print(f"⚠️ Error during VQE computation: {e}")
        return

    optimal_parameters = result.optimal_point
    print(f"📌 Optimal parameters found by VQE: {optimal_parameters}")

    qc = ansatz.assign_parameters(optimal_parameters)
    qc.measure_all()

    print("🧪 Quantum circuit with measurements:")
    print(qc.draw(output='text'))

    from qiskit.primitives import Sampler
    sampler = Sampler()
    sampled = sampler.run(qc).result()
    counts = sampled.quasi_dists[0]

    print(f"📈 Measurement results (quasi-distribution):")
    for bitstring, prob in counts.items():
        print(f"  {format(bitstring, f'0{num_assets}b')} → {prob:.4f}")

    top_key = max(counts.items(), key=lambda x: x[1])[0]
    top_bitstring = format(top_key, f'0{num_assets}b')
    print(f"🏆 Most probable bitstring: {top_bitstring}")

    zero_indices = [i for i, bit in enumerate(top_bitstring[::-1]) if bit == '0']
    one_indices = [i for i, bit in enumerate(top_bitstring[::-1]) if bit == '1']

    print(f"🔍 Qubits measured to 0: {zero_indices}")
    print(f"🔍 Qubits measured to 1: {one_indices}")

    if not zero_indices or not one_indices:
        print("⚠️ Quantum state suggests no profitable reallocation.")
        return

    source_asset = valid_assets[zero_indices[0]]
    target_asset = valid_assets[one_indices[0]]

    print(f"💱 Proposed quantum swap: {source_asset} → {target_asset}")

    if "SOL" in (source_asset, target_asset):
        print(f"⛔ Swap involving SOL is not allowed: {source_asset} → {target_asset}")
        return

    if source_asset in THRESHOLDS and target_asset in THRESHOLDS:
        diff = variations[valid_assets.index(target_asset)] - variations[valid_assets.index(source_asset)]
        threshold_diff = max(THRESHOLDS[target_asset]["up"], abs(THRESHOLDS[source_asset]["down"]))
        print(f"📏 Variation diff: {diff:.4f} / Threshold: {threshold_diff:.4f}")
        if diff > threshold_diff:
            amount = wallet.get(source_asset, 0) * 0.5
            print(f"✅ Quantum recommendation: Swap {amount:.4f} {source_asset} → {target_asset}")
            asyncio.run(trade(source_asset, target_asset, amount))
        else:
            print("⚠️ Quantum analysis indicates no beneficial swap at this time.")




def classical_swap(wallet, trends):
    print("🔬 Performing classical-based trading decision...")
    TOP_VARIATION_THRESHOLD = 2.0

    valid_assets = []
    for asset in THEORETICAL_WALLET:
        if asset == "SOL" or asset not in trends:
            continue
        usd_value = wallet.get(asset, 0) * trends[asset]['current_price']
        variation = trends[asset].get('1h', 0.0)
        if usd_value > MIN_USD_THRESHOLD or variation >= TOP_VARIATION_THRESHOLD:
            valid_assets.append(asset)

    if len(valid_assets) < 2:
        print("⚠️ Not enough valid assets for classical swap.")
        return

    variations = np.array([trends[asset].get('1h', 0.0) for asset in valid_assets])
    best_asset_index = np.argmax(variations)
    worst_asset_index = np.argmin(variations)

    source_asset = valid_assets[worst_asset_index]
    target_asset = valid_assets[best_asset_index]

    if "SOL" in (source_asset, target_asset):
        print(f"⛔ Swap involving SOL is not allowed: {source_asset} → {target_asset}")
        return

    diff = variations[best_asset_index] - variations[worst_asset_index]
    threshold_diff = max(THRESHOLDS[target_asset]["up"], abs(THRESHOLDS[source_asset]["down"]))

    if source_asset in wallet and source_asset in THRESHOLDS and target_asset in THRESHOLDS and diff > threshold_diff:
        amount = wallet[source_asset] * 0.5
        source_value_usd = amount * trends[source_asset]['current_price']
        if source_value_usd < MIN_USD_THRESHOLD:
            print(f"⚠️ Classical swap cancelled: {source_asset} value too low (${source_value_usd:.6f} USD).")
        elif amount > 0:
            print(f"⚛️ Classical recommendation: Swap {amount:.4f} {source_asset} → {target_asset}")
            asyncio.run(trade(source_asset, target_asset, amount))
        else:
            print("⚠️ Not enough balance for a meaningful classical swap.")
    else:
        print("⚠️ Classical analysis indicates no beneficial swap at this time.")

if __name__ == "__main__":
    analyze_and_trade()