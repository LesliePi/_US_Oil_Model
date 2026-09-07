# Exergy-Molecular Oil Model — Pillar 1/2 addendum: SPR Crude Oil Assay Manual [GOF update]

**Date:** 2026-09-01 · **Owner:** Tatai László · **Session:** AllocLaw / Exergy-track, session 3
**Related document:** `AllocLaw_Session_Handoff_005.md` §0, item 3
**Precursor:** the owner explicitly requested, in session 2, direct verification of the DOE SPR Crude Oil Assay Manual (5th edition, 2024) and Appendix B — session 2 closed with a negative result (the search only returned infrastructure/RFP content).

**Goal:** close out session 2's highest-priority open sourcing item.

---

## 1. Resolving the negative result [GOF]

The end-of-session-2 assumption (a search-engine query for the pattern `spr.doe.gov/reports/Assays/[year]/[code]_Assays.html`) was the wrong strategy. The correct route — as the handoff itself suggested — is direct navigation from `spr.doe.gov`: the main navigation bar on `www.spr.doe.gov/gas/default.htm` includes a **"SPR Crude Oil Comprehensive Analysis"** menu item directly, which links to `www.spr.doe.gov/reports/Crude_Oil_Assays.html`. This page contains direct links to the Sweet/Sour assay files for all four SPR sites (Bayou Choctaw, West Hackberry, Big Hill, Bryan Mound), as well as the Crude Oil Assay Manual PDF itself.

## 2. Contents of the Manual [GOF]

**Strategic Petroleum Reserve Crude Oil Assay Manual, 5th Edition, August 1, 2024** (supersedes the 4th edition, March 2017). Read in full successfully.

### 2.1 Table I — SPR Crude Oil Specifications (SPRO June 2023)

