# Resolving the "Problems and open matters" of the Schrödinger–Newton collapse interpretation

**Project:** penrose-1 · **Date:** 2026-08-18 · **Status:** all three problems addressed; numerical evidence in `figures/` and `results/`

---

## 0. What is claimed, and what is not

The Wikipedia article on the Schrödinger–Newton (SN) equation lists three problems with
interpreting the SN equation as the cause of wave-function collapse:

> 1. Excessive residual probability far from the collapse point
> 2. Lack of any apparent reason for the Born rule
> 3. Promotion of the previously strictly hypothetical wave function to an observable (real) quantity.

All three criticisms are aimed at the **deterministic SN equation taken alone** as the
collapse mechanism. The article itself points at the way out — *"It might be possible that a
model based on Penrose's idea could provide such an explanation"* and *"whether this problem
can be resolved by applying the right collapse prescription, yet to be found, consistently to
the full quantum system"*. This project constructs that completion explicitly and
demonstrates, analytically and numerically, that within it **each of the three problems is
resolved**:

- the deterministic SN equation is kept as the **mean-field / many-body limit** (where it is
  experimentally relevant and unproblematic), and
- the **collapse mechanism** is carried by the stochastic Diósi–Penrose (DP) dynamics — a
  norm-preserving stochastic Schrödinger equation whose localization rate is fixed by
  Penrose's own gravitational self-energy criterion, λ ≃ ΔE_G/ħ — with gravity sourced from
  the collapsing state in the operator-valued (Tilloy–Diósi) way, not from the raw
  expectation value ⟨ψ|ρ̂|ψ⟩.

None of these ingredients is new: the collapse SDE and its Born-rule martingale property go
back to Gisin (1984) and Pearle (1989), the DP dynamics to Diósi (1987, 1989), and the
operator sourcing to Tilloy–Diósi (2016) — see the References at the end. What this project
adds is the explicit assembly of those known pieces against the article's three criticisms,
plus the numerical demonstrations.

What is *not* claimed: that fundamental physics is finished. The model is nonrelativistic,
its relativistic completion is open, and its parameters are constrained (not yet confirmed)
by experiment. Section 6 states these limits precisely. But the three listed problems, as
stated, are problems *of the deterministic-SN-only reading*, and they disappear in the
completed model — which is the strongest sense in which problems of this kind can be
"solved" short of experimental confirmation of gravitational collapse itself.

---

## 1. The framework

### 1.1 The deterministic SN equation and its role

In units ħ = m = Gm² = 1 the SN equation for a single particle reads

    i ∂ψ/∂t = −½∇²ψ + Φψ,   Φ(x) = −∫ |ψ(x′)|² / |x−x′| d³x′.

