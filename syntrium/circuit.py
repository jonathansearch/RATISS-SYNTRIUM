#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""SYNTRIUM v0.1 — simulation in silico de l'émetteur (étape A : le circuit).

Étiquette de terrain : 🧮 calcul — AUCUNE mesure matérielle dans ce module.

Le circuit modélisé (celui que Jonathan remontera plus tard en dur sur Arduino) :

   AD9833 (sinus f, amplitude numérique)  ->  étage MOSFET (passe-bas RC)
   ->  bobine R_s + L en série  ->  champ B(t) = mu0 * n * I(t)

Modèles standard (textbooks) :
  - DDS : sinusoïde de fréquence f, amplitude programmée (0..1 par code),
  - filtre RC passe-bas du premier ordre : H_RC(f) = 1 / (1 + j f/f_c),
  - bobine réelle : impédance Z(f) = R_s + j L omega,
  - courant : I(f) = V(f) / |Z(f)|  (source de Thévenin V_th, résistance R_out),
  - champ : B(f) = mu0 * n_eff * I(f)  (solénoïde/Biot-Savart approx),
  - champ induit interne (Faraday) et verdict ICNIRP (cf. physique.py).

Graine fixée : 20260929. Déterministe : mêmes entrées -> mêmes courbes.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, asdict, field

import numpy as np

GRAINE = 20260929

# ───────────────────────── paramètres du circuit (réalistes, sourcés datasheets) ─────

@dataclass
class Circuit:
    """Paramètres de l'émetteur — valeurs d'un montage d'atelier honnête."""
    v_alim: float = 5.0            # V — Arduino 5 V, unifilaire, sécurité du BOM
    r_sortie: float = 50.0         # ohm — étage MOSFET + résistance série (datasheet type)
    r_bobine: float = 6.0          # ohm — fil de cuivre émaillé 0,4 mm, ~200 spires (mesurable au multimètre)
    l_bobine_uh: float = 2200.0    # µH — inductance cible du bobinage (L-mètre d'atelier)
    c_filtre_nf: float = 100.0     # nF — condensateur du passe-bas après le DDS
    r_filtre: float = 10000.0      # ohm — résistance du passe-bas (fc ≈ 159 Hz : laisse passer l'ELF, coupe les résidus DDS)
    n_spires: int = 200            # spires
    rayon_bobine_cm: float = 3.0   # cm — rayon moyen du bobinage
    gain_mosfet: float = 0.9       # v/v — pont diviseur de sortie (0..1)

    # dérivés
    @property
    def f_c_filtre(self) -> float:
        return 1.0 / (2.0 * math.pi * self.r_filtre * self.c_filtre_nf * 1e-9)

    @property
    def l_bobine(self) -> float:
        return self.l_bobine_uh * 1e-6

    @property
    def n_eff_m(self) -> float:
        """spires/mètre équivalentes pour B ≈ mu0 * n_eff * I (bobine courte : n/D)."""
        return self.n_spires / (2.0 * self.rayon_bobine_cm / 100.0)


def gain_circuit(f_hz: np.ndarray, c: Circuit) -> np.ndarray:
    """Chaîne complète DDS -> RC -> bobine : amplitude de courant I(f) en ampères.

    V(f)  = v_alim * gain * |H_RC(f)|
    Z(f)  = sqrt(R_s^2 + (L omega)^2)   (bobine réelle série)
    + pont diviseur avec R_sortie : I = V * R_tot/(R_sortie+R_tot) / R_tot = V/(R_sortie+R_tot)
    """
    h_rc = 1.0 / np.sqrt(1.0 + (f_hz / c.f_c_filtre) ** 2)
    v_sorte = c.v_alim * c.gain_mosfet * h_rc
    z_bobine = np.sqrt(c.r_bobine ** 2 + (2.0 * math.pi * f_hz * c.l_bobine) ** 2)
    return v_sorte / (c.r_sortie + z_bobine)


def champ_b(f_hz: np.ndarray, c: Circuit) -> np.ndarray:
    """Champ magnétique crête au centre de la bobine (tesla) : B = mu0 * n_eff * I."""
    mu0 = 4.0 * math.pi * 1e-7
    return mu0 * c.n_eff_m * gain_circuit(f_hz, c)


def champ_induit(f_hz: np.ndarray, b_t: np.ndarray, rayon_tissu_m: float = 0.05) -> np.ndarray:
    """Champ électrique interne induit crête (V/m) : E = pi * f * r * B (cf. physique.py)."""
    return math.pi * f_hz * rayon_tissu_m * b_t


def icnirp_ratio(f_hz: np.ndarray, e_v_m: np.ndarray) -> np.ndarray:
    """Ratio E / limite ICNIRP publique (phosphènes <25 Hz, nerfs ≥400 Hz, interp log-log)."""
    f = np.asarray(f_hz, dtype=float)
    e = np.asarray(e_v_m, dtype=float)
    # points d'ancrage officiels (public) : (Hz, V/m)
    ancres_f = np.array([10.0, 25.0, 400.0, 1000.0, 3000.0, 100_000.0])
    ancres_e = np.array([0.010, 0.010, 0.100, 0.400, 0.800, 0.800])
    limite = np.interp(np.log10(f), np.log10(ancres_f), ancres_e)
    return e / limite


# ─────────────────────────────── la campagne ────────────────────────────────

def campagne(c: Circuit | None = None, n_points: int = 4000) -> dict:
    """Balayage spectral complet 10 Hz -> 100 kHz. Retourne tout pour les figures."""
    c = c or Circuit()
    f = np.logspace(math.log10(10.0), math.log10(100_000.0), n_points)
    b = champ_b(f, c)
    e = champ_induit(f, b)
    ratio = icnirp_ratio(f, e)
    return {
        "graine": GRAINE,
        "circuit": asdict(c),
        "f_c_filtre_hz": c.f_c_filtre,
        "f": f, "B": b, "E": e, "ratio": ratio,
        "i_1khz_ma": float(gain_circuit(np.array([1000.0]), c)[0] * 1e3),
        "B_1khz_ut": float(champ_b(np.array([1000.0]), c)[0] * 1e6),
        "E_1khz_mvm": float(champ_induit(np.array([1000.0]),
                                         champ_b(np.array([1000.0]), c))[0] * 1e3),
        "f_zone_verte_max_hz": float(f[np.where(ratio <= 0.30)[0]].max()) if (ratio <= 0.30).any() else 0.0,
    }


if __name__ == "__main__":
    r = campagne()
    print("═══ SYNTRIUM v0.1 — simulation du circuit (🧮 in silico) ═══")
    print(f"  fréquence de coupure du filtre RC : {r['f_c_filtre_hz']:.0f} Hz")
    print(f"  courant @1 kHz  : {r['i_1khz_ma']:.1f} mA")
    print(f"  champ B @1 kHz  : {r['B_1khz_ut']:.1f} µT")
    print(f"  champ E induit @1 kHz : {r['E_1khz_mvm']:.1f} mV/m")
    print(f"  plus haute fréquence en zone verte (≤30 % ICNIRP) : {r['f_zone_verte_max_hz']:.0f} Hz")
