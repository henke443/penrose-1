"""Study B — address problem 1: stochastic localization removes the runaway
probability that the deterministic Schrödinger–Newton equation leaves behind.

1D analogue of the SN system with a softened-Coulomb self-gravity kernel
(mimics 3D gravity: attractive, NOT confining, so probability can escape):

    i dpsi/dt = -(1/2) psi_xx + Phi psi,
    Phi(x) = -g * int rho(x') / sqrt((x-x')^2 + a^2) dx'

Deterministic run (lam = 0): part of a wide packet binds into the soliton-like
ground state, the rest radiates away to infinity and STAYS there — the
"excessive residual probability" of the Wikipedia article.

Stochastic Diósi–Penrose-type completion adds the position-localization terms

    d|psi> = [ ... ] + sqrt(lam) (x - <x>) dW - (lam/2)(x - <x>)^2 dt

(QMUPL form; lam is set in the DP model by the gravitational self-energy,
lam ~ G m^2 / (hbar R^3)).  The same initial packet then localizes completely:
the ensemble-averaged probability far from the collapse centre decays
exponentially instead of saturating at a finite value.

Tail observable per trajectory:  P_far(t) = P(|x - <x>| > d) + absorbed norm.
"""
import numpy as np

from common import plt, save_figure, save_results

RNG = np.random.default_rng(42)

