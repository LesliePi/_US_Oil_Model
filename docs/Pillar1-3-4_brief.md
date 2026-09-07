# Exergy-Molecular Oil Model — Pillar 1, 3, 4 brief v0.1

**Date:** 2026-08-31 · **Owner:** Tatai László · **Session:** AllocLaw / Exergy-track, session 1
**Framing source:** `Alap-Elmeletek.md` (owner-supplied), the five-pillar "Exergy-Molecular Oil Model"
**Related project materials:** `no-single-oil-market_C12-C18-EROI_methodology-note.md`, `EIP_C12C18_EROI_Framework_v0_3.md` (companion EIP framework, Zenodo)

**Goal:** apply the physical (second-law) correction to the crude→diesel conversion, in place of the naive first-law (mass/heating-value) balance, and then feed that correction into the well-to-wheels EROI chain.

**Tag convention:** GOF = sourced/confirmed; DER = derived from GOF inputs with an explicit formula; EST = estimate/interpolation, with no type-specific measured data behind it.

---

## 1. Pillar 1 — Refinery exergy efficiency, the crude→diesel path

### 1.1 The definitional trap (a critical methodological finding)

The term "exergy efficiency" covers **two conceptually distinct** quantities in the literature:

- **(a) Retention type:** product exergy / input exergy. This is the quantity that matches the Allocation Law's η_j role (a multiplier showing how much resource survives a given step).
- **(b) Process-efficiency type** (second-law/availability efficiency): theoretical minimum required work / exergy actually consumed. This measures how wasteful distillation is *as a process* — it does **not** measure how much exergy survives in the product.

**Source, type (b), EXCLUDED from the model:** Dinçer, S. & Erkan, D. (1986). "Available energy analysis of a petroleum-refinery operation." *Applied Energy*, 22(2), 157–163. — a whole-refinery "availability efficiency" of 5.9% — this pertains to the process-efficiency type, not to the η_j role used in this model. **GOF, but not applicable here.**

