"""Study D — address problem 3: 'the wave function becomes a real, observable
quantity, so entanglement + gravity gives faster-than-light signaling.'

Setup (the sharpest version of the article's objection, cf. Eppley–Hannah and
Kent's discussion): Alice (far away) shares an entangled pair with Bob.
Bob holds a massive particle B in a superposition of two locations, correlated
with Alice's qubit A:

    |Psi> = (|0>_A |L>_B + |1>_A |R>_B) / sqrt(2)

A test mass T sits at Bob's site and feels B's gravity. The three signaling
questions are answered by three dynamical models:

(i)  SEMICLASSICAL / MEAN-FIELD SN GRAVITY  (the criticized picture):
     T evolves under the potential of the EXPECTED mass density of B,
     H_T(t) = <Pi_L> V_L + <Pi_R> V_R  with branch potentials V_L != V_R.
     If Alice does nothing, <Pi_L> = 1/2 forever and T sees the average
     potential (one unitary). If Alice measures her qubit, each outcome leaves
     B localized and T sees V_L or V_R (a mixture of two different unitaries).
     A mixture of unitaries != unitary of the average, so rho_T differs at
     O(1) — an instantaneous, distance-independent signal. Problem reproduced.

(ii) STOCHASTIC DP COLLAPSE + OPERATOR-VALUED GRAVITY (Tilloy–Diósi sourcing):
     gravity enters as the OPERATOR  H_int = Pi_L (x) V_L + Pi_R (x) V_R
     (the potential is entangled with B's position), while the DP noise
     decoheres/collapses B's superposition locally at rate lam_DP.
     The ensemble dynamics is the LINEAR Lindblad equation
        drho/dt = -i[H_int, rho] + lam D[sigma_z^B] rho (+ feedback noise),
     so Alice's local trace-preserving map can never change rho_{BT}:
     signal = 0 to machine precision — and per TRAJECTORY the collapse still
     happens (each run ends with B localized), so nothing is lost.

(iii) The same comparison at the trajectory level (Monte-Carlo unraveling):
     ensembles with and without Alice's measurement agree to MC accuracy.

Conclusion demonstrated: the wave function may be ontologically real per
trajectory, but because the noise realization is not controllable and the
ensemble map stays linear, it is NOT an operationally observable quantity —
no cloning, no faster-than-light channel.
"""
import numpy as np

from common import plt, save_figure, save_results

RNG = np.random.default_rng(7)

# Pauli matrices and helpers ------------------------------------------------
I2 = np.eye(2, dtype=complex)
SX = np.array([[0, 1], [1, 0]], dtype=complex)
SY = np.array([[0, -1j], [1j, 0]], dtype=complex)
SZ = np.array([[1, 0], [0, -1]], dtype=complex)


def kron(*ops):
    out = ops[0]
    for o in ops[1:]:
        out = np.kron(out, o)
    return out


def dag(a):
    return a.conj().T


def trace_dist(r1, r2):
    ev = np.linalg.eigvalsh(r1 - r2)
    return 0.5 * float(np.sum(np.abs(ev)))


# Branch potentials felt by the test mass T (v sets Bob's LOCAL gravity;
# crucially the signal in (i) does not decrease with Alice's distance).
V_STRENGTH = 1.0
V_L = V_STRENGTH * SZ
V_R = V_STRENGTH * SX

T_END = 3.0
N_STEPS = 3000
DT = T_END / N_STEPS


# ---------------------------------------------------------------- model (i)
def semiclassical():
    """Mean-field SN gravity on A (x) B (x) T, exact branch evolution.

    Because H only acts on T and <Pi_L> is constant within each branch
    configuration, the evolution integrates exactly to unitaries on T.
    """
    t = np.linspace(0.0, T_END, N_STEPS + 1)
    psi_T0 = np.array([1.0, 0.0], dtype=complex)
    rho_T0 = np.outer(psi_T0, psi_T0.conj())

    def U(H, tt):
        w, v = np.linalg.eigh(H)
        return (v * np.exp(-1j * w * tt)) @ dag(v)

    dist = np.empty_like(t)
    H_avg = 0.5 * (V_L + V_R)
    for i, tt in enumerate(t):
        # no measurement: <Pi_L> = 1/2 for all times -> average potential
        rho_no = U(H_avg, tt) @ rho_T0 @ dag(U(H_avg, tt))
        # Alice measures at t=0: branch L or R with prob 1/2 each
        rho_me = 0.5 * (U(V_L, tt) @ rho_T0 @ dag(U(V_L, tt))
                        + U(V_R, tt) @ rho_T0 @ dag(U(V_R, tt)))
        dist[i] = trace_dist(rho_no, rho_me)
    return t, dist


