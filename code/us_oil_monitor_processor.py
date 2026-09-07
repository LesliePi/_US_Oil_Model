# US Oil Allocation Law Monitor — Derived-Quantities Processor
# us_oil_monitor_processor.py
# Version: v0.1  (2026-08-30)
# Author: László Tatai / BarefootRealism Labs (sibling of eu_monitor_* family)
# License: Apache License 2.0 WITH Commons Clause v1.0
# -*- coding: utf-8 -*-

"""
Turns the raw EIA JSON pulled by us_oil_monitor_downloader.py into the
derived quantities the Allocation Law brief (v0.7) actually needs:

  s_j(t)          - state production share, latest month  (brief §16.2)
  alpha_prod(t)   - 1 - R_prod(t+1)/R_prod(t), monthly     (brief §16.3, DER)
  Delta_SPR(t)    - first difference of the SPR stock level, weekly (brief §17.3, DER)
  Delta_Comm(t)   - first difference of commercial stock level, weekly (brief §17.3, DER)
  R_effective(t)  - R_prod(t) + R_import(t) + Delta_SPR(t) - R_export(t), monthly (brief §17.5)
  alpha_eff(t)    - 1 - R_effective(t+1)/R_effective(t), monthly (brief §17.5, DER)

Nothing here is new SOURCING -- every series it reads was identified
and tagged in the brief before this script existed. This script only
computes what the brief already specified, from whatever raw files are
actually present in data/raw/. If a required file is missing, it says
so explicitly and skips only the derived quantity that needed it --
it does not fail, so partial runs (e.g. production downloaded, flow
layer not yet pulled) still produce whatever they can.

Design note -- frequency alignment (brief v0.7 §17.5, flagged as an
implementation decision, not a sourcing question): production is
monthly, the flow layer (SPR/commercial/imports/exports) is weekly.
This script aggregates weekly -> monthly by MEAN over the weeks
falling in each calendar month before combining with production. This
is a defensible default (smooths weekly noise, matches the production
series' own monthly cadence) but is a choice, not a fact -- an
end-of-month snapshot or a sum-of-weekly-flows alternative would give
different Delta_SPR / R_effective numbers. Flagged here so it isn't
silently baked in.

Usage:
    python us_oil_monitor_processor.py                # run everything available, print summary
    python us_oil_monitor_processor.py --csv           # also write PROCESSED_CSV / PROCESSED_FLOWS_CSV
"""

import os
import sys
import json
import glob
import argparse
import datetime

import pandas as pd

from us_oil_monitor_config import (
    CRUDE_PRODUCTION, SPR_STOCKS, COMMERCIAL_STOCKS, TOTAL_STOCKS_INCL_SPR,
    CRUDE_IMPORTS, CRUDE_EXPORTS,
    PADD3_HEAVY_CRUDE_IMPORTS, RAW_MANUAL_PADD3_HEAVY,
    TIGHT_OIL_PRODUCTION,
    RAW_EIA_PRODUCTION, RAW_EIA_STOCKS, RAW_EIA_TRADE,
    PROCESSED_DIR, PROCESSED_CSV, PROCESSED_FLOWS_CSV, PROCESSED_PADD3_HEAVY_CSV,
    PROCESSED_TIGHT_VS_HEAVY_CSV,
)


def _section(title: str):
    print(f"\n{'='*60}\n  {title}\n{'='*60}")


# ============================================================
# LOADING
# ============================================================

def _find_downloaded_file(output_dir: str, file_prefix: str) -> str | None:
    """
    Locates the file for a given dataset by PREFIX match rather than
    reconstructing an exact expected filename. This is deliberately
    robust to naming inconsistencies between downloader versions (see
    run_flow_layer_downloads() docstring in us_oil_monitor_downloader.py
    for the specific bug this works around: files downloaded under the
    old naming scheme, e.g. "spr_stocks_petroleum.stocks.spr.json", are
    still found even though a hardcoded exact-name lookup would miss
    them). If more than one file matches the prefix, the most recently
    modified one is used and the others are reported, since that
    situation means either a stale duplicate from a re-download or a
    genuine naming collision worth the user's attention.
    """
    if not os.path.isdir(output_dir):
        return None
    matches = sorted(glob.glob(os.path.join(output_dir, f"{file_prefix}_*.json")),
                      key=os.path.getmtime, reverse=True)
    if not matches:
        return None
    if len(matches) > 1:
        print(f"    [NOTE] {len(matches)} files match prefix '{file_prefix}_*.json' in {output_dir} "
              f"-- using most recent: {os.path.basename(matches[0])}")
        for m in matches[1:]:
            print(f"           (ignoring older match: {os.path.basename(m)})")
    return matches[0]


def load_eia_series(path: str) -> pd.Series | None:
    """
    Loads one raw EIA JSON (as saved by us_oil_monitor_downloader.py's
    _save_json) into a pandas Series indexed by period, sorted
    ascending. Returns None if the file doesn't exist -- callers must
    handle that (this is how "not yet downloaded" is reported).
    Handles both monthly ("YYYY-MM") and weekly ("YYYY-MM-DD") periods.
    """
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        body = json.load(f)
    rows = body.get("response", {}).get("data", [])
    if not rows:
        return None
    periods = [r["period"] for r in rows]
    values = [r["value"] for r in rows]
    # EIA periods are "YYYY-MM" (monthly) or "YYYY-MM-DD" (weekly/daily)
    idx = pd.to_datetime(periods, format="%Y-%m" if len(periods[0]) == 7 else None)
    s = pd.Series(values, index=idx, dtype="float64").sort_index()
    s = s[~s.index.duplicated(keep="last")]
    return s


