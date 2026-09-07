# Exergy-Molecular Oil Model — Pillar 1 and 3 addendum [GOF update]

**Date:** 2026-08-31 · **Owner:** Tatai László · **Session:** AllocLaw / Exergy-track, session 2
**Related document:** `Pillar1-3-4_brief.md` §1.2–1.3 (elemental composition) and §2.2 footnote (citation completion)
**Precursor:** `AllocLaw_Session_Handoff_004.md` §3, items 1 and 2

**Goal:** replace/refine the Pillar 1 table's US domestic, dilbit, and SCO rows — so far EST, interpolated from a type-independent range — with real, type-specific measured data.

---

## 1. New GOF sources

| Type | Assay | Origin | H (%wt) | S (%wt) | N (ppm) | API |
|---|---|---|---|---|---|---|
| US domestic (anchor 1) | ExxonMobil "Domestic Sweet" (ref. DOMSW22Y, 2022-06-17) | Texas | **14.0** | 0.43 | 610 | 42.9 |
| US domestic (anchor 2) | ExxonMobil "WTI Light" (ref. WTIL220Y, 2020-10-23) | Texas | **14.4** | 0.05 | 106 | 47.5 |
| Dilbit | ExxonMobil "Cold Lake Blend" (ref. CLKBL23B, 2023-10-26) | Alberta | **12.1** | 3.87 | 3,062 | 19.5 |
| SCO | CrudeMonitor.ca "Synthetic Sweet Blend" (batch SYN-6351, 2026-07-10) | AB (Suncor/Syncrude/CNRL blend) | *not measured in this source* | **0.19** (5-yr avg 0.25) | — | 33.3 (5-yr avg 32.4) |

**Cross-validation (US domestic):** two independent, identically-methodology (ExxonMobil EMTEC) measured Texas-origin anchors' H% agree almost perfectly (14.0% vs. 14.4%) — a strong confirmation of the region's typical H content.

**SCO API/S confirmation:** the live CrudeMonitor.ca data (33.3°, 0.19–0.25% S) essentially matches Pillar 1 v0.1's original EST estimate (32.0°, 0.2% S) — this is a **retroactive GOF confirmation**, not a correction. **No type-specific measured H content for SCO was found this session either — it remains EST.**

---

## 2. Recomputed φ and η_ex (Szargut–Styrylska formula, per Pillar 1 §1.2's methodology, O%=0.3% EST triangulation unchanged)

$$\varphi = 1.0401 + 0.1728 \cdot (H/C) + 0.0432 \cdot (O/C) + 0.2169 \cdot (S/C) \cdot (1 - 2.0628 \cdot (H/C))$$

| Type | C (%wt, DER, with O=0.3% EST) | φ_crude (DER) | η_energy (GOF, Cai 2015 Table S11) | **η_ex (DER) — new** | η_ex — old (v0.1, EST-based) |
|---|---|---|---|---|---|
| US domestic (Domestic Sweet) | 85.2 | 1.0694 | 90.8% | **91.3%** | 91.0% |
| US domestic (WTI Light) | 85.2 | 1.0695 | 90.8% | **91.3%** | 91.0% |
| Dilbit (Cold Lake Blend) | 83.4 | 1.0724 | 87.8% | **88.0%** | 88.3% |
| SCO | — (H missing) | — | 92.2% | *unchanged, EST* | 92.5% |
| Bitumen | (unchanged, already GOF in v0.1) | 1.0702 | 86.0% | 86.4% (unchanged) | 86.4% |

**Interpretation:** the size of the refinement is small (±0.3 points), but it now rests on **a real US-domestic anchor measured two independent ways** (rather than a single type-independent range interpolation) — a genuine quality improvement from a GOF/EST-discipline standpoint, even though the numeric result barely moves.

---

## 3. Still open

