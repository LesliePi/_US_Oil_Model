# Exergy-Molecular Oil Model — Pillar 5 brief v0.1
## PADD3 heavy-crude imports vs. domestic tight-oil production — the central empirical result

**Date:** 2026-09-05 · **Owner:** Tatai László · **Session:** AllocLaw / Exergy-track, session 4
**Framing source:** `Alap-Elmeletek.md` (Pillar 5 outline), `AllocLaw_Session_Handoff_006.md` (open items 1–2)
**Related project materials:** `Pillar5_geopolitical-vulnerability_brief.md`, `us_oil_monitor_config.py` / `_downloader.py` / `_processor.py`

**Goal:** to quantify Pillar 5's central claim — that growth in domestic tight-oil production does not primarily reduce imports, but instead shifts their *quality composition* toward heavy crude, because Gulf Coast (PADD3) refineries are optimized for heavy crude, which the (typically ultra-light) tight oil cannot substitute for.

**Tag convention:** GOF = sourced/confirmed; DER = derived from GOF inputs with an explicit formula/code; EST = estimate/interpolation; OPEN = unresolved question.

> **Translator's note (added for the English/GitHub edition):** open items #1 and #2 below were resolved in a later session (session 5) via a formal Chow structural-break test, with Granger causality explicitly and deliberately excluded (justification: non-stationarity of `heavy_import_volume` even in first differences; too few observations per phase for a reliable VAR fit; see Perron, 1989). The best-fit single breakpoint was found at 2019, not 2016, pointing toward the Venezuela-sanctions hypothesis. A country-of-origin decomposition of the 2016–2025 decline additionally found Venezuela accounting for 51.6% and Mexico 25.8% (Canada partially offsetting at −5.9%). **See [`Pillar5_mechanism-and-causal-framing_brief.md`](./Pillar5_mechanism-and-causal-framing_brief.md) for the full methodological write-up** — the open-questions section below is left as originally written, as the historical record of this brief's own original scope.

---

## 1. Data sources

### 1.1 PADD3 heavy-crude imports — DER, from row-level GOF microdata

**Source:** EIA "Company Level Imports" (Form EIA-814, "Monthly Imports Report"), `eia.gov/petroleum/imports/companylevel/`. Record-level (per-shipment) data: annual "Including Final Revisions" archives (1986–2025) + monthly files (2026). **No queryable API series exists at this level of granularity** — the files were downloaded manually and processed with `us_oil_monitor_processor.py --company-imports-dir`.

