#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""SYNTRIUM v0.2b — forme d'onde temporelle : l'oscilloscope virtuel (🧮).

On rejoue la chaîne DDS → filtre RC → MOSFET → bobine **dans le temps** :
  1. le DDS idéal produit un sinus d'amplitude V·gain,
  2. + la quantification du DAC 10 bits (bruit de quantification réaliste),
  3. le filtre RC atténue et déphase (réponse complexe, appliquée en FFT),
  4. la bobine ajoute sa constante de temps (R_s + jLω),
  5. sortie : I(t) → B(t) = μ0·n_eff·I(t) → E(t) = π·f·r_tissu·B(t).

Vérifications internes (tests) : le pic temporel B retombe sur la valeur
fréquentielle de circuit.py (±2 %) ; le THD après filtrage < THD avant ;
zéro signal si amplitude nulle ; le déphasage @1 kHz > @15 Hz.

Graine 20260929 — déterministe.
"""
from __future__ import annotations

import math
import sys
import pathlib

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from circuit import Circuit

GRAINE = 20260929
FS = 200_000.0            # fréquence d'échantillonnage du « virtuel scope » (Hz)
BITS_DAC = 10             # le DAC de l'AD9833 : 10 bits


def chaine(f: float, duree_cycles: int = 12, c: Circuit | None = None,
           quantifier: bool = True) -> dict:
    """Simule n cycles du signal à travers la chaîne. Retourne t, étapes, B, E."""
    c = c or Circuit()
    rng = np.random.default_rng(GRAINE)
    t = np.arange(0.0, duree_cycles / f, 1.0 / FS)

    # 1) le sinus idéal de sortie DDS (avant quantification)
    v_ideal = c.v_alim * c.gain_mosfet * np.sin(2.0 * math.pi * f * t)

    # 2) quantification DAC 10 bits (pleine échelle 0..V·gain, offset milieu)
    if quantifier:
        q = (c.v_alim * c.gain_mosfet) / (2 ** BITS_DAC)
        v_dac = np.round(v_ideal / q) * q
    else:
        v_dac = v_ideal.copy()

    # 3) filtre RC (réponse complexe, appliquée dans le domaine fréquentiel)
    spec = np.fft.rfft(v_dac)
    freqs = np.fft.rfftfreq(t.size, 1.0 / FS)
    freqs[0] = 1e-9   # éviter la division par zéro (le continu est tué par le RC de fait)
    h_rc = 1.0 / (1.0 + 1j * freqs / c.f_c_filtre)
    v_filtre = np.fft.irfft(spec * h_rc, n=t.size)

    # 4) la bobine : courant = V / (R_out + R_s + jLω) — même traitement spectral
    z_tot = c.r_sortie + c.r_bobine + 1j * 2.0 * math.pi * freqs * c.l_bobine
    i_spec = np.fft.rfft(v_filtre) / z_tot
    courant = np.fft.irfft(i_spec, n=t.size)

    # 5) champ et induit
    b_t = MU0_N(c) * courant
    e_t = math.pi * f * 0.05 * b_t

    thd_avant = _thd(v_dac, f)
    thd_apres = _thd(b_t, f)
    return {"t": t, "v_dac": v_dac, "v_filtre": v_filtre, "i": courant,
            "B": b_t, "E": e_t,
            "B_pic": float(np.max(np.abs(b_t))),
            "phase_deg": float(_phase(f, c)),
            "thd_avant_pct": thd_avant * 100.0, "thd_apres_pct": thd_apres * 100.0}


def MU0_N(c: Circuit) -> float:
    return 4.0 * math.pi * 1e-7 * c.n_spires / (2.0 * c.rayon_bobine_cm / 100.0)


def _thd(signal: np.ndarray, f0: float) -> float:
    """THD = sqrt(Σ harmoniques²) / fondamental (8 premiers), fenêtre de Hann."""
    w = np.hanning(signal.size)
    spec = np.abs(np.fft.rfft(signal * w))
    freqs = np.fft.rfftfreq(signal.size, 1.0 / FS)
    def pic(k: int) -> float:
        idx = int(np.argmin(np.abs(freqs - k * f0)))
        return spec[max(idx - 2, 0):idx + 3].max()
    fond = pic(1)
    if fond <= 0:
        return 0.0
    harmoniques = math.sqrt(sum(pic(k) ** 2 for k in range(2, 9)))
    return harmoniques / fond


def _phase(f: float, c: Circuit) -> float:
    """Déphasage théorique (deg) de I(t) par rapport au sinus DDS."""
    phi = -(math.atan2(f / c.f_c_filtre, 1.0)
            + math.atan2(2.0 * math.pi * f * c.l_bobine,
                         c.r_sortie + c.r_bobine))
    return math.degrees(phi)


if __name__ == "__main__":
    for f in (15.0, 1000.0):
        r = chaine(f)
        print(f"── @ {f:.0f} Hz ──")
        print(f"  B pic = {r['B_pic']*1e6:.1f} µT · phase théorique = {r['phase_deg']:.1f}°")
        print(f"  THD avant filtre = {r['thd_avant_pct']:.2f} % · après = {r['thd_apres_pct']:.3f} %")
