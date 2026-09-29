#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""SYNTRIUM v0.2a — figure de la cartographie (🧮, depuis design.py)."""
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from design import Design, evaluer, limite_icnirp_publique

MENTHE, AMBRE, ROUGE, GRIS = "#0d7377", "#d9a441", "#c0392b", "#5b6b73"
FIGDIR = pathlib.Path(__file__).resolve().parents[1] / "figures"


def main():
    FIGDIR.mkdir(exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(11.4, 4.6), sharey=True)
    n_vals = np.arange(50, 1201, 25)

    for ax, v in zip(axes, (5.0, 12.0, 24.0)):
        ax.set_facecolor("#f7fbfb")
        ax.add_patch(plt.Rectangle((50, 500.0), 1150, 1500.0, facecolor=AMBRE,
                                   alpha=0.22, edgecolor=AMBRE, lw=1.0))
        ax.text(180, 1050, "bande clinique\n0,5–2 mT", fontsize=8, color="#7a5c1e")
        for fil, coul, ls in ((0.4, MENTHE, "-"), (0.8, "#7c2d12", "--")):
            b = [evaluer(Design(int(n), 3.0, fil, v))["B_mT"] * 1e3 for n in n_vals]
            ax.semilogy(n_vals, b, color=coul, lw=1.9, ls=ls, label=f"fil {fil} mm")
        # la frontière de conformité (E induit > limite ICNIRP publique) : B_max conform
        b_lim = limite_icnirp_publique(75.0) * 75.0 / limite_icnirp_publique(15.0)
        # E = pi f r B ; le ratio à 75 Hz domine : B_max = lim75/(pi·75·r)
        b_lim75 = limite_icnirp_publique(75.0) / (math.pi * 75.0 * 0.05) * 1e3
        ax.axhline(b_lim75 * 1e3, color=ROUGE, ls=":", lw=1.2)
        ax.text(60, b_lim75 * 1.4e3, "plafond de conformité ICNIRP (75 Hz)",
                fontsize=7.5, color=ROUGE)
        ax.set_title(f"{v:.0f} V", fontsize=11, color="#0b3c42")
        ax.grid(True, which="both", alpha=0.25, lw=0.5)
        ax.set_xlabel("nombre de spires")
        for cote in ("top", "right"):
            ax.spines[cote].set_visible(False)
    axes[0].set_ylabel("B @15 Hz (µT)")
    axes[0].legend(frameon=False, fontsize=8.5, loc="lower right")
    fig.suptitle("Cartographie des designs — atteindre la bande clinique en restant conforme "
                 "(in silico · calcul · graine 20260929)", fontsize=11, color="#0b3c42")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(FIGDIR / "fig_F_designs.png", dpi=300)
    plt.close(fig)
    print("✔ figures/fig_F_designs.png")


import math  # noqa: E402  (pour le plafond)
main()
