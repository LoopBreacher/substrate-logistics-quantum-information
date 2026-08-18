# ==============================================================================
# SUBSTRATE LOGISTICS: QUANTUM DEPHASING & FIDELITY SIMULATION (QuTiP)
# ==============================================================================

import numpy as np
import matplotlib.pyplot as plt

# Auto-install QuTiP in Google Colab environment
try:
    from qutip import qeye, sigmaz, basis, mesolve
except ImportError:
    import subprocess, sys
    print("Installing QuTiP library... (takes ~15 seconds)")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "qutip"])
    from qutip import qeye, sigmaz, basis, mesolve

# --- 1. Substrate Hardware Constants ---
C_delta = 4.72e-4                     # Topological Drag Constant
phi = (1 + np.sqrt(5)) / 2            # Golden Ratio Modulus (1.61803399)
theta_chiral = np.deg2rad(36)         # 36-degree Chiral Twist angle in radians

# First-Order Precision Hardware Bounds
epsilon_floor = C_delta * phi          # 7.63712e-4 (0.00076371)
F_max = 1.0 - epsilon_floor            # 0.999236288 (99.9236%)
gamma_delta = 2 * epsilon_floor        # Dephasing rate: 2 * C_delta * phi = 0.0015274

# --- 2. Quantum Operators & Initial State ---
sz = sigmaz()
I = qeye(2)

# Substrate Jump Operator with 36-degree Chiral Phase Angle
# L_delta = sqrt(C_delta * phi) * exp(i * 36 deg) * sigma_z
L_delta = np.sqrt(C_delta * phi) * np.exp(1j * theta_chiral) * sz

# Initialize qubit in maximum superposition: |+> = (|0> + |1>) / sqrt(2)
psi0 = (basis(2, 0) + basis(2, 1)).unit()
rho0 = psi0 * psi0.dag()               # Density matrix rho(0)

# Track simulation across N = 0 to 1500 execution clock cycles
N_cycles = np.linspace(0, 1500, 1501)
H = 0 * sz                             # Free evolution (no external driving field)

# --- 3. Solve Master Equation ---
result = mesolve(H, rho0, N_cycles, c_ops=[L_delta])

# Calculate Off-Diagonal Coherence (rho_01) and State Fidelity F(N)
coherence = [np.abs(state[0, 1]) for state in result.states]
fidelity = [(1 + 2 * c) / 2 for c in coherence]

# --- 4. Print Diagnostics to Screen ---
print("\n" + "="*58)
print(" SUBSTRATE LOGISTICS QUANTUM TELEMETRY RESULTS")
print("="*58)
print(f"Single-Cycle Error Floor (epsilon_floor) : {epsilon_floor:.6e} (~7.6371e-4)")
print(f"Max Single-Gate Fidelity Ceiling (F_max) : {F_max * 100:.4f}% (~99.9236%)")
print(f"Dephasing Rate (gamma_delta)             : {gamma_delta:.6f} per cycle")
print(f"1/e Coherence Limit (N_1/e)              : {N_cycles[np.argmin(np.abs(np.array(coherence) - 0.5/np.e))]:.0f} cycles")
print(f"1/e^2 Frame Drop Ceiling (N_max)         : {N_cycles[np.argmin(np.abs(np.array(coherence) - 0.5/(np.e**2)))]:.0f} cycles")
print("="*58 + "\n")

# --- 5. Plot Visual Chart ---
plt.figure(figsize=(9.5, 5.5))
plt.plot(N_cycles, fidelity, label='Substrate Metric Fidelity F(N)', color='#1f77b4', linewidth=2.5)

# Benchmark Lines
plt.axhline(F_max, color='#2ca02c', linestyle='-.', linewidth=1.2, 
            label=f'F_max Ceiling ({F_max*100:.2f}%, ε = {epsilon_floor:.4e})')
plt.axhline((1 + 1/np.e) / 2, color='#ff7f0e', linestyle='--', linewidth=1.5, 
            label='1/e Coherence Limit (N ≈ 655)')
plt.axhline((1 + 1/(np.e**2)) / 2, color='#d62728', linestyle=':', linewidth=1.5, 
            label='1/e² Frame Drop Ceiling (N ≈ 1309)')

plt.xlabel('Execution Clock Cycles (N)', fontsize=12)
plt.ylabel('State Fidelity F(N)', fontsize=12)
plt.title('Substrate Logistics: Single-Qubit Dephasing & State Fidelity Decay', fontsize=13, fontweight='bold')
plt.xlim(0, 1500)
plt.ylim(0.5, 1.02)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(fontsize=9.5, loc='upper right')
plt.tight_layout()
plt.show()