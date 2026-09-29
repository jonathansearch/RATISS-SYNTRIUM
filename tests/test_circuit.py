# -*- coding: utf-8 -*-
"""Tests du circuit SYNTRIUM v0.1 (🧮) — valeurs analytiques + témoins zéro."""
import math
import sys
import pathlib

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "syntrium"))
from circuit import Circuit, gain_circuit, champ_b, champ_induit, icnirp_ratio, campagne


def test_courant_continu_valeur_exacte():
    # à f -> 0 : H_RC = 1, impédance bobine = R_s  =>  I = V*gain/(R_out + R_s)
    c = Circuit()
    i0 = gain_circuit(np.array([1e-9]), c)[0]
    attendu = c.v_alim * c.gain_mosfet / (c.r_sortie + c.r_bobine)
    assert abs(i0 - attendu) < 1e-12


def test_temoins_zero():
    c = Circuit()
    assert float(gain_circuit(np.array([0.0]), c)[0]) > 0.0          # pas d'erreur à f=0
    assert float(champ_b(np.array([0.0]), c)[0]) > 0.0
    assert float(champ_induit(np.array([0.0]), np.array([1e-3]))[0]) == 0.0  # E=0 à f=0 (Faraday)


def test_rolloff_haute_frequence():
    # au-dessus de fc du filtre ET avec l'inductance, le courant doit chuter
    c = Circuit()
    i_bf = gain_circuit(np.array([50.0]), c)[0]
    i_hf = gain_circuit(np.array([100_000.0]), c)[0]
    assert i_hf < 0.05 * i_bf   # < 5 % du courant basse fréquence


def test_fenetre_elf_plus_forte():
    # dans la bande ELF (15-75 Hz) le circuit délivre quasi son courant max
    c = Circuit()
    i_max = gain_circuit(np.array([1e-9]), c)[0]
    i_15 = gain_circuit(np.array([15.0]), c)[0]
    assert i_15 > 0.90 * i_max


def test_icnirp_ancrage_1khz():
    # ratio = E/0.400 exactement à 1 kHz (ancre officielle)
    c = Circuit()
    f = np.array([1000.0])
    ratio = icnirp_ratio(f, champ_induit(f, champ_b(f, c)))[0]
    e = champ_induit(f, champ_b(f, c))[0]
    assert abs(ratio - e / 0.400) < 1e-12


def test_zone_verte_et_realisme():
    r = campagne()
    # le banc 5 V reste sous 30 % ICNIRP partout (sûr par construction)
    assert float(np.max(r["ratio"])) < 0.30
    # et il produit des µT (pas des mT) : réalisme d'un montage d'atelier
    assert 20.0 < r["B_1khz_ut"] < 100.0
    assert 5.0 < r["i_1khz_ma"] < 200.0


if __name__ == "__main__":
    for nom, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print(f"✔ {nom}")
    print("TOUS LES TESTS PASSENT")
