#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Sceau SHA-256 de RATISS-SYNTRIUM (convention RATISS Labs).
Usage : python3 outils/manifeste.py            -> scelle (écrit MANIFESTE.json)
        python3 outils/manifeste.py --verifier -> vérifie."""
import hashlib, json, pathlib, sys, datetime

racine = pathlib.Path(__file__).resolve().parents[1]

def empreintes():
    fichiers, octets = {}, 0
    for p in sorted(racine.rglob("*")):
        if not p.is_file() or ".git" in p.parts or p.name == "MANIFESTE.json":
            continue
        b = p.read_bytes()
        fichiers[str(p.relative_to(racine))] = hashlib.sha256(b).hexdigest()
        octets += len(b)
    return fichiers, octets

if "--verifier" in sys.argv:
    m = json.loads((racine / "MANIFESTE.json").read_text())
    ok = ko = 0
    for chemin, attendu in m["fichiers"].items():
        p = racine / chemin
        if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != attendu:
            print(f"NON CONFORME : {chemin}"); ko += 1
        else:
            ok += 1
    print(f"{ok}/{ok+ko} empreinte(s) conforme(s), {ko} problème(s)")
    sys.exit(1 if ko else 0)
else:
    fichiers, octets = empreintes()
    json.dump({"total_fichiers": len(fichiers), "octets_total": octets,
               "compile_le": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "fichiers": fichiers},
              open(racine / "MANIFESTE.json", "w"), ensure_ascii=False, indent=1)
    print(f"MANIFESTE scellé : {len(fichiers)} fichiers, {octets} octets")
