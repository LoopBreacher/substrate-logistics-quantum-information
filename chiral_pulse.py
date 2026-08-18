# ==============================================================================
# SUBSTRATE LOGISTICS: CHIRAL PHASE COMPENSATION SIMULATION (QuTiP)
# ==============================================================================

import matplotlib.pyplot as plt
import numpy as np

# Auto-install QuTiP in Google Colab environment
try:
    from qutip import basis, mesolve, qeye, sigmaz
except ImportError:
    import subprocess, sys

    print("Installing QuTiP library... (takes ~15 seconds)")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "qutip"])
    from qutip import basis, mesolve, qeye, sigmaz

# --- 1. Substrate Hardware Constants ---
C_delta = 4.72e-4  # Topological Drag Constant
phi = (1 + np.sqrt(5)) / 2  # Golden Ratio Modulus (1.618034)
theta_chiral = np.deg2rad(36)  # 36-degree Chiral Twist angle in radians

# --- 2. Operators & Initial Target State |+> ---
sz = sigmaz()
I = qeye(2)

psi_target = (basis(2, 0) + basis(2, 1)).unit()
rho_target = psi_target * psi_target.dag()

# Coherent Chiral Drift Hamiltonian (36 degrees precession per cycle)
H_chiral = (theta_chiral / 2) * sz

# Stochastic Substrate Jump Operator
L_delta = np.sqrt(C_delta * phi) * sz

# Active R_z(-36 deg) Counter-Rotation Operator: exp(+i * theta_chiral/2 * sigma_z)
Rz_compensate = (1j * (theta_chiral / 2) * sz).expm()

# --- 3. Step-by-Step Cycle Simulation (1500 Cycles) ---
N_steps = 1500
dt_cycle = [0, 1]  # 1 clock cycle evolution per step

rho_uncompensated = rho_target.copy()
rho_compensated = rho_target.copy()

fidelities_uncomp = [1.0]
fidelities_comp = [1.0]

for n in range(1, N_steps + 1):
    # --- Uncompensated Evolution ---
    # Evolves under both Coherent Chiral Drift AND Stochastic Dephasing
    res_uncomp = mesolve(H_chiral, rho_uncompensated, dt_cycle, c_ops=[L_delta])
    rho_uncompensated = res_uncomp.states[-1]
    f_uncomp = (
        (rho_target * rho_uncompensated).tr().real
    )  # State Fidelity vs Initial |+> Target
    fidelities_uncomp.append(f_uncomp)

    # --- Compensated Evolution ---
    # 1. Evolve under Coherent Drift + Dephasing
    res_comp = mesolve(H_chiral, rho_compensated, dt_cycle, c_ops=[L_delta])
    rho_step = res_comp.states[-1]

    # 2. Apply Active R_z(-36 deg) Chiral Counter-Pulse: U * rho * U_dag
    rho_compensated = Rz_compensate * rho_step * Rz_compensate.dag()

    f_comp = (rho_target * rho_compensated).tr().real
    fidelities_comp.append(f_comp)

# --- 4. Print Telemetry Summary ---
print("\n" + "=" * 60)
print(" CHIRAL PHASE COMPENSATION TELEMETRY RESULTS")
print("=" * 60)
print(f"Uncompensated Fidelity at Cycle 10  : {fidelities_uncomp[10]:.4f}")
print(f"Compensated Fidelity at Cycle 10    : {fidelities_comp[10]:.4f}")
print(f"Uncompensated Fidelity at Cycle 25  : {fidelities_uncomp[25]:.4f}")
print(f"Compensated Fidelity at Cycle 25    : {fidelities_comp[25]:.4f}")
print(f"Uncompensated Fidelity at Cycle 75  : {fidelities_uncomp[75]:.4f}")
print(f"Compensated Fidelity at Cycle 75    : {fidelities_comp[75]:.4f}")
print(f"Uncompensated Fidelity at Cycle 100  : {fidelities_uncomp[100]:.4f}")
print(f"Compensated Fidelity at Cycle 100    : {fidelities_comp[100]:.4f}")
print(f"Uncompensated Fidelity at Cycle 655  : {fidelities_uncomp[655]:.4f}")
print(f"Compensated Fidelity at Cycle 655    : {fidelities_comp[655]:.4f}")
print(f"Uncompensated Fidelity at Cycle 1309 : {fidelities_uncomp[1309]:.4f}")
print(f"Compensated Fidelity at Cycle 1309   : {fidelities_comp[1309]:.4f}")
print("=" * 60 + "\n")

# --- 5. Visual Chart ---
plt.figure(figsize=(10, 5))
plt.plot(
    fidelities_uncomp,
    label="Uncompensated (Coherent Drift + Dephasing)",
    color="#d62728",
    linewidth=2,
)
plt.plot(
    fidelities_comp,
    label="Active R_z(-36°) Chiral Compensated",
    color="#2ca02c",
    linewidth=2.5,
)

plt.axhline(
    (1 + 1 / np.e) / 2,
    color="#ff7f0e",
    linestyle="--",
    linewidth=1.2,
    label="1/e Coherence Limit",
)
plt.axhline(
    (1 + 1 / (np.e**2)) / 2,
    color="#7f7f7f",
    linestyle=":",
    linewidth=1.2,
    label="1/e² Frame Drop Ceiling",
)

plt.xlabel("Execution Clock Cycles (N)", fontsize=12)
plt.ylabel("Fidelity relative to target |+> state", fontsize=12)
plt.title(
    "QuTiP Simulation: Active Chiral Pulse Shaping vs Uncompensated Drift",
    fontsize=13,
    fontweight="bold",
)
plt.xlim(0, 1500)
plt.ylim(0.4, 1.02)
plt.grid(True, linestyle="--", alpha=0.5)
plt.legend(fontsize=10, loc="upper right")
plt.tight_layout()
plt.show()