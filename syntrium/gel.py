#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""SYNTRIUM v0.2c — le fantôme gélose simulé (🧮 in silico).

On modélise le disque de gel du protocole (phase 3) AVANT de le couler :
  - géométrie : disque axisymétrique r = 0 → 8 cm (rayon utile du banc) ;
  - excitation : B(t) uniforme → E_θ(r) = π·f·r·B (Faraday, boucle circulaire) ;
  - dépôt : p(r) = σ·E²  [W/m³]  (Joule dans le gel conducteur) ;
  - thermique : ρc·∂T/∂t = p + k·(1/r)·d/dr(r·dT/dr)  résolue en FTCS explicite,
    frontières : dT/dr = 0 au centre · convection -k·dT/dr = h·(T−T_amb) au bord.

Constantes (gel physiologique standard, cf. littérature fantômes diélectriques) :
  σ = 0,5 S/m (réglée au sel, mesurée au banc) · k = 0,5 W/m/K · ρ = 1000 kg/m³
  c = 3600 J/kg/K · h = 10 W/m²/K (air calme) · T_amb = 25 °C.

Graine 20260929 — déterministe. RÉSULTAT ATTENDU (et vérifié par tests) :
des ΔT ~ 10⁻⁷ K — le fantôme ne bouge pas d'un millionième de degré.
"""
from __future__ import annotations

import json
import math
import pathlib

import numpy as np

GRAINE = 20260929
SIGMA = 0.5            # S/m
K_TH = 0.5             # W/m/K
RHO = 1000.0           # kg/m³
C_TH = 3600.0          # J/kg/K
H_CONV = 10.0          # W/m²/K
R_DISQUE = 0.08        # m
N_PTS = 161


def e_induit_radial(f: float, b_t: float) -> np.ndarray:
    """E_θ(r) crête (V/m) dans le disque — linéaire en r, nul au centre."""
    r = np.linspace(0.0, R_DISQUE, N_PTS)
    return math.pi * f * r * b_t


def run_thermique(f: float, b_t: float, duree_s: float = 600.0,
                  dt_s: float = 0.2) -> dict:
    """FTCS explicite : retourne ΔT(r) final + l'historique au point de contrôle."""
    dr = R_DISQUE / (N_PTS - 1)
    r = np.linspace(0.0, R_DISQUE, N_PTS)
    p = SIGMA * e_induit_radial(f, b_t) ** 2          # W/m³ (indépendant du temps)

    dT = np.zeros(N_PTS)
    pas = int(duree_s / dt_s)
    alpha = K_TH * dt_s / (RHO * C_TH * dr * dr)      # ~0.09 < 0.25 : stable
    historique = []

    for n in range(pas):
        lap = np.zeros(N_PTS)
        lap[1:-1] = (dT[2:] + dT[:-2] - 2.0 * dT[1:-1]) / (dr * dr) \
                    + (dT[2:] - dT[:-2]) / (2.0 * dr * r[1:-1])     # (1/r)d/dr(r dT/dr)
        lap[0] = 2.0 * (dT[1] - dT[0]) / (dr * dr)                   # régularité au centre
        dT += dt_s * (p + K_TH * lap) / (RHO * C_TH)
        # bord convectif (Robin) : -k dT/dr = h (T - 0)   (ΔT mesuré au-dessus de l'ambiant)
        dT[-1] = dT[-2] / (1.0 + H_CONV * dr / K_TH)
        if (n + 1) % max(pas // 6, 1) == 0:
            historique.append(float(dT[N_PTS // 2]))

    return {"r": r, "delta_T": dT, "delta_T_max_K": float(dT.max()),
            "delta_T_centre_K": float(dT[0]), "historique_centre": historique,
            "E_edge_V_m": float(e_induit_radial(f, b_t)[-1]),
            "f": f, "B_mT": b_t * 1e3, "duree_s": duree_s}


def campagne_fantome() -> dict:
    """Le pire cas réel : 75 Hz (E ∝ f·B dans la bande) pendant 10 min, 4 designs."""
    designs = {
        "banc 5V (0,335 mT)": 0.335e-3,
        "clinique basse (0,5 mT)": 0.5e-3,
        "clinique médiane (1 mT)": 1.0e-3,
        "clinique haute (2 mT)": 2.0e-3,
    }
    resultats = {nom: run_thermique(75.0, b) for nom, b in designs.items()}
    # JSON : scalaires + historique seulement (les tableaux r/delta_T servent aux figures)
    resume = {nom: {k: v for k, v in r.items() if k not in ("r", "delta_T")}
              for nom, r in resultats.items()}
    return {"graine": GRAINE, "constantes": {"sigma": SIGMA, "k": K_TH, "rho": RHO,
                                             "c": C_TH, "h": H_CONV, "r_m": R_DISQUE},
            "designs": resume, "_tableaux": resultats}


if __name__ == "__main__":
    print("═══ SYNTRIUM v0.2c — fantôme gélose simulé (🧮) ═══")
    e = e_induit_radial(75.0, 1e-3)
    print(f"  E au bord @75 Hz/1 mT : {e[-1]*1e3:.1f} mV/m (linéaire en r, 0 au centre)")
    camp = campagne_fantome()
    for nom, r in camp["designs"].items():
        print(f"  {nom:26s} → ΔT max sur 600 s = {r['delta_T_max_K']:.2e} K")
    out = pathlib.Path(__file__).resolve().parents[1] / "resultats"
    out.mkdir(exist_ok=True)
    resume = {k: v for k, v in camp.items() if k != "_tableaux"}
    (out / "fantome.json").write_text(json.dumps(resume, ensure_ascii=False, indent=1))
    print("  → resultats/fantome.json écrit")
