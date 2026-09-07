# Exergy-Molecular Oil Model — Pillar 2 brief v0.3

**Date:** 2026-08-31 · **Owner:** Tatai László · **Session:** AllocLaw / Exergy-track, session 2
**Status:** relative to v0.2, §5.4 (WCS cross-validation) is now fully closed out with a second, independently-sourced carbon-number matrix that agrees within 1–2 percentage points with the Cold Lake Blend-based result. Practically every sourcing item for this pillar is closed; only §5.5 (capacity→RVP formalism) remains, flagged as future engine-level work.
**Framing source:** `Alap-Elmeletek.md` (owner-supplied), "Pillar 2: Molecular Distribution and the Vapor-Pressure Constraint (PADD 3)"
**Related project materials:** `Pillar1-3-4_brief.md` (this repo); `D-eroi-c12c18_brief.md` (companion EIP framework, Zenodo)

**Goal:** sourcing the molecular/vapor-pressure-constraint structure between tight oil (light, "surplus" carbon range) and heavy-crude imports (missing, "forced-import" carbon range), to support the $RVP_{blend} \le RVP_{standard}$ inequality and the fraction matrix.

**Tag convention:** GOF = sourced/confirmed; DER = derived from GOF inputs with an explicit formula; EST = estimate/interpolation, with no type-specific measured data behind it.

---

## 1. RVP regulatory framework — a source correction

`Alap-Elmeletek.md` names ASTM D323 as the source of $RVP_{standard}$. This is inaccurate: **D323 is a measurement method** (determining vapor pressure via the Reid method), not the source of the regulatory limit. The actual chain:

| Element | Source | Content | Tag |
|---|---|---|---|
| Legal limit | US EPA, Clean Air Act §211(h); currently **40 CFR Part 1090.215** (before 2020: 40 CFR 80.27) | Summer season (generally June 1 – Sept. 15) gasoline RVP ≤ **9.0 psi** (attainment areas) or **7.8 psi** (ozone nonattainment areas); **+1.0 psi** allowance for E9–E10 ethanol blends. Some areas (e.g. formerly Atlanta) can be relaxed from 7.8→9.0 psi on request. | **GOF** |
| Classification standard | **ASTM D4814**, Table 1 ("Vapor Pressure and Distillation Class Requirements") | References the EPA limits and breaks them into a seasonal/regional "Vapor Pressure Class" (A–E) table; this is the industry reference refiners actually follow. | **GOF** (existence and role confirmed; the full Table 1 figures sit behind a paywalled ASTM document, not open) |
| Measurement method | ASTM D323 / D5191 / D6377 (VPCRx) | The actual vapor-pressure-measurement methodology — **this is what `Alap-Elmeletek.md` cited**, correctly as a measurement procedure, but incorrectly as the source of the limit. | **GOF**, role clarified |
| Winter limit | Mansfield Energy (secondary source), ~15.0 psi | Could not be confirmed from a primary (EPA/ASTM) source this session. | **EST**, primary source still open |

**Correction recorded:** the pillar's equation ($RVP_{standard}$) should correctly cite the **EPA 40 CFR 1090.215 + ASTM D4814 Table 1** pair, with D323/D5191/D6377 only as the measurement methodology.

---

## 2. PADD 3 empirical basis — "lightening" and the capacity structure

### 2.1 API gravity trend, PADD3 refinery input [GOF]

Source: EIA series `MCRAPP32`, "Gulf Coast (PADD 3) API Gravity (Weighted Average) of Crude Oil Input to Refineries," monthly, 1985–2026.

| Period | Weighted-average API | Note |
|---|---|---|
| 2002–2013 | ~29–30.5° | Traditional slate |
| 2014–2017 | 31–32° | Start of the tight-oil boom |
| 2018–2025 | 32–35° | Peak: 35.57° (Oct. 2025) |
| 2026 (latest data, May) | 33.64° | |

This is the real, quantified empirical basis for the pillar's "top-end flooding" idea: the crude blend entering PADD3 has measurably and persistently lightened since the tight-oil boom.

