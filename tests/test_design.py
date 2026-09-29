# -*- coding: utf-8 -*-
"""Tests cartographie SYNTRIUM (🧮) — cohérences analytiques + témoins."""
import math
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "syntrium"))
from design import Design, evaluer, feasible, limite_icnirp_publique, cartographie


def test_resistance_formule_litterale():
    d = Design(200, 3.0, 0.4, 5.0)
    a = math.pi * (0.4e-3) ** 2 / 4.0
    attendu = 1.68e-8 * 200 * 2 * math.pi * 0.03 / a
    assert abs(d.resistance - attendu) < 1e-12


def test_inductance_cohorente_banc():
    # N=200, r=3 cm → ~2,2-2,4 mH : cohérent avec le circuit.py du banc (2,2 mH)
    d = Design(200, 3.0, 0.4, 5.0)
    assert 2.0e-3 < d.inductance < 2.6e-3


def test_banc_5v_retrouve_les_335_ut():
    # le design du banc (200 sp, 0,4 mm, 5 V) doit retomber sur ~0,34 mT @15 Hz
    r = evaluer(Design(200, 3.0, 0.4, 5.0))
    assert abs(r["B_mT"] - 0.335) < 0.05


def test_temoin_zero_courant():
    d = Design(200, 3.0, 0.4, 0.0)   # zéro volt → zéro champ
    assert d.champ_b_t == 0.0
    assert d.champ_induit_v_m(15.0) == 0.0


def test_24v_atteint_la_bande():
    r = evaluer(Design(200, 3.0, 0.4, 24.0))
    assert 0.5 <= r["B_mT"] <= 2.0
    assert r["dans_bande"] and r["conforme"] and r["froid"]


def test_limites_icnirp_ancres():
    assert abs(limite_icnirp_publique(25.0) - 0.010) < 1e-9
    assert abs(limite_icnirp_publique(1000.0) - 0.400) < 1e-9
    assert limite_icnirp_publique(75.0) > limite_icnirp_publique(25.0)  # croît avec f


def test_la_cartographie_trouve_des_solutions():
    res = cartographie()
    ok = [r for r in res if feasible(r)]
    assert len(ok) >= 5, "la cartographie doit trouver des designs conformes en bande"
    # et au moins une solution à 5 V (le souverain parfait)
    assert any(r["v"] == 5.0 for r in ok), "il doit exister une solution 5 V"


if __name__ == "__main__":
    for nom, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print(f"✔ {nom}")
    print("TOUS LES TESTS PASSENT")