# --------------------------------------------------------------- model (ii)
def lindblad():
    """DP collapse + operator gravity on A (x) B (x) T (8-dim), RK4.

    Alice's local action (projective sigma_z measurement, or a sigma_x unitary)
    is applied at t = 0.5; rho_BT is compared against the do-nothing protocol.
    """
    lam = 2.0
    Pi_L = np.array([[1, 0], [0, 0]], dtype=complex)
    Pi_R = np.array([[0, 0], [0, 1]], dtype=complex)
    H = kron(I2, Pi_L, V_L) + kron(I2, Pi_R, V_R)
    Lop = kron(I2, SZ, I2) * np.sqrt(lam)

    def rhs(rho):
        return (-1j * (H @ rho - rho @ H)
                + Lop @ rho @ dag(Lop) - 0.5 * (dag(Lop) @ Lop @ rho + rho @ dag(Lop) @ Lop))

    def step(rho):
        k1 = rhs(rho)
        k2 = rhs(rho + 0.5 * DT * k1)
        k3 = rhs(rho + 0.5 * DT * k2)
        k4 = rhs(rho + DT * k3)
        return rho + DT / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)

    # initial entangled state (|0 L> + |1 R>)/sqrt2 (x) |0>_T
    psi = np.zeros(8, dtype=complex)
    psi[0] = 1.0 / np.sqrt(2.0)          # |0 L 0>
    psi[6] = 1.0 / np.sqrt(2.0)          # |1 R 0>
    rho0 = np.outer(psi, psi.conj())

    def alice_measure(rho):
        P0 = kron(np.array([[1, 0], [0, 0]], dtype=complex), I2, I2)
        P1 = kron(np.array([[0, 0], [0, 1]], dtype=complex), I2, I2)
        return P0 @ rho @ P0 + P1 @ rho @ P1

    def alice_unitary(rho):
        Ua = kron((np.cos(0.7) * I2 - 1j * np.sin(0.7) * SX), I2, I2)
        return Ua @ rho @ dag(Ua)

    def rho_BT(rho):
        r = rho.reshape(2, 4, 2, 4)
        return np.einsum("iaib->ab", r)

    t = np.linspace(0.0, T_END, N_STEPS + 1)
    t_act = 0.5
    runs = {"none": None, "measure": alice_measure, "unitary": alice_unitary}
    traces = {}
    for name, action in runs.items():
        rho = rho0.copy()
        out = [rho_BT(rho)]
        for i in range(N_STEPS):
            if action is not None and abs(t[i] - t_act) < 0.5 * DT:
                rho = action(rho)
            rho = step(rho)
            out.append(rho_BT(rho))
        traces[name] = out
    d_meas = np.array([trace_dist(a, b) for a, b in zip(traces["none"], traces["measure"])])
    d_unit = np.array([trace_dist(a, b) for a, b in zip(traces["none"], traces["unitary"])])
    return t, d_meas, d_unit


# -------------------------------------------------------------- model (iii)
def trajectories(n_traj=4000, n_steps=6000):
    """Trajectory-level comparison of two collapse prescriptions.

    B's branch weight collapses under the DP SDE  dP = 4 sqrt(lam) P(1-P) dW.
    Alice's measured ensemble is EXACTLY  1/2 rho_L(t) + 1/2 rho_R(t)  (each
    outcome leaves B localized, then T rotates under V_L or V_R). The
    no-measurement ensemble is estimated by Monte-Carlo for two ways of
    sourcing gravity from the collapsing state:

    (a) NAIVE mean-field sourcing:  H_T = P(t) V_L + (1-P(t)) V_R per
        trajectory — collapse tames the semiclassical signal but a transient
        nonlinear residual survives (vanishing as lam grows);
    (b) OPERATOR (Tilloy–Diósi) sourcing: the trajectory state stays
        branch-entangled, |chi> = c_L |L, psi_L> + c_R |R, psi_R>, so
        rho_T = P(t) rho_L(t) + (1-P(t)) rho_R(t); the martingale property
        E[P(t)] = 1/2 makes the ensembles agree exactly (MC noise only).
    """
    dt_tr = T_END / n_steps
    t_grid = np.linspace(0.0, T_END, n_steps + 1)
    rec_every = 100
    t_rec = t_grid[::rec_every]

    def U(H, tt):
        w, v = np.linalg.eigh(H)
        return (v * np.exp(-1j * w * tt)) @ dag(v)

    psi0 = np.array([1.0, 0.0], dtype=complex)
    rho_L = [U(V_L, tt) @ np.outer(psi0, psi0.conj()) @ dag(U(V_L, tt)) for tt in t_rec]
    rho_R = [U(V_R, tt) @ np.outer(psi0, psi0.conj()) @ dag(U(V_R, tt)) for tt in t_rec]
    rho_measured = [0.5 * (a + b) for a, b in zip(rho_L, rho_R)]

    out = {}
    for lam in (2.0, 10.0):
        P = np.full(n_traj, 0.5)
        psi = np.tile(psi0, (n_traj, 1))            # variant (a) per-trajectory T state
        d_naive, d_oper = [], []
        for k in range(n_steps + 1):
            if k % rec_every == 0:
                rho_a = np.einsum("ti,tj->ij", psi, psi.conj()) / n_traj
                idx = k // rec_every
                d_naive.append(trace_dist(rho_a, rho_measured[idx]))
                pbar = P.mean()
                rho_b = pbar * rho_L[idx] + (1.0 - pbar) * rho_R[idx]
                d_oper.append(trace_dist(rho_b, rho_measured[idx]))
            if k == n_steps:
                break
            # variant (a): exact one-step rotation under H = v (n . sigma)
            nx, nz = V_STRENGTH * (1.0 - P), V_STRENGTH * P
            nn = np.sqrt(nx**2 + nz**2)
            th = nn * dt_tr
            c, s = np.cos(th), np.sin(th) / np.maximum(nn, 1e-300)
            a0, a1 = psi[:, 0].copy(), psi[:, 1].copy()
            psi[:, 0] = c * a0 - 1j * s * (nz * a0 + nx * a1)
            psi[:, 1] = c * a1 - 1j * s * (nx * a0 - nz * a1)
            # DP collapse of B's branch weight
            dW = RNG.standard_normal(n_traj) * np.sqrt(dt_tr)
            P = np.clip(P + 4.0 * np.sqrt(lam) * P * (1.0 - P) * dW, 0.0, 1.0)
        out[lam] = (np.array(d_naive), np.array(d_oper))
    return t_rec, out, n_traj