As a fundamental single-particle collapse law it fails in the three listed ways (we
reproduce failure #1 numerically in Study A, and #3 in Study D). As the **Hartree
mean-field limit of many-body gravitating quantum matter** it is correct and useful — this
is the regime in which the SN equation survives in the completed picture.

### 1.2 The stochastic completion (Diósi–Penrose dynamics)

The collapse mechanism is the Itô stochastic Schrödinger equation

    d|ψ⟩ = [ −iH dt + √λ (A − ⟨A⟩) dW − (λ/2)(A − ⟨A⟩)² dt ] |ψ⟩            (SSE)

with a mass-density collapse operator A and rate λ fixed by Penrose's criterion: for a
superposition of two mass configurations with gravitational self-energy difference ΔE_G,

    λ ≃ ΔE_G / ħ,     ΔE_G = (1/G)∫ |∇Φ₁ − ∇Φ₂|²/(8π) d³x  ~  G m²/R₀,

R₀ being the mass-density regularization scale. This is *Penrose's own collapse time-scale*
τ ~ ħ/ΔE_G, now realized as an explicit dynamical law rather than an informal criterion.

Two structural facts do all the work below:

- **(F1) The ensemble average of (SSE) is a linear Lindblad master equation**
  dρ/dt = −i[H,ρ] + λ(AρA − ½{A²,ρ}). Linearity ⇒ the no-signaling theorem applies exactly.
- **(F2) Branch weights are martingales.** For H that does not transfer probability between
  collapse branches, the weight P of a branch obeys dP = (const)·P(1−P) dW, so
  E[P(t)] = P(0) and P → {0,1} almost surely.

Gravity is sourced from the collapsing state in the **operator-valued** way (Tilloy–Diósi):
the potential seen by other matter is entangled with the collapsing mass's position
(H_int = Σ_branches Π_b ⊗ V_b), and the collapse noise itself feeds the gravitational field.
The ensemble dynamics stays linear; the Newtonian pair attraction is recovered; the price is
a small, experimentally testable gravitational decoherence and heating.

---

## 2. Problem 1 — "Excessive residual probability far from the collapse point"

**The problem, reproduced (Study A, `src/sn_radial.py`, `figures/fig_a_sn_radial.png`).**
We solve the spherically-symmetric deterministic SN equation with a Crank–Nicolson scheme,
self-consistent Newtonian potential, and an absorbing boundary that measures exactly the
probability escaping to infinity. Validation: the ground state computed by imaginary time
has chemical potential **μ = −0.1637**, matching the Moroz–Penrose–Tod literature value
(−0.163), and satisfies the Choquard virial identities E = −T (ratio 1.022) and μ = 3E
(ratio 0.993). The ~2 % virial residual is the honest discretization accuracy bar on these
numbers.

A wide wave packet (σ = 6 vs ground-state r_rms = 4.6) indeed "collapses": the overlap with
the stationary ground state rises to ≈ 0.91. But, exactly as the numerical studies cited by
the article find, **a small portion runs away**: ≈ 2.8 % of the probability is beyond
r = 25 (≫ the ground-state radius) or already absorbed at infinity at t = 1500 (0.66 % was
actually absorbed at the boundary), and it never comes back. The linear Schrödinger equation disperses ≈ 99.9 % — confirming the article's
remark that SN alone at least *decelerates* the spreading but cannot finish the job.

**The resolution (Study B, `src/tails_1d.py`, `figures/fig_b_tails.png`).**
In a 1D self-gravitating analogue (softened −1/r kernel: attractive, non-confining, so
probability *can* escape) the same phenomenology appears: the deterministic run **saturates**
at a residual tail probability of **5.2 %** beyond d = 10 from the collapse centre — a
fixed, permanent runaway fraction (the linear equation is at 13.3 % and still slowly
dispersing toward 1). Adding the DP localization terms of (SSE) with A = x̂ changes the
character of the solution qualitatively: the ensemble-averaged residual probability
(96 trajectories per λ) **plunges exponentially** — at fitted rate 1.6 per time unit for
λ = 0.01, five orders of magnitude down to ~3×10⁻⁷ by t ≈ 8 — and then settles at a small
noise-sustained level set by the localization–dispersion balance: final values **3.0×10⁻⁴**
(λ = 0.003) and **4.9×10⁻⁶** (λ = 0.01), i.e. **10⁴ times below** the deterministic plateau
at the stronger coupling and a factor ~1.7×10² at the weaker. The level is not strictly
stationary: after its minimum it drifts back up by roughly an order of magnitude over the
run as the soliton heats and its centre diffuses — it stays orders of magnitude below the
deterministic plateau throughout. The runaway probability is not merely diluted; it is
dynamically suppressed, because the localization term damps a far-away component at a rate
growing with its squared distance from the bulk (the observed initial rate ~1.6 matches the
λℓ² scale of the ejecta distances). A real physical feature surfaced by the simulation:
position localization makes the collapsed soliton's *centre* random-walk (momentum
diffusion, x_rms ~ √(λt³/3)), which is why "far from the collapse point" must be — and here
is — measured relative to the trajectory's own collapse centre, and why λ cannot be cranked
arbitrarily high without observable heating (this is exactly the effect current experiments
constrain; see §6).

Two further points close this problem completely:

- *Environment.* The article notes the effect "might disappear if the environment is taken
  into account". The DP noise term **is** an intrinsic environment of exactly this kind —
  the demonstration above is that remark made quantitative.
- *The philosophical "tails problem"* (collapse models never make tails exactly zero): the
  standard and adequate answer is the mass-density ontology — what is physically real is the
  (smeared) mass density m(x) = m⟨ψ|ρ̂(x)|ψ⟩ of the collapsed trajectory, and a tail
  carrying exponentially small weight contributes an exponentially small mass density,
  which *is* "the system being there" to an exponentially small degree — not a residual
  chance of finding the whole particle far away. Under the completed dynamics the
  operational probability of ever *detecting* the system far away is the Born weight of the
  tail, which Study B shows is exponentially suppressed to a floor orders of magnitude below
  the deterministic plateau (and lower for stronger coupling). The deterministic SN
  pathology — a *fixed, finite* fraction permanently at infinity — is gone.

---

## 3. Problem 2 — "Lack of any apparent reason for the Born rule"

**The resolution (Study C, `src/born_rule.py`, `figures/fig_c_born_rule.png`).**
In the completed model the Born rule is not an assumption — it is a **theorem** (fact F2).
For a two-branch superposition ψ = c_L|L⟩ + c_R|R⟩ with A|L⟩ = +|L⟩, A|R⟩ = −|R⟩, Itô
calculus applied to (SSE) gives, for the branch weight P = |c_L|²:

    dP = 4√λ · P(1−P) · dW.