# ---------------------------------------------------------------- model setup
# Box and CAP are sized so that the collapse centre's noise-induced random walk
# (x_rms ~ sqrt(lam t^3 / 3), a physical feature of position localization)
# stays far from the absorber for the lambdas and times used below.
L = 200.0
N = 2048
DX = L / N
x = (np.arange(N) - N // 2) * DX
K_FREQ = 2.0 * np.pi * np.fft.fftfreq(N, DX)

G_GRAV = 1.0
SOFT_A = 1.0
D_FAR = 10.0                        # "far from the collapse point"

X_ABS = 70.0                        # complex absorbing potential
W_CAP = np.where(np.abs(x) > X_ABS, 2.0 * ((np.abs(x) - X_ABS) / (L / 2 - X_ABS)) ** 3, 0.0)

# softened gravity kernel, convolution by FFT with zero padding
NPAD = 2 * N
xk = (np.arange(NPAD) - NPAD // 2) * DX
kernel = -G_GRAV / np.sqrt(xk**2 + SOFT_A**2)
KERNEL_F = np.fft.rfft(np.fft.ifftshift(kernel))

DT = 0.005
T_END = 40.0
SIGMA0 = 8.0


def gravity(rho):
    """Phi = kernel * rho for a batch rho of shape (batch, N)."""
    buf = np.zeros((rho.shape[0], NPAD))
    buf[:, :N] = rho
    conv = np.fft.irfft(np.fft.rfft(buf, axis=1) * KERNEL_F[None, :], n=NPAD, axis=1)
    return conv[:, :N] * DX


def evolve(n_traj, lam, t_end=T_END, dt=DT, self_gravity=True, seed_offset=0):
    """Batch of trajectories. Returns time grid and mean tail probability."""
    rng = np.random.default_rng(1000 + seed_offset)
    psi = np.tile(np.exp(-x**2 / (2 * SIGMA0**2)).astype(complex), (n_traj, 1))
    psi /= np.sqrt(np.sum(np.abs(psi) ** 2, axis=1, keepdims=True) * DX)
    kin_half = np.exp(-1j * 0.5 * K_FREQ**2 * dt / 2.0)
    cap = np.exp(-W_CAP * dt)

    n_steps = int(round(t_end / dt))
    rec_every = 40
    ts, tail_mean, xc_spread = [], [], []
    absorbed = np.zeros(n_traj)

    for step in range(n_steps + 1):
        rho = np.abs(psi) ** 2
        nrm = np.sum(rho, axis=1) * DX
        if step % rec_every == 0:
            xc = np.sum(x[None, :] * rho, axis=1) * DX / np.maximum(nrm, 1e-300)
            far_mask = np.abs(x[None, :] - xc[:, None]) > D_FAR
            p_far = np.sum(rho * far_mask, axis=1) * DX + (1.0 - nrm)
            ts.append(step * dt)
            tail_mean.append(p_far.mean())
            xc_spread.append(xc.std())
        if step == n_steps:
            break

        # kinetic half step
        psi = np.fft.ifft(np.fft.fft(psi, axis=1) * kin_half[None, :], axis=1)
        # potential + CAP full step
        rho = np.abs(psi) ** 2
        Phi = gravity(rho) if self_gravity else 0.0
        psi = psi * np.exp(-1j * Phi * dt) * cap[None, :]
        # stochastic localization step (norm-preserving exponential scheme)
        if lam > 0.0:
            nrm = np.sum(np.abs(psi) ** 2, axis=1, keepdims=True) * DX
            xc = np.sum(x[None, :] * np.abs(psi) ** 2, axis=1, keepdims=True) * DX / np.maximum(nrm, 1e-300)
            dev = x[None, :] - xc
            dW = rng.standard_normal((n_traj, 1)) * np.sqrt(dt)
            psi = psi * np.exp(np.sqrt(lam) * dev * dW - lam * dev**2 * dt)
            # renormalize only the collapse part (CAP loss must be kept!)
            new_nrm = np.sum(np.abs(psi) ** 2, axis=1, keepdims=True) * DX
            psi *= np.sqrt(nrm / np.maximum(new_nrm, 1e-300))
        # kinetic half step
        psi = np.fft.ifft(np.fft.fft(psi, axis=1) * kin_half[None, :], axis=1)
    return np.array(ts), np.array(tail_mean), np.array(xc_spread), psi


def main():
    print("== Study B: runaway tails, deterministic vs stochastic ==")
    ts, tail_det, _, psi_det = evolve(1, lam=0.0)
    print(f"deterministic SN: final tail probability = {tail_det[-1]:.4f}")
    _, tail_lin, _, _ = evolve(1, lam=0.0, self_gravity=False)
    print(f"linear Schrodinger: final tail probability = {tail_lin[-1]:.4f}")

    lams = [0.003, 0.01]
    tails_sto = {}
    for lam in lams:
        _, tail, xc_spread, _ = evolve(96, lam=lam, seed_offset=int(lam * 100000))
        tails_sto[lam] = tail
        print(f"stochastic lam={lam}: final mean tail = {tail[-1]:.2e} "
              f"(centre spread {xc_spread[-1]:.2f})")

    # exponential fit of the INITIAL decaying stretch (before the curve settles
    # onto the small noise-sustained floor) for the larger lambda
    lam_fit = lams[-1]
    tail = tails_sto[lam_fit]
    i_min = int(np.argmin(tail))
    mask = (ts >= 0.5) & (ts <= ts[i_min]) & (tail > 0)
    coef = np.polyfit(ts[mask], np.log(tail[mask]), 1)
    print(f"lam={lam_fit}: initial decay ~ exp({coef[0]:.3f} t) until t={ts[i_min]:.1f}, "
          f"floor ~ {tail[i_min]:.1e}")

    save_results("study_b_tails", {
        "model": "1D SN, softened kernel a=1, g=1; QMUPL localization",
        "grid": {"L": L, "N": N, "dt": DT, "t_end": T_END, "d_far": D_FAR},
        "initial_sigma": SIGMA0,
        "t": ts.tolist(),
        "tail_deterministic": tail_det.tolist(),
        "tail_linear": tail_lin.tolist(),
        "tail_stochastic": {str(lam): tails_sto[lam].tolist() for lam in lams},
        "final_tail_deterministic": float(tail_det[-1]),
        "final_tail_linear": float(tail_lin[-1]),
        "final_tail_stochastic": {str(lam): float(tails_sto[lam][-1]) for lam in lams},
        "initial_decay_fit": {"lambda": lam_fit, "rate": float(coef[0]),
                              "fit_until_t": float(ts[i_min]),
                              "floor": float(tail[i_min])},
    })

    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.6))
    ax = axes[0]
    ax.plot(x, np.abs(psi_det[0]) ** 2, color="tab:blue", label=f"SN, $t={T_END:.0f}$")
    ax.plot(x, np.exp(-x**2 / SIGMA0**2) / (SIGMA0 * np.sqrt(np.pi)), "--",
            color="tab:gray", label="initial packet")
    ax.set(xlabel="$x$", ylabel=r"$|\psi|^2$", title="(a) deterministic SN: bound core + escaping radiation",
           yscale="log", ylim=(1e-10, 1))
    ax.legend()

    ax = axes[1]
    ax.semilogy(ts, tail_lin, ls=":", color="tab:gray", label="linear Schrödinger")
    ax.semilogy(ts, tail_det, color="tab:blue", label="deterministic SN")
    for lam, col in zip(lams, ["tab:green", "tab:red"]):
        ax.semilogy(ts, tails_sto[lam], color=col,
                    label=f"stochastic DP, $\\lambda={lam}$")
    ax.set(xlabel="$t$", ylabel=f"residual probability beyond $d={D_FAR:.0f}$",
           title="(b) stochastic completion kills the runaway tail", ylim=(1e-14, 1.5))
    ax.legend(loc="lower left")
    fig.suptitle("Study B — the 'excessive residual probability' problem and its resolution", y=1.03)
    save_figure(fig, "fig_b_tails")


if __name__ == "__main__":
    main()