def load_production_panel() -> dict[str, pd.Series | None]:
    """Loads every state + US_TOTAL production series. Missing files -> None."""
    panel = {}
    for key, meta in CRUDE_PRODUCTION["entities"].items():
        fname = f"{CRUDE_PRODUCTION['file_prefix']}_{key.lower()}.json"
        path = os.path.join(RAW_EIA_PRODUCTION, fname)
        panel[key] = load_eia_series(path)
    return panel


def load_tight_oil_panel() -> dict[str, pd.Series | None]:
    """Loads every tight-oil-by-formation series (STEO Table 10b). Missing files -> None,
    same contract as load_production_panel()."""
    panel = {}
    for key in TIGHT_OIL_PRODUCTION["entities"]:
        fname = f"{TIGHT_OIL_PRODUCTION['file_prefix']}_{key.lower()}.json"
        path = os.path.join(TIGHT_OIL_PRODUCTION["output_dir"], fname)
        panel[key] = load_eia_series(path)
    return panel


def compare_tight_oil_vs_padd3_heavy(tight_oil_total: pd.Series | None,
                                      padd3_heavy: pd.DataFrame | None) -> pd.DataFrame | None:
    """
    The actual Session Handoff #6 item #1/#2 comparison: domestic tight
    oil production (million bbl/d) alongside PADD3 heavy-crude import
    volume and heavy-share (kbbl/d, %), on a common annual grid. This
    does not compute a causal claim -- it lines the two series up so
    the correlation (or lack of it) is visible; interpretation is
    still the owner's / the brief's job, not this function's.
    """
    if tight_oil_total is None or padd3_heavy is None:
        return None
    tight_annual = tight_oil_total.groupby(tight_oil_total.index.year).mean()  # million bbl/d
    heavy_annual = padd3_heavy.groupby(padd3_heavy.index.year).agg(
        total=("total", "sum"), heavy=("heavy", "sum"))
    heavy_annual["heavy_pct"] = 100 * heavy_annual["heavy"] / heavy_annual["total"]
    heavy_annual["heavy_kbbl_d"] = heavy_annual["heavy"] / heavy_annual.index.map(
        lambda y: 366 if pd.Timestamp(year=y, month=12, day=31).is_leap_year else 365)
    years = sorted(set(tight_annual.index) & set(heavy_annual.index))
    if not years:
        return None
    rows = [{"year": y, "tight_oil_mbbl_d": tight_annual[y],
             "padd3_heavy_import_kbbl_d": heavy_annual.loc[y, "heavy_kbbl_d"],
             "padd3_heavy_pct": heavy_annual.loc[y, "heavy_pct"]} for y in years]
    return pd.DataFrame(rows).set_index("year")


def load_flow_layer() -> dict[str, pd.Series | None]:
    """Loads the v0.7 flow-layer series. Missing files -> None (reported by caller)."""
    flows = {}
    for key, cfg in [
        ("SPR_STOCKS", SPR_STOCKS),
        ("COMMERCIAL_STOCKS", COMMERCIAL_STOCKS),
        ("TOTAL_STOCKS_INCL_SPR", TOTAL_STOCKS_INCL_SPR),
        ("CRUDE_IMPORTS", CRUDE_IMPORTS),
        ("CRUDE_EXPORTS", CRUDE_EXPORTS),
    ]:
        path = _find_downloaded_file(cfg["output_dir"], cfg["file_prefix"])
        flows[key] = load_eia_series(path) if path else None
    return flows


# ============================================================
# s_j(t)  — production share, latest month  (brief §16.2)
# ============================================================

def compute_s_j(panel: dict[str, pd.Series | None]) -> pd.DataFrame | None:
    us_total = panel.get("US_TOTAL")
    if us_total is None:
        return None
    latest = us_total.index.max()
    rows = []
    named_sum = 0.0
    for key, s in panel.items():
        if key == "US_TOTAL" or s is None:
            continue
        v = s.get(latest, None)
        if v is None:
            continue
        rows.append((key, v))
        named_sum += v
    total_v = us_total.get(latest)
    if total_v is None or not rows:
        return None
    df = pd.DataFrame(rows, columns=["state", "value"]).sort_values("value", ascending=False)
    df["share_pct"] = 100 * df["value"] / total_v
    other_share = 100 * (total_v - named_sum) / total_v
    df = pd.concat([df, pd.DataFrame([{"state": "OTHER (residual)", "value": total_v - named_sum,
                                        "share_pct": other_share}])], ignore_index=True)
    df.attrs["period"] = latest.strftime("%Y-%m")
    df.attrs["us_total"] = total_v
    return df


# ============================================================
# alpha_prod(t)  (brief §16.3, DER)
# ============================================================

def compute_alpha_prod(us_total: pd.Series | None) -> pd.Series | None:
    if us_total is None:
        return None
    # alpha(t) = 1 - R(t+1)/R(t)
    alpha = 1 - us_total.shift(-1) / us_total
    alpha = alpha.dropna()
    alpha.name = "alpha_prod"
    return alpha


def annualized_alpha_by_regime(alpha_prod: pd.Series, regimes: list[tuple[str, str, str]]) -> pd.DataFrame:
    """
    Reproduces the brief's §16.3 regime table: mean monthly alpha over
    each named window, annualized as (1+mean_monthly)^12 - 1.
    regimes: list of (label, start "YYYY-MM", end "YYYY-MM"), inclusive.
    """
    rows = []
    for label, start, end in regimes:
        window = alpha_prod.loc[start:end]
        if window.empty:
            rows.append((label, None))
            continue
        annualized = (1 + window.mean()) ** 12 - 1
        rows.append((label, annualized))
    return pd.DataFrame(rows, columns=["regime", "annualized_alpha"])


