# -*- coding: utf-8 -*-
"""Tests oscilloscope virtuel SYNTRIUM (🧮) — cohérences temporel ↔ fréquentiel."""
import math
import sys
import pathlib

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "syntrium"))
from onde import chaine
from circuit import Circuit, champ_b
import numpy as np


def test_pic_b_coherent_avec_frequentiel():
    # le pic temporel @15 Hz doit retomber sur circuit.py (valeur quasi DC) à ±2 %
    c = Circuit()
    r = chaine(15.0)
    b_freq = float(champ_b(np.array([15.0]), c)[0])
    assert abs(r["B_pic"] - b_freq) / b_freq < 0.02


def test_temoin_zero_amplitude():
    from circuit import Circuit as C
    c = C(v_alim=0.0)
    r = chaine(15.0, c=c)
    assert float(np.max(np.abs(r["B"]))) == 0.0


def test_thd_baisse_apres_filtre():
    # à 1 kHz les harmoniques (2-8 kHz) sont au-dessus de fc=159 Hz : le filtre les taille
    r = chaine(1000.0)
    assert r["thd_apres_pct"] < 0.5 * r["thd_avant_pct"]
    # à 15 Hz les harmoniques sont sous fc : le filtre ne fait presque rien (et n'a pas à le faire)
    r15 = chaine(15.0)
    assert r15["thd_apres_pct"] <= 1.01 * r15["thd_avant_pct"] + 0.01
    # mais le THD source (DAC 10 bits) reste faible : la chaîne est propre
    assert r15["thd_avant_pct"] < 5.0


def test_phase_croissante_avec_f():
    r15 = chaine(15.0)
    r1k = chaine(1000.0)
    assert abs(r1k["phase_deg"]) > abs(r15["phase_deg"]) > 0.0


def test_e_induit_taux_zero():
    # E(t) = pi·f·r·B(t) : cohérence point par point
    r = chaine(15.0)
    attendu = math.pi * 15.0 * 0.05 * r["B"]
    assert float(np.max(np.abs(r["E"] - attendu))) < 1e-15


if __name__ == "__main__":
    for nom, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print(f"OK {nom}")
    print("TOUS LES TESTS PASSENT")
