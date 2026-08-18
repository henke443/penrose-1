"""Study C — address problem 2: the Born rule is a THEOREM of the stochastic
(Diósi–Penrose-type) collapse dynamics, not an extra assumption.

The norm-preserving collapse SDE (Itô form) for a Hermitian collapse operator A
with localization rate lambda (fixed, in the DP model, by Penrose's gravitational
self-energy criterion lambda ~ Delta E_G / hbar):

    d|psi> = [ -i H dt + sqrt(lam) (A - <A>) dW - (lam/2) (A - <A>)^2 dt ] |psi>

For a two-branch superposition  psi = c_L |L> + c_R |R>  with A|L>=+|L>,
A|R>=-|R>, H=0 (branches energetically degenerate), Itô calculus gives the
closed equation for the branch weight P = |c_L|^2:

    dP = 4 sqrt(lam) P (1 - P) dW              (*)

  * P is a MARTINGALE:  E[P(t)] = P(0) for all t.
  * The fixed points are P=0 and P=1, reached almost surely.
  * Therefore Prob(collapse to L) = P(0) = |c_L(0)|^2  — exactly Born's rule.

This script verifies the theorem numerically two independent ways:
  (1) the exact scalar reduction (*), Euler–Maruyama;
  (2) the full two-component state SDE with renormalization (integrator-level
      cross-check, no use of the analytic reduction).
"""
import numpy as np

from common import plt, save_figure, save_results

RNG = np.random.default_rng(20260818)
LAM = 1.0
T_END = 8.0
DT = 5e-4
N_TRAJ = 20000
P0_LIST = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]


def run_scalar(p0, n_traj=N_TRAJ, record=False):
    """Euler–Maruyama on dP = 4 sqrt(lam) P(1-P) dW."""
    n_steps = int(round(T_END / DT))
    snap_steps = {int(round(tv / DT)): tv for tv in (0.05, 0.2, 1.0)}
    P = np.full(n_traj, p0)
    means = [P.mean()] if record else None
    snapshots = {}
    for step in range(n_steps):
        dW = RNG.standard_normal(n_traj) * np.sqrt(DT)
        P = np.clip(P + 4.0 * np.sqrt(LAM) * P * (1.0 - P) * dW, 0.0, 1.0)
        if record and (step + 1) % 200 == 0:
            means.append(P.mean())
        if record and (step + 1) in snap_steps:
            snapshots[snap_steps[step + 1]] = P.copy()
    return P, means, snapshots


def run_state_sde(p0, n_traj=4000):
    """Full 2-component SDE d|psi> with renormalization each step."""
    n_steps = int(round(T_END / DT))
    c = np.empty((n_traj, 2), dtype=complex)
    c[:, 0] = np.sqrt(p0)
    c[:, 1] = np.sqrt(1.0 - p0)
    a = np.array([1.0, -1.0])
    for _ in range(n_steps):
        P = np.abs(c[:, 0]) ** 2
        meanA = 2.0 * P - 1.0
        dW = RNG.standard_normal(n_traj)[:, None] * np.sqrt(DT)
        dev = a[None, :] - meanA[:, None]
        c = c * np.exp(np.sqrt(LAM) * dev * dW - LAM * dev**2 * DT)
        c /= np.linalg.norm(c, axis=1, keepdims=True)
    return np.abs(c[:, 0]) ** 2


def main():
    print("== Study C: Born rule from the collapse SDE ==")
    freqs, errs, freqs_state, resolved_fracs = [], [], [], []
    martingale_curve = None
    hist_snapshots = None
    for p0 in P0_LIST:
        record = abs(p0 - 0.3) < 1e-9
        P_fin, means, snaps = run_scalar(p0, record=record)
        resolved = np.mean(np.minimum(P_fin, 1.0 - P_fin) < 1e-3)
        resolved_fracs.append(float(resolved))
        f = float(np.mean(P_fin > 0.5))
        e = float(np.sqrt(f * (1 - f) / len(P_fin)))
        freqs.append(f)
        errs.append(e)
        if record:
            martingale_curve = means
            hist_snapshots = snaps
        P_fin_state = run_state_sde(p0)
        freqs_state.append(float(np.mean(P_fin_state > 0.5)))
        print(f"p0={p0:.1f}: scalar freq={f:.4f}+-{e:.4f}  state-SDE freq={freqs_state[-1]:.4f}"
              f"  resolved={resolved:.4f}")

    freqs, errs = np.array(freqs), np.array(errs)
    chi2 = float(np.sum((freqs - np.array(P0_LIST)) ** 2 / errs**2))
    max_dev_sigma = float(np.max(np.abs(freqs - np.array(P0_LIST)) / errs))
    mart_drift = float(abs(martingale_curve[-1] - martingale_curve[0]))
    print(f"chi2 (9 dof) = {chi2:.2f}, max deviation = {max_dev_sigma:.2f} sigma, "
          f"martingale drift |E[P](T)-P0| = {mart_drift:.5f}")

    save_results("study_c_born_rule", {
        "lambda": LAM, "t_end": T_END, "dt": DT, "n_traj_scalar": N_TRAJ,
        "p0": P0_LIST, "freq_scalar": freqs.tolist(), "freq_err": errs.tolist(),
        "freq_state_sde": freqs_state,
        "chi2_9dof": chi2, "max_deviation_sigma": max_dev_sigma,
        "martingale_drift": mart_drift,
        "resolved_frac": resolved_fracs, "min_resolved_frac": min(resolved_fracs),
    })

    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.4))
    ax = axes[0]
    ts = np.array([0.05, 0.2, 1.0])
    colors = ["tab:blue", "tab:orange", "tab:red"]
    for tval, col in zip(ts, colors):
        ax.hist(hist_snapshots[tval], bins=60, range=(0, 1), density=True,
                histtype="step", color=col, label=f"$t={tval}$")
    ax.set(xlabel=r"branch weight $P_L$", ylabel="density", yscale="log",
           title=r"(a) weights migrate to $\{0,1\}$ ($P_0=0.3$)")
    ax.legend()

    ax = axes[1]
    tm = np.linspace(0, T_END, len(martingale_curve))
    ax.plot(tm, martingale_curve, color="tab:blue")
    ax.axhline(0.3, color="tab:red", ls="--", label=r"$P_0=0.3$")
    ax.set(xlabel="$t$", ylabel=r"$\mathbb{E}[P_L(t)]$", ylim=(0.27, 0.33),
           title="(b) martingale property")
    ax.legend()

    ax = axes[2]
    ax.errorbar(P0_LIST, freqs, yerr=errs, fmt="o", ms=4, capsize=3,
                color="tab:blue", label="scalar SDE (20k traj.)")
    ax.plot(P0_LIST, freqs_state, "s", ms=4, mfc="none", color="tab:orange",
            label="full state SDE (4k traj.)")
    ax.plot([0, 1], [0, 1], "--", color="tab:red", label=r"Born rule $|c_L|^2$")
    ax.set(xlabel=r"initial weight $|c_L(0)|^2$", ylabel="collapse frequency to $L$",
           title=f"(c) Born rule emerges ($\\chi^2$={chi2:.1f}/9 dof)")
    ax.legend()
    fig.suptitle("Study C — Born rule as a theorem of stochastic Diósi–Penrose collapse", y=1.03)
    save_figure(fig, "fig_c_born_rule")


if __name__ == "__main__":
    main()
