"""Study A — reproduce problem 1: deterministic spherically-symmetric
Schrödinger–Newton collapse leaves runaway probability at infinity.

Model (units hbar = m = G m^2 = 1, the Choquard convention):

    i dpsi/dt = -(1/2) lap psi + Phi psi,      Phi = -(1/|x|) * |psi|^2   (convolution)

Spherical symmetry, reduced wave u(r) = r * psi(r), norm 4*pi*int |u|^2 dr = 1.

    Phi(r) = -( M(r)/r + 4*pi * int_r^inf |psi|^2 s ds ),  M(r) = 4*pi int_0^r |psi|^2 s^2 ds

Numerics: Strang splitting — half-step potential phase kick, Crank–Nicolson
kinetic step (tridiagonal), half-step kick, recompute Phi. Complex absorbing
potential (CAP) near the outer edge soaks up outgoing "runaway" probability;
the absorbed norm is exactly the probability that escaped to infinity.

Ground state via imaginary-time evolution on the same grid; validated with the
virial identities of the Choquard equation (E_tot = -T, mu = 3 E_tot).
"""
import numpy as np
from scipy.linalg import solve_banded

from common import plt, save_figure, save_results

# ---------------------------------------------------------------- grid & CAP
R_MAX = 200.0
N = 4000
DR = R_MAX / (N + 1)
r = DR * np.arange(1, N + 1)          # r_1 .. r_N, u=0 at r=0 and r=R_MAX

R_ABS = 160.0                          # CAP starts here
W_CAP = np.where(r > R_ABS, 0.5 * ((r - R_ABS) / (R_MAX - R_ABS)) ** 3, 0.0)

R_FAR = 25.0                           # "far from the collapse point"
far_mask = r > R_FAR


def norm2(u):
    return 4.0 * np.pi * np.sum(np.abs(u) ** 2) * DR


def potential(u):
    """Self-consistent Newtonian potential Phi(r) from |psi|^2 = |u|^2/r^2."""
    rho_r2 = np.abs(u) ** 2                       # |psi|^2 r^2
    M = 4.0 * np.pi * np.cumsum(rho_r2) * DR      # mass inside r
    g = rho_r2 / r                                # |psi|^2 r
    outer = 4.0 * np.pi * (np.sum(g) - np.cumsum(g)) * DR
    return -(M / r + outer)


def kinetic_banded(dt_factor):
    """Banded form of (I + dt_factor * K) with K = -1/2 d^2/dr^2."""
    main = 1.0 + dt_factor * (1.0 / DR**2)
    off = dt_factor * (-0.5 / DR**2)
    ab = np.zeros((3, N), dtype=complex)
    ab[0, 1:] = off
    ab[1, :] = main
    ab[2, :-1] = off
    return ab


def apply_tridiag(main, off, u):
    out = main * u
    out[:-1] += off * u[1:]
    out[1:] += off * u[:-1]
    return out


def energies(u):
    """(kinetic T, self-gravity pair energy V, chemical potential mu)."""
    du = np.gradient(u, DR)
    T = 4.0 * np.pi * 0.5 * np.sum(np.abs(du) ** 2) * DR
    Phi = potential(u)
    PhiExp = 4.0 * np.pi * np.sum(Phi * np.abs(u) ** 2) * DR   # <Phi> = 2V
    V = 0.5 * PhiExp
    mu = T + PhiExp
    return T, V, mu


# ------------------------------------------------------------- ground state
def ground_state(dtau=0.05, max_iter=20000, tol=1e-12):
    u = r * np.exp(-r**2 / (2 * 3.0**2))
    u /= np.sqrt(norm2(u))
    ab = kinetic_banded(dtau)          # implicit Euler in imaginary time
    mu_old = np.inf
    for it in range(max_iter):
        Phi = potential(u)
        u = u * np.exp(-Phi * dtau)
        u = solve_banded((1, 1), ab, u.astype(complex)).real
        u /= np.sqrt(norm2(u))
        if it % 200 == 0:
            _, _, mu = energies(u)
            if abs(mu - mu_old) < tol:
                break
            mu_old = mu
    return u


# ---------------------------------------------------------------- dynamics
def evolve(u0, t_max, dt, self_gravity=True, u_gs=None, rec_every=25):
    A = kinetic_banded(0.5j * dt)                       # (I + i dt/2 K)
    b_main = 1.0 - 0.5j * dt / DR**2                    # (I - i dt/2 K)
    b_off = 0.5j * dt * 0.5 / DR**2
    cap_half = np.exp(-W_CAP * dt / 2.0)

    u = u0.astype(complex).copy()
    n_steps = int(round(t_max / dt))
    rec = {"t": [], "norm": [], "far": [], "overlap": [], "r_exp": []}
    gs_norm2 = norm2(u_gs) if u_gs is not None else None

    for step in range(n_steps + 1):
        if step % rec_every == 0:
            nrm = norm2(u)
            absorbed = 1.0 - nrm
            far = 4.0 * np.pi * np.sum(np.abs(u[far_mask]) ** 2) * DR + absorbed
            rec["t"].append(step * dt)
            rec["norm"].append(nrm)
            rec["far"].append(far)
            if u_gs is not None:
                ov = np.abs(4.0 * np.pi * np.sum(np.conj(u_gs) * u) * DR) ** 2 / gs_norm2
                rec["overlap"].append(ov)
            rec["r_exp"].append(4.0 * np.pi * np.sum(r * np.abs(u) ** 2) * DR / max(nrm, 1e-300))
        if step == n_steps:
            break
        Phi = potential(u) if self_gravity else 0.0
        u = u * np.exp(-1j * Phi * dt / 2.0) * cap_half
        u = solve_banded((1, 1), A, apply_tridiag(b_main, b_off, u))
        Phi = potential(u) if self_gravity else Phi
        u = u * np.exp(-1j * Phi * dt / 2.0) * cap_half
    return {k: np.array(v) for k, v in rec.items()}, u


