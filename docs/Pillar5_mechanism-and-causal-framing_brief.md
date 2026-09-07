# Exergy-Molecular Oil Model — Pillar 5 addendum: mechanism + causal framing, brief v0.1

**Date:** 2026-09-05 · **Owner:** Tatai László · **Session:** AllocLaw / Exergy-track, session 5
**Framing source:** `AllocLaw_Session_Handoff_007.md` §2, items #1 and #2
**Related project materials:** `Pillar5_PADD3-heavy-import-vs-tight-oil_brief.md`, `tight_oil_vs_padd3_heavy_annual.csv`, `padd3_heavy_crude_imports_monthly.csv`, `padd3_heavy_crude_imports_by_country_annual.csv` (NEW, this session), `us_oil_monitor_config.py` / `us_oil_monitor_processor.py` (updated this session — supersede every prior version)

**Goal:** (a) decide and record how to handle the causal framing of the previously documented three-phase pattern; (b) uncover and quantify the mechanism behind the 2016–2026 PADD3 heavy-crude-import-volume collapse.

**Tag convention:** GOF = sourced/confirmed; DER = derived from GOF inputs with an explicit formula/code; EST = estimate/interpolation, without type-specific measured data; OPEN = unresolved question.

---

## 1. Item #2 — causal framing: DECISION

**Owner decision this session:** a formal structural-break test (Chow test) is incorporated into the analysis of `tight_oil_vs_padd3_heavy_annual.csv` (N=27, 2000–2026); a Granger causality test is **deliberately excluded**, with the justification recorded — not as an oversight, but as an explicit methodological decision.

### 1.1 Why not Granger [DER — justification]

- **ADF test on levels:** all three key series (`tight_oil_mbbl_d`, `padd3_heavy_import_kbbl_d`, `padd3_heavy_pct`) are non-stationary (p = 0.87–0.997).
- **First differences:** `tight_oil` and `heavy_pct` become stationary (p < 0.001), but **`heavy_import_volume` does NOT** (p = 0.277). Per Perron's (1989) classic result, this is exactly the typical signature of an *unaddressed structural break* on a simple unit-root test — not genuine random-walk behavior.
- **N=27, breaking down to 7–11 observations per phase** — methodologically indefensible for a reliable VAR fit, even setting the stationarity problem aside.
- **Conclusion (EST/OPEN, explicitly recorded):** a formal Granger test on this data would produce noise rather than DER-level evidence. Excluding it is a deliberate methodological decision, consistent with the project's own principle ("don't present an uncertain result as more solid than it is").

### 1.2 Chow test — at the mechanism level (a break in the *relationship*, not just each series' own trend) [DER]

Regression: `heavy_import ~ tight_oil`, tested with a Chow test at the hypothesized phase boundaries.

| Dependent variable | Break @2008/09 | Break @2015/16 |
|---|---|---|
| `heavy_pct ~ tight_oil` | F=4.62, **p=0.021** | F=16.50, **p<0.0001** |
| `heavy_volume ~ tight_oil` | F=3.14, p=0.063 (borderline) | F=8.69, **p=0.0015** |

**Phase-by-phase slope:**

| Phase | n | heavy_pct slope (points per +1 Mbbl/d) | R² | heavy_volume slope (kbbl/d per +1 Mbbl/d) | R² |
|---|---|---|---|---|---|
| 2000–2008 | 9 | 14.03 (p=0.44, **not signif.**) | 0.09 | +832.1 (p=0.55, **not signif.**) | 0.05 |
| 2009–2015 | 7 | **5.79** (p<0.0001) | 0.98 | **−55.9** (p=0.027) | 0.66 |
| 2016–2026 | 11 | **2.67** (p=0.0002) | 0.81 | **−251.6** (p=0.0003) | 0.78 |

**Interpretation:** in phase 1 there is no detectable relationship (tight oil is still too small/too noisy). In phase 2, every +1 Mbbl/d of tight-oil growth produces +5.8 points of heavy share, while the heavy *volume* itself only declines weakly and marginally (−56 kbbl/d) — this is the numerical counterpart of the "displacement, not volume reduction" narrative. In phase 3, the share effect slows (a ceiling effect near 70–80%+), **but the volume effect strengthens to 4.5× its prior size** (−252 kbbl/d) — this is the precise magnitude of the "collapse."

