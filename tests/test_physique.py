# -*- coding: utf-8 -*-
"""Tests SYNTRIUM — formules standard, limites connues, témoin zéro."""
import math
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from syntrium.physique import (champ_induit_faraday, potentiel_membrane_schwan,
                               sar, echauffement, verdict_icnirp, ICNIRP_2010)


def test_faraday_valeur_exacte():
    # E = pi * f * r * B0 : vérification littérale
    e = champ_induit_faraday(15.0, 1.0e-3, 0.05)
    assert abs(e - math.pi * 15.0 * 0.05 * 1.0e-3) < 1e-15
    assert abs(e - 2.356194490192345e-03) < 1e-9   # ~2.36 mV/m


def test_faraday_temoins_zero():
    # TÉMOIN : sans champ ou sans fréquence, pas de champ induit
    assert champ_induit_faraday(0.0, 1.0e-3, 0.05) == 0.0
    assert champ_induit_faraday(15.0, 0.0, 0.05) == 0.0


def test_schwan_limite_basse_frequence():
    # ω·τ → 0 : Vm -> 1.5 * a * E (propriété classique de l'équation de Schwan)
    a, e = 10.0e-6, 1.0
    assert abs(potentiel_membrane_schwan(a, e, 1e-9) - 1.5 * a * e) < 1e-12
    # ω·τ >> 1 : Vm s'effondre (la membrane se « court-circuite »)
    hf = potentiel_membrane_schwan(a, e, 1e9)
    assert hf < 0.01 * 1.5 * a * e   # < 1 % de la valeur basse fréquence


def test_thermique_temoins():
    assert sar(0.0, 1.0) == 0.0
    assert echauffement(0.0, 1000.0) == 0.0
    # PEMF type os : aucun échauffement mesurable (<< 0.001 K sur 1000 s)
    e = champ_induit_faraday(15.0, 1.0e-3, 0.05)
    assert echauffement(sar(0.5, e / math.sqrt(2)), 1000.0) < 1.0e-3


def test_verdict_icnirp():
    v = verdict_icnirp(0.00236, "phosphenes_CNS_10-25Hz_public")
    assert v["conforme"] is True and v["ratio_limite"] < 1.0
    v2 = verdict_icnirp(1.0, "nerve_1kHz_public")
    assert v2["conforme"] is False   # 1 V/m > 0.4 V/m : dépassement détecté
    assert "ICNIRP" in v["source"]


if __name__ == "__main__":
    for nom, fn in sorted({k: v for k, v in globals().items() if k.startswith("test_")}.items()):
        fn()
        print(f"✔ {nom}")
    print("TOUS LES TESTS PASSENT")
