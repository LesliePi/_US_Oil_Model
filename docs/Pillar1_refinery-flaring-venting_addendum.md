# Exergy-Molecular Oil Model — Pillar 1 addendum: refinery flaring/venting loss [GOF/DER update]

**Date:** 2026-09-01 · **Owner:** Tatai László · **Session:** AllocLaw / Exergy-track, session 3
**Related document:** `AllocLaw_Session_Handoff_005.md` §0, item 4
**Precursor:** the owner's explicit instruction at the close of session 2 — *"this is a plain loss... it doesn't fit to leave it out, because that's the complete picture right now"*

**Goal:** lay the sourcing foundation for the exergy loss caused by refinery flaring/venting, which had not appeared anywhere in Pillar 1's refinery exergy balance (η_ex,refinery) until now.

---

## 1. First negative/corrective finding: the EIA is not a suitable source [GOF]

The handoff's original assumption ("EIA flaring/venting volumes at PADD or refinery level") does not hold up. On checking: the EIA's flaring/venting data (*Natural Gas Annual*, *AEO*) is exclusively **upstream (production-side)** in origin, limited to 9 producing states (AK, CA, CO, LA, NM, ND, TX, UT, WY) — the same dataset already implicitly used in the Bakken energy-mix work (Pillar 4), **not refinery data**.

## 2. The correct source: EPA GHGRP Subpart Y + EPA GHG Inventory Annex 3.5 [GOF]

- **Primary regulatory basis:** 40 CFR 98.250–98.258 (Subpart Y, Petroleum Refineries) — mandatory for every U.S. refinery with no minimum-size threshold, since 2010.
- **Methodology:** refinery flare CO2 emissions must be calculated per §98.253 (Equation Y-3); default emission factor: **60 kg CO2/MMBtu (HHV basis)** — a directly citable constant fixed in U.S. federal regulation.
- **National aggregate:** the "Refining" subcategory of the EPA's annual *Inventory of U.S. Greenhouse Gas Emissions and Sinks*, Petroleum Systems chapter, has been derived **directly from year-specific GHGRP Subpart Y data since 2010** (per Annex 3.5, Table 3.5-9's methodological note, citing "EPA 2023a" — for 1990–2009 it uses a fixed factor derived from the 2010–2013 average).
- **Specific file, successfully processed:** `2024_ghgi_petroleum_systems_annex35_tables.xlsx` (owner-uploaded), Tables 3.5-2 (CH4), 3.5-7 (CO2), 3.5-10 (N2O) — broken down by "Segment/Source," 1990–2022.

## 3. Source breakdown of the "Refining" segment [GOF]

The "Refining" segment breaks down into 13 subcategories, which sum to the segment total in every year to within 0.001%:

Uncontrolled Blowdowns · Asphalt Blowing · Process Vents · CEMS · Equipment Leaks · Storage Tanks · Wastewater Treating · Cooling Towers · Loading Operations · Catalytic Cracking/Coking/Reforming · **Flares** · Delayed Cokers · Coke Calcining

**The Flares subcategory dominates:** **95.2% (1990) → 98.7% (2022)** of the segment's total CO2 emissions — the remaining 12 sources together account for only 1–5%. This means the "Refining" national process-emissions figure is practically **flaring-dominated**, so the "Flares" row alone is adequate for the combined flaring+venting purpose, without needing to sum all 13 categories.

### Key values (kt/yr)

| Year | CO2 (Flares) | CH4 (Flares) | N2O (Flares) | Flare share of the Refining segment |
|---|---|---|---|---|
| 1990 | 3,023.0 | 8.97 | 0.0274 | 95.2% |
| 2000 | 3,405.9 | 10.11 | — | 95.2% |
| 2010 | 3,645.4 | 10.40 | 0.0355 | 96.1% |
| 2015 | 3,311.7 | 10.73 | — | 95.5% |
| 2018 | 2,814.2 | 9.51 | — | 97.8% |
| 2019 | 3,522.8 | 12.26 | — | 98.7% |
| 2020 | 2,859.2 | 10.95 | — | 98.8% |
| 2021 | 2,989.3 | 11.04 | — | 98.9% |
| **2022 (most recent)** | **2,835.7** | **10.35** | **0.0284** | **98.7%** |

Full 1990–2022 series (CO2, kt): 3023.0 · 2998.7 · 3031.8 · 3068.9 · 3126.0 · 3150.2 · 3208.8 · 3305.3 · 3356.5 · 3337.4 · 3405.9 · 3410.4 · 3369.6 · 3450.1 · 3498.3 · 3431.2 · 3436.2 · 3416.9 · 3311.4 · 3231.9 · 3645.4 · 3653.3 · 3252.3 · 2948.8 · 2866.8 · 3311.7 · 3146.8 · 2808.2 · 2814.2 · 3522.8 · 2859.2 · 2989.3 · 2835.7

