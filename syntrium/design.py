#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""SYNTRIUM v0.2a — cartographie des designs (🧮 in silico).

Question : quels (N spires, diamètre de fil, tension) atteignent la bande
clinique documentée (0,5–2 mT à 15 Hz — précisée en phase 4) en restant
conforme ICNIRP et sans chauffer la bobine ?

Physique du bobinage (formules standard) :
  - longueur de fil   : L_fil = N · 2πr
  - résistance        : R_s = ρ_cu · L_fil / A_fil   (A = π d²/4, ρ_cu = 1,68e−8 Ω·m)
  - inductance (bobine courte) : L = μ0 · N² · π·r / 2
  - courant @15 Hz    : I = V·gain / (R_out + sqrt(R_s² + (ωL)²))
  - champ au centre   : B = μ0 · N · I / (2r)
  - E induit (tissu 5 cm) : E = π·f·r_tissu·B   (cf. physique.py)
  - échauffement bobine : P = I²·R_s

Graine 20260929 — déterministe.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

RHO_CU = 1.68e-8          # Ω·m
MU0 = 4.0 * math.pi * 1e-7
F_CIBLE = 15.0            # Hz — la bande PEMF os
F_CHECK = 75.0            # Hz — borne haute de la bande clinique
R_TISSU = 0.05            # m — boucle de tissu pour le champ induit
BANDE_B_MT = (0.5, 2.0)   # la bande clinique cible (mT)
P_BOBINE_MAX_W = 4.0      # critère d'échauffement de la bobine (banc sans ventilateur)


@dataclass(frozen=True)
class Design:
    n_spires: int
    rayon_cm: float
    fil_mm: float
    v_alim: float
    gain: float = 0.9
    r_sortie: float = 50.0

    @property
    def resistance(self) -> float:
        a = math.pi * (self.fil_mm * 1e-3) ** 2 / 4.0
        return RHO_CU * self.n_spires * 2.0 * math.pi * (self.rayon_cm / 100.0) / a

    @property
    def inductance(self) -> float:
        """L = μ0·N²·π·r/2 (bobine courte) — cohérent avec les 2,2 mH du banc."""
        r = self.rayon_cm / 100.0
        return MU0 * self.n_spires ** 2 * math.pi * r / 2.0

    def courant(self, f: float) -> float:
        z = math.sqrt(self.resistance ** 2 + (2.0 * math.pi * f * self.inductance) ** 2)
        return self.v_alim * self.gain / (self.r_sortie + z)

    @property
    def champ_b_t(self) -> float:
        """B crête au centre (T) @ F_CIBLE."""
        return MU0 * self.n_spires * self.courant(F_CIBLE) / (2.0 * self.rayon_cm / 100.0)

    def champ_induit_v_m(self, f: float) -> float:
        b = MU0 * self.n_spires * self.courant(f) / (2.0 * self.rayon_cm / 100.0)
        return math.pi * f * R_TISSU * b

    @property
    def puissance_bobine_w(self) -> float:
        i = self.courant(F_CIBLE)
        return i * i * self.resistance


def limite_icnirp_publique(f: float) -> float:
    """Interpolation log-log des ancres publiques (cohérente avec circuit.py)."""
    ancres_f = np.array([10.0, 25.0, 400.0, 1000.0])
    ancres_e = np.array([0.010, 0.010, 0.100, 0.400])
    return float(np.interp(math.log10(f), np.log10(ancres_f), ancres_e))


def evaluer(d: Design) -> dict:
    b_mt = d.champ_b_t * 1e3
    e15 = d.champ_induit_v_m(F_CIBLE)
    e75 = d.champ_induit_v_m(F_CHECK)
    return {
        "n": d.n_spires, "fil_mm": d.fil_mm, "v": d.v_alim,
        "r_bobine_ohm": d.resistance, "i_ma": d.courant(F_CIBLE) * 1e3,
        "B_mT": b_mt,
        "E15_mV_m": e15 * 1e3, "ratio15": e15 / limite_icnirp_publique(F_CIBLE),
        "E75_mV_m": e75 * 1e3, "ratio75": e75 / limite_icnirp_publique(F_CHECK),
        "P_bobine_w": d.puissance_bobine_w,
        "dans_bande": BANDE_B_MT[0] <= b_mt <= BANDE_B_MT[1],
        "conforme": max(e15 / limite_icnirp_publique(F_CIBLE),
                        e75 / limite_icnirp_publique(F_CHECK)) <= 1.0,
        "froid": d.puissance_bobine_w <= P_BOBINE_MAX_W,
    }


def feasible(d: dict) -> bool:
    return d["dans_bande"] and d["conforme"] and d["froid"]


def cartographie() -> list[dict]:
    """Le scan complet : N × fil × tension."""
    resultats = []
    for v in (5.0, 12.0, 24.0):
        for fil in (0.3, 0.4, 0.5, 0.6, 0.8):
            for n in range(50, 1201, 25):
                resultats.append(evaluer(Design(n, 3.0, fil, v)))
    return resultats


if __name__ == "__main__":
    res = cartographie()
    ok = [r for r in res if feasible(r)]
    print("═══ SYNTRIUM v0.2a — cartographie des designs (🧮) ═══")
    print(f"  designs scannés : {len(res)} · faisables (bande+conforme+froid) : {len(ok)}")
    if ok:
        ok.sort(key=lambda r: r["P_bobine_w"])
        print("\n  Top 5 (le plus froid d'abord) :")
        for r in ok[:5]:
            print(f"   {r['v']:.0f} V · {r['n']} sp · fil {r['fil_mm']} mm · "
                  f"B = {r['B_mT']:.2f} mT · I = {r['i_ma']:.0f} mA · "
                  f"ratio ICNIRP {max(r['ratio15'], r['ratio75'])*100:.0f} % · "
                  f"P = {r['P_bobine_w']:.2f} W · R_bobine = {r['r_bobine_ohm']:.1f} Ω")
