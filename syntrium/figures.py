#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""SYNTRIUM v0.1 — les figures (🧮 calcul, depuis les tableaux de la campagne).

Règle RATISS R7 : aucun graphique décoratif — chaque courbe vient du calcul,
tout se régénère par une commande : python3 syntrium/figures.py
Palette menthe RATISS (#0d7377). Sorties : figures/*.png (300 dpi).
"""
from __future__ import annotations

import math
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from circuit import campagne, Circuit, gain_circuit, champ_b, champ_induit, icnirp_ratio

MENTHE = "#0d7377"
AMBRE = "#d9a441"
ROUGE = "#c0392b"
GRIS = "#5b6b73"

FIGDIR = pathlib.Path(__file__).resolve().parents[1] / "figures"


def _cadre(ax, titre):
    ax.set_facecolor("#f7fbfb")
    for cote in ("top", "right"):
        ax.spines[cote].set_visible(False)
    for cote in ("left", "bottom"):
        ax.spines[cote].set_color(GRIS)
    ax.grid(True, which="both", alpha=0.25, linewidth=0.5)
    ax.set_title(titre, fontsize=10.5, color="#0b3c42", pad=8)


def fig_circuit(r):
    """La réponse en fréquence de la chaîne complète + courbe depuis les formules."""
    f = np.array(r["f"])
    c = Circuit(**{k: r["circuit"][k] for k in r["circuit"]})
    i = gain_circuit(f, c) * 1e3   # mA

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.4, 6.4), sharex=True)

    ax1.semilogx(f, i, color=MENTHE, lw=2)
    ax1.axvline(r["f_c_filtre_hz"], color=AMBRE, ls="--", lw=1.2,
                label=f"coupe filtre RC {r['f_c_filtre_hz']:.0f} Hz")
    ax1.set_ylabel("courant bobine I (mA)")
    _cadre(ax1, "SYNTRIUM étape A · réponse du circuit émetteur (in silico, graine 20260929)")
    ax1.legend(frameon=False, fontsize=8.5)

    ax2.semilogx(f, np.array(r["B"]) * 1e6, color=MENTHE, lw=2)
    ax2.set_xlabel("fréquence (Hz)")
    ax2.set_ylabel("champ B crête (µT)")
    _cadre(ax2, "Champ magnétique au centre de la bobine — B = µ0 · n · I(f)")

    fig.tight_layout()
    fig.savefig(FIGDIR / "fig_A_circuit.png", dpi=300)
    plt.close(fig)


def fig_fenetres(r):
    """La carte des fenêtres : E induit vs limites ICNIRP, zones verte/jaune/rouge."""
    f = np.array(r["f"])
    e = np.array(r["E"])
    ratio = np.array(r["ratio"])

    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    ax.semilogx(f, e * 1e3, color=MENTHE, lw=2, label="E induit SYNTRIUM (r tissu 5 cm)")
    ax.fill_between(f, 0, 10, color="#2ecc71", alpha=0.10)
    ax.fill_between(f, 10, 400, color=AMBRE, alpha=0.08)
    ax.fill_between(f, 400, 1e5, color=ROUGE, alpha=0.06)
    ax.axhline(10, color="#27ae60", ls="--", lw=1, label="ICNIRP public 10 mV/m (10–25 Hz)")
    ax.axhline(400, color=ROUGE, ls="--", lw=1, label="ICNIRP public 400 mV/m (1 kHz)")
    # la courbe du ratio sur l'axe droit, en %
    ax2 = ax.twinx()
    ax2.semilogx(f, ratio * 100, color=GRIS, lw=1.2, ls=":", label="ratio limite ICNIRP (%)")
    ax2.axhline(30, color=GRIS, ls=":", lw=0.8)
    ax2.set_ylabel("ratio limite ICNIRP (%)", color=GRIS)
    ax2.set_ylim(0, 300)
    ax2.spines["top"].set_visible(False)

    ax.set_yscale("log")
    ax.set_xlabel("fréquence (Hz)")
    ax.set_ylabel("champ interne induit (mV/m)")
    _cadre(ax, "Carte des fenêtres : verte = <10 mV/m · ambre = intermédiaire · rouge = >400 mV/m")
    lignes = [l for l in [ax.get_legend_handles_labels()[0], ax2.get_legend_handles_labels()[0]]]
    ax.legend(handles=lignes[0] + lignes[1], frameon=False, fontsize=8.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIGDIR / "fig_B_fenetres.png", dpi=300)
    plt.close(fig)


def fig_fenetres_low(r):
    """Zoom basse fréquence 10 Hz -> 2 kHz : où vit vraiment le dispositif."""
    f = np.array(r["f"])
    mask = f <= 2000.0
    e = np.array(r["E"])[mask] * 1e3
    ratio = np.array(r["ratio"])[mask] * 100

    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    ax.semilogx(f[mask], e, color=MENTHE, lw=2, label="E induit (mV/m)")
    ax.semilogx(f[mask], ratio, color=AMBRE, lw=1.6, ls="--", label="ratio ICNIRP (%)")
    ax.axhline(30, color=GRIS, ls=":", lw=1, label="seuil zone verte 30 %")
    if r["f_zone_verte_max_hz"] > 0:
        ax.axvline(r["f_zone_verte_max_hz"], color="#27ae60", ls="-.", lw=1.2,
                   label=f"limite zone verte {r['f_zone_verte_max_hz']:.0f} Hz")
    ax.set_xlabel("fréquence (Hz)")
    ax.set_ylabel("mV/m · %")
    _cadre(ax, "Zoom basse fréquence — la fenêtre d'exploitation honnête de SYNTRIUM")
    ax.legend(frameon=False, fontsize=8.5)
    fig.tight_layout()
    fig.savefig(FIGDIR / "fig_C_low_freq.png", dpi=300)
    plt.close(fig)


def fig_circuit_schema():
    """Le schéma du circuit simulé — celui que Jonathan remontera en dur plus tard."""
    fig, ax = plt.subplots(figsize=(8.6, 3.6))
    ax.axis("off")
    boites = [
        (0.02, "AD9833\n(DDS)\n[plus tard,\nsur Arduino]"),
        (0.27, "filtre RC\npasse-bas\nfc ≈ 16 Hz"),
        (0.52, "étage\nMOSFET\ngain 0,9"),
        (0.77, "bobine\n200 sp.\n2,2 mH"),
    ]
    for x, t in boites:
        ax.add_patch(plt.Rectangle((x, 0.30), 0.19, 0.40, fill=True,
                                   facecolor="#e8f4f4", edgecolor=MENTHE, lw=1.8))
        ax.text(x + 0.095, 0.50, t, ha="center", va="center", fontsize=9, color="#0b3c42")
    for x in (0.21, 0.46, 0.71):
        ax.annotate("", xy=(x + 0.06, 0.50), xytext=(x, 0.50),
                    arrowprops=dict(arrowstyle="->", color=GRIS, lw=1.6))
    ax.text(0.985, 0.50, "champ B\nvers le\nfantôme\n(plus tard)", ha="center", va="center",
            fontsize=8.5, color=GRIS)
    ax.annotate("", xy=(0.965, 0.50), xytext=(0.925, 0.50),
                arrowprops=dict(arrowstyle="->", color=GRIS, lw=1.6))
    ax.text(0.5, 0.08, "Le circuit que la simulation fait tourner — et que le chef remontera "
            "en dur quand la phase matérielle sera ordonnée.",
            ha="center", fontsize=8.5, color=GRIS, style="italic")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(FIGDIR / "fig_D_schema.png", dpi=300)
    plt.close(fig)


def fig_bande_clinique(r):
    """LA figure de la question : le banc 5 V peut-il atteindre la bande clinique documentée ?

    Bande clinique affichée : ordres de grandeur PEMF os typiques (15–75 Hz,
    0,5–2 mT) — les valeurs exactes, dispositif par dispositif, sont l'objet de
    la phase 4 (revue PubMed/openFDA). Ici on compare des NIVEAUX, pas des allégations.
    """
    f = np.array(r["f"])
    b_ut = np.array(r["B"]) * 1e6

    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    ax.semilogx(f, b_ut, color=MENTHE, lw=2,
                label="B du banc 5 V simulé (69 mA max, 200 spires)")
    # la bande clinique 15-75 Hz, 0.5-2 mT (500-2000 µT)
    ax.add_patch(plt.Rectangle((15.0, 500.0), 75.0 - 15.0, 2000.0 - 500.0,
                               facecolor=AMBRE, alpha=0.25, edgecolor=AMBRE, lw=1.2))
    ax.text(24.0, 950.0, "bande clinique PEMF os\ntypique (15–75 Hz, 0,5–2 mT)\n— précisée en phase 4",
            fontsize=8.5, color="#7a5c1e", ha="left")
    ax.axhline(1000.0, color=AMBRE, ls="--", lw=1)

    ax.set_yscale("log")
    ax.set_xlabel("fréquence (Hz)")
    ax.set_ylabel("champ B crête (µT)")
    _cadre(ax, "Écart mesuré : le banc 5 V vs les niveaux cliniques — quantifier le fossé avant de le combler")
    ax.legend(frameon=False, fontsize=8.5, loc="lower left")
    # annotation de l'écart
    b15 = float(np.interp(15.0, f, b_ut))
    ax.annotate(f"@15 Hz : {b15:.0f} µT\n≈ {1000.0/b15:.0f}× sous le niveau clinique médian",
                xy=(15.0, b15), xytext=(60.0, b15 * 2.2), fontsize=8.5, color=GRIS,
                arrowprops=dict(arrowstyle="->", color=GRIS, lw=1.1))
    fig.tight_layout()
    fig.savefig(FIGDIR / "fig_E_bande_clinique.png", dpi=300)
    plt.close(fig)


def main():
    FIGDIR.mkdir(exist_ok=True)
    r = campagne()
    fig_circuit(r)
    fig_fenetres(r)
    fig_fenetres_low(r)
    fig_circuit_schema()
    fig_bande_clinique(r)
    print("figures écrites dans figures/ :")
    for p in sorted(FIGDIR.glob("*.png")):
        print("  ·", p.name)


if __name__ == "__main__":
    main()