**Source, type (a), EST (a global aggregate, not US-specific):** Michalakakis, C.; Fouillou, J.; Lupton, R.C.; Gonzalez Hernandez, A.; Cullen, J.M. (2021). "Calculating the chemical exergy of materials." *Journal of Industrial Ecology*, 25(2), 274–287. DOI: 10.1111/jiec.13120. — the global "refining" sector, 2013, 72% resource-efficient (retention type, explicitly distinguished in the source's own definition). **GOF source, EST applicability (global, not US, 2013 vintage).**

### 1.2 Our own (DER) calculation — crude→diesel chemical exergy retention

**Methodological chain:** crude/diesel elemental composition (C, H, O, S mass%) → Szargut–Styrylska correlation → φ (exergy/LHV ratio) → η_ex = η_energy,GOF × (φ_diesel/φ_crude).

**Formula (GOF, standard):** φ = 1.0401 + 0.1728·(H/C) + 0.0432·(O/C) + 0.2169·(S/C)·(1 − 2.0628·(H/C))
Source: Szargut, J.; Morris, D.R.; Steward, F.R. (1988). *Exergy Analysis of Thermal, Chemical and Metallurgical Processes.* Hemisphere Publishing. (Standard reference, confirmed in multiple independent papers' reference lists, e.g. Rivero et al. 2004.)

**Elemental composition — crude oil (non-bitumen), EST, six converging sources:**
- Britannica, "Crude oil" entry: C 82–87%, H 12–15%
- eng-tips.com forum (a table sourced from Speight/Gary-Handwerk-Kaiser, poster "RKCMurphy"): C 83.9–86.8%, H 11.0–14.0%, S 0.06–8.00%, N 0.02–1.70%, O 0.08–1.82%
- University teaching slide deck ("Physical and chemical properties of petroleum," SlideShare): C 82–87%, H 12–15%, S 0.1–6%, N 0.1–2%, O 0.1–5%
- US patent ("Crude oil desulfurization"): "average crude oil ~84% C, ~14% H"
- ScienceDirect Topics, "Petroleum Product": C/H mass ratio between 6–8
- Po, J. (1977). "The Composition of Petroleum." (a classic geochemical summary): H 10–15%, S 0–10%, N 0–1%, O 0–5%

→ interpolated by API gravity (lighter crude → higher H%, per the eng-tips note). **EST, from a type-independent range, NOT type-specifically measured.**

**Elemental composition — bitumen, GOF (dual/triple-sourced, type-specific):**
- ScienceDirect Topics, "Bitumen" chapter, SHRP-core bitumen elemental analysis (ref. [24]): C 80–88%, H 8–12%, H/C molar ratio ~1.5
- Athabasca bitumen patent (cross-check): H/C molar ratio 1.50→1.55 after heat treatment
- University slide deck, "asphalt" row: C 80–85%, H 9–11%

**Elemental composition — diesel, GOF, ACTUALLY MEASURED (not an estimate):**
Proniewicz, M.; Petela, K.; Szlęk, A.; Przybyła, G.; Nadimi, E.; Ziółkowski, Ł.; Løvås, T.; Adamczyk, W. (2023). "Energy and Exergy Assessments of a Diesel-, Biodiesel-, and Ammonia-Fueled Compression Ignition Engine." *International Journal of Energy Research*, 2023, Article ID 9920670. DOI: 10.1155/2023/9920670. Open access (CC BY), full text checked. Table 3, laboratory elemental analysis (Polish market diesel): **C 80.78%, H 15.56%, O 3.63%, N 0.03%.**

**Source data for crude API/sulfur content (already GOF in this project):** Cai, H. et al. (2015), SI Table S4 (`es5b01255_si_001.pdf`).
**Source data for diesel-specific energy efficiency (already GOF in this project):** Cai, H. et al. (2015), SI Table S11.

### 1.3 Results table — Pillar 1

| Crude | API | S% | C% (EST/GOF) | H% (EST/GOF) | φ_crude | φ_diesel (GOF) | η_energy (GOF) | **η_ex (DER)** |
|---|---|---|---|---|---|---|---|---|
| US domestic | 30.7 | 1.4 | 82.62 (EST) | 14.50 (EST) | 1.0729 | 1.0753 | 90.8% | **91.0%** |
| Canada bitumen | 8.0 | 4.8 | 84.00 (GOF) | 10.00 (GOF) | 1.0702 | 1.0753 | 86.0% | **86.4%** |
| Canada dilbit | 21.5 | 3.7 | 87.00 (EST) | 11.00 (EST) | 1.0689 | 1.0753 | 87.8% | **88.3%** |
| Canada SCO | 32.0 | 0.2 | 82.00 (EST) | 15.00 (EST) | 1.0722 | 1.0753 | 92.2% | **92.5%** |

**Physical picture:** with the real, measured diesel data (H=15.56%, considerably higher than a naive textbook estimate), the exergy-based efficiency comes out **slightly higher** (+0.2–0.6 points) than the energy-based one — because diesel is measurably more hydrogen-rich than the average of the crude blend it's made from.

**Known limitation / open item for the next session:** bitumen has its own measured anchor (GOF), but the other three types (US domestic, dilbit, SCO) are only interpolated from a type-independent range (EST) — this produces a visible non-monotonic artifact in the table (dilbit's C% is higher than bitumen's, even though dilbit is lighter). Obtaining type-specific elemental analysis (ASTM D5291) for these types is the next refinement step.

**Note on oxygen content:** crude oil's O% was not measured type-specifically; the midpoint of the triangulated range (0.3%) was used instead — because the Szargut formula's O-coefficient is small (0.0432), the effect on the final result is <0.05 points, negligible.

---

## 2. Pillar 3 — Motive exergy extraction, theoretical vs. real

### 2.1 Theoretical cycle formulas (GOF, standard textbook thermodynamics)

Otto: η = 1 − 1/ε^(κ−1)
Diesel: η = 1 − (1/ε^(κ−1))·[(r_c^κ − 1)/(κ(r_c−1))]

### 2.2 Results table — fitted to real, measured compression ratios

| | **Otto (gasoline, C5–C8), ε=9** | **Diesel (diesel fuel, C12–C30), ε=16.5** |
|---|---|---|
| Theoretical max (κ=1.40) | 58.5% | 57.5–64.4% (r_c=3–1.5, EST) |
| Theoretical max (κ=1.35) | 53.7% | 52.7–59.5% (r_c=3–1.5, EST) |
| Real, measured (fitted experiment) | energy 31.0% / exergy 28.9% | energy 33.6% / exergy 31.9% |
| Real, literature peak (commercial) | 30–36% | 42–43% |

**Sources:**
- Compression ratio ε=9 and the real SI measurement: ScienceDirect (2024), "A comprehensive analysis of energy, exergy, performance, and emissions of a spark-ignition engine running on blends of gasoline, ethanol, and isoamyl alcohol." *(full author list/volume number not yet verified — DOI/exact citation to be completed in a future session; currently only a URL identifier is available: S0360544224023223)*
- Compression ratio ε=16.5 and the real CI measurement: Proniewicz et al. (2023), see above, Table 2 (engine specification).
- Commercial peak range (SI 30–36%, CI 42–43%): a peer-reviewed review, MDPI *Energies* 15(17):6222 (2022), "Improving Thermal Efficiency of Internal Combustion Engines" *(author list not yet verified — to be completed)*.

**Note on r_c (diesel cutoff ratio):** not reported in the Proniewicz paper — a typical textbook range (1.5–3) was used, tagged EST.

---

## 3. Pillar 4 — EROI_soc (well-to-wheels, to useful work)

### 3.1 Starting point — EROI_pump (already GOF in this project)

Source: `no-single-oil-market_C12-C18-EROI_methodology-note.md`, the Hall, Lambert & Balogh (2014) additive "EROI at point of use" construction, the Elgowainy et al. (2014) refinery regression, the JEC WTT v5 transport chain. **Energy (LHV) basis, every term in MJ/MJ.**

### 3.2 A methodological error and its fix (important to record)

The first attempt multiplied the energy-based EROI_pump by an exergy-based engine efficiency (31.88%) — **a unit-basis mismatch**. Fix: the engine term also needs to be an energy (thermal) efficiency, to stay consistent with EROI_pump's own basis.

**Important labeling note:** the multiplication EROI_soc = EROI_pump × η_energy,engine does **not** appear in either the Hall-Lambert-Balogh or the Hall-Klitgaard sources — it is this project's own DER extension of the Pillar 4 idea (`Alap-Elmeletek.md`), not a cited literature convention. The EROI literature typically stops, deliberately, at the pump.

### 3.3 Results table — Pillar 4 (final, consistent on an energy basis)

| Chain | EROI_pump (GOF) | **EROI_soc — measured lab engine (GOF)** | **EROI_soc — commercial peak (GOF)** |
|---|---|---|---|
| US, domestic conventional | 5.40 | **1.81** | **2.27–2.32** |
| EU, typical blend | 3.80 | **1.28** | **1.60–1.63** |
| Canada→US, dilbit | 2.85 | **0.96** | **1.20–1.23** |
| Canada→US, SCO | 2.01 | **0.67** | **0.84–0.86** |

**Headline, robust finding:** the Canada-SCO chain **falls below 1.0 even with a peak commercial engine** (0.84–0.86); the dilbit chain does too, with a lab-test engine (0.96). This survived the basis correction, so it is not a calculation artifact.

**Open, not-yet-started thread:** a fully exergy-basis EROI_soc variant (Pillar 1's exergy-corrected η_ex,refining × an exergy-based η_ex,engine × a wellhead EROI converted to an exergy basis) — this would also require converting wellhead EROI to an exergy basis, which is separate work.

---

## References (new sources used this session)

1. Dinçer, S. & Erkan, D. (1986). Available energy analysis of a petroleum-refinery operation. *Applied Energy*, 22(2), 157–163.
2. Michalakakis, C.; Fouillou, J.; Lupton, R.C.; Gonzalez Hernandez, A.; Cullen, J.M. (2021). Calculating the chemical exergy of materials. *Journal of Industrial Ecology*, 25(2), 274–287. DOI: 10.1111/jiec.13120.
3. Rivero, R.; Rendón, C.; Gallegos, S. (2004). Exergy and exergoeconomics analysis of a crude oil combined distillation unit. *Energy*, 29, 1909–1927.
4. Valero, A. & Valero, A. (2010). Physical geonomics: combining the exergy and Hubbert peak analysis for predicting mineral resources depletion. *Resources, Conservation & Recycling*, 54(12), 1074–1083.
5. Szargut, J.; Morris, D.R.; Steward, F.R. (1988). *Exergy Analysis of Thermal, Chemical and Metallurgical Processes.* Hemisphere Publishing.
6. Proniewicz, M. et al. (2023). Energy and Exergy Assessments of a Diesel-, Biodiesel-, and Ammonia-Fueled Compression Ignition Engine. *International Journal of Energy Research*, Article ID 9920670. DOI: 10.1155/2023/9920670.
7. ScienceDirect Topics, "Bitumen" (overview chapter, SHRP data, ref. [24]).
8. Britannica, "Crude oil" entry.
9. Po, J. (1977). The Composition of Petroleum.
10. ScienceDirect (2024). Spark-ignition engine gasoline-ethanol-isoamyl alcohol exergy study. *(citation to be completed)*
11. MDPI *Energies* 15(17):6222 (2022). Improving Thermal Efficiency of Internal Combustion Engines. *(author list to be completed)*
12. Cai, H. et al. (2015). Well-to-Wheels GHG Emissions of Canadian Oil Sands Products. *Environ. Sci. Technol.* 49(13), 8219–8227 + SI. (already GOF in this project, Tables S4/S11 reused)
