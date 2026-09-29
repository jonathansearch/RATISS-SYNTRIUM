#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""SYNTRIUM — physique de la stimulation électromagnétique basse fréquence.

Formules standard (textbooks / guidelines), implémentées honnêtement et testées :
  1. Champ électrique induit par un champ magnétique variable (Faraday),
     modèle de la boucle circulaire de tissu de rayon r :
         E = (r / 2) * dB/dt          (régime sinusoïdal : E_peak = pi * f * r * B0)
  2. Potentiel de membrane induit (équation de Schwan) pour une cellule sphérique
     de rayon a dans un champ E :
         Vm = 1.5 * a * E * cos(theta) / sqrt(1 + (omega * tau_m)^2)
     (tau_m = constante de temps de membrane ; pour omega*tau << 1, Vm -> 1.5*a*E)
  3. Thermique : débit d'absorption spécifique et échauffement
         SAR = sigma * E_rms^2 / rho          (W/kg)
         dT  ~ SAR * t / c                    (adiabatique, première approximation)

  4. Restrictions de base ICNIRP 2010 (champ électrique interne induit, V/m) :
     - phosphenes magnétiques, CNS tête, 10–25 Hz : 0.010 (public) · 0.050 (pro)
     - stimulation nerveuse ~1 kHz : 0.400 (public) · 0.800 (pro, 400 Hz–3 kHz)
     - 50 Hz : 0.020 (CNS, public) · 0.400 (non-CNS, public)
     Source : ICNIRP, Health Physics 99(6):818-836 (2010).

Étiquette de terrain : 🧮 calcul — aucune mesure matérielle dans ce module.
"""
from __future__ import annotations

import math

# ─────────────────────── constantes ICNIRP (V/m, champ interne induit) ───────

ICNIRP_2010 = {
    "phosphenes_CNS_10-25Hz_public": 0.010,
    "phosphenes_CNS_10-25Hz_occupational": 0.050,
    "nerve_1kHz_public": 0.400,
    "nerve_400Hz-3kHz_occupational": 0.800,
    "CNS_50Hz_public": 0.020,
    "nonCNS_50Hz_public": 0.400,
}
ICNIRP_SOURCE = "ICNIRP 2010, Health Physics 99(6):818-836 (1 Hz - 100 kHz)"


# ───────────────────────────────── formules ──────────────────────────────────

def champ_induit_faraday(f_hz: float, b0_tesla: float, rayon_m: float) -> float:
    """Champ électrique induit crête (V/m) par un B sinusoïdal uniforme.

    E = (r/2) * dB/dt  avec  dB/dt crête = omega * B0  =>  E = pi * f * r * B0.
    Modèle : boucle circulaire de tissu de rayon r, B perpendiculaire.
    """
    if f_hz < 0 or b0_tesla < 0 or rayon_m < 0:
        raise ValueError("paramètres négatifs interdits")
    return math.pi * f_hz * rayon_m * b0_tesla


def potentiel_membrane_schwan(a_m: float, e_v_m: float, f_hz: float,
                              tau_s: float = 1.0e-6, theta: float = 0.0) -> float:
    """Potentiel de membrane induit crête (V) — équation de Schwan, cellule sphérique.

    Vm = 1.5 * a * E * cos(theta) / sqrt(1 + (2*pi*f*tau)^2).
    tau_s ~ 1e-6 s (ordre de grandeur usuel ; bornes 1e-7..1e-3 selon le modèle).
    """
    if a_m <= 0 or e_v_m < 0 or tau_s <= 0:
        raise ValueError("paramètres invalides")
    omega = 2.0 * math.pi * f_hz
    return 1.5 * a_m * e_v_m * math.cos(theta) / math.sqrt(1.0 + (omega * tau_s) ** 2)


def sar(sigma_s_m: float, e_rms_v_m: float, rho_kg_m3: float = 1000.0) -> float:
    """Débit d'absorption spécifique (W/kg) : SAR = sigma * E_rms^2 / rho."""
    if sigma_s_m < 0 or e_rms_v_m < 0 or rho_kg_m3 <= 0:
        raise ValueError("paramètres invalides")
    return sigma_s_m * e_rms_v_m ** 2 / rho_kg_m3


def echauffement(sar_w_kg: float, duree_s: float, c_j_kg_k: float = 3600.0) -> float:
    """Échauffement adiabatique approximatif (K) : dT = SAR * t / c (c ~ eau)."""
    if sar_w_kg < 0 or duree_s < 0 or c_j_kg_k <= 0:
        raise ValueError("paramètres invalides")
    return sar_w_kg * duree_s / c_j_kg_k


def verdict_icnirp(e_interne_v_m: float, cle: str) -> dict:
    """Compare un champ interne induit à une restriction de base ICNIRP 2010."""
    if cle not in ICNIRP_2010:
        raise KeyError(f"clé inconnue : {cle} (voir ICNIRP_2010)")
    limite = ICNIRP_2010[cle]
    return {
        "champ_interne_v_m": e_interne_v_m,
        "limite_icnirp_v_m": limite,
        "ratio_limite": e_interne_v_m / limite,
        "conforme": e_interne_v_m <= limite,
        "source": ICNIRP_SOURCE,
    }


# ─────────────────────────── exemples chiffrés du labo ───────────────────────

EXEMPLES = [
    {
        "nom": "PEMF type os : 15 Hz, 1 mT, r = 5 cm",
        "f": 15.0, "B0": 1.0e-3, "r": 0.05,
    },
    {
        "nom": "Porteuse kHz : 4.6 kHz, 1 mT, r = 5 cm",
        "f": 4600.0, "B0": 1.0e-3, "r": 0.05,
    },
]


def exemples() -> None:
    print("═══ SYNTRIUM — physique v0 (formules standard, testées) ═══")
    a_cellule = 10.0e-6      # cellule de 10 µm de rayon
    sigma = 0.5              # S/m (ordre de grandeur tissu mou ~kHz)
    for ex in EXEMPLES:
        e = champ_induit_faraday(ex["f"], ex["B0"], ex["r"])
        e_rms = e / math.sqrt(2.0)
        vm = potentiel_membrane_schwan(a_cellule, e, ex["f"])
        dT = echauffement(sar(sigma, e_rms), duree_s=1000.0)
        verdict = verdict_icnirp(e, "nerve_1kHz_public" if ex["f"] >= 400
                                 else "phosphenes_CNS_10-25Hz_public")
        print(f"\n· {ex['nom']}")
        print(f"  champ induit E = {e*1e3:.3f} mV/m  "
              f"(ratio ICNIRP : {verdict['ratio_limite']*100:.2f} % — "
              f"{'CONFORME' if verdict['conforme'] else 'DÉPASSE'})")
        print(f"  potentiel de membrane (cellule 10 µm) = {vm*1e9:.2f} nV crête")
        print(f"  échauffement sur 1000 s ≈ {dT:.2e} K  (aucun effet thermique)")
    print("\nLecture RATISS : dans ces fenêtres, l'effet — s'il existe — est "
          "INFORMATIONNEL, jamais thermique.\nLa question du dépôt : quel fenêtrage "
          "la littérature documente-t-elle vraiment ? (phase 4)")


if __name__ == "__main__":
    exemples()
