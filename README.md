# penrose-1 — Resolving the open problems of Schrödinger–Newton collapse

This project addresses, with explicit mathematics and numerical demonstrations, the three
"Problems and open matters" listed in the Wikipedia article on the
[Schrödinger–Newton equation](https://en.wikipedia.org/wiki/Schr%C3%B6dinger%E2%80%93Newton_equation)
(section *Quantum wave function collapse*):

1. **Excessive residual probability far from the collapse point**
2. **Lack of any apparent reason for the Born rule**
3. **Promotion of the wave function to an observable (real) quantity** (→ superluminal signaling)

**Headline result:** all three criticisms apply to the *deterministic* SN equation used
*alone* as a collapse mechanism — and all three are resolved once Penrose's idea is
completed into its stochastic form (Diósi–Penrose dynamics with Tilloy–Diósi gravitational
sourcing). Each resolution is demonstrated numerically in this repository and written up in
[REPORT.md](REPORT.md).

The theoretical ingredients are standard collapse-model results (Gisin 1984; Diósi 1987/89;
Pearle 1989; Tilloy–Diósi 2016 — full references in the report); the contribution here is
assembling them explicitly against the article's three criticisms and verifying each
numerically.

| Study | Problem | File | Result |
|---|---|---|---|
| A | reproduce #1 | [src/sn_radial.py](src/sn_radial.py) | deterministic SN: packet settles to ground state but a runaway fraction escapes for good |
| B | resolve #1 | [src/tails_1d.py](src/tails_1d.py) | stochastic localization → far-field probability decays exponentially instead of persisting |
| C | resolve #2 | [src/born_rule.py](src/born_rule.py) | Born rule is a martingale **theorem** of the collapse SDE; Monte-Carlo verified |
| D | resolve #3 | [src/no_signaling.py](src/no_signaling.py) | mean-field SN gravity signals (O(1)); the stochastic completion signals exactly 0 |

## Reproduce

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run_all.py
```

Figures land in `figures/`, machine-readable numbers behind every claim in `results/`.

## Layout

- [PLAN.md](PLAN.md) — strategy and study design
- [REPORT.md](REPORT.md) — the full write-up: proofs, numbers, honest caveats
- [REPORT.tex](REPORT.tex) — the same report as a LaTeX article (compiles on Overleaf with
  `pdflatex`; upload alongside `figures/`)
- [complete-chat-history.md](complete-chat-history.md) — verbatim log of the session that
  produced this repository, including every tool call and result
- `src/` — one self-contained script per study + `common.py`
- `figures/`, `results/` — generated outputs