# ============================================================
# Flow layer deltas + R_effective(t) + alpha_eff(t)  (brief §17.3, §17.5)
# ============================================================

def compute_flow_deltas(flows: dict[str, pd.Series | None]) -> dict[str, pd.Series | None]:
    out = {}
    for key in ("SPR_STOCKS", "COMMERCIAL_STOCKS"):
        s = flows.get(key)
        out[f"delta_{key.lower()}"] = s.diff().dropna() if s is not None else None
    return out


def cross_check_total_stocks(flows: dict[str, pd.Series | None]) -> pd.Series | None:
    """SPR + Commercial should equal Total (brief §17.3 note) -- returns the residual, or None."""
    spr, comm, total = flows.get("SPR_STOCKS"), flows.get("COMMERCIAL_STOCKS"), flows.get("TOTAL_STOCKS_INCL_SPR")
    if spr is None or comm is None or total is None:
        return None
    combined = (spr + comm).dropna()
    aligned_total = total.reindex(combined.index)
    return (combined - aligned_total).dropna()


def _weekly_to_monthly_mean(s: pd.Series | None) -> pd.Series | None:
    if s is None:
        return None
    m = s.resample("MS").mean()  # see module docstring: MEAN aggregation is a stated choice
    m.index = m.index.to_period("M").to_timestamp()
    return m


def compute_r_effective(us_total_prod: pd.Series | None,
                         flows: dict[str, pd.Series | None]) -> pd.Series | None:
    """
    R_effective(t) = R_prod(t) + R_import(t) - R_export(t) - Delta_SPR(t)

    SIGN CONVENTION (owner decision, 2026-08-30, brief v0.7 addendum
    pending): Delta_SPR enters with a MINUS sign, matching the standard
    EIA supply-disposition identity (Product Supplied = Production +
    Imports - Exports - Stock Change). This is not a fixed "always
    subtract" rule -- Delta_SPR's own sign already encodes flow
    direction (negative during a drawdown/release, positive during a
    fill), so "- Delta_SPR" automatically ADDS to R_effective during a
    release (oil physically leaving storage onto the market) and
    SUBTRACTS during a fill (oil being pulled off the market into
    storage), with no separate conditional needed. Confirmed against
    the real April-August 2026 SPR drawdown episode (weekly draws of
    -4,000 to -9,900 thousand barrels): the OLD "+Delta_SPR" version
    produced a physically backwards signal (R_effective collapsing
    during a real release); this version rises instead, matching
    physical reality.

    NOT modeled here, flagged as open limitations rather than guessed
    at (owner note, same session): (1) the SPR has a hard physical
    floor -- it cannot be drawn below some minimum (roughly 70M bbl
    operational floor per DOE statements, distinct from the 252.4M bbl
    statutory threshold) -- not an issue for this HISTORICAL
    computation, since the real observed EIA level data already
    reflects whatever physical constraint actually applied, but would
    need explicit modeling if this series is ever used to forward-
    simulate beyond the observed data range; (2) the maximum
    sustainable withdrawal RATE itself declines as the cavern empties
    (salt-cavern pressure/geometry effect) -- again already implicit
    in the historical data used here, but not captured as a standalone
    rate-capacity function, so this term should not be extrapolated
    predictively without further sourcing; (3) refill is not the
    physical mirror of drawdown (different rate limits, and requires
    purchasing oil against its own budget/market constraints) -- noted,
    not modeled.
    """
    if us_total_prod is None:
        return None
    imports_m = _weekly_to_monthly_mean(flows.get("CRUDE_IMPORTS"))
    exports_m = _weekly_to_monthly_mean(flows.get("CRUDE_EXPORTS"))
    spr = flows.get("SPR_STOCKS")
    if spr is not None:
        day_gaps = spr.index.to_series().diff().dt.days
        spr_delta_daily_rate = spr.diff() / day_gaps  # thousand barrels PER DAY, not per week
        delta_spr_m = _weekly_to_monthly_mean(spr_delta_daily_rate)
    else:
        delta_spr_m = None

    missing = [name for name, s in
               [("R_import", imports_m), ("R_export", exports_m), ("Delta_SPR", delta_spr_m)]
               if s is None]
    if missing:
        print(f"  [R_effective] cannot compute yet -- missing: {', '.join(missing)}")
        return None

    df = pd.concat({"R_prod": us_total_prod, "R_import": imports_m,
                     "Delta_SPR": delta_spr_m, "R_export": exports_m}, axis=1).dropna()
    r_eff = df["R_prod"] + df["R_import"] - df["R_export"] - df["Delta_SPR"]
    r_eff.name = "R_effective"
    return r_eff


def compute_alpha_eff(r_effective: pd.Series | None) -> pd.Series | None:
    if r_effective is None:
        return None
    alpha = 1 - r_effective.shift(-1) / r_effective
    alpha = alpha.dropna()
    alpha.name = "alpha_eff"
    return alpha


# ============================================================
# PADD3 HEAVY-CRUDE IMPORT LAYER (Pillar 5, session 4, manual ingest)
# Session Handoff #6, item #1: PADD3-specific heavy-crude import
# volumes vs. domestic tight-oil production. Source: EIA "Company
# Level Imports" (Form EIA-814), manually downloaded per year/month --
# see PADD3_HEAVY_CRUDE_IMPORTS in the config for the full provenance
# note and the 2025 cross-validation against MCRIPP32 (1,390 vs. 1,391
# kbbl/d, 0.07% off).
# ============================================================

