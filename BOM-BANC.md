# 📡 BOM-BANC — le matériel réel de SYNTRIUM v0

**Philosophie : des modules du commerce, assemblés à la main, mesurés indépendamment.**
C'est l'atelier électronique (Arduino) au service direct du labo — chaque montage du cours
devient un organe du banc. Coût total visé : **budget étudiant**, pas budget labo.

---

## 🧰 La liste (prix indicatifs, dispo en ligne/là-bas)

| # | Module | Rôle dans le banc | Prix ≈ |
|---|---|---|---|
| 1 | **Arduino Nano / Uno** (ou Pico) | le chef d'orchestre : génère les signaux, timing exact | 3–8 k FCFA |
| 2 | **AD9833** (module DDS, SPI) | générateur de sinusoïdes 0–12,5 MHz, fréquence programmable | 3–6 k FCFA |
| 3 | **Bobine** (à bobiner soi-même) | émet le champ B — fil de cuivre émaillé 0,3–0,5 mm, ~100–500 spires | 1–3 k FCFA |
| 4 | **Magnatomètre 3 axes** MLX90393 (ou HMC5883L) | **la mesure indépendante** — le juge du critère maître ±20 % | 5–12 k FCFA |
| 5 | **Oscilloscope d'entrée de gamme** (DSO138 / DSO-TC3) | voir la forme d'onde réelle aux bornes de la bobine | 15–25 k FCFA |
| 6 | **Résistances/MOSFET de puissance** + dissipateur | piloter le courant de bobine proprement | 2–5 k FCFA |
| 7 | **Multimètre** | courants, tensions, continuité — l'indispensable | 5–15 k FCFA |
| 8 | Agar-agar + NaCl | le **fantôme gélose** conducteur (recette phase 3) | 2–4 k FCFA |
| 9 | Sonde de température (DS18B20) | la mesure thermique réelle du fantôme | 1–3 k FCFA |

**Total ≈ 40–80 k FCFA** selon ce qui est déjà là. (Le banc NV complet, lui, reste à ~3,5 M FCFA —
un autre chapitre.)

## 🧪 Le fantôme gélose (recette standard de la littérature d'ingénierie)

- 1 L d'eau + 10–20 g d'agar-agar + 1–5 g de NaCl (la conductivité se règle par le sel —
  et elle se **mesure**, on ne la devine pas)
- coulé dans un moule, refroidi ; c'est notre « tissu » de test — **jamais de la chair**

## ⚙️ La chaîne du signal (phase 2)

```
Arduino ──SPI──> AD9833 (sinus f programmable) ──> étage MOSFET ──> bobine
                                                                      │
                              champ B ≈ µT–mT (courts polypes, faible voltage)
                                                                      ▼
        magnatomètre MLX90393 (I²C) ──> Arduino ──> série PC ──> comparaison
                                                                      avec
                                        syntrium/physique.py (le calcul indépendant)
```

## 🛑 Les limites de sécurité du banc (figées, non négociables)

1. Alimentation ≤ 24 V DC, courant ≤ 500 mA dans la bobine.
2. Aucun condensateur de stockage d'énergie > 10 J (pas de « TMS maison », jamais).
3. Séances de fonctionnement < 10 min, bobine à l'air libre, jamais contre le corps.
4. Débranchement physique (interrupteur secteur) avant toute modification de câblage.
5. Étiquette 📡 pour chaque chiffre mesuré — le 🧮 du calcul reste à part.

## 🗺️ L'ordre des montages (l'atelier → le banc)

| Étape | Montage | Il est vert quand… |
|---|---|---|
| A | blink LED (le « bonjour » de l'atelier) | la LED clignote à 1 Hz mesuré |
| B | lecture MLX90393 | le magnatomètre renvoie le champ terrestre (~50 µT) et réagit à un aimant |
| C | AD9833 en sinus | l'oscilloscope voit le sinus programmé (100 Hz puis 1 kHz) |
| D | bobine + MOSFET | la bobine chauffe normalement (doux), champ mesuré ≠ 0 |
| E | **critère maître** | mesuré = calculé à ±20 % sur 3 fréquences × 3 amplitudes |
| F | fantôme | cartographie E/T dans le gel, 3 runs reproductibles |
