# Penrose-1: Study plan — the "open problems" of the Schrödinger–Newton collapse interpretation

Goal: address, with explicit mathematics and numerical demonstrations, the three problems
listed in the Wikipedia article on the Schrödinger–Newton (SN) equation under
"Quantum wave function collapse → Problems and open matters":

1. **Excessive residual probability far from the collapse point** — deterministic SN
   collapse leaves a runaway portion of the wave packet escaping to infinity.
2. **Lack of any apparent reason for the Born rule** — SN says nothing about why outcomes
   occur with probability |ψ|².
3. **Promotion of the wave function to an observable (real) quantity** — sourcing gravity
   by ⟨ψ|ρ̂|ψ⟩ makes the nonlinear dynamics usable for faster-than-light signaling via
   entanglement.

## Strategy

All three criticisms target the *deterministic* SN equation used *alone* as the collapse
mechanism. The article itself hints at the resolution ("a model based on Penrose's idea
could provide such an explanation", "applying the right collapse prescription ... to the
full quantum system"). We construct that completion explicitly: the **stochastic
Diósi–Penrose (DP) dynamics** — a norm-preserving stochastic Schrödinger equation whose
localization rate is fixed by Penrose's own gravitational self-energy criterion
(λ ~ ΔE_G/ħ) and whose ensemble average is a **linear** Lindblad master equation.

Within this completed model each problem becomes a demonstrable theorem:

| Problem | Resolution in the stochastic completion | Demonstration |
|---|---|---|
| Runaway tails | Localization term suppresses far-field probability exponentially in time | Study B |
| Born rule | ⟨P_branch⟩ is a martingale ⇒ collapse frequencies = initial |c|² (3-line proof + Monte-Carlo) | Study C |
| Signaling / real ψ | Ensemble dynamics is linear (Lindblad) ⇒ no-signaling theorem applies exactly; gravity is sourced à la Tilloy–Diósi by the collapse signal, not by raw ⟨ψ|ρ̂|ψ⟩ | Study D |

## Numerical studies

- **Study A — reproduce the problem** (`src/sn_radial.py`):
  3D spherically-symmetric deterministic SN equation (Crank–Nicolson + self-consistent
  Newtonian potential, absorbing boundary). Ground state via imaginary time. Show a wide
  packet settles toward the ground state **but** a finite fraction of probability runs
  away to infinity and never returns. Linear Schrödinger comparison (full dispersal).
- **Study B — tail suppression** (`src/tails_1d.py`):
  1D self-gravitating SN toy (kernel |x−x′|) evolved (i) deterministically and (ii) with
  DP-type stochastic localization. Ensemble-averaged tail probability
  P(|x−x_collapse| > d): plateaus at a finite value for (i), decays ~exponentially for (ii).
- **Study C — Born rule** (`src/born_rule.py`):
  Two-branch superposition under the collapse SDE, ~10⁴ trajectories per amplitude.
  Empirical collapse frequencies vs |c|² with binomial error bars; martingale check.
- **Study D — no-signaling** (`src/no_signaling.py`):
  Entangled pair. (i) Deterministic semiclassical (SN-style mean-field) dynamics: Alice's
  choice to measure or not changes Bob's reduced density matrix ⇒ reproduces the article's
  criticism. (ii) DP stochastic dynamics: trajectory ensemble and the Lindblad equation
  give identical ρ_B regardless of Alice's action (machine precision + Monte-Carlo).

## Deliverables in this folder

- `PLAN.md` (this file), `REPORT.md` (findings write-up), updated `README.md`
- `src/` — the four studies + shared utilities; `run_all.py` orchestrator
- `figures/` — publication-style figures for each study
- `results/` — machine-readable JSON of every quantitative claim
- Published artifact report with embedded figures

## Tools

Python 3.14 in `.venv` (numpy 2.5.2, scipy 1.18.0, matplotlib 3.11.1). No GPU required.

## Honesty constraints

The report states precisely what is proven/demonstrated inside the model versus what
remains open in physics at large (relativistic completion, experimental confirmation;
note the 2021 Donadi et al. underground test constraining the parameter-free DP model and
the surviving regularization-cutoff parameter space).