def main():
    print("== Study A: deterministic Schrodinger-Newton, spherical symmetry ==")
    u_gs = ground_state()
    T, V, mu = energies(u_gs)
    E = T + V
    r_rms = np.sqrt(4.0 * np.pi * np.sum(r**2 * np.abs(u_gs) ** 2) * DR)
    print(f"ground state: T={T:.6f} V={V:.6f} E={E:.6f} mu={mu:.6f} r_rms={r_rms:.3f}")
    print(f"virial checks: E/-T = {E / -T:.4f} (want 1.0), mu/3E = {mu / (3 * E):.4f} (want 1.0)")

    # initial condition: normalized Gaussian, wider than the ground state
    sigma0 = 6.0
    u0 = r * np.exp(-r**2 / (2 * sigma0**2))
    u0 = u0 / np.sqrt(norm2(u0))

    dt, t_max = 0.05, 1500.0
    rec_sn, u_fin = evolve(u0, t_max, dt, self_gravity=True, u_gs=u_gs)
    rec_lin, _ = evolve(u0, t_max, dt, self_gravity=False, u_gs=u_gs)

    esc_sn = 1.0 - rec_sn["norm"][-1]
    esc_lin = 1.0 - rec_lin["norm"][-1]
    ov_fin = rec_sn["overlap"][-1]
    far_fin = rec_sn["far"][-1]
    print(f"SN run:    escaped={esc_sn:.4f}  P_far(final)={far_fin:.4f}  GS overlap(final)={ov_fin:.4f}")
    print(f"linear:    escaped={esc_lin:.4f}  P_far(final)={rec_lin['far'][-1]:.4f}")

    save_results("study_a_sn_radial", {
        "units": "hbar = m = G m^2 = 1 (Choquard convention)",
        "grid": {"R_max": R_MAX, "N": N, "dt": dt, "t_max": t_max, "R_far": R_FAR},
        "ground_state": {"T": T, "V": V, "E_total": E, "mu": mu, "r_rms": r_rms,
                         "virial_E_over_minusT": E / -T, "virial_mu_over_3E": mu / (3 * E)},
        "initial_sigma": sigma0,
        "sn": {"escaped_fraction": esc_sn, "P_far_final": far_fin,
               "gs_overlap_final": ov_fin,
               "t": rec_sn["t"].tolist(), "far": rec_sn["far"].tolist(),
               "overlap": rec_sn["overlap"].tolist(), "norm": rec_sn["norm"].tolist()},
        "linear": {"escaped_fraction": esc_lin, "P_far_final": rec_lin["far"][-1],
                   "t": rec_lin["t"].tolist(), "far": rec_lin["far"].tolist()},
    })

    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.4))
    ax = axes[0]
    psi2_0 = np.abs(u0 / r) ** 2
    psi2_f = np.abs(u_fin / r) ** 2
    psi2_gs = np.abs(u_gs / r) ** 2
    ax.semilogy(r, psi2_0, label="initial ($t=0$)", color="tab:gray")
    ax.semilogy(r, psi2_f, label=f"SN, $t={t_max:.0f}$", color="tab:blue")
    ax.semilogy(r, psi2_gs, "--", label="SN ground state", color="tab:red")
    ax.set(xlim=(0, 60), ylim=(1e-12, 1), xlabel="$r$", ylabel=r"$|\psi|^2$",
           title="(a) collapse toward the ground state")
    ax.legend()

    ax = axes[1]
    ax.plot(rec_sn["t"], rec_sn["overlap"], color="tab:red",
            label=r"$|\langle\psi_{\rm gs}|\psi(t)\rangle|^2$")
    ax.plot(rec_sn["t"], rec_sn["norm"], color="tab:blue", label="surviving norm")
    ax.set(xlabel="$t$", ylabel="probability", ylim=(0, 1.02),
           title="(b) settling is incomplete")
    ax.legend()

    ax = axes[2]
    ax.plot(rec_sn["t"], rec_sn["far"], color="tab:blue", label="SN equation")
    ax.plot(rec_lin["t"], rec_lin["far"], color="tab:gray", ls="--",
            label="linear Schrödinger")
    ax.set(xlabel="$t$", ylabel=f"$P(r>{R_FAR:.0f})$ + escaped",
           title="(c) residual probability far away", ylim=(0, 1.05))
    ax.legend()
    fig.suptitle("Study A — deterministic Schrödinger–Newton: a runaway fraction never collapses", y=1.03)
    save_figure(fig, "fig_a_sn_radial")


if __name__ == "__main__":
    main()
