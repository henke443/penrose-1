"""Shared utilities: output paths, JSON results, matplotlib style."""
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURES = os.path.join(ROOT, "figures")
RESULTS = os.path.join(ROOT, "results")
os.makedirs(FIGURES, exist_ok=True)
os.makedirs(RESULTS, exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 130,
    "savefig.dpi": 130,
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "legend.fontsize": 8,
    "lines.linewidth": 1.4,
    "axes.grid": True,
    "grid.alpha": 0.3,
})


def save_results(name: str, data: dict) -> str:
    path = os.path.join(RESULTS, name + ".json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=float)
    print(f"[results] wrote {path}")
    return path


def save_figure(fig, name: str) -> str:
    path = os.path.join(FIGURES, name + ".png")
    fig.savefig(path, bbox_inches="tight")
    print(f"[figure] wrote {path}")
    return path
