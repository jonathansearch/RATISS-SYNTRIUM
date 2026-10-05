# ⚡ RATISS-SYNTRIUM — The low-voltage biomimetic emitter

**RATISS-BIOELECTRO Program · External bioelectricity · v0.2-in-silico**

*By **RATISS Labs** — Jonathan Evina · Yaoundé · MIT*

> **v0.2 (29/09/2026): ALL the in-silico validation is delivered.** Circuit, virtual
> oscilloscope, design mapping, agar phantom (heat equation) — **8 figures,
> 29 green tests, seed 20260929, zero hardware required.** The Arduino bench will come AFTER,
> and it will already have its complete digital twin. 🧮

---

## 🖥️ v0.1 — the in-silico campaign (what the simulator already shows)

The modeled circuit (the one the chief will physically rebuild later):

```
AD9833 (sine f) → RC low-pass filter (fc ≈ 159 Hz) → MOSFET (gain 0.9) → 200-turn coil, 2.2 mH
```

**The five figures** (all regenerable with `python3 syntrium/figures.py`, seed 20260929):

| Figure | What it shows |
|---|---|
| `fig_A_circuit.png` | circuit response: coil current and B field vs frequency (the 159 Hz filter passes the ELF, cuts the DDS residue) |
| `fig_B_fenetres.png` | **the window map**: induced E vs ICNIRP limits, green/amber/red zones + limit ratio in % |
| `fig_C_low_freq.png` | zoom 10 Hz – 2 kHz: the honest operating window |
| `fig_D_schema.png` | the simulated circuit diagram — to understand before soldering |
| `fig_E_bande_clinique.png` | **THE key figure**: the 5 V bench against the documented clinical PEMF band |

**The simulation's numerical verdicts (🧮):**

- **@15 Hz (bone PEMF band)**: I ≈ 80 mA, **B ≈ 335 µT**, induced E ≈ 2.5 mV/m — **6% of the public ICNIRP limit**. Fully green zone.
- **@1 kHz**: I ≈ 12.3 mA, B ≈ 51 µT, E ≈ 8.1 mV/m — **2.0% of the limit**. *(v0.2 figures: v0.1 added |Z| and R_out instead of the complex sum — a 12% underestimate, corrected and verified by the time domain.)*
- **Across the whole 10 Hz – 100 kHz sweep: the 5 V bench stays under 30% of ICNIRP — safe by construction.** And ΔT < 10⁻⁹ K: strictly nothing in thermal terms.
- *(The "3× gap" announced in v0.1 with the 0.4 mm wire was **swept away by the v0.2a mapping**: it was an artifact of the too-thin wire — see below.)*

---

## 🗺️ v0.2 — the three in-silico validation projects (figs F, G, H)

### (a) Design mapping — `syntrium/design.py` + `fig_F_designs.png`

**705 configurations scanned** (50–1200 turns × 5 wire diameters × 5/12/24 V), criteria: within the 0.5–2 mT band · ICNIRP-compliant (15 **and** 75 Hz) · cold coil (P ≤ 4 W).

> 💥 **Major result: the 5 V REACHES the clinical band.** 275 turns in 0.8 mm wire →
> **B = 0.50 mT @15 Hz, I = 87 mA, ICNIRP ratio 13%, P = 0.01 W.** The "3× gap"
> of v0.1 was the artifact of the 0.4 mm wire (too resistant: 21 Ω). **308 designs are
> feasible, including 105 at 5 V** — the sovereign bench (USB power bank) is THE main track.
> *The chief will wind the coil in 0.8 mm, not 0.4: the simulator says so.*

### (b) Virtual oscilloscope — `syntrium/onde.py` + `fig_G_oscillo.png`

The complete chain resolved **in the time domain**: DDS sine → 10-bit DAC quantization (step 4.4 mV) → RC filter (FFT) → coil → B(t), E(t).