The official U.S. government yield specification (Vol%), across four distillation cuts, on a °C basis (not the n-alkane convention — differs from the project's current C1–C4/…/C19+ matrix):

| Fraction | Sour (Vol%) | Sweet (Vol%) |
|---|---|---|
| Naphtha [28–191°C] | 24–30 | 21–42 |
| Distillate [191–327°C] | 17–31 | 19–45 |
| Gas Oil [327–566°C] | 26–38 | 20–42 |
| Residuum [>566°C] | 10–19 | 14 max |

Other specification limits: API max. 30 (Sour) / 45 (Sweet), sulfur max. 1.99% (Sour) / 0.50% (Sweet), VPCR4 max. 9.0 psia for both, TAN max. 1.00 mg KOH/g.

### 2.2 Table III — Comprehensive Assay Grid

A full test matrix by fraction (Whole Crude, C2–C4 Gas, then 9 cut bands from 175°F to 1050°F+): API/density (D5002), sulfur (D4294), H/C mass% (D5291), PIAN (modified D5134), metals (D5708), nitrogen (D5762), viscosity, asphaltene, wax, etc. — this test grid matches exactly what appears in the actually-downloaded assay files.

### 2.3 Appendix A — the eight SPR streams' actual composition (June 2024)

Real blend composition by source crude, in Vol%. Example: **Bryan Mound Sweet** = Forties 34% + Ninian 15% + (Brent+Es Sider) 12.5% + **Domestic Sweet (DSW) 6%** + (Bonny Light/Forcados/Sirtica) 4% + (Kole/Saharan) 2% + other 1% each.

### 2.4 Appendix B

Just a placeholder ("*Screenshot of Assay landing page*") — the actual data lives in separate Excel files (see item 3), not in the PDF. This explains session 2's negative result.

## 3. Result of processing the eight assay files [GOF]

The owner uploaded all 8 files (without the PIANOs). Read in full (openpyxl; the `xlrd` engine for the legacy `.xls` file).

### 3.1 Whole-crude summary table

| Stream | API | S (mass%) | N (mass%) | RelDens 60/60°F | MCR (mass%) |
|---|---|---|---|---|---|
| Bayou Choctaw Sweet | 39.4 | 0.427 | 0.097 | 0.828 | 2.17 |
| Bayou Choctaw Sour | 30.4 | 1.745 | 0.141 | 0.874 | 5.43 |
| West Hackberry Sweet | 36.8 | 0.343 | 0.093 | 0.841 | 1.94 |
| West Hackberry Sour | 33.0 | 1.486 | 0.117 | 0.860 | 4.09 |
| Big Hill Sweet | 35.6 | 0.409 | 0.110 | 0.847 | 2.28 |
| Big Hill Sour | 31.0 | 1.840 | 0.150 | 0.871 | 6.81 |
| Bryan Mound Sweet | 36.5 | 0.377 | 0.087 | 0.842 | 2.12 |
| Bryan Mound Sour | 33.3 | 1.440 | 0.120 | 0.859 | 4.19 |

Some values in the source files are marked with a `*` — per Manual §IV, this indicates the value is not a direct lab measurement but a modeled/computed output of the Haverly system (interpolated from the cavern blend). Per this project's own GOF/DER principle, these must be treated as **DER** for any stream where they are starred.

### 3.2 Fraction-level H/C profile, example (Bryan Mound Sweet vs. Sour)

| Cut | Sweet H% | Sweet C% | Sour H% | Sour C% |
|---|---|---|---|---|
| 250–375°F | — | — | — | — |
| 375–530°F | 14.16 | 85.84 | 14.02 | 85.91 |
| 530–650°F | 13.70 | 86.20 | 13.63 | 85.98 |
| 650–850°F | 13.39 | 86.36 | 12.84 | 85.99 |
| 850–1050°F | 12.75 | 86.66 | 13.64 | 84.35 |
| 1050°F+ (residuum) | 11.02 | 87.33 | 12.83 | 84.22 |

**Observation:** the Sweet and Sour H/C profiles are surprisingly close to each other fraction-by-fraction (H% roughly 11–14% for both, C% roughly 84–87%) — the main difference isn't in the elemental H/C ratio but shows up in the sulfur distribution (Sweet: 0.001–0.75% by fraction; Sour: 0.007–2.49%) and in the heavy-residuum share (Sour's MCR% is roughly double Sweet's).

## 4. Cross-validation attempt and its limitation [GOF-based negative/clarifying result]

**None of the 8 SPR streams is a dilbit or SCO type.** The Manual's own specification (Table I) fixes the range: Sour max. 30° API, Sweet max. 45° API — the entire SPR inventory falls in the "medium-gravity sweet/sour" category.

Compared against the project's existing data:
- **Cold Lake Blend (dilbit, Pillar 1):** API 19.5°, S 3.87% — considerably heavier and more sour than any SPR stream (even the worst SPR sour is only API 30–31°, S 1.4–1.8%).
- **Bryan Mound Sweet contains 6% DSW** (Appendix A), but the whole stream (API 36.5°) is far from the pure ExxonMobil "Domestic Sweet" assay (API 42.9°, Pillar 1 addendum) — expected, since BM Sweet is primarily a Forties/Ninian-based blend.

**Conclusion:** this is a primary, real, U.S.-government GOF source — useful for cross-validating Pillar 2's RVP/fraction work (a real Vol%-based yield spec) and for confirming the "medium-gravity imported/blended crude" category, **but it does not resolve the open dilbit/SCO wellhead-energy-mix question** (session 5 handoff §3, item 2) — that still requires a separate, type-specific source.

## 5. Open items

1. Explicitly tagging the starred (computed, not measured) values as DER once they enter the model.
2. Formally linking Table I's °C-based yield bands (Naphtha/Distillate/GasOil/Residuum) to the project's n-alkane-convention carbon-number matrix — not yet done, separate DER work.
3. The dilbit/SCO wellhead-energy-mix question — still open, requires another source.

---

## References

1. U.S. Department of Energy, Office of Petroleum Reserves. *Strategic Petroleum Reserve Crude Oil Assay Manual*, 5th Edition, August 1, 2024. `spr.doe.gov/reports/docs/CrudeOilAssayManual.pdf`.
2. U.S. DOE SPR. *SPR Crude Oil Comprehensive Analysis* (assay landing page). `spr.doe.gov/reports/Crude_Oil_Assays.html`.
3. Owner-uploaded assay files (2026-09-01): BayouChoctawSwAssay_20260319.xlsx, BayouChoctawSrAssay.xls, WestHackberrySwAssay.xlsx, WestHackberrySrAssay.xlsx, BigHillSwAssay.xlsx, BigHillSrAssay.xlsx, BryanMoundSwAssay.xlsx, BM_SourCalAssay.xlsx.