_COMPANY_IMPORTS_REQUIRED_COLS = PADD3_HEAVY_CRUDE_IMPORTS["required_columns"]
_COMPANY_IMPORTS_OPTIONAL_COLS = PADD3_HEAVY_CRUDE_IMPORTS["optional_columns"]


def _band_for_api(api, bands: dict) -> str | None:
    """
    Classifies one API-gravity value into HEAVY/MEDIUM/LIGHT per the
    config's band definitions. Returns None for an unclassifiable
    value (missing/non-numeric) -- NOT observed on any Crude-Oil-
    flagged row in the 2025 validation file, but if another vintage
    has one, this surfaces as an explicit exclusion, never a silent
    zero folded into HEAVY.
    """
    try:
        api = float(api)
    except (TypeError, ValueError):
        return None
    _, heavy_hi = bands["HEAVY"]
    med_lo, med_hi = bands["MEDIUM"]
    if api <= heavy_hi:
        return "HEAVY"
    if med_lo < api < med_hi:
        return "MEDIUM"
    return "LIGHT"  # api >= bands["LIGHT"][0]


def _normalize_padd(series: pd.Series) -> pd.Series:
    """
    PCOMP_PADD (and PORT_PADD) should be comparable as plain integers,
    but some vintages store it as text ('3') rather than a number (3)
    -- confirmed this session on the real 2001 archive, where
    `df["PCOMP_PADD"] == 3` matched ZERO rows even though 3,611 rows
    genuinely had PADD 3, because the column dtype was string. Coerces
    to numeric so int/string/float all compare equal; unparseable
    values (e.g. an embedded duplicate header row -- also seen in the
    2001 file, where a literal 'PCOMP_PADD' string shows up as a data
    value) become NaN and simply never match any real PADD number.
    """
    return pd.to_numeric(series, errors="coerce")


def _parse_rpt_period(series: pd.Series) -> pd.Series:
    """
    RPT_PERIOD is a real Timestamp in modern (~2016+) files, but a
    plain 'YYMM' text string in older archives (confirmed this session
    on the real 2001 file: '0101' = Jan 2001, per the cli_note.php
    documentation's own stated format for this field, which the
    2025-era files no longer follow). Handles both, plus garbage
    values (the 2001 file also contains a literal 'RPT_PERIOD' string
    as a data value -- an embedded duplicate header row -- which this
    returns as NaT rather than raising, so one corrupt row doesn't
    take out the whole file).
    """
    def parse_one(v):
        if isinstance(v, (pd.Timestamp, datetime.datetime, datetime.date)):
            return pd.Timestamp(v).replace(day=1)
        # Some vintages (confirmed: 2002) store YYMM as a bare number,
        # which drops the leading zero ("0201" becomes the int 201) --
        # zero-pad back to 4 digits before applying the YYMM rule below.
        if isinstance(v, (int, float)) and not pd.isna(v):
            s = f"{int(v):04d}"
        else:
            s = str(v).strip()
        if len(s) == 4 and s.isdigit():
            yy, mm = int(s[:2]), int(s[2:])
            if not (1 <= mm <= 12):
                return pd.NaT
            year = 1900 + yy if yy >= 50 else 2000 + yy
            return pd.Timestamp(year=year, month=mm, day=1)
        try:
            return pd.Timestamp(pd.to_datetime(s)).replace(day=1)
        except Exception:
            return pd.NaT
    return series.apply(parse_one)


def _normalize_prod_code(series: pd.Series) -> pd.Series:
    """
    PROD_CODE should mean the same thing ("025" = Crude Oil) no matter
    whether a given vintage's file stored it as text "025", text "25",
    or a plain number 25 / 25.0. Excel silently turns zero-padded
    numeric-looking codes into real numbers, and if even one row in
    the column is blank, pandas then upcasts the WHOLE column to
    float64 -- which is exactly what turned "025" into "25.0" in the
    older archives and made every zfill(3) comparison fail (confirmed
    this session: reproduced the exact symptom the owner saw --
    an entire file coming back with zero matched crude rows -- with a
    synthetic float64 PROD_CODE column, and this fix resolves it).
    Coerces to numeric first and re-pads from the numeric value, so
    "025", "25", 25, and 25.0 all normalize to "025"; a value that
    truly isn't numeric at all falls back to a plain stripped string
    instead of being silently dropped.
    """
    numeric = pd.to_numeric(series, errors="coerce")
    as_text = series.astype(str).str.strip()
    normalized = numeric.apply(lambda v: f"{int(v):03d}" if pd.notna(v) else None)
    return normalized.where(normalized.notna(), as_text)