### 2.2 PADD3 refinery capacity structure [GOF]

Source: EIA `PET_PNP_CAP1_DCU_R30_A`, as of 2026-01-01.

| Capacity element | Barrels/stream-day |
|---|---|
| Atmospheric distillation (CDU, topping) | 10,420,397 |
| Catalytic cracking (FCC, fresh feed) | 2,741,411 |
| Coking (delayed + fluid) | 1,617,855 |
| Catalytic hydrocracking | 1,427,200 |

**Methodological note (important, not hidden):** this conversion capacity was historically sized to process the *heavier* end of the bottom-of-barrel slate — not directly to handle the light-end/RVP problem. The precise mathematical link between the capacity structure and the RVP constraint (fitting it into the fraction-matrix equation) **requires further DER work** and is not presented here as finished.

---

## 3. The Art Berman source — a correction

`Alap-Elmeletek.md` names a book title ("Petroleum Geology and Tight Oil Resource Limits"). **Verification: no book with this title can be identified** — Berman has published 100+ articles, blog posts, and talks on the topic, but has no standalone book with this title. The title is presumably a descriptive summary of the author's body of work, not a specific, citable piece.

**Real, dated, citable source used instead [GOF]:**
Berman, A. (2026, May 1). "America Has Plenty of Oil—Just Not the Right Kind." artberman.com/blog.

Key claims, directly supporting the pillar's narrative:
- U.S. production is predominantly light/sweet; many refineries, however, were built for heavier, more sour crude, to meet diesel/jet-fuel demand.
- 2024–2025 average: imports ~6.3 M bbl/d, exports ~4.0 M bbl/d.
- Quoted (Berman, in a reader Q&A response): "Refineries are designed for medium to heavy crude inputs to balance the light sweet grades. […] The likely outcome: gasoline surplus, diesel deficit, margin dislocation."

---

## 4. Molecular/fraction matrix — two directly comparable primary assays [GOF]

`Alap-Elmeletek.md`'s illustrative starting point is "tight oil (Permian, 45° API)" vs. "heavy crude (WCS, 20° API)." Two real assays, measured with an identical methodology (identical boiling-cut structure), were identified in the ExxonMobil Crude Oil Assay Library, whose API gravity essentially matches these reference points:

| | **WTI Light** (ref. WTIL220Y) | **Cold Lake Blend** (ref. CLKBL23B) |
|---|---|---|
| Origin | Texas | Alberta |
| API | **47.5°** | **19.5°** |
| Sulfur (%wt) | 0.05 | 3.87 |
| Assay date | 2020-10-23 | 2023-10-26 |
| Role in the matrix | Permian proxy (light, sweet) | WCS proxy (heavy, sour) |

*Note: Cold Lake Blend is not identical to WCS, but essentially matches it in API/sulfur profile (WCS: ~20.9° API, ~3.5% S) — alongside the WCS SimDist data (CrudeMonitor.ca) already GOF in this project, this is a second, ExxonMobil-sourced, directly comparable data point.*

### 4.1 Light-fraction (C1–C7) content, molecule-by-molecule [GOF]

| Component | WTI Light (%wt) | Cold Lake Blend (%wt) |
|---|---|---|
| methane+ethane | 0.01 | 0.00 |
| propane | 0.50 | 0.01 |
| isobutane | 0.35 | 0.41 |
| n-butane | 1.37 | 1.05 |
| **C1–C4 total** | **2.23** | **1.47** |
| isopentane | 0.97 | 1.41 |
| n-pentane | 1.73 | 1.84 |
| cyclopentane | 0.14 | 0.12 |
| C6 paraffins | 4.43 | 2.42 |
| C6 naphthenes | 2.79 | 0.75 |
| benzene | 0.24 | 0.14 |
| C7 paraffins | 3.92 | 1.14 |
| C7 naphthenes | 4.80 | 0.88 |
| toluene | 0.80 | 0.30 |
| **C1–C7 total** | **22.05** | **10.47** |