- **Time/frequency coherence verified to < 0.1%**: B(t) peak @15 Hz = 335.1 µT ↔ 335 µT in frequency domain.
- **Theoretical phase confirmed**: −5.6° @15 Hz (nearly transparent) · **−94.8° @1 kHz** (the filter dominates).
- **THD (Hann window)**: 0.001% @15 Hz · 0.01% → 0.002% @1 kHz (the filter cleans 5× the harmonics, which themselves exceed fc).
- **Channel #4 of the figure is the real lesson**: at 1 kHz, the 159 Hz filter **crushes the field by 6.5×** and shifts its phase — it is the FILTER that sculpts the emitted spectrum, not the coil.

### (c) Simulated agar phantom — `syntrium/gel.py` + `fig_H_fantome.png` + `resultats/fantome.json`

The gel disc of phase 3, modeled **before** being cast: E(r) = π·f·r·B (zero at center, max at edge), power deposit p = σE², **heat equation solved in FTCS** (161 points, Robin convective boundary, 10 min session, worst case 75 Hz).

| Design | Max phantom ΔT over 600 s |
|---|---|
| 5 V bench (0.335 mT) | **2.5 × 10⁻⁹ K** |
| low clinical (0.5 mT) | 5.6 × 10⁻⁹ K |
| mid clinical (1 mT) | 2.3 × 10⁻⁸ K |
| high clinical (2 mT) | **9.0 × 10⁻⁸ K** |

> Even at the high clinical design, **the phantom does not move by one ten-millionth of a degree**.
> SYNTRIUM's effect, if any, will be informational or will not be — the simulator repeats it
> at every layer of the stack.

**In one sentence: the in-silico validation is COMPLETE — the optimal design is known
(275 turns, 0.8 mm, 5 V), the waveform is clean and predictable, and the phantom is
thermally invisible. The hardware phase now has its digital twin.**

---

## 🎯 The vision (in one sentence)

**An external low-voltage device that "speaks" the body's electrical language** —
pulsed fields calibrated in the windows where the literature shows real biological effects —
without ever invading the cells: no implant, no nanoparticle, no molecule.

The inspiration: the body is already electric. Wounds create **endogenous electric fields**
that guide cell migration (electrotaxis); pulsed electromagnetic field stimulation
(PEMF) has been **approved since 1979 in the USA** to consolidate recalcitrant fractures;
bioelectricity is an active research field. SYNTRIUM targets the RATISS question:

> **What is the real intensity / frequency / duration windowing — measured, not mythified —
> and can we produce it with affordable, sovereign and safe hardware?**

## ⚖️ The three RATISS corrections (what the "pitch" version said — and what we do instead)

The lab's method forbids building on unsourced claims. Three foundational corrections:

| The pitch said… | The reality (measured) | What RATISS does |
|---|---|---|
| Simulate **7 billion atoms** with NumPy | Impossible: only the world's supercomputers handle ~10⁹ atoms. A laptop: ~10⁵–10⁶ atoms in MD (OpenMM — see `ratiss-bio`) | Honest MD at the real scale of our means + **tagged** toy model 🧮, never presented as tissue |
| Frequencies "emitted by white blood cells" | This is not an established measurement. What IS established: endogenous wound fields (electrotaxis), parameters of approved PEMF devices, ICNIRP limits | **Real database**: PubMed (242 PEMF×wound-healing papers queried on day 1), openFDA (510(k) devices), ICNIRP 2010 (numerical limits) |
| A simulated "virtual cancer map" | Carcinogenesis cannot be simulated in a NumPy model — that would be a pretension, forbidden in the lab | The **real safety envelope**: internal induced field < ICNIRP basic restrictions + thermal (SAR/ΔT) computed by our own tools |

In other words: **the SYNTRIUM windowing will be extracted from the real literature and approvals,
then verified by our calculators and our bench — not guessed.**

## 🧪 The three layers of the program (honest version)

