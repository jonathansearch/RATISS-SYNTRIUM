# ⚡ RATISS-SYNTRIUM — L'émetteur biomimétique à faible voltage

**Programme RATISS-BIOELECTRO · Bioélectricité externe · v0.0-bases**

*Par **RATISS Labs** — Jonathan Evina · Yaoundé · MIT*

---

## 🎯 La vision (en une phrase)

**Un dispositif externe à faible voltage qui « parle » au langage électrique du corps** —
champs pulsés calibrés dans les fenêtres où la littérature montre des effets biologiques réels —
sans jamais envahir les cellules : pas d'implant, pas de nanoparticule, pas de molécule.

L'inspiration : le corps est déjà électrique. Les blessures créent des **champs électriques
endogènes** qui guident la migration cellulaire (électrotaxie) ; la stimulation électromagnétique
pulsée (PEMF) est **autorisée depuis 1979 aux USA** pour consolider les fractures récalcitrantes ;
la bioélectricité est un domaine de recherche actif. SYNTRIUM vise la question RATISS :

> **Quel est le vrai fenêtrage intensité / fréquence / durée — mesuré, pas mythifié —
> et peut-on le produire avec un matériel abordable, souverain, et sûr ?**

## ⚖️ Les trois corrections RATISS (ce que la version « pitch » disait — et ce qu'on fait à la place)

La méthode du labo interdit de bâtir sur du non-sourcé. Trois corrections fondatrices :

| Le pitch disait… | La réalité (mesurée) | Ce que RATISS fait |
|---|---|---|
| Simuler **7 milliards d'atomes** avec NumPy | Impossible : seulement les supercalculateurs mondiaux traitent ~10⁹ atomes. Un portable : ~10⁵–10⁶ atomes en MD (OpenMM — cf. `ratiss-bio`) | MD honnête à l'échelle réelle de nos moyens + modèle jouet **étiqueté** 🧮, jamais présenté comme du tissu |
| Fréquences « émises par les globules blancs » | Ce n'est pas une mesure établie. Ce qui EST établi : les champs endogènes de blessure (électrotaxie), les paramètres des dispositifs PEMF autorisés, les limites ICNIRP | **Base de données réelle** : PubMed (242 papiers PEMF×cicatrisation interrogés le jour 1), openFDA (dispositifs 510(k)), ICNIRP 2010 (limites chiffrées) |
| Une « carte du cancer virtuel » simulée | La cancérogenèse ne se simule pas dans un modèle NumPy — ce serait une prétention, interdite au labo | L'**enveloppe de sécurité réelle** : champ induit interne < restrictions de base ICNIRP + thermique (SAR/ΔT) calculés par nos propres outils |

Autrement dit : **le fenêtrage SYNTRIUM sera extrait de la littérature et des autorisations
réelles, puis vérifié par nos calculateurs et notre banc — pas deviné.**

## 🧪 Les trois couches du programme (version honnête)

| Couche | Contenu | Statut v0 |
|---|---|---|
| 📚 **Bases réelles** | PubMed (PEMF × cicatrisation, champs endogènes), openFDA 510(k), limites ICNIRP 2010 chiffrées | ✅ interrogées le jour 1, snapshots dans `DONNEES/` |
| 🧮 **Physique calculée** | Champ induit (Faraday), potentiel de membrane (Schwan), thermique (SAR, ΔT) — comparés aux limites ICNIRP | ✅ `syntrium/physique.py` + tests |
| 📡 **Banc réel** | Générateur de signaux + bobine + magnatomètre + fantôme gélose — construit autour de **Arduino** (l'atelier en cours !) | 🔜 `BOM-BANC.md` |

## 📐 Ce que les calculateurs montrent déjà (premier verdict honnête)

Avec `syntrium/physique.py` (formules standard, testées) :

- **PEMF typique os (15 Hz, 1 mT, rayon 5 cm)** → champ induit interne ≈ **2,4 mV/m** : très en
  dessous des limites ICNIRP (10–800 mV/m selon fréquence/cas). La fenêtre PEMF historique est
  **faible et prudente** — c'est précisément pour ça qu'elle a 45 ans d'usage.
- **Porteuse kHz (4,6 kHz, 1 mT)** → ≈ **0,72 V/m** : c'est la **porteuse**, pas la répétition,
  qui fait le champ induit. Le fenêtrage réel se joue là.
- **Thermique** : à ces niveaux, ΔT < 0,001 °C — **aucun échauffement**. Le mécanisme de SYNTRIUM,
  s'il existe, est **informationnel**, pas thermique. C'est une hypothèse de travail, pas un résultat.

## 🚦 Les phases (critères figés au protocole)

0. **Bases réelles** — snapshots PubMed/openFDA/ICNIRP scellés. *Fait — jour 1.*
1. **Calculateurs** — formules standard, tests verts, exemples chiffrés. *Fait — jour 1.*
2. **Banc d'émission** — Arduino + AD9833 + bobine ; mesure indépendante par magnatomètre ; le
   **témeno** : le champ mesuré doit correspondre au champ calculé à ±20 %.
3. **Fantôme gélose** — mesures dans un gel conducteur (recette du banc), cartographie E/T réelle.
4. **Extraction de fenêtres** — revue systématique de la littérature (paramètres des études
   positives ET négatives publiées) → carte des fenêtres **documentées**, avec leurs preuves.
5. **Et ensuite ?** — la validation cellulaire exige un **laboratoire BSL partenaire** (cf. quête
   RATISS). Aucune expérience sur l'humain, jamais, à aucun stade de ce dépôt.

## 🛑 Règles de sécurité et d'honnêteté (non négociables)

1. **Jamais sur un être humain.** Le banc teste des fantômes de gel, pas des gens.
2. **Basse tension uniquement** (≤ 24 V, milliampères). Rien qui ressemble à la TMS/capacitifs haute énergie.
3. **Aucune culture cellulaire à la maison** — c'est du BSL, ça attend une institution.
4. **Aucune promesse de soin.** SYNTRIUM v0 est un **instrument de mesure et de documentation**.
   *Prouver, pas prétendre.*
5. 🧮 calcul · 📡 banc matériel — étiquettes séparées, jamais mélangées.

## 🗂️ Structure

```
RATISS-SYNTRIUM/
├── README.md                ← vous êtes ici
├── PROTOCOLE.md             ← critères, témoins, fenêtres
├── BOM-BANC.md              ← le matériel réel (Arduino, AD9833, capteurs, gel)
├── DONNEES/
│   └── bases_externes.json  ← snapshots réels : PubMed, openFDA, ICNIRP (datés, URL)
├── syntrium/
│   └── physique.py          ← Faraday, Schwan, SAR + limites ICNIRP
├── tests/
│   └── test_physique.py
├── outils/
│   └── manifeste.py         ← le sceau SHA-256 du labo
├── MANIFESTE.json
└── LICENSE                  ← MIT
```

## ▶️ Rejouer

```bash
git clone https://github.com/jonathansearch/RATISS-SYNTRIUM.git
cd RATISS-SYNTRIUM
python3 syntrium/physique.py          # les exemples chiffrés
python3 -m pytest tests/ -q           # les tests
python3 outils/manifeste.py --verifier  # le sceau
```

Dépendances : Python 3.10+, rien d'autre (numpy optionnel).

---

*RATISS Labs · Jonathan Evina · Yaoundé · 29/09/2026 · MIT*
*« La technologie la plus puissante n'est pas celle qui force la nature — mais pour l'écouter,
il faut d'abord des capteurs. »* ⚡
