#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""SYNTRIUM v0.2c — figure fantôme gélose (🧮, depuis gel.py)."""
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gel import e_induit_radial, run_thermique

MENTHE, AMBRE, ROUGE, GRIS, VIOLET = "#0d7377", "#d9a441", "#c0392b", "#5b6b73", "#6c5b9e"
FIGDIR = pathlib.Path(__file__).resolve().parents[1] / "figures"


def _cadre(ax, titre):
    ax.set_facecolor("#f7fbfb")
    for cote in ("top", "right"):
        ax.spines[cote].set_visible(False)
    ax.grid(True, alpha=0.25, lw=0.5)
    ax.set_title(titre, fontsize=9.5, color="#0b3c42", pad=6)


def main():
    FIGDIR.mkdir(exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.6))

    # (1) le champ induit DANS le disque : E(r) à B = 1 mT, 3 fréquences
    ax = axes[0]
    r = np.linspace(0, 0.08, 161)
    for f, coul in ((15.0, MENTHE), (50.0, AMBRE), (75.0, ROUGE)):
        e = e_induit_radial(f, 1e-3)
        ax.plot(r * 100, e * 1e3, color=coul, lw=2, label=f"{f:.0f} Hz")
    ax.set_xlabel("rayon dans le disque (cm)")
    ax.set_ylabel("E induit crête (mV/m)")
    _cadre(ax, "Champ induit dans le gel — nul au centre, max au bord (E = π·f·r·B, ici B = 1 mT)")
    ax.legend(frameon=False, fontsize=8.5)

    # (2) ΔT(r) après 10 min à 75 Hz : les 4 designs
    ax = axes[1]
    for nom, b, coul in (("banc 5V (0,335 mT)", 0.335e-3, MENTHE),
                         ("clinique 0,5 mT", 0.5e-3, AMBRE),
                         ("clinique 1 mT", 1.0e-3, VIOLET),
                         ("clinique 2 mT", 2.0e-3, ROUGE)):
        res = run_thermique(75.0, b, duree_s=600.0)
        ax.plot(res["r"] * 100, res["delta_T"] * 1e9, color=coul, lw=2, label=nom)
    ax.set_xlabel("rayon dans le disque (cm)")
    ax.set_ylabel("ΔT après 600 s (nanokelvins)")
    _cadre(ax, "Échauffement du fantôme à 75 Hz, 10 min — pire cas de la bande")
    ax.legend(frameon=False, fontsize=7.8, loc="upper left")
    ax.text(0.98, 0.04, "même le design clinique haut :\n< 100 nanokelvins",
            transform=ax.transAxes, ha="right", fontsize=8.5, color=GRIS, style="italic")

    fig.suptitle("SYNTRIUM v0.2c — fantôme gélose simulé (calcul · FTCS 161 pts · graine 20260929)",
                 fontsize=11.5, color="#0b3c42")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(FIGDIR / "fig_H_fantome.png", dpi=300)
    plt.close(fig)
    print("✔ figures/fig_H_fantome.png")


main()