**Trend observation:** refinery flaring does **not** show the dramatic late-2010s runup seen in upstream (wellhead-side, Bakken/Permian) flaring — it stays in a relatively stable, mildly fluctuating band since 1990 (~2,800–3,650 kt CO2/yr).

## 4. Activity basis and emission factor [GOF]

- **Activity unit:** Mbbl (thousand barrels) of refinery input (Table 3.5-5).
- **CO2 factor applied:** 617.6461 kg CO2/Mbbl input, fixed across the entire series (Table 3.5-8) — a national-level implied factor derived from GHGRP facilities' 2010–2013 average reported data.

## 5. Energy-content conversion [DER]

Back-calculated using the 60 kg CO2/MMBtu (HHV) default factor, for 2022:

$$E_{flare,2022} = \frac{2{,}835{,}700{,}000 \text{ kg CO}_2}{60 \text{ kg/MMBtu}} \approx 47.26 \text{ million MMBtu (HHV)} \approx 49.9 \text{ PJ}$$

**Methodological limitation, not hidden:** this inversion applies the national-level implied factor in reverse — not every GHGRP-reporting facility necessarily uses the 60 kg/MMBtu default (some report via direct carbon-content measurement/CEMS under §98.253), so the 49.9 PJ figure is a **good national approximation, not a facility-level-precision measurement. DER**, not GOF.

**Context:** relative to the total energy content of U.S. refinery crude input (roughly ~36,700 PJ/yr, a rough estimate), this represents a **~0.13–0.14%** loss — small, but quantifiable and real, consistent with the owner's original instruction.

## 6. Breakdown by crude type — checked, not found [GOF, negative result]

Reviewing the full Annex 3.5 workbook: the "heavy crude / light crude" distinction applies **exclusively to the upstream Production segment** (wellheads, separators, headers, basin-level tables 3.5-14–26). **The Refining segment, including the Flares row, has no breakdown of any kind by PADD or by crude type (domestic sweet vs. dilbit/WCS vs. SCO) in this source.**

**This is consistent with the project's already-established USA_TOTAL-scaling principle** (a lesson from the US-track: "scope narrowing resolves blocking problems"): since the available data is already a national average across the entire U.S. refining sector (which already implicitly reflects the actual blend ratio of WCS/dilbit imports and domestic sweet crude), the Flares loss can be **applied uniformly at the US_TOTAL level to both the domestic and the dilbit/SCO pathways** — a type-specific breakdown is neither necessary nor, based on this source, possible. If this ever becomes necessary in the future (e.g. if coking-intensive heavy-crude processing turns out to show a materially different flaring rate), it would require linking facility-level GHGRP data with facility-level crude-slate data — separate, substantially larger work, not warranted at present.

## 7. Open items

1. **Incorporation into Pillar 1's η_ex,refinery formula** — needs formalizing: should the flaring loss appear as part of the $B_{heat\text{-}loss}$ term, or as its own separate $B_{flare\text{-}loss}$ term in the $B_{out}/B_{in}$ ratio? Requires an owner decision.
2. **Converting CH4/N2O to CO2e** — per the owner's decision (2026-09-01, session 3), this is **dropped**, as not material to the overall picture (its GWP-weighted contribution is orders of magnitude smaller than CO2's).
3. **Future utilization potential** — the owner explicitly noted in session 2 that flare gas is also a potential future utilization/recovery opportunity, not just a loss — this thread is not yet sourced, a separate task.
4. **Facility-level, crude-slate-specific breakdown** — only relevant if the US_TOTAL approximation above ever proves insufficient (see item 6).

---

## References

1. U.S. EPA. 40 CFR Part 98, Subpart Y — Petroleum Refineries (§98.250–98.258, especially §98.253 "Equation Y-3"). eCFR.
2. U.S. EPA. *Inventory of U.S. Greenhouse Gas Emissions and Sinks: 1990–2022* (published April 2024), Chapter 3.6 Petroleum Systems.
3. U.S. EPA. *Annex 3.5: Methodology for Estimating CH4, CO2, and N2O Emissions from Petroleum Systems* — Electronic Tables (`2024_ghgi_petroleum_systems_annex35_tables.xlsx`), Tables 3.5-2, 3.5-5, 3.5-7, 3.5-8, 3.5-9, 3.5-10. Updated April 5, 2024.
4. U.S. EPA. *2011-2021 GHGRP Sector Profile: Petroleum Refineries* — context for the whole-sector (combined combustion+process) figure of 164.9 MMT CO2e for 2021, distinguished from the process-only "Refining" data used above.