| Layer | Content | v0 status |
|---|---|---|
| 📚 **Real databases** | PubMed (PEMF × wound healing, endogenous fields), openFDA 510(k), numerical ICNIRP 2010 limits | ✅ queried on day 1, snapshots in `DONNEES/` |
| 🧮 **Computed physics** | Induced field (Faraday), membrane potential (Schwan), thermal (SAR, ΔT) — compared to ICNIRP limits | ✅ `syntrium/physique.py` + tests |
| 📡 **Real bench** | Signal generator + coil + magnetometer + agar phantom — built around **Arduino** (the workshop in progress!) | 🔜 `BOM-BANC.md` |

## 📐 What the calculators already show (first honest verdict)

With `syntrium/physique.py` (standard formulas, tested):

- **Typical bone PEMF (15 Hz, 1 mT, 5 cm radius)** → internal induced field ≈ **2.4 mV/m**: far
  below the ICNIRP limits (10–800 mV/m depending on frequency/case). The historical PEMF window is
  **weak and cautious** — that is precisely why it has 45 years of use.
- **kHz carrier (4.6 kHz, 1 mT)** → ≈ **0.72 V/m**: it is the **carrier**, not the repetition,
  that creates the induced field. The real windowing is played there.
- **Thermal**: at these levels, ΔT < 0.001 °C — **no heating**. SYNTRIUM's mechanism,
  if it exists, is **informational**, not thermal. This is a working hypothesis, not a result.

## 🚦 The phases (criteria frozen in the protocol)

0. **Real databases** — sealed PubMed/openFDA/ICNIRP snapshots. *Done — day 1.*
1. **Calculators** — standard formulas, green tests, numerical examples. *Done — day 1.*
2. **Emission bench** — Arduino + AD9833 + coil; independent measurement by magnetometer; the
   **control**: the measured field must match the computed field within ±20%.
3. **Agar phantom** — measurements in a conductive gel (bench recipe), real E/T mapping.
4. **Window extraction** — systematic literature review (parameters of published positive AND
   negative studies) → map of **documented** windows, with their evidence.
5. **And then?** — cellular validation requires a **partner BSL laboratory** (see the RATISS
   quest). No experiment on humans, ever, at any stage of this repository.

## 🛑 Safety and honesty rules (non-negotiable)

1. **Never on a human being.** The bench tests gel phantoms, not people.
2. **Low voltage only** (≤ 24 V, milliamperes). Nothing resembling TMS/high-energy capacitive systems.
3. **No cell culture at home** — that is BSL work, it waits for an institution.
4. **No care promise.** SYNTRIUM v0 is a **measurement and documentation instrument**.
   *Prove, not pretend.*
5. 🧮 computation · 📡 hardware bench — separate tags, never mixed.

## 🗂️ Structure

```
RATISS-SYNTRIUM/
├── README.md                ← you are here
├── PROTOCOLE.md             ← criteria, controls, windows
├── BOM-BANC.md              ← the real hardware (Arduino, AD9833, sensors, gel)
├── DONNEES/
│   └── bases_externes.json  ← real snapshots: PubMed, openFDA, ICNIRP (dated, URL)
├── syntrium/
│   ├── physique.py          ← Faraday, Schwan, SAR + ICNIRP limits
│   ├── circuit.py           ← the simulated emitter circuit (DDS→RC→MOSFET→coil)
│   └── figures.py           ← the 5 figures (300 dpi, from the computation)
├── tests/
│   ├── test_physique.py
│   └── test_circuit.py
├── outils/
│   └── manifeste.py         ← the lab's SHA-256 seal
├── figures/                 ← fig_A..fig_E (the simulation outputs)
├── MANIFESTE.json
└── LICENSE                  ← MIT
```

## ▶️ Replay

```bash
git clone https://github.com/jonathansearch/RATISS-SYNTRIUM.git
cd RATISS-SYNTRIUM
python3 syntrium/physique.py          # the numerical examples
python3 -m pytest tests/ -q           # the tests
python3 outils/manifeste.py --verifier  # the seal
```

Dependencies: Python 3.10+, nothing else (numpy optional).

---

*RATISS Labs · Jonathan Evina · Yaoundé · 29/09/2026 · MIT*
*"The most powerful technology is not the one that forces nature — but to listen to it,
you first need sensors."* ⚡