This is the standard Gisin–Pearle martingale property of norm-preserving collapse SDEs
(Gisin 1984; Pearle 1989; reviewed in Bassi et al. 2013), stated here in the DP setting.
Proof of the Born rule in three lines:
1. P is a martingale: E[P(t)] = P(0) (no dt term above).
2. P(t) → {0,1} almost surely (the fixed points; the variance argument
   d E[P²]/dt = 16λ E[P²(1−P)²] > 0 pushes P to the edges, and bounded martingales converge).
3. Therefore Prob(collapse → L) = lim E[P] = P(0) = |c_L(0)|². ∎

The measurement problem asked for exactly this: *why the dot appears at different positions,
with |ψ|² probabilities*. Here outcome randomness is objective dynamical noise, and the |ψ|²
weighting follows from the structure of the SSE with no extra postulate.

**Numerical verification.** Two independent integrations — the exact scalar reduction above
(20 000 trajectories per amplitude) and the full renormalized two-component state SDE
(4 000 trajectories, no use of the analytic reduction) — across nine initial weights
|c_L|² = 0.1 … 0.9:

- empirical collapse frequencies match |c_L|² with χ² = 10.5 over 9 d.o.f.
  (p ≈ 0.31; max deviation 2.1 σ);
- the martingale property holds along the way (|E[P(t)] − P(0)| ≤ 1.0×10⁻⁴);
- collapse is complete (min(P, 1−P) < 10⁻³ in 100 % of runs at t = 8).

*Why this is a legitimate "reason for the Born rule":* the class of collapse SDEs of form
(SSE) is essentially forced — it is the unique norm-preserving unraveling structure whose
ensemble level is linear (no-signaling, F1). Within that class the Born rule is derived, not
postulated. What Penrose's proposal contributes is the *physical identity* of the noise
(gravitational, rate ΔE_G/ħ); what the SSE structure contributes is the statistics. Together
they answer the article's question: a model based on Penrose's idea in which Born's rule
arises naturally — the very possibility the article says "might" exist, made concrete.

---

## 4. Problem 3 — "The wave function becomes an observable quantity" (superluminal signaling)

**The problem, reproduced (Study D (i), `src/no_signaling.py`, `figures/fig_d_no_signaling.png`).**
Sharpest form of the objection: Alice, arbitrarily far away, shares the entangled state
(|0⟩_A|L⟩_B + |1⟩_A|R⟩_B)/√2 with Bob, whose massive particle B is in a superposition of two
places; a local test mass T probes B's gravity. If gravity is sourced by the expectation
value of the mass density (mean-field SN), then:
- Alice does nothing → T evolves under the *average* potential (one unitary);
- Alice measures → T evolves under V_L or V_R per outcome (a mixture of two unitaries).

A mixture of unitaries ≠ the unitary of the average. Numerically the trace distance between
Bob's two ensembles reaches **0.585** — an order-one, *distance-independent*, instantaneous
signal. (The signal strength is set by Bob's local gravity, not by any A–B interaction, so
it does not fall off with separation: this is a genuine causality violation, not an ordinary
force.) The wave function has indeed become ensemble-observable — the article's criticism is
exactly right about mean-field sourcing.

**The resolution (Study D (ii)/(iii)).** In the completed model, gravity enters as the
operator H_int = Π_L⊗V_L + Π_R⊗V_R (the potential is *entangled* with B's position — the
Tilloy–Diósi sourcing), and B's superposition collapses locally under DP noise at rate λ.
The ensemble dynamics is the linear Lindblad equation, so Alice's local trace-preserving
operation cannot change Tr_A ρ — **the signal is exactly zero**. Numerically:

- master-equation level: max signal = **0** (Alice measures) and **1.2×10⁻¹⁵** (Alice applies
  a local unitary) — machine precision. (This vanishing is an algebraic identity — no
  trace-preserving map on Alice's factor can move Tr_A ρ — so the numerics here are a
  consistency check of the implementation; the physical content is that the completed
  model's ensemble dynamics *is* such a linear map);
- trajectory level (4 000 runs): the branch-entangled (operator-sourced) ensemble agrees with
  Alice's measured ensemble within the Monte-Carlo noise floor (≈ 8×10⁻³) — the martingale
  property E[P(t)] = ½ is precisely what makes the two ensembles coincide;
- instructively, the *naive* hybrid — keeping mean-field ⟨⟩-sourcing but adding collapse —
  still signals a little (max residual 0.059 at λ = 2, falling to 0.015 at λ = 10, the
  latter only about twice the MC floor): collapse
  alone tames the signal, but only the **right collapse prescription applied consistently to
  the full quantum system** (the article's own phrase) eliminates it identically. Study D is
  that prescription, exhibited.

**"Promotion of ψ to a real quantity."** The completed model dissolves the dilemma by
splitting two notions the criticism runs together:
- *Ontological reality:* per trajectory the wave function (equivalently its mass density) is
  real — collapse events objectively happen, dots appear on screens.
- *Operational observability:* ensemble statistics depend on the state only through ρ and
  evolve linearly, so no experiment can read out ψ itself, clone it, or exploit entanglement
  for signaling. The noise realization dW is not controllable by any agent — that is the
  precise sense in which a real ψ remains unmeasurable.

Because the ensemble theory is a completely-positive linear semigroup, the standard
no-signaling theorem is not an accident of our examples but a structural guarantee — it
holds for *every* protocol, not just the ones simulated. The Eppley–Hannah-type paradoxes
(article ref. [22]) and Kent's causality discussion (ref. [21]) are thereby answered in the
only way they can be: the consistent coupling is neither "classical gravity measures ψ
without collapse" nor "mean-field sourcing", but collapse-sourced operator gravity, which is
causal by construction.

---

## 5. Summary table

| # | Problem (article's wording) | Status in completed model | Evidence |
|---|---|---|---|
| 1 | Excessive residual probability far from the collapse point | **Resolved** — residual probability decays exponentially; deterministic runaway reproduced and eliminated | Studies A, B |
| 2 | Lack of any apparent reason for the Born rule | **Resolved** — Born rule is a martingale theorem of the dynamics; verified to χ² = 10.5/9 | Study C |
| 3 | Wave function promoted to observable quantity / superluminal signaling | **Resolved** — ensemble dynamics linear ⇒ signal exactly 0 (machine precision); mean-field pathology reproduced for contrast; ψ real per trajectory yet operationally hidden | Study D |

## 6. Honest boundary of the claims

1. **Scope.** The resolutions hold within the nonrelativistic completed model (DP collapse +
   Tilloy–Diósi sourcing). That model is mathematically consistent, contains Penrose's
   collapse criterion as its rate, keeps the SN equation as its mean-field limit, and is
   free of all three listed problems. No claim is made that nature certainly works this way.
2. **Relativity.** A fully relativistic collapse theory remains open research; the
   no-signaling property demonstrated here is the necessary precondition for one, and
   relativistic CSL-type constructions exist as candidates.
3. **Experiment.** The completed model is falsifiable and partially constrained: the
   parameter-free DP variant (regularization at nuclear radii) is excluded by underground
   radiation-emission tests (Donadi et al., Nat. Phys. 2021); variants with mass-density
   smearing R₀ ≳ 10⁻¹⁰ m survive. Levitated-optomechanics and matter-wave interferometry
   are closing in on the surviving window — the question is now experimental, which is
   scientific progress over an open conceptual problem.
4. **Wikipedia's text is accurate** about the deterministic SN equation alone; nothing here
   contradicts the cited numerical studies — Study A reproduces them. What this project
   shows is that the three "open matters" have a concrete, working closure along exactly the
   lines the article gestures at ("the right collapse prescription ... applied consistently
   to the full quantum system").

## 7. Reproducibility

All figures and every number quoted above regenerate with `run_all.py`
(Python 3.14, numpy/scipy/matplotlib; fixed RNG seeds). Machine-readable values live in
`results/*.json`.

## References

- N. Gisin, *Quantum measurements and stochastic processes*, Phys. Rev. Lett. **52**, 1657 (1984).
- L. Diósi, *A universal master equation for the gravitational violation of quantum mechanics*, Phys. Lett. A **120**, 377 (1987).
- L. Diósi, *Models for universal reduction of macroscopic quantum fluctuations*, Phys. Rev. A **40**, 1165 (1989).
- P. Pearle, *Combining stochastic dynamical state-vector reduction with spontaneous localization*, Phys. Rev. A **39**, 2277 (1989).
- R. Penrose, *On gravity's role in quantum state reduction*, Gen. Relativ. Gravit. **28**, 581 (1996).
- I. M. Moroz, R. Penrose, and P. Tod, *Spherically-symmetric solutions of the Schrödinger–Newton equations*, Class. Quantum Grav. **15**, 2733 (1998).
- A. Bassi, K. Lochan, S. Satin, T. P. Singh, and H. Ulbricht, *Models of wave-function collapse, underlying theories, and experimental tests*, Rev. Mod. Phys. **85**, 471 (2013).
- A. Tilloy and L. Diósi, *Sourcing semiclassical gravity from spontaneously localized quantum matter*, Phys. Rev. D **93**, 024026 (2016).
- K. Eppley and E. Hannah, *The necessity of quantizing the gravitational field*, Found. Phys. **7**, 51 (1977).
- S. Donadi, K. Piscicchia, C. Curceanu, L. Diósi, M. Laubenstein, and A. Bassi, *Underground test of gravity-related wave function collapse*, Nat. Phys. **17**, 74 (2021).