### 1.3 Own-trend breakpoint scan [DER]

Scanning `heavy_import_volume`'s own trend (not its relationship with tight oil) across candidate breakpoints (2008–2021), the **best-fit single break is at 2019** (F=32.2), not the hypothesized 2016 — though 2016 is also a significant break. **This discrepancy is what led to the Venezuela lead in §2 below.**

---

## 2. Item #1 — the mechanism behind the 2016–2026 heavy-import collapse

### 2.1 Pipeline extension — country-of-origin breakdown [DER, code-based, session 5]

New field introduced: **`CNTRY_NAME`** (country name), source: EIA's own `cli_note.php` data dictionary (`eia.gov/petroleum/imports/companylevel/cli_note.php`) — **the same page already GOF-tagged in this project** as the source of the "summation of volumes... will not equal aggregate import totals" quote. Handled as an optional column (following the `PROD_CODE` pattern), since it could not be pre-verified across every vintage (1986–2026).

**Validation, on real data:**
- Cross-check against the existing heavy/medium/light series: **perfect agreement across all 40 years (1986–2026), `diff = 0.0` in EVERY year.**
- **Zero "UNKNOWN" rows** — the `CNTRY_NAME` column existed reliably in every single vintage file; the assumed column name was correct on the first try.

**Code:** `us_oil_monitor_config.py` (new `CNTRY_NAME` optional_columns entry), `us_oil_monitor_processor.py` (`_build_padd3_monthly_winners()` refactored into a shared core, plus a new `load_padd3_heavy_imports_by_country()` function). **Both files supersede the prior version.** New output: `padd3_heavy_crude_imports_by_country_annual.csv`.

### 2.2 Examining four candidate explanations

| Candidate | Result | Tag |
|---|---|---|
| Venezuela sanctions (2019-01-28, PDVSA) | **Confirmed, dominant factor** | GOF/DER |
| Mexico's structural production and export decline | **Confirmed, second-largest factor** | GOF/DER |
| Refinery efficiency gains / reduced heavy demand | **Not supported — negative result** | GOF (negative) |
| Canadian pipeline capacity "bypass" | **Not supported — effect runs the opposite way** | GOF/DER (negative) |