**Filter:** `PROD_NAME` contains the string "CRUDE OIL" (substring match, see §1.2) AND `PCOMP_PADD == 3` (the *processing* PADD — **not** the port-of-entry PADD; this is confirmed by EIA's own published methodological note: *"crude oil ... reported by the PAD District in which they are processed"*).

**Heavy/Medium/Light convention [GOF, EIA Today in Energy, 2015-02-10]:** Heavy ≤27° API, Medium 27–35°, Light ≥35°.

**Cross-validation [GOF-level confirmation]:** total PADD3 crude-oil imports computed for 2025 (507,511 thousand barrels/year → 1,390 kbbl/d average) **match EIA's own published annual aggregate within 0.07%** (`MCRIPP32`, 1,391 kbbl/d). The remaining gap is explained by EIA's own documented note: *"summation of volumes for PAD Districts 1-5 from the Company-Level Imports will not equal aggregate import totals"* (some imports appear in the aggregate as an estimated top-up but are not present in the row-level file).

### 1.2 Methodological bugs — found and fixed this session

The four-decade archive **has no unified schema** — each decade used a different format. Four independent bugs were found and fixed during processing; documenting them has methodological value in its own right, since they are likely to recur in any future processing of similar EIA archives:

| # | Field | 2016+ (modern) | Older vintage | Failure mode if unhandled | Fix |
|---|---|---|---|---|---|
| 1 | `PROD_NAME` | `"Crude Oil"` | 2001: `"CRUDE OIL,FOREIGN"` | exact-match excluded every 2001 row | substring match (does it contain `"CRUDE OIL"`) |
| 2 | `PROD_CODE` | `025` (int) | `20` (sometimes `16`, 1986–89), type also varies (int/float/string) | used as an AND-gate, excluded every pre-2016 row | demoted to an audit-only diagnostic, no longer gates inclusion |
| 3 | `PCOMP_PADD` | int | 2001: string (`'3'`) | `== 3` (int) silently returned zero matches | numeric normalization (`pd.to_numeric`) before comparison |
| 4 | `RPT_PERIOD` | real date object | 2001: `"0101"` string (YYMM); 2002: `201` bare int (no leading zero) | date parsing failed or silently misfired | unified parser handling date object / YYMM string / no-leading-zero int alike |

Sheet names (`sheet_name`) also vary by vintage (`"IMPORTS"`, `"Imports"`, a year-named sheet, `"Sheet1"`) — this is handled (fallback + audit log) and caused no data loss.

**Coverage after fixes: 1986–2026, 486 months, zero missing months.**

### 1.3 Domestic tight-oil production — GOF, formation-level

**Source:** EIA Short-Term Energy Outlook (STEO), Table 10b, "Crude Oil and Natural Gas Production from Shale and Tight Formations." Replaced the earlier Drilling Productivity Report as of June 2024.

**Verified, genuinely real series (confirmed with `--verify`):**
- `TOTAL_US` = `STEO.TOPRL48.M` — **GOF**, explicitly named in EIA's own 2024-11-14 STEO data-correction notice
- `PERMIAN` = `STEO.TOPRPM.M` — **GOF**, same source
- `EAGLE_FORD` = `STEO.TOPREF.M` — **GOF**, resolved successfully via `--verify`
- `AUSTIN_CHALK` = `STEO.TOPRAC.M` — **GOF**, resolved successfully via `--verify`

**OPEN — unresolved:** `BAKKEN`, `NIOBRARA`, `ANADARKO` — the assumed mnemonic pattern (`TOPR`+abbreviation) did not resolve to a real series for these. Does not block the core comparison (which only needs `TOTAL_US`).

**Data range:** 2000-01 – 2026-07 (319 months).

---

## 2. Result — the three phases

Comparing the full 1986–2026 PADD3 heavy-import series against the 2000–2026 tight-oil production series reveals **three sharply distinct phases**:

| Phase | Years | Tight oil (M bbl/d) | PADD3 heavy-import volume (kbbl/d) | Heavy % |
|---|---|---|---|---|
| **1. Baseline (pre-boom)** | 2000–2008 | 0.25 → 0.42 | ~1,770 → 2,240 (**mild rise**) | 34.5% → 42.4% |
| **2. Boom (shale boom)** | 2009–2015 | 0.49 → **4.58** (18.6×) | ~2,310 → 2,210 (**stable**) | 45.9% → **69.5%** |
| **3. Maturity** | 2016–2026 | 4.26 → 9.39 | 2,200 → **583** (**collapses**) | 65.3% → **82.4%** |

**Interpretation (non-causal note: this comparison shows a correlation; the brief on its own does not establish causation):**

- **Phase 1:** tight oil is essentially absent; PADD3 imports are of mixed quality and rise slowly and mildly, in step with refinery capacity expansion.
- **Phase 2 (the core of the mechanism):** as tight-oil production takes off, **total import volume barely changes** — but its quality composition shifts dramatically toward heavy. Domestic light tight oil does not primarily reduce imports; it **displaces light/medium imports specifically**, and the capacity that frees up is filled by heavy imports drawn from that same total volume.
- **Phase 3:** only *after* the heavy share has already climbed above 70% does **the heavy-import volume itself** start to shrink — this brief does not address the reason (refinery efficiency gains, demand shifts, alternative heavy sourcing), which remains an **OPEN** question.

### 2.1 Full annual table (1986–2026)

| Year | Total (kbbl/yr) | Heavy % | | Year | Total (kbbl/yr) | Heavy % |
|---|---|---|---|---|---|---|
| 1986 | 752,845 | 28.7% | | 2007 | 2,038,136 | 43.6% |
| 1987 | 863,315 | 29.4% | | 2008 | 1,937,951 | 42.4% |
| 1988 | 989,339 | 24.4% | | 2009 | 1,835,597 | 45.9% |
| 1989 | 1,179,194 | 20.0% | | 2010 | 1,944,923 | 45.3% |
| 1990 | 1,188,027 | 21.2% | | 2011 | 1,794,255 | 48.3% |
| 1991 | 1,166,673 | 23.0% | | 2012 | 1,634,972 | 50.6% |
| 1992 | 1,233,525 | 25.5% | | 2013 | 1,363,749 | 57.2% |
| 1993 | 1,363,540 | 29.5% | | 2014 | 1,223,290 | 63.5% |
| 1994 | 1,474,725 | 29.5% | | 2015 | 1,159,806 | 69.5% |
| 1995 | 1,482,360 | 30.7% | | 2016 | 1,232,376 | 65.3% |
| 1996 | 1,587,641 | 34.4% | | 2017 | 1,131,736 | 69.0% |
| 1997 | 1,683,236 | 35.5% | | 2018 | 1,017,321 | 73.7% |
| 1998 | 1,782,685 | 34.7% | | 2019 | 717,640 | 82.0% |
| 1999 | 1,804,816 | 30.1% | | 2020 | 666,250 | 74.2% |
| 2000 | 1,876,065 | 34.5% | | 2021 | 567,285 | 74.6% |
| 2001 | 1,954,060 | 39.8% | | 2022 | 597,650 | 75.9% |
| 2002 | 1,883,111 | 43.3% | | 2023 | 624,614 | 77.4% |
| 2003 | 2,003,874 | 41.7% | | 2024 | 602,542 | 77.8% |
| 2004 | 2,111,145 | 43.6% | | 2025 | 507,511 | 79.7% |
| 2005 | 2,062,230 | 41.8% | | 2026* | 258,246 | 82.4% |
| 2006 | 2,059,060 | 43.1% | | | | |

*2026: only 6 months (2026-01 – 2026-06), not a full year.

### 2.2 Tight oil vs. PADD3 heavy imports, year-by-year (2000–2026)

See: `tight_oil_vs_padd3_heavy_annual.csv` (included with the project data). 27 years, zero gaps.

---

## 3. Epistemic status

- **GOF, high confidence:** the `TOTAL_US`, `PERMIAN`, `EAGLE_FORD`, `AUSTIN_CHALK` tight-oil series (STEO Table 10b, real mnemonics confirmed via `--verify`); the heavy/medium/light API-band convention; the 2025 cross-validation result.
- **DER, source-based but with our own aggregation:** the full 1986–2026 PADD3 heavy-import monthly/annual series (from raw EIA-814 microdata, with documented filtering logic, validated to GOF level for 2025).
- **EST / OPEN, unresolved:** the `BAKKEN`/`NIOBRARA`/`ANADARKO` mnemonics; the reason behind the phase-3 (2016+) heavy-import collapse; the import-weighted linking function (`f(·)`) planned for σ_j — this brief does not address that, only the raw empirical backbone it would need.

---

## 4. Open questions (detailed in Handoff #7)

1. Should this be formalized into causal language (e.g. a Granger test), or does it remain a descriptive correlation? *(See the translator's note at the top of this document — resolved in a later session; full write-up pending.)*
2. Uncovering the mechanism behind the phase-3 (2016+) heavy-import decline — a new sourcing task. *(See the translator's note — partially resolved in a later session; full write-up pending.)*
3. Filling in the Bakken/Niobrara/Anadarko mnemonics (not blocking).
4. How should this brief's empirical, import-weighted supplier breakdown be formalized into a single Pillar 5 vulnerability metric? (Internal design work, not yet part of this repository.)