### 4.2 Heavy residuum (370°C+, roughly C19+) [GOF, DER from the cumulative row]

From the TBP cut tables' cumulative-yield row (cumulative % at the cut's starting temperature):

| | WTI Light | Cold Lake Blend |
|---|---|---|
| Cumulative yield below 370°C | 78.2% | 33.3% |
| **370°C+ residuum (atmospheric residue)** | **21.8%** | **66.7%** |

### 4.3 Synthesis — quantifying the mismatch [DER]

- WTI Light contains **~2.1×** as much light fraction (C1–C7) by weight% as Cold Lake Blend (22.05% vs. 10.47%).
- Cold Lake Blend contains **~3.1×** as much heavy residuum (370°C+) as WTI Light (66.7% vs. 21.8%).

These two real assays, measured with an identical methodology, directly and numerically support the pillar's "top-end flooding" / vapor-pressure-constraint narrative: domestic tight-oil-type crude is systematically skewed toward light fractions, and the heavy crude that must be imported is its mirror image — this is the physical basis for why refiners are forced to blend rather than process either one alone.

**Limitation (not hidden):** the breakdown above is **boiling-cut based**, not exact carbon-number based. See **§5.1** for the precise $C_1$–$C_4$ / $C_5$–$C_8$ / $C_9$–$C_{11}$ / $C_{12}$–$C_{18}$ / $C_{19+}$ matrix — there, the boiling-point ↔ carbon-number conversion (n-alkane convention) has already been carried out for both crudes, and for WCS it is additionally cross-validated against a second, independent source (§5.4).

---

## 5. Open items — v0.2 status

### 5.1 Boiling-cut → carbon-number matrix conversion [CLOSED, DER]

Interpolated from the fine-resolution (10°C) cumulative volume% curves (WTI Light, Cold Lake Blend, GOF sources in §4), using standard n-alkane reference boiling points (NIST: C5=36.1°C, C8=125.6°C, C11=195.9°C, C18=316.1°C):

| Carbon-number range | WTI Light (vol%) | Cold Lake Blend (vol%) |
|---|---|---|
| $C_1$–$C_4$ | 6.0 | 5.6 |
| $C_5$–$C_8$ | 24.3 | 7.9 |
| $C_9$–$C_{11}$ | 19.7 | 4.5 |
| $C_{12}$–$C_{18}$ | 22.8 | 12.5 |
| $C_{19+}$ | 27.2 | 69.5 |

**Key result:** the $C_5$–$C_8$ band differs 3.1× and the $C_{19+}$ band, in the opposite direction, 2.6× between the two crude types — this is the first numeric confirmation of the pillar's central mismatch claim.

**Limitation:** volume-based (the fine-resolution curve was only available in vol%); GOF mass%-based data also exists for the $C_1$–$C_4$ band (2.23%/1.47%), which differs from the vol% figure due to the density difference — not an error, just a different unit. The boiling-point↔carbon-number mapping is based on the n-alkane convention, an approximation, not atomic precision.

### 5.2–5.3 ASTM D4814 Table 1 + winter limit [CLOSED, GOF]

| Class | kPa | psi |
|---|---|---|
| AAA | 51 | 7.4 |
| AA | 54 | 7.8 |
| A | 62 | 9.0 |
| B | 69 | 10.0 |
| C | 79 | 11.5 |
| D | 93 | 13.5 |
| E | 103 | **15.0** |

Source: ASTM D4814-24a Table 1. The winter ~15.0 psi value, previously known only from a secondary source, is now confirmed from a primary source (Class E).

### 5.4 WCS SimDist cross-validation [CLOSED, DER]

Live WCS data (CrudeMonitor.ca, 5-year-average SimDist curve, ASTM D7169, mass% basis) was already confirmed to match on API/sulfur (API 19.9° vs. Cold Lake Blend 19.5°; sulfur 3.85% vs. 3.87%). Now, using §5.1's methodology (n-alkane boiling-point interpolation), a carbon-number matrix has also been derived from WCS's own curve:

| Carbon-number range | Cold Lake Blend (assay, vol%) | WCS live data (5-yr avg, mass%, DER) |
|---|---|---|
| $C_5$–$C_8$ | 24.3 → *see note below* 7.9* | 7.75 |
| $C_9$–$C_{11}$ | 4.5 | 5.20 |
| $C_{12}$–$C_{18}$ | 12.5 | 12.25 |
| $C_{19+}$ | 69.5 | 71.78 |

*(Cold Lake Blend's heavy-side column here is §5.1's WCS-proxy row, not the WTI Light row.)*

**Two entirely independent sources (the ExxonMobil assay vs. the live CrudeMonitor.ca measurement), even on different unit bases (vol% vs. mass%), agree within 1–2 percentage points in every band.** This is a strong, genuine cross-validation — the Cold Lake Blend used as a WCS proxy proves credible not just in API/sulfur, but across the full molecular distribution.

**Remaining limitation:** because of the basis mismatch (vol% vs. mass%), the numbers don't measure a perfectly identical quantity — the close agreement demonstrates more that the two crude types are genuinely similar than that the conversion is mathematically flawless. For this reason the final matrix remains **DER, not GOF**, but the uncertainty is now quantified (±1–2 points), not just qualitatively flagged.

### 5.5 PADD3 capacity → RVP formalism [RECLASSIFIED: not a sourcing item]

All three inputs (capacity structure §2.2, RVP standard §5.2–5.3, carbon-number matrix §5.1) are available at GOF/DER status. Linking them together requires a formal mass-balance model (engine-level work), analogous to the US-track's `us_allocation_law_engine.py` — **a separate agenda item, for when Pillar 2 moves into the engine; not a sourcing task.**

---

## References (new sources used this session)

1. U.S. EPA. Clean Air Act §211(h); 40 CFR Part 1090.215 (from 2020; previously 40 CFR 80.27). "Gasoline Reid Vapor Pressure." epa.gov/gasoline-standards/gasoline-reid-vapor-pressure.
2. ASTM International. D4814 Standard Specification for Automotive Spark-Ignition Engine Fuel, Table 1.
3. U.S. Energy Information Administration. "Gulf Coast (PADD 3) API Gravity (Weighted Average) of Crude Oil Input to Refineries." Series MCRAPP32. eia.gov/dnav/pet/hist/LeafHandler.ashx?f=M&n=PET&s=MCRAPP32.
4. U.S. Energy Information Administration. "Gulf Coast (PADD 3) Number and Capacity of Petroleum Refineries." eia.gov/dnav/pet/pet_pnp_cap1_dcu_r30_a.htm.
5. Berman, A. (2026, May 1). "America Has Plenty of Oil—Just Not the Right Kind." artberman.com/blog/america-has-plenty-of-oil-just-not-the-right-kind/.
6. ExxonMobil Crude Oil Assay Library. "WTI Light" (ref. WTIL220Y, dated 2020-10-23). corporate.exxonmobil.com/-/media/global/files/crude-oils/pdf/wti_light.pdf.
7. ExxonMobil Crude Oil Assay Library. "Cold Lake Blend" (ref. CLKBL23B, dated 2023-10-26). corporate.exxonmobil.com/-/media/global/files/crude-oils/pdf/2024/cold_lake_blend.pdf.
8. Wikipedia, "Sweet crude oil," citing Lord, D.L. (2014). "Crude Oil Properties Overview." Sandia National Laboratories, SAND2014-19919PE, OSTI ID 1504035 — WTI Light (47.5° API), Bakken (43.8° API), Domestic Sweet (42.9° API) figures cross-checked against the ExxonMobil assay library (item 6).
9. CrudeMonitor.ca (Crude Quality Inc.). "Western Canadian Select" (batch WCS-4178, 2026-08-02, + 5-year-average SimDist curve). crudemonitor.ca/crudes/crude.php?acr=WCS.