- **SCO H content** (and the C% derived from it) — still no type-specific measured source. API/S are now GOF; H/N are still EST/missing.
- **O content for every type** — still the 0.3% EST-triangulated value set in Pillar 1 v0.1, not type-specifically measured for any of them. (Per Pillar 1's own note, its effect on the final result is <0.05 points — low priority.)
- **DOE SPR Crude Oil Assay Manual Appendix B** (the original target of the Session 4 handoff) — this session was not closed out via that route; the ExxonMobil/CrudeMonitor.ca sources proved faster to access and at least as credible. The SPR route remains open if a third, independent cross-check is ever warranted.

---

## 4. Pillar 3 — two missing citations closed [GOF]

`Pillar1-3-4_brief.md` §2.2's footnote cited two sources that, at the time, had only a URL identifier / partial DOI. Both now have a complete citation, cross-validated from multiple independent sources:

1. **Yadav, P.S.; Gautam, R.; Le, T.T.; Khandelwal, N.; Le, A.T.; Hoang, A.T. (2024).** "A Comprehensive Analysis of Energy, Exergy, Performance, and Emissions of a Spark-Ignition Engine Running on Blends of Gasoline, Ethanol, and Isoamyl Alcohol." *Energy*, 307, 132548. DOI: 10.1016/j.energy.2024.132548. (Previously: only PII S0360544224023223.)
2. **Dahham, R.Y.; Wei, H.; Pan, J. (2022).** "Improving Thermal Efficiency of Internal Combustion Engines: Recent Progress and Remaining Challenges." *Energies*, 15(17), 6222. DOI: 10.3390/en15176222. Received: 2022-08-10, accepted: 2022-08-23, published: 2022-08-26. Author affiliation: State Key Laboratory of Engines, Tianjin University, China (first author also affiliated with the University of Babylon, Iraq).

---

## 5. Pillar 3 — the diesel cutoff ratio (r_c), Proniewicz engine [CONFIRMED NEGATIVE RESULT]

The full text of Proniewicz et al. (2023) (open access, Birmingham repository) was reviewed. **Table 2, engine specification:**

| Parameter | Value |
|---|---|
| Model | LIFAN |
| Type | CI, 4-stroke, single-cylinder, air-cooled |
| Bore × stroke | 86 × 70 mm |
| Displacement | 418 cm³ |
| Compression ratio | 16.5:1 |
| Intake valve open/close | 14° BTDC / 45° ABDC |
| Exhaust valve open/close | 50° BBDC / 16° ATDC |
| Injection start | 15.5° BTDC |
| Injection pressure | 200 bar |

**Confirmed negative result:** the paper reports the injection end, duration, or the diesel cutoff ratio (r_c) directly nowhere — not in Table 2, nor anywhere else in the text. This is not a prior oversight but a genuine absence in the source's actual content. **Pillar 3's EST tag (a typical textbook range, 1.5–3) therefore remains confirmed — the source itself does not allow further refinement; only supplementary data requested from the authors (e.g. injector specifications) could resolve it.**

---

## References (new sources used this session)

1. ExxonMobil Crude Oil Assay Library. "Domestic Sweet" (ref. DOMSW22Y, 2022-06-17). corporate.exxonmobil.com/-/media/global/files/crude-oils/pdf/2024/domestic_sweet.pdf.
2. ExxonMobil Crude Oil Assay Library. "WTI Light" (ref. WTIL220Y, 2020-10-23). corporate.exxonmobil.com/-/media/global/files/crude-oils/pdf/wti_light.pdf.
3. ExxonMobil Crude Oil Assay Library. "Cold Lake Blend" (ref. CLKBL23B, 2023-10-26). corporate.exxonmobil.com/-/media/global/files/crude-oils/pdf/2024/cold_lake_blend.pdf.
4. CrudeMonitor.ca (Crude Quality Inc.). "Synthetic Sweet Blend" (batch SYN-6351, 2026-07-10). crudemonitor.ca/crudes/crude.php?acr=SYN.
5. Yadav, P.S.; Gautam, R.; Le, T.T.; Khandelwal, N.; Le, A.T.; Hoang, A.T. (2024). "A Comprehensive Analysis of Energy, Exergy, Performance, and Emissions of a Spark-Ignition Engine Running on Blends of Gasoline, Ethanol, and Isoamyl Alcohol." *Energy*, 307, 132548. DOI: 10.1016/j.energy.2024.132548.
6. Dahham, R.Y.; Wei, H.; Pan, J. (2022). "Improving Thermal Efficiency of Internal Combustion Engines: Recent Progress and Remaining Challenges." *Energies*, 15(17), 6222. DOI: 10.3390/en15176222.
7. Proniewicz, M.; Petela, K.; Szlęk, A.; Przybyła, G.; Nadimi, E.; Ziółkowski, Ł.; Løvås, T.; Adamczyk, W. (2023). "Energy and Exergy Assessments of a Diesel-, Biodiesel-, and Ammonia-Fueled Compression Ignition Engine." *International Journal of Energy Research*, 2023, 9920670. Full text: pure-oai.bham.ac.uk (Birmingham repository, CC BY).