**Venezuela [GOF, primary source: US Treasury/OFAC + CRS report (congress.gov/crs-product/R46213), and EIA Today in Energy #60762]:** the PDVSA sanctions of 2019-01-28, with wind-down through 2019-04-28. At the national level, U.S. imports from Venezuela fell 50% in a single month (January→February 2019), then to essentially zero by mid-2019. Citgo (a PDVSA subsidiary)'s two PADD3 refineries (Lake Charles, Corpus Christi) were specifically designed for heavy-crude processing.

**Mexico [GOF, primary/secondary: EIA import statistics, OilPrice.com/RBN Energy reporting on Pemex data]:** Pemex production fell from 2.25 to 1.37 million barrels/day (2015→2025). In parallel, Mexico expanded its own refining capacity (the 340,000 bbl/d Dos Bocas/Olmeca refinery, specifically built for domestic processing of Maya heavy crude, part of the AMLO/Sheinbaum government's energy self-sufficiency program, with a declared export-reduction intent from 2021 onward) — this redirects heavy crude from exports into domestic consumption.

**Refinery efficiency — a negative result, honestly recorded [GOF, RBN Energy/OPIS]:** PADD3 capacity is roughly stable/mildly growing over this period (the LyondellBasell Houston closure, −264 kb/d in 2025, was more than offset by the ExxonMobil Beaumont expansion, +240–250 kb/d in 2023); utilization stayed high (~93% average in 2025). A January 2026 RBN/OPIS analysis explicitly characterizes Gulf Coast refiners as wanting *more* Venezuelan heavy crude if they could get access to it — which contradicts the declining-demand hypothesis.

**Canadian "bypass" — also unsupported, and our own microdata confirms this [DER, see §2.3]:** Canada's PADD3-specific heavy imports actually **grew** between 2016 and 2025 (126,327 → 150,052 kbbl/yr) — an offsetting, not a causal, factor.

### 2.3 Numeric decomposition, 2016→2025 (full years only, avoiding distortion from the partial 2026 year) [DER]

| | Change (kbbl/yr) | Share of the total decline |
|---|---:|---:|
| **Total decline** | **−400,381** | 100% |
| Venezuela | −206,570 | **51.6%** |
| Mexico | −103,488 | **25.8%** |
| Canada | **+23,725** | −5.9% (offsetting) |
| Other (scattered: Colombia, Iraq, Brazil, Angola, Ecuador, Chad, Saudi Arabia, etc.) | −114,048 | 28.5% |

Within the "Other" category, the largest single element is Colombia (73,905 → 49,733 kbbl/yr); the remaining countries decline in a scattered, smaller way — there is no single dominant third contributor.

### 2.4 Venezuela time series — direct confirmation of the sanctions timeline from PADD3-specific microdata [DER]

| Year | Venezuela heavy imports, PADD3 (kbbl/yr) | Event |
|---|---:|---|
| 2016 | 253,551 | |
| 2017 | 214,389 | |
| 2018 | 178,527 | |
| 2019 | 28,904 | Sanctions Jan. 28, wind-down through Apr. 28 |
| 2020 | 0 | Full embargo |
| 2021 | 0 | Full embargo |
| 2022 | 0 | Full embargo |
| 2023 | 45,920 | Chevron waiver (granted Nov. 2022, resumes Jan. 2023) |
| 2024 | 77,173 | |
| 2025 | 46,981 | |
| 2026* | 67,692 | *partial year |

**This is now DER-level (from the project's own microdata), not just a GOF-level literature claim** — the sanctions timeline (exactly 0 in 2020–2022, resumption exactly in 2023) is reproduced perfectly in our own processed data.

---

## 3. Open items (priorities for the next session)

1. **Formalizing a single Pillar 5 vulnerability metric** — combining a supplier's import share with that supplier's own political/geopolitical stability into one number is a natural next step. The import-share weights for Venezuela/Mexico/Canada **are now available as DER data** (this brief) — this makes that next step easier, but the country-specific stability indices (see #2) and the exact way to combine the two are still missing. (Internal design work, not yet part of this repository.)
2. **Country-specific σ_i(t) stability indices** (Fraser/WGI, for Venezuela/Mexico/Canada/Persian Gulf) — not yet pulled; the other missing half of the σ_j extension.
3. **Item-by-item review of the "Other" category** (Colombia, Iraq, etc.) — low priority, a scattered effect, probably not worth deep individual sourcing.
4. **Bakken/Niobrara/Anadarko tight-oil mnemonics** — still open, not blocking.
5. **A formal Bai–Perron multi-break test** (instead of the simpler, pre-specified-breakpoint Chow test) — an optional refinement, if a more precise breakpoint estimate (e.g. a confidence interval for the standalone 2019 trend break) becomes important.

---

## References

1. EIA. "Company Level Imports" data dictionary. `eia.gov/petroleum/imports/companylevel/cli_note.php` — source of the `CNTRY_NAME`/`GCTRY_CODE` fields.
2. Congressional Research Service. "Oil Market Effects from U.S. Economic Sanctions: Iran, Russia, Venezuela." `congress.gov/crs-product/R46213`.
3. U.S. EIA, Today in Energy, "Venezuela's oil production..." `eia.gov/todayinenergy/detail.php?id=60762` (Chevron waiver, granted Nov. 2022 / resumed Jan. 2023).
4. OilPrice.com (2025-10-04). "Pemex's Dos Bocas Turns Into Mexico's Refinery Nightmare" (Pemex production 2.25→1.37 M bbl/d, 2015→2025).
5. RBN Energy. "Look What You Made Me Do — Cut in Mexican Crude Exports Has U.S. Refiners Looking for Alternatives" (Pemex's 2021 export-reduction intent, Dos Bocas/Olmeca).
6. RBN Energy / OPIS (2026-01). "US Gulf Coast Refining Outlook Remains Bright for Coming Years" (PADD3 capacity stable/mildly growing, utilization ~93%, demand for "advantageous heavy crude from Venezuela").
7. Perron, P. (1989). "The Great Crash, the Oil Price Shock, and the Unit Root Hypothesis." *Econometrica*, 57(6), 1361–1401. — methodological reference for the structural-break-vs-spurious-unit-root question.