def _read_company_level_imports_file(path: str, sheet_name: str = "IMPORTS") -> pd.DataFrame | None:
    """
    Reads one manually downloaded Company Level Imports file (annual
    "...d.xls[x]" or a current-year monthly "import.xlsx") and returns
    just the columns this pipeline needs, column-NAME-indexed (not
    positional) so a schema/column-order change between vintages can't
    silently misalign data -- it is reported and the file skipped
    instead, per the project's "no silent substitutions" rule.
    """
    ext = os.path.splitext(path)[1].lower()
    engine = "xlrd" if ext == ".xls" else "openpyxl"
    try:
        xls = pd.ExcelFile(path, engine=engine)
    except Exception as e:
        print(f"    [SKIP] {os.path.basename(path)}: cannot open ({e})")
        return None
    sn = sheet_name if sheet_name in xls.sheet_names else xls.sheet_names[0]
    if sn != sheet_name:
        print(f"    [NOTE] {os.path.basename(path)}: sheet '{sheet_name}' not found, "
              f"using '{sn}' -- verify this vintage's layout by hand.")
    df = xls.parse(sn)
    missing = [c for c in _COMPANY_IMPORTS_REQUIRED_COLS if c not in df.columns]
    if missing:
        print(f"    [SKIP] {os.path.basename(path)}: missing required column(s) {missing} "
              f"-- found {list(df.columns)}")
        return None
    present_optional = [c for c in _COMPANY_IMPORTS_OPTIONAL_COLS if c in df.columns]
    missing_optional = [c for c in _COMPANY_IMPORTS_OPTIONAL_COLS if c not in df.columns]
    if missing_optional:
        print(f"    [NOTE] {os.path.basename(path)}: optional column(s) {missing_optional} not "
              f"present in this vintage -- the PROD_NAME/PROD_CODE cross-check will run on "
              f"PROD_NAME alone for this file (not a reason to skip it).")
    return df[_COMPANY_IMPORTS_REQUIRED_COLS + present_optional].copy()


def load_padd3_heavy_crude_imports(source_dir: str = RAW_MANUAL_PADD3_HEAVY,
                                    padd: int = None,
                                    bands: dict = None) -> pd.DataFrame | None:
    """
    Scans source_dir for Company Level Imports files (any *.xls* that
    pandas can open with the required columns present -- works both on
    ingested copies from USManualIngestor.ingest_directory(), prefixed
    "company_imports_...", and directly on EIA's own original
    filenames, e.g. "impa25d.xlsx" or "import.xlsx", so the owner does
    NOT have to run the ingest step first).

    For each file: filters to PROD_NAME=="Crude Oil" (the authoritative
    test -- this text was confirmed stable across every vintage seen
    this session, 1986-2026) AND PCOMP_PADD==padd (processing PADD --
    NOT the port-of-entry PADD; see the config note on why crude oil
    specifically uses this field). PROD_CODE is cross-checked against
    "025" for audit purposes ONLY and logged both directions when it
    disagrees -- it does NOT gate inclusion, because it is an internal
    EIA registry number that changed over time (confirmed this
    session: "20", sometimes "16" in 1986-89, before ~2016; "025"
    after) and using it as a hard AND-gate silently dropped every
    genuine pre-2016 crude-oil row.

    De-duplication across files: EIA's annual archives are explicitly
    "Including Final Revisions" (filenames end "...d.xlsx"/"...d.xls");
    the current year instead comes as separate monthly files. If the
    same (year, month) is covered by more than one file, the ANNUAL
    file wins as the more authoritative revision; among files of the
    same kind, the more recently modified one wins. Every override is
    printed, never applied silently.

    Returns a DataFrame indexed by month (Timestamp, month start) with
    columns: total, heavy, medium, light, heavy_pct, n_shipments,
    source_file (thousand barrels for total/heavy/medium/light). None
    if source_dir has no usable files.
    """
    padd = padd if padd is not None else PADD3_HEAVY_CRUDE_IMPORTS["padd_filter"]
    bands = bands if bands is not None else PADD3_HEAVY_CRUDE_IMPORTS["api_gravity_bands"]
    prod_filter = PADD3_HEAVY_CRUDE_IMPORTS["product_filter"]

    if not os.path.isdir(source_dir):
        return None
    paths = sorted(glob.glob(os.path.join(source_dir, "*.xls*")))
    if not paths:
        return None

    winners: dict[str, dict] = {}   # "YYYY-MM" -> {"file", "is_annual", "mtime", "rows"}
    total_mismatches = 0

    for path in paths:
        df = _read_company_level_imports_file(
            path, sheet_name=PADD3_HEAVY_CRUDE_IMPORTS.get("sheet_name", "IMPORTS"))
        if df is None or df.empty:
            continue

        fname = os.path.basename(path).lower()
        is_annual = fname.endswith("d.xlsx") or fname.endswith("d.xls")
        mtime = os.path.getmtime(path)

        name_ok = df["PROD_NAME"].astype(str).str.strip().str.upper().str.contains(
            prod_filter["PROD_NAME"].upper(), regex=False)
        # PROD_NAME is the authoritative crude-oil test, matched as a
        # SUBSTRING ("CRUDE OIL" in the text) rather than exact equality --
        # confirmed this session that the label itself varies by era: the
        # real 2001 archive uses "CRUDE OIL,FOREIGN", not the modern
        # files' plain "Crude Oil". Exact-equality would have silently
        # excluded every row in an era using a variant label. PROD_CODE
        # stays diagnostic-only (see below): confirmed separately that it
        # ALSO drifted ("20" pre-2016, "025" after), so it cannot gate
        # inclusion either.
        if "PROD_CODE" in df.columns:
            code_norm = _normalize_prod_code(df["PROD_CODE"])
            code_ok = code_norm == prod_filter["PROD_CODE"]
            n_mismatch_this_file = int((name_ok != code_ok).sum())
            total_mismatches += n_mismatch_this_file
            if n_mismatch_this_file:
                stray_codes = sorted(set(code_norm[name_ok & ~code_ok].unique()))
                stray_names = sorted(set(df.loc[code_ok & ~name_ok, "PROD_NAME"].astype(str).unique()))
                if stray_codes:
                    print(f"    [NOTE] {os.path.basename(path)}: rows matching 'CRUDE OIL' use "
                          f"PROD_CODE {stray_codes[:10]}{'...' if len(stray_codes) > 10 else ''} "
                          f"instead of 025 in this vintage -- kept (PROD_NAME governs), logged for audit.")
                if stray_names:
                    print(f"    [NOTE] {os.path.basename(path)}: rows coded 025 use PROD_NAME "
                          f"{stray_names[:10]}{'...' if len(stray_names) > 10 else ''} instead of "
                          f"a 'CRUDE OIL' variant in this vintage -- NOT counted as crude oil here; "
                          f"inspect by hand if these should be included.")
        padd_norm = _normalize_padd(df["PCOMP_PADD"])
        # PCOMP_PADD is normalized the same way as PROD_CODE: confirmed
        # this session that the real 2001 archive stores it as TEXT
        # ('3'), not a number -- `df["PCOMP_PADD"] == 3` matched zero
        # rows there even though 3,611 genuinely were PADD 3.
        crude = df[name_ok & (padd_norm == padd)].copy()
        if crude.empty:
            continue

        crude["month"] = _parse_rpt_period(crude["RPT_PERIOD"])
        bad_period = crude["month"].isna()
        if bad_period.any():
            print(f"    [NOTE] {os.path.basename(path)}: {int(bad_period.sum())} row(s) had an "
                  f"unparseable RPT_PERIOD value (e.g. an embedded duplicate header row, seen in "
                  f"the real 2001 archive as a literal 'RPT_PERIOD' text value) -- excluded.")
            crude = crude[~bad_period]
        if crude.empty:
            continue
        crude["band"] = crude["APIGRAVITY"].apply(lambda v: _band_for_api(v, bands))
        unclassified = int(crude["band"].isna().sum())
        if unclassified:
            print(f"    [NOTE] {os.path.basename(path)}: {unclassified} crude-oil/PADD{padd} "
                  f"row(s) had no usable APIGRAVITY -- excluded from the band split (still "
                  f"present in n_shipments, not silently dropped from the quantity total).")

        for month, g in crude.groupby("month"):
            mkey = pd.Timestamp(month).strftime("%Y-%m")
            candidate = {"file": path, "is_annual": is_annual, "mtime": mtime, "rows": g}
            existing = winners.get(mkey)
            if existing is None:
                winners[mkey] = candidate
            elif candidate["is_annual"] and not existing["is_annual"]:
                print(f"    [OVERRIDE] {mkey}: annual {os.path.basename(path)} supersedes "
                      f"monthly {os.path.basename(existing['file'])}")
                winners[mkey] = candidate
            elif existing["is_annual"] and not candidate["is_annual"]:
                pass  # keep the existing annual file, ignore the monthly duplicate
            elif candidate["mtime"] > existing["mtime"] and candidate["is_annual"] == existing["is_annual"]:
                print(f"    [OVERRIDE] {mkey}: {os.path.basename(path)} (newer) supersedes "
                      f"{os.path.basename(existing['file'])}")
                winners[mkey] = candidate

    if not winners:
        return None
    if total_mismatches:
        print(f"    [NOTE] {total_mismatches} row(s) across all files had a PROD_NAME/PROD_CODE "
              f"disagreement (see per-file notes above for which direction) -- these were NOT "
              f"excluded; PROD_NAME governs inclusion, PROD_CODE is logged for audit only.")

    records = []
    for mkey in sorted(winners):
        g = winners[mkey]["rows"]
        heavy  = g.loc[g["band"] == "HEAVY",  "QUANTITY"].sum()
        medium = g.loc[g["band"] == "MEDIUM", "QUANTITY"].sum()
        light  = g.loc[g["band"] == "LIGHT",  "QUANTITY"].sum()
        total  = g["QUANTITY"].sum()
        records.append({
            "month": pd.Timestamp(mkey), "total": total, "heavy": heavy,
            "medium": medium, "light": light,
            "heavy_pct": 100 * heavy / total if total else None,
            "n_shipments": len(g),
            "source_file": os.path.basename(winners[mkey]["file"]),
        })
    return pd.DataFrame.from_records(records).set_index("month").sort_index()


