# 📐 PROTOCOLE — RATISS-SYNTRIUM

**Figé le 29/09/2026, avant exécution. Aucun critère ne sera ajusté après coup.**

---

## Question directrice

> Quel fenêtrage **intensité · fréquence · durée** de stimulation électromagnétique externe
> basse fréquence est **documenté** par la littérature et les autorisations réelles —
> et un banc à matériel abordable peut-il **produire et mesurer** ces fenêtres avec
> une vérification indépendante ?

## Le critère maître (le seul verdict de la v0)

> **Le champ mesuré par l'instrument indépendant doit correspondre au champ calculé
> par `syntrium/physique.py` à ±20 %, sur trois fréquences et trois amplitudes.**

C'est tout. Tant que ce critère n'est pas vert, SYNTRIUM est un banc, pas un « traitement ».
Toute affirmation biologique est **interdite** tant qu'aucune phase partenaire (BSL) n'existe.

## Les témoins (obligatoires, donnent zéro)

| Témoin | Attendu |
|---|---|
| Générateur éteint | lecture magnatomètre ≈ bruit ambiant, écart < seuil de résolution |
| Bobine sans signal | idem |
| Formule vs géométrie connue | erreur < 1 % sur bobine étalon (Helmholtz simplifiée) |
| Echantillon non conducteur (mousse) | pas de signal induit mesurable vs gel conducteur |

## Phases

| # | Phase | Critère figé | Étiquette | Statut |
|---|---|---|---|---|
| 0 | Bases réelles | snapshots PubMed/openFDA/ICNIRP scellés + URL | 📚/🌐 | ✅ jour 1 |
| 1 | Calculateurs | tests verts, formules littérales, témoins zéro | 🧮 | ✅ jour 1 |
| 2 | Banc d'émission | **critère maître** ±20 % ×3 fréq ×3 amp | 📡 | 🔜 |
| 3 | Fantôme gélose | cartographie E/T dans le gel, reproductible 3 runs | 📡 | 🔜 |
| 4 | Fenêtres documentées | table (fréq, amp, durée, résultat, PMID/K-n°) ≥ 20 sources primaires, positives ET négatives | 📚 | 🔜 |
| 5 | Partenaire BSL | hors périmètre de ce dépôt — voir quête RATISS | 🧬 | ⛔ non commencé |

## Ce qui est interdit ici (le frontal, écrit avant tout)

1. Toute mesure **sur un être humain** — même le chef. Jamais.
2. Toute tension > 24 V ou énergie stockée > 10 J. Le banc reste en milliampères.
3. Toute culture cellulaire hors laboratoire partenaire (BSL).
4. Toute promesse de cicatrisation, « accélération de guérison », ou effet thérapeutique —
   dans le README, les commits, les messages Discord. Le vocabulaire est : *mesurer, documenter, vérifier*.
5. Mélanger 🧮 et 📡 : chaque chiffre porte son étiquette.

## Corrections fondatrices vs le pitch d'origine (gravées)

1. ~~7 milliards d'atomes~~ → MD honnête 10⁵–10⁶ atomes (OpenMM, cf. ratiss-bio) **quand**
   la phase moléculaire sera ouverte — modèle jouet étiqueté sinon.
2. ~~fréquences des globules blancs~~ → fenêtres issues de PubMed/openFDA/ICNIRP (réelles, citées).
3. ~~carte du cancer virtuel~~ → enveloppe de sécurité ICNIRP + SAR/ΔT calculée par nos outils.