def main():
    print("== Study D: no-signaling ==")
    t1, d_semi = semiclassical()
    print(f"(i) semiclassical mean-field: max signal (trace distance) = {d_semi.max():.4f}")

    t2, d_meas, d_unit = lindblad()
    print(f"(ii) DP-Lindblad: max signal, Alice measures = {d_meas.max():.3e}")
    print(f"(ii) DP-Lindblad: max signal, Alice unitary  = {d_unit.max():.3e}")

    t3, mc, n_traj = trajectories()
    mc_expected = 0.5 / np.sqrt(n_traj)
    for lam, (d_naive, d_oper) in mc.items():
        print(f"(iii) lam={lam}: naive mean-field sourcing max residual = {d_naive.max():.4f}; "
              f"operator (TD) sourcing max residual = {d_oper.max():.4f} "
              f"(MC noise ~ {mc_expected:.4f})")

    save_results("study_d_no_signaling", {
        "t_end": T_END,
        "semiclassical_max_signal": float(d_semi.max()),
        "lindblad_max_signal_measure": float(d_meas.max()),
        "lindblad_max_signal_unitary": float(d_unit.max()),
        "mc_n_traj": n_traj,
        "mc_noise_scale": float(mc_expected),
        "mc_max_residual": {f"lam={lam}": {"naive_meanfield": float(dn.max()),
                                           "operator_TD": float(do.max())}
                            for lam, (dn, do) in mc.items()},
        "t_semiclassical": t1.tolist(), "signal_semiclassical": d_semi.tolist(),
        "t_lindblad": t2.tolist(),
        "signal_lindblad_measure": d_meas.tolist(),
        "signal_lindblad_unitary": d_unit.tolist(),
        "t_mc": t3.tolist(),
        "signal_mc": {f"lam={lam}": {"naive_meanfield": dn.tolist(),
                                     "operator_TD": do.tolist()}
                      for lam, (dn, do) in mc.items()},
    })

    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.6))
    ax = axes[0]
    ax.plot(t1, d_semi, color="tab:red", label="mean-field SN gravity, no collapse (i)")
    for lam, col in zip(mc, ["tab:purple", "tab:brown"]):
        ax.plot(t3, mc[lam][0], color=col, ls="--",
                label=f"mean-field + DP collapse, $\\lambda={lam:g}$ (iii-a)")
    ax.plot(t3, mc[2.0][1], ".", ms=4, color="tab:orange",
            label="operator (Tilloy–Diósi) sourcing (iii-b)")
    ax.axhspan(0, mc_expected, color="tab:orange", alpha=0.15, label="MC noise floor")
    ax.set(xlabel="$t$", ylabel=r"signal $D(\rho_T^{\rm no},\rho_T^{\rm meas})$",
           title="(a) Alice measures vs not: effect on Bob")
    ax.legend(fontsize=7)

    ax = axes[1]
    ax.semilogy(t2, np.maximum(d_meas, 1e-18), color="tab:blue",
                label="Alice measures (DP-Lindblad)")
    ax.semilogy(t2, np.maximum(d_unit, 1e-18), ls="--", color="tab:green",
                label="Alice applies unitary (DP-Lindblad)")
    ax.axhline(1e-15, color="tab:gray", ls=":", label="machine precision")
    ax.set(xlabel="$t$", ylabel="signal (trace distance)", ylim=(1e-18, 1),
           title="(b) linear ensemble dynamics: signal $= 0$")
    ax.legend()
    fig.suptitle("Study D — mean-field SN gravity signals; the stochastic completion does not", y=1.03)
    save_figure(fig, "fig_d_no_signaling")


if __name__ == "__main__":
    main()
