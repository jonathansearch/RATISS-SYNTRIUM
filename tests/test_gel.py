# -*- coding: utf-8 -*-
"""Tests fantôme simulé SYNTRIUM (🧮) — témoins + lois physiques + ordres de grandeur."""
import math
import sys
import pathlib

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "syntrium"))
from gel import e_induit_radial, run_thermique, campagne_fantome, R_DISQUE


def test_temoin_zero_champ():
    r = run_thermique(75.0, 0.0, duree_s=60.0)
    assert float(np.max(np.abs(r["delta_T"]))) == 0.0


def test_e_lineaire_en_r():
    e = e_induit_radial(75.0, 1e-3)
    # nul au centre, doublé quand r double
    assert e[0] == 0.0
    i40 = int(0.04 / R_DISQUE * (len(e) - 1))
    i20 = int(0.02 / R_DISQUE * (len(e) - 1))
    assert abs(e[i40] / e[i20] - 2.0) < 1e-9


def test_e_proportionnel_a_f_et_b():
    a = e_induit_radial(75.0, 1e-3)[-1]
    b = e_induit_radial(150.0, 1e-3)[-1]
    c = e_induit_radial(75.0, 2e-3)[-1]
    assert abs(b / a - 2.0) < 1e-9 and abs(c / a - 2.0) < 1e-9


def test_delta_T_proportionnel_a_B_carre():
    r1 = run_thermique(75.0, 1e-3, duree_s=120.0)
    r2 = run_thermique(75.0, 2e-3, duree_s=120.0)
    rapport = r2["delta_T_max_K"] / r1["delta_T_max_K"]
    assert abs(rapport - 4.0) < 0.05      # p = σE² ∝ B²


def test_chauffage_negligeable_meme_a_2mT():
    # 2 mT à 75 Hz pendant 10 min : le fantôme reste au millionième de degré
    r = run_thermique(75.0, 2e-3, duree_s=600.0)
    assert r["delta_T_max_K"] < 1e-6


def test_montee_monotone_au_centre():
    r = run_thermique(75.0, 1e-3, duree_s=600.0)
    h = r["historique_centre"]
    assert all(h[i + 1] >= h[i] for i in range(len(h) - 1)) and h[-1] > 0


if __name__ == "__main__":
    for nom, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print(f"✔ {nom}")
    print("TOUS LES TESTS PASSENT")
