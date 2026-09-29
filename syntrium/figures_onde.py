#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""SYNTRIUM v0.2b — figure oscilloscope virtuel (🧮, depuis onde.py)."""
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from onde import chaine
from circuit import Circuit

MENTHE, AMBRE, ROUGE, GRIS = "#0d7377", "#d9a441", "#c0392b", "#5b6b73"
FIGDIR = pathlib.Path(__file__).resolve().parents[1] / "figures"


def _cadre(ax, titre):
    ax.set_facecolor("#f7fbfb")
    for cote in ("top", "right"):
        ax.spines[cote].set_visible(False)
    ax.grid(True, alpha=0.25, lw=0.5)
    ax.set_title(titre, fontsize=9.5, color="#0b3c42", pad=6)


def main():
    FIGDIR.mkdir(exist_ok=True)
    c = Circuit()
    r15 = chaine(15.0)
    r1k = chaine(1000.0)

    fig, axes = plt.subplots(2, 2, figsize=(10.6, 6.8))

    # (1) la sortie DAC @15 Hz (un cycle, effet d'escalier 10 bits)
    ax = axes[0, 0]
    f = 15.0
    masque = r15["t"] >= (11.0 / f)          # dernier cycle (régime établi)
    t_c = (r15["t"][masque] - 11.0 / f) * 1e3
    ax.step(t_c, r15["v_dac"][masque], where="post", color=MENTHE, lw=1.4,
            label="DAC 10 bits (quantifié)")
    ax.plot(t_c, c.v_alim * c.gain_mosfet * np.sin(2 * np.pi * f * (r15["t"][masque] - 11.0 / f)),
            color=GRIS, lw=0.9, ls="--", label="sinus idéal")
    _cadre(ax, "Sortie AD9833 @15 Hz — l'escalier 10 bits (ε ≈ 4,4 mV)")
    ax.set_xlabel("temps (ms)"); ax.set_ylabel("tension (V)")
    ax.legend(frameon=False, fontsize=8)

    # (2) B(t) @15 Hz — le champ du banc
    ax = axes[0, 1]
    ax.plot(t_c, r15["B"][masque] * 1e6, color=MENTHE, lw=2)
    ax.axhline(0, color=GRIS, lw=0.6)
    _cadre(ax, "B(t) @15 Hz — crête 335 µT, retard -5,6° (le champ du banc)")
    ax.set_xlabel("temps (ms)"); ax.set_ylabel("B (µT)")

    # (3) E induit @15 Hz
    ax = axes[1, 0]
    ax.plot(t_c, r15["E"][masque] * 1e3, color=ROUGE, lw=2)
    ax.axhline(0, color=GRIS, lw=0.6)
    _cadre(ax, "E(t) induit (boucle 5 cm) @15 Hz — crête 2,5 mV/m, soit 6 % ICNIRP")
    ax.set_xlabel("temps (ms)"); ax.set_ylabel("E (mV/m)")

    # (4) @1 kHz : l'écrasement par le filtre + la bobine (le vrai enseignement)
    ax = axes[1, 1]
    masque1k = r1k["t"] >= 10.0 / 1000.0
    t_c1k = (r1k["t"][masque1k] - 10.0 / 1000.0) * 1e3
    b_ref = (c.v_alim * c.gain_mosfet / (c.r_sortie + c.r_bobine)) * MU0N(c)  # sans filtre (courant parfait)
    ax.plot(t_c1k, b_ref * np.sin(2 * np.pi * 1000.0 * (r1k["t"][masque1k] - 10.0 / 1000.0)) * 1e6,
            color=GRIS, lw=1.0, ls="--", label="sans filtre (réf. 335 µT)")
    ax.plot(t_c1k, r1k["B"][masque1k] * 1e6, color=MENTHE, lw=2,
            label="réel filtré : 51 µT, -95°")
    _cadre(ax, "@1 kHz : le filtre 159 Hz écrase 6,5× et déphase — c'est LUI le sculpteur")
    ax.set_xlabel("temps (ms)"); ax.set_ylabel("B (µT)")
    ax.legend(frameon=False, fontsize=8)

    fig.suptitle("SYNTRIUM v0.2b — oscilloscope virtuel (calcul · graine 20260929)",
                 fontsize=11.5, color="#0b3c42")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(FIGDIR / "fig_G_oscillo.png", dpi=300)
    plt.close(fig)
    print("✔ figures/fig_G_oscillo.png")


def MU0N(c):
    return 4.0 * np.pi * 1e-7 * c.n_spires / (2.0 * c.rayon_bobine_cm / 100.0)


main()