def cross_check_padd3_heavy_against_official(
        monthly_df: pd.DataFrame | None,
        official_all_countries: pd.Series | None) -> pd.DataFrame | None:
    """
    Optional quality gate, same spirit as cross_check_total_stocks
    above: if EIA's own "PADD3 Total (all countries)" series
    (MCRIPP32, PADD3_IMPORTS/ALL_COUNTRIES in the config, kbbl/day) has
    ALSO been downloaded via EIADownloader, compares its annual
    average against the annual average implied by this function's
    monthly 'total' column (thousand bbl/month -> kbbl/day). This is
    exactly the check that validated the 2025 sample file (1,390 vs.
    1,391 kbbl/d) -- reproduced here per-year so future years get the
    same scrutiny automatically instead of a one-off manual check.
    Returns a per-year comparison DataFrame, or None if either input
    is missing. The heavy/medium/light split is usable without this --
    it only tells you how much to trust it.
    """
    if monthly_df is None or official_all_countries is None:
        return None
    computed_annual = monthly_df["total"].groupby(monthly_df.index.year).sum()      # thousand bbl/year
    official_annual = official_all_countries.groupby(official_all_countries.index.year).mean()  # kbbl/day
    rows = []
    for year in sorted(set(computed_annual.index) & set(official_annual.index)):
        days = 366 if pd.Timestamp(year=year, month=12, day=31).is_leap_year else 365
        computed_kbbld = computed_annual[year] / days
        official_kbbld = official_annual[year]
        rows.append({
            "year": year, "computed_kbbl_d": computed_kbbld, "official_kbbl_d": official_kbbld,
            "diff_pct": 100 * (computed_kbbld - official_kbbld) / official_kbbld if official_kbbld else None,
        })
    return pd.DataFrame(rows)


# ============================================================
# MAIN
# ============================================================

REGIMES = [
    ("1986-2008", "1986-01", "2008-12"),
    ("2009-2014", "2009-01", "2014-12"),
    ("2015-2016", "2015-01", "2016-12"),
    ("2017-2019", "2017-01", "2019-12"),
    ("2020",      "2020-01", "2020-12"),
    ("2021-2026", "2021-01", "2026-12"),
]


def run(write_csv: bool = False, company_imports_dir: str = RAW_MANUAL_PADD3_HEAVY):
    print("\n" + "="*60)
    print("  US Oil Allocation Law Monitor - Processor")
    print("="*60)

    # ---- production layer ----
    _section("PRODUCTION LAYER — s_j(t), alpha_prod(t)")
    panel = load_production_panel()
    have = [k for k, v in panel.items() if v is not None]
    missing = [k for k, v in panel.items() if v is None]
    print(f"  Loaded: {len(have)}/{len(panel)} entities "
          f"({', '.join(have) if have else 'none'})")
    if missing:
        print(f"  MISSING (not yet downloaded): {', '.join(missing)}")

    s_j_df = compute_s_j(panel)
    if s_j_df is not None:
        print(f"\n  s_j(t), {s_j_df.attrs['period']}, "
              f"US_TOTAL = {s_j_df.attrs['us_total']:.2f} MBBL/D:")
        for _, row in s_j_df.iterrows():
            print(f"    {row['state']:<20s} {row['share_pct']:6.2f}%")
    else:
        print("  s_j(t): cannot compute -- US_TOTAL production not loaded.")

    us_total_series = panel.get("US_TOTAL")
    alpha_prod = compute_alpha_prod(us_total_series)
    if alpha_prod is not None:
        print(f"\n  alpha_prod(t): {len(alpha_prod)} monthly points, "
              f"{alpha_prod.index.min():%Y-%m} .. {alpha_prod.index.max():%Y-%m}")
        regime_table = annualized_alpha_by_regime(alpha_prod, REGIMES)
        print("\n  Regime table (validation against brief §16.3):")
        for _, row in regime_table.iterrows():
            val = f"{row['annualized_alpha']*100:+.2f}%" if row["annualized_alpha"] is not None else "n/a"
            print(f"    {row['regime']:<12s} {val}")
    else:
        print("  alpha_prod(t): cannot compute -- US_TOTAL production not loaded.")

    # ---- flow layer ----
    _section("FLOW LAYER — SPR / commercial stocks / imports / exports (brief v0.7 §17.3, §17.5)")
    flows = load_flow_layer()
    still_needed = []
    for key, s in flows.items():
        status = f"{len(s)} rows, {s.index.min():%Y-%m-%d}..{s.index.max():%Y-%m-%d}" if s is not None else "NOT DOWNLOADED"
        print(f"  {key:<24s} {status}")
        if s is None:
            still_needed.append(key)

    if still_needed:
        print(f"\n  --> Still needs downloading: {', '.join(still_needed)}")
        print(f"      Run: python us_oil_monitor_downloader.py --flows-only")
    else:
        print("\n  All flow-layer series present.")

    residual = cross_check_total_stocks(flows)
    if residual is not None:
        max_abs = residual.abs().max()
        print(f"\n  Cross-check SPR+Commercial vs Total: max |residual| = {max_abs:.1f} "
              f"thousand barrels {'(OK, rounding-level)' if max_abs < 5000 else '(FLAG — larger than expected)'}")

    deltas = compute_flow_deltas(flows)
    for key, s in deltas.items():
        if s is not None:
            print(f"\n  {key}: {len(s)} weekly points, "
                  f"mean={s.mean():+.1f}, std={s.std():.1f} (thousand barrels/week)")

    # ---- R_effective / alpha_eff ----
    _section("R_effective(t) and alpha_eff(t)  (brief v0.7 §17.5)")
    r_eff = compute_r_effective(us_total_series, flows)
    if r_eff is not None:
        print(f"  R_effective(t): {len(r_eff)} monthly points, "
              f"{r_eff.index.min():%Y-%m} .. {r_eff.index.max():%Y-%m}")
        alpha_eff = compute_alpha_eff(r_eff)
        if alpha_eff is not None:
            print(f"  alpha_eff(t):   {len(alpha_eff)} monthly points")
            comparison = pd.concat({"alpha_prod": alpha_prod, "alpha_eff": alpha_eff}, axis=1).dropna()
            if not comparison.empty:
                comparison["divergence"] = comparison["alpha_eff"] - comparison["alpha_prod"]
                print(f"\n  alpha_eff vs alpha_prod, {len(comparison)} overlapping months:")
                print(f"    mean divergence = {comparison['divergence'].mean()*100:+.3f} pts/month")
                print(f"    std  divergence = {comparison['divergence'].std()*100:.3f} pts/month")
    else:
        print("  R_effective(t) not yet computable — see FLOW LAYER section above for what's missing.")

    # ---- PADD3 heavy-crude import layer ----
    _section("PADD3 HEAVY-CRUDE IMPORT LAYER (Pillar 5, Session Handoff #6 item #1)")
    padd3_heavy = load_padd3_heavy_crude_imports(source_dir=company_imports_dir)
    if padd3_heavy is None:
        print(f"  No usable Company Level Imports files found in: {company_imports_dir}")
        print(f"  Download annual/monthly xlsx files from "
              f"https://www.eia.gov/petroleum/imports/companylevel/ into that folder "
              f"(or point --company-imports-dir elsewhere), or run "
              f"us_oil_monitor_downloader.py --ingest-padd3-heavy-dir <folder> first.")
    else:
        n_months = len(padd3_heavy)
        print(f"  {n_months} month(s) loaded, "
              f"{padd3_heavy.index.min():%Y-%m} .. {padd3_heavy.index.max():%Y-%m}")
        annual = padd3_heavy.groupby(padd3_heavy.index.year).agg(
            total=("total", "sum"), heavy=("heavy", "sum"))
        annual["heavy_pct"] = 100 * annual["heavy"] / annual["total"]
        print("\n  Annual heavy-crude share of PADD3 crude imports:")
        for year, row in annual.iterrows():
            print(f"    {year}   heavy = {row['heavy_pct']:5.1f}%   "
                  f"(total {row['total']:,.0f} kbbl/yr)")

        official_padd3_total = load_eia_series(
            _find_downloaded_file(RAW_EIA_TRADE, "padd3_imports_all_countries")
            or "")  # graceful no-op path if not present
        check = cross_check_padd3_heavy_against_official(padd3_heavy, official_padd3_total)
        if check is not None and not check.empty:
            print("\n  Cross-check vs. official MCRIPP32 (PADD3 all-countries) annual average:")
            for _, row in check.iterrows():
                print(f"    {int(row['year'])}   computed {row['computed_kbbl_d']:,.0f} kbbl/d   "
                      f"official {row['official_kbbl_d']:,.0f} kbbl/d   "
                      f"({row['diff_pct']:+.2f}%)")
        else:
            print("\n  (No official PADD3_IMPORTS/ALL_COUNTRIES series downloaded yet -- "
                  "skip cross-check. Not required for the heavy/medium/light split itself.)")

    # ---- tight-oil production layer (item #2) ----
    _section("TIGHT-OIL PRODUCTION LAYER (STEO Table 10b, Session Handoff #6 item #2)")
    tight_panel = load_tight_oil_panel()
    t_have = [k for k, v in tight_panel.items() if v is not None]
    t_missing = [k for k, v in tight_panel.items() if v is None]
    print(f"  Loaded: {len(t_have)}/{len(tight_panel)} entities "
          f"({', '.join(t_have) if t_have else 'none'})")
    if t_missing:
        print(f"  MISSING (not yet downloaded / not yet verified): {', '.join(t_missing)}")
        print(f"  Run: python us_oil_monitor_downloader.py --verify   (check which series IDs resolve)")
        print(f"       python us_oil_monitor_downloader.py --tight-oil-only")

    tight_total = tight_panel.get("TOTAL_US")
    comparison_table = compare_tight_oil_vs_padd3_heavy(tight_total, padd3_heavy)
    if comparison_table is not None:
        print("\n  Domestic tight oil vs. PADD3 heavy-crude imports, by year:")
        print(f"    {'Year':<6}{'Tight oil (M bbl/d)':<22}{'PADD3 heavy import (kbbl/d)':<30}{'Heavy %':<8}")
        for year, row in comparison_table.iterrows():
            print(f"    {year:<6}{row['tight_oil_mbbl_d']:<22.2f}"
                  f"{row['padd3_heavy_import_kbbl_d']:<30,.0f}{row['padd3_heavy_pct']:<8.1f}")
    else:
        print("\n  Comparison table not yet computable -- needs both TOTAL_US tight-oil "
              "production and the PADD3 heavy-crude import layer above.")

    # ---- CSV output ----
    if write_csv:
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        if alpha_prod is not None and us_total_series is not None:
            out = pd.concat({"R_prod": us_total_series, "alpha_prod": alpha_prod}, axis=1)
            out.to_csv(PROCESSED_CSV)
            print(f"\n  Wrote {PROCESSED_CSV}")
        if r_eff is not None:
            out2 = pd.concat({"R_effective": r_eff, "alpha_eff": compute_alpha_eff(r_eff)}, axis=1)
            for key, s in deltas.items():
                if s is not None:
                    out2 = out2.join(s.rename(key), how="outer")
            out2.to_csv(PROCESSED_FLOWS_CSV)
            print(f"  Wrote {PROCESSED_FLOWS_CSV}")
        if padd3_heavy is not None:
            padd3_heavy.to_csv(PROCESSED_PADD3_HEAVY_CSV)
            print(f"  Wrote {PROCESSED_PADD3_HEAVY_CSV}")
        if comparison_table is not None:
            comparison_table.to_csv(PROCESSED_TIGHT_VS_HEAVY_CSV)
            print(f"  Wrote {PROCESSED_TIGHT_VS_HEAVY_CSV}")

    print("\n" + "="*60)
    print("  Processor run complete.")
    print("="*60)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="US Oil Allocation Law Monitor - Processor")
    p.add_argument("--csv", action="store_true", help="Also write processed CSV outputs")
    p.add_argument("--company-imports-dir", metavar="FOLDER", default=RAW_MANUAL_PADD3_HEAVY,
                    help="Folder of manually downloaded EIA 'Company Level Imports' xlsx/xls "
                         "files (PADD3 heavy-crude layer, Pillar 5). Reads EIA's original "
                         f"filenames directly, no ingest step required. Default: {RAW_MANUAL_PADD3_HEAVY}")
    args = p.parse_args()
    run(write_csv=args.csv, company_imports_dir=args.company_imports_dir)
