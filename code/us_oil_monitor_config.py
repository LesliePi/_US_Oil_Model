# US Oil Allocation Law Monitor — Central Pipeline Configuration
# us_oil_monitor_config.py
# Version: v0.1  (2026-08-30)
# Author: László Tatai / BarefootRealism Labs (sibling of eu_monitor_* family)
# License: Apache License 2.0 WITH Commons Clause v1.0
# -*- coding: utf-8 -*-

"""
Central configuration for the US Oil Allocation Law Monitor.

Purpose
-------
Feeds REAL, audited EIA data into the Allocation Law master equation

    R_j(t+1) = (1 - alpha(t)) * R_total(t) * s_j(t) * eta_j(t) * sigma_j(t)

applied to the US crude oil market, entity j = producing state.

Mirrors the structure of eu_monitor_config.py:
  - same directory layout (data/raw, data/processed, data/audit)
  - same AUDIT_SCHEMA / SHA256 hash-on-ingest philosophy
  - same "skip if exists, idempotent" downloader contract

Data source
-----------
U.S. Energy Information Administration (EIA) Open Data API v2.
Free registration required: https://www.eia.gov/opendata/
Set the key as an environment variable before running:
    export EIA_API_KEY="your_key_here"        (Linux/macOS)
    set EIA_API_KEY=your_key_here              (Windows CMD)

IMPORTANT — verify before first real run
-----------------------------------------
The series IDs below follow EIA's documented naming convention
(MCRFP + 2-letter state postal code + "2" + .M = monthly field
production of crude oil, thousand barrels/day) and were spot-checked
against EIA's own pages for Texas (MCRFPTX2) and the US total
(MCRFPUS2). The remaining state codes follow the identical pattern
but were NOT individually spot-checked one by one — run
`us_oil_monitor_downloader.py --verify` first, which calls the EIA
/seriesid/ endpoint for every series below and reports any that
don't resolve, before pulling real data into the pipeline.
"""

import os

# ============================================================
# ROOT PATHS
# ============================================================

_HERE         = os.path.dirname(os.path.abspath(__file__))
ROOT          = _HERE

DATA_DIR      = os.path.join(ROOT, "data")
RAW_DIR       = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
AUDIT_DIR     = os.path.join(DATA_DIR, "audit")

RAW_EIA_PRODUCTION = os.path.join(RAW_DIR, "eia_crude_production")
RAW_EIA_PRICE      = os.path.join(RAW_DIR, "eia_wti_price")
RAW_EIA_STOCKS     = os.path.join(RAW_DIR, "eia_crude_stocks")     # SPR + commercial, brief v0.7 §17.3
RAW_EIA_TRADE      = os.path.join(RAW_DIR, "eia_crude_trade")      # imports/exports, brief v0.7 §17.5
RAW_MANUAL_RIGS    = os.path.join(RAW_DIR, "manual_rig_count")   # Baker Hughes, manual ingest

PROCESSED_CSV        = os.path.join(PROCESSED_DIR, "us_oil_allocation_law_monthly.csv")
PROCESSED_FLOWS_CSV  = os.path.join(PROCESSED_DIR, "us_oil_flow_layer_weekly.csv")  # SPR/commercial/import/export + R_effective, alpha_eff
PROCESSED_PADD3_HEAVY_CSV = os.path.join(PROCESSED_DIR, "padd3_heavy_crude_imports_monthly.csv")  # Pillar 5, session 4
PROCESSED_TIGHT_VS_HEAVY_CSV = os.path.join(PROCESSED_DIR, "tight_oil_vs_padd3_heavy_annual.csv")  # item #1/#2 comparison
AUDIT_LOG            = os.path.join(AUDIT_DIR, "audit_log.json")

# ============================================================
# GLOBAL BEHAVIOUR FLAGS
# ============================================================

DELETE_RAW   = False   # keep raw downloads for audit (recommended)
HTTP_TIMEOUT = 30
HTTP_SLEEP   = 0.3
HTTP_RETRIES = 3

EIA_API_BASE = "https://api.eia.gov/v2"

# ============================================================
# ENTITIES (j) — Allocation Law regions for the US oil market
# ============================================================
# Top producing states by 2024-2025 volume (~90%+ of US total),
# plus an implicit "Other" residual computed as US_total - sum(states)
# in the processor (never downloaded directly — it's a derived check).
#
# v1-compatible EIA series IDs, resolved via the /v2/seriesid/ endpoint
# (this avoids guessing v2 "duoarea" facet codes — EIA translates the
# classic PET.xxxxx.M identifiers automatically).

STATE_ENTITIES = {
    "US_TOTAL":     {"series_id": "PET.MCRFPUS2.M", "label": "U.S. Total (R_total)"},
    "TEXAS":        {"series_id": "PET.MCRFPTX2.M", "label": "Texas"},
    "NEW_MEXICO":   {"series_id": "PET.MCRFPNM2.M", "label": "New Mexico"},
    "NORTH_DAKOTA": {"series_id": "PET.MCRFPND2.M", "label": "North Dakota"},
    "ALASKA":       {"series_id": "PET.MCRFPAK2.M", "label": "Alaska"},
    "OKLAHOMA":     {"series_id": "PET.MCRFPOK2.M", "label": "Oklahoma"},
    "COLORADO":     {"series_id": "PET.MCRFPCO2.M", "label": "Colorado"},
    "CALIFORNIA":   {"series_id": "PET.MCRFPCA2.M", "label": "California"},
    "WYOMING":      {"series_id": "PET.MCRFPWY2.M", "label": "Wyoming"},
    "LOUISIANA":    {"series_id": "PET.MCRFPLA2.M", "label": "Louisiana"},
    "UTAH":         {"series_id": "PET.MCRFPUT2.M", "label": "Utah"},
}

CRUDE_PRODUCTION = {
    "dataset_id":    "petroleum.crude.production.state",
    "label":         "US Crude Oil Field Production by State (EIA-914)",
    "source":        "EIA",
    "unit":          "thousand barrels per day",
    "frequency":     "monthly",
    "history_start": "1981-01",   # EIA state-level series begin 1981
    "output_dir":    RAW_EIA_PRODUCTION,
    "file_prefix":   "crude_prod",
    "entities":      STATE_ENTITIES,
}

# ============================================================
# MARKET SIGNAL — WTI spot price (context, not an entity)
# ============================================================
# Used only as an exogenous covariate (e.g. to check whether alpha(t)
# or the implied eta*sigma multipliers correlate with price regime),
# NOT as part of the R_j allocation itself.

WTI_SPOT = {
    "dataset_id":    "petroleum.price.wti_spot",
    "label":         "Cushing, OK WTI Spot Price FOB",
    "source":        "EIA",
    "series_id":     "PET.RWTC.D",
    "unit":          "USD per barrel",
    "frequency":     "daily",
    "history_start": "1986-01-01",
    "output_dir":    RAW_EIA_PRICE,
    "file_prefix":   "wti_spot",
}

# ============================================================
# FLOW LAYER — SPR, commercial ("buffer") crude stocks, imports,
# exports. Brief v0.7 §17.3 / §17.5.
#
# Feeds:
#     R_effective(t) = R_prod(t) + R_import(t) + Delta_SPR(t) - R_export(t)
#
# Per owner decision (brief v0.7 §17.3), SPR and commercial stocks are
# tracked as SEPARATE series and only ever combined as deltas (flows),
# never as a single merged "buffer" level -- they move for structurally
# different reasons (policy-driven vs. market-driven). The processor
# (us_oil_monitor_processor.py) computes deltas; this config only
# defines where the raw LEVEL series come from.
#
# All four identifiers below were located and cross-verified against
# multiple independent secondary sources this session (brief v0.7
# §17.3, §17.5) but NOT YET independently spot-checked against a live
# EIA API call, unlike TX/US_TOTAL in CRUDE_PRODUCTION above. Treat as
# GOF (identifier) / not yet pulled, same status as WTI_SPOT was before
# Session 2 -- run --verify before a real pull.
# ============================================================

SPR_STOCKS = {
    "dataset_id":    "petroleum.stocks.spr",
    "label":         "US Strategic Petroleum Reserve — crude stock level",
    "source":        "EIA",
    "series_id":     "PET.WCSSTUS1.W",
    "unit":          "thousand barrels",
    "frequency":     "weekly",
    "history_start": "1982-01",   # weekly SPR series begins 1982 (monthly MCSSTUS1 goes back to 1977)
    "output_dir":    RAW_EIA_STOCKS,
    "file_prefix":   "spr_stocks",
}

COMMERCIAL_STOCKS = {
    "dataset_id":    "petroleum.stocks.commercial",
    "label":         "US commercial crude oil stocks (excl. SPR)",
    "source":        "EIA",
    "series_id":     "PET.WCESTUS1.W",
    "unit":          "thousand barrels",
    "frequency":     "weekly",
    "history_start": "1982-01",
    "output_dir":    RAW_EIA_STOCKS,
    "file_prefix":   "commercial_stocks",
}

TOTAL_STOCKS_INCL_SPR = {
    "dataset_id":    "petroleum.stocks.total",
    "label":         "US total crude oil stocks, incl. SPR",
    "source":        "EIA",
    "series_id":     "PET.WCRSTUS1.W",
    "unit":          "thousand barrels",
    "frequency":     "weekly",
    "history_start": "1982-01",
    "output_dir":    RAW_EIA_STOCKS,
    "file_prefix":   "total_stocks",
    # Cross-check only: SPR_STOCKS + COMMERCIAL_STOCKS should sum to this,
    # to within rounding -- the processor checks this and flags a mismatch.
}

CRUDE_IMPORTS = {
    "dataset_id":    "petroleum.trade.imports",
    "label":         "US weekly imports of crude oil",
    "source":        "EIA",
    "series_id":     "PET.WCRIMUS2.W",
    "unit":          "thousand barrels per day",
    "frequency":     "weekly",
    "history_start": "1991-01",   # weekly trade series begin ~1991
    "output_dir":    RAW_EIA_TRADE,
    "file_prefix":   "crude_imports",
}

CRUDE_EXPORTS = {
    "dataset_id":    "petroleum.trade.exports",
    "label":         "US weekly exports of crude oil (crude only, not products)",
    "source":        "EIA",
    "series_id":     "PET.WCREXUS2.W",
    "unit":          "thousand barrels per day",
    "frequency":     "weekly",
    "history_start": "1991-01",
    "output_dir":    RAW_EIA_TRADE,
    "file_prefix":   "crude_exports",
    # NOTE (brief v0.7 §17.5): do NOT substitute PET.WTTEXUS2.W here --
    # that series is crude + refined products combined and would break
    # the crude-only consistency of the R_effective identity.
}

FLOW_LAYER_SERIES = {
    "SPR_STOCKS":            SPR_STOCKS,
    "COMMERCIAL_STOCKS":     COMMERCIAL_STOCKS,
    "TOTAL_STOCKS_INCL_SPR": TOTAL_STOCKS_INCL_SPR,
    "CRUDE_IMPORTS":         CRUDE_IMPORTS,
    "CRUDE_EXPORTS":         CRUDE_EXPORTS,
}

# ============================================================
# PADD3 (GULF COAST) CRUDE IMPORTS BY COUNTRY OF ORIGIN
# Exergy-track, Pillar 5 (geopolitical/logistical vulnerability),
# session 3, 2026-09-01. Feeds the proposed sigma_j extension
# (Exergy-Model_strukturalis-integracio_dontes_v0_1.md): sigma_j is
# extended with an import-weighted external-supplier-stability term,
# weighted by each country's share of PADD3 crude imports.
#
# IMPORTANT -- verify before first real run (same caveat as
# STATE_ENTITIES above): series IDs below follow EIA's documented
# "MCRIPP3<country>2" naming convention for PADD3 (Gulf Coast),
# CRUDE OIL ONLY (product code EPC0, NOT EP00 which is crude+products
# combined -- see the CRUDE_EXPORTS note above for why this distinction
# matters for R_effective-style identities). Spot-checked this session
# against EIA's own page for "All Countries" (MCRIPP32) and Canada
# (MCRIPP3CA2); the remaining country codes follow the identical
# pattern but were NOT individually spot-checked -- run
# `us_oil_monitor_downloader.py --verify` first.
#
# NOTE: unlike national CRUDE_IMPORTS (weekly, WCRIMUS2), country-level
# PADD breakdown from EIA is only published at MONTHLY granularity --
# no weekly country-level series exists. This is an EIA publication
# constraint, not a config choice.
#
# Country selection: the top-2 suppliers (Canada, Mexico) plus the two
# entities Pillar 5's session-3 findings flagged as showing recent,
# sharp movements worth tracking (Venezuela import surge 2025-2026;
# Persian Gulf collapse over the same window) plus Saudi Arabia as the
# largest single Persian Gulf supplier. "Other" is a derived residual
# (ALL_COUNTRIES minus the sum of the named entities), computed in the
# processor, same convention as STATE_ENTITIES' implicit "Other".
# ============================================================

PADD3_IMPORT_ENTITIES = {
    "ALL_COUNTRIES":  {"series_id": "PET.MCRIPP32.M",   "label": "PADD3 Total (all countries)"},
    "CANADA":         {"series_id": "PET.MCRIPP3CA2.M", "label": "Canada"},
    "MEXICO":         {"series_id": "PET.MCRIPP3MX2.M", "label": "Mexico"},
    "VENEZUELA":      {"series_id": "PET.MCRIPP3VE2.M", "label": "Venezuela"},
    "SAUDI_ARABIA":   {"series_id": "PET.MCRIPP3SA2.M", "label": "Saudi Arabia"},
    "PERSIAN_GULF":   {"series_id": "PET.MCRIPP3PG2.M", "label": "Persian Gulf (aggregate)"},
    "COLOMBIA":       {"series_id": "PET.MCRIPP3CO2.M", "label": "Colombia"},
}

PADD3_IMPORTS = {
    "dataset_id":    "petroleum.trade.imports.padd3_by_country",
    "label":         "Gulf Coast (PADD 3) Crude Oil Imports by Country of Origin",
    "source":        "EIA",
    "unit":          "thousand barrels per day",
    "frequency":     "monthly",
    "history_start": "1981-01",   # matches national MCRIMUS2-family start; PADD3-specific coverage may be shorter per-country (many begin 1993 or 1995, see EIA page notes)
    "output_dir":    RAW_EIA_TRADE,
    "file_prefix":   "padd3_imports",
    "entities":      PADD3_IMPORT_ENTITIES,
    # NOTE: this gives country-of-origin composition at PADD3 level, but
    # NOT API-gravity/heavy-light banding at PADD3 level -- that remains
    # an open sourcing gap (Session Handoff #6, open item #1). The
    # national-level gravity bands (EIA Petroleum Marketing Monthly,
    # Table 25 / Form EIA-856) are NOT part of this downloader pipeline
    # (no clean EIA API series id found for it yet -- it's published as
    # a PDF table, not a queryable series) and were sourced manually
    # into Exergy-Model_Pillar5_geopolitikai-serulekenyseg_brief_v0_1.md
    # instead.
}

# ============================================================
# MANUAL INGEST — PADD3 crude imports by API-gravity band
# (Company Level Imports, Form EIA-814, "Monthly Imports Report")
# Exergy-track, Pillar 5, session 4 (Session Handoff #6, item #1).
# ============================================================
# EIA does not publish a queryable API series for PADD-level
# API-gravity-banded crude imports -- see the note at the end of
# PADD3_IMPORTS above (national Table 25 is a PDF, not a series; no
# PADD-level equivalent exists as a series at all). The gap IS closed
# by a different, real EIA source: "Company Level Imports"
# (eia.gov/petroleum/imports/companylevel/), record-level (per
# shipment) data collected on Form EIA-814. Fields include PCOMP_PADD,
# APIGRAVITY, SULFUR, QUANTITY -- exactly what's needed. Published as
# one XLSX/XLS per year ("Including Final Revisions", 1986-2025+) plus
# one XLSX per month for the current year. NO bulk API -- must be
# downloaded by hand from the page above and pointed at by this
# config; there is nothing for EIADownloader to fetch here.
#
# VALIDATED this session (2025 annual file, impa25d.xlsx): filtering
# PROD_NAME=="Crude Oil" AND PCOMP_PADD==3, summing QUANTITY monthly
# and converting the annual total to a barrels/day average reproduces
# EIA's own published PADD3 annual aggregate (MCRIPP32) almost exactly
# -- 1,390 kbbl/d computed vs. 1,391 kbbl/d published, 0.07% off,
# rounding-level. This is the same quality gate as the US-track's
# TX/NM share cross-check. It also settles, empirically, that
# PCOMP_PADD (processing PADD) -- NOT PORT_PADD (port-of-entry PADD)
# -- is the correct field for crude oil, matching EIA's own published
# methodology note ("crude oil ... reported by the PAD District in
# which they are processed").
#
# Heavy/Medium/Light convention [GOF, EIA TodayInEnergy, 2015-02-10,
# "EIA tracking tool shows light-sweet crude oil imports to Gulf Coast
# virtually eliminated"]:
#   Heavy:  API <= 27
#   Medium: 27 < API < 35
#   Light:  API >= 35

RAW_MANUAL_PADD3_HEAVY = os.path.join(RAW_DIR, "manual_padd3_company_imports")

PADD3_API_GRAVITY_BANDS = {
    # (low, high) in degrees API; None = unbounded on that side.
    # Bucketing rule applied by the processor: low < API <= high for
    # HEAVY's upper edge and MEDIUM's edges; LIGHT is API >= 35 (i.e.
    # the 35.0 boundary itself counts as LIGHT, matching the EIA note's
    # own "greater than or equal to 35" phrasing for light crude).
    "HEAVY":  (None, 27.0),
    "MEDIUM": (27.0, 35.0),
    "LIGHT":  (35.0, None),
}

PADD3_HEAVY_CRUDE_IMPORTS = {
    "dataset_id":    "petroleum.trade.imports.padd3_by_api_gravity",
    "label":         "PADD3 (Gulf Coast) Crude Oil Imports by API-Gravity Band (Company Level Imports, EIA-814)",
    "source":        "EIA",
    "unit":          "thousand barrels (raw, per shipment); aggregated monthly",
    "frequency":     "monthly",
    "history_start": "1986-01",  # Company Level Imports archive start; Pillar 5's own target range is 2008-2026
    "fetch_mode":    "manual_xlsx",
    "output_dir":    RAW_MANUAL_PADD3_HEAVY,
    "file_prefix":   "company_imports",
    "sheet_name":    "IMPORTS",
    "padd_filter":   3,             # PCOMP_PADD, not PORT_PADD -- see validation note above
    "product_filter": {"PROD_NAME": "Crude Oil", "PROD_CODE": "025"},  # both checked when PROD_CODE is present; PROD_NAME alone otherwise -- see required_columns/optional_columns below
    # SINGLE SOURCE OF TRUTH for both us_oil_monitor_downloader.py's
    # --ingest-padd3-heavy-dir validation AND
    # us_oil_monitor_processor.py's file reader. Session 4 bug (found by
    # owner): these were two independently hardcoded column lists that
    # drifted apart -- the downloader's ingest check didn't require
    # PROD_CODE, the processor's reader did, so pre-2016 .xls files
    # (which may lack a PROD_CODE column, or use a different name for
    # it) passed ingest but were then silently skipped by the
    # processor. Fixed by having both read from here, and by making
    # PROD_CODE specifically OPTIONAL (see optional_columns) rather
    # than required -- its absence degrades the crude-oil filter to
    # PROD_NAME-only (reported per file when it happens), it does not
    # drop the whole file.
    "required_columns": ["RPT_PERIOD", "PROD_NAME", "PCOMP_PADD", "QUANTITY", "APIGRAVITY"],
    "optional_columns": ["PROD_CODE"],
    "api_gravity_bands": PADD3_API_GRAVITY_BANDS,
    "manual_note": (
        "No public API for this breakdown. Download annual archive files "
        "(2008-2025, 'Including Final Revisions') and current-year monthly "
        "files from https://www.eia.gov/petroleum/imports/companylevel/ "
        "-- e.g. archive/2025/data/impa25d.xlsx (annual) or "
        "archive/2026/2026_06/data/import.xlsx (monthly) -- into a local "
        "folder, then either: (a) point "
        "us_oil_monitor_processor.py --company-imports-dir at that folder "
        "directly (reads files in place, no copy/hash step), or (b) run "
        "us_oil_monitor_downloader.py --ingest-padd3-heavy-dir <folder> "
        "first to copy+SHA256+audit-log each file into "
        f"{RAW_MANUAL_PADD3_HEAVY} the way rig-count ingest works, "
        "then run the processor with no extra flag (it reads that "
        "directory by default)."
    ),
}

# ============================================================
# TIGHT-OIL PRODUCTION (STEO Table 10b) — Session Handoff #6 item #2
# ============================================================
# The counterpart series to PADD3_HEAVY_CRUDE_IMPORTS above: this is
# the domestic side of the "heavy-crude import vs. domestic tight-oil
# production" comparison (Pillar 5's original framing).
#
# Deliberately NOT the same thing as CRUDE_PRODUCTION/STATE_ENTITIES
# above (PET.MCRFPUS2.M) -- that is TOTAL US field production
# (conventional + tight combined, all API-gravity grades, including
# some genuinely heavy domestic crude e.g. California). Using it as a
# stand-in for "tight oil production" would blur exactly the
# light-domestic-vs-heavy-import contrast Pillar 5 is about, so it is
# NOT substituted here even though tight oil dominates total US
# production growth since ~2010.
#
# Source: EIA Short-Term Energy Outlook (STEO), Table 10b, "Crude Oil
# and Natural Gas Production from Shale and Tight Formations" --
# broken out BY GEOLOGIC FORMATION, which EIA explicitly distinguishes
# from the geographic PADD/region breakdown in STEO Tables 4a/5a (the
# two "lead to differences... surface-level activity does not
# distinguish between formations, which can overlap each other like
# layers of a cake" -- EIA TodayInEnergy, 2026-03-17). Table 10b is
# also the correct successor to the old Drilling Productivity Report
# (DPR), which EIA folded into STEO in June 2024 and no longer
# publishes standalone -- so this single source replaces DPR too.
#
# VALIDATED this session: TOPRL48 (total) and TOPRPM (Permian) are
# real, currently-active EIA internal series mnemonics (confirmed via
# EIA's own STEO data-correction notices referencing them by name).
# Classic-style v1-compatible IDs follow the same "STEO.<mnemonic>.M"
# pattern already proven for CRUDE_PRODUCTION's "PET.<mnemonic>.M"
# IDs, so EIADownloader's existing /seriesid/ route needs NO code
# changes -- this is just a new dataset entry.
#
# NOT verified -- per-formation candidate IDs below follow the visible
# "TOPR"+abbreviation pattern but were NOT found in any EIA source
# text this session (unlike TOPRL48/TOPRPM, which were). Run
# `us_oil_monitor_downloader.py --verify` before trusting any of
# these; a wrong guess fails cleanly (EIA's API returns no data for a
# non-existent ID, same as any other unverified entry in this file),
# it does not silently return the wrong series.

TIGHT_OIL_ENTITIES = {
    "TOTAL_US":    {"series_id": "STEO.TOPRL48.M", "label": "Total U.S. tight oil production"},          # GOF -- confirmed real mnemonic
    "PERMIAN":     {"series_id": "STEO.TOPRPM.M",  "label": "Permian formation tight oil production"},   # GOF -- confirmed real mnemonic
    "BAKKEN":      {"series_id": "STEO.TOPRBAK.M", "label": "Bakken formation tight oil production"},     # UNVERIFIED -- run --verify
    "EAGLE_FORD":  {"series_id": "STEO.TOPREF.M",  "label": "Eagle Ford formation tight oil production"}, # UNVERIFIED -- run --verify
    "NIOBRARA":    {"series_id": "STEO.TOPRNIO.M", "label": "Niobrara formation tight oil production"},   # UNVERIFIED -- run --verify
    "ANADARKO":    {"series_id": "STEO.TOPRANA.M", "label": "Anadarko formation tight oil production"},   # UNVERIFIED -- run --verify
    "AUSTIN_CHALK":{"series_id": "STEO.TOPRAC.M",  "label": "Austin Chalk formation tight oil production"}, # UNVERIFIED -- run --verify
}

TIGHT_OIL_PRODUCTION = {
    "dataset_id":    "steo.production.tight_oil_by_formation",
    "label":         "U.S. Tight Oil Production by Formation (STEO Table 10b)",
    "source":        "EIA",
    "unit":          "million barrels per day",
    "frequency":     "monthly",
    "history_start": "2000-01",  # STEO Table 10b's own stated coverage; NOT independently verified this session -- check actual first data point on first real pull
    "output_dir":    RAW_EIA_PRODUCTION,   # same physical layer as CRUDE_PRODUCTION -- both are "production", just different scope
    "file_prefix":   "tight_oil_prod",
    "entities":      TIGHT_OIL_ENTITIES,
}

# ============================================================
# MANUAL INGEST — Rig count (proxy for eta_j, extraction efficiency)
# ============================================================
# Baker Hughes weekly rig count has no free public API (same situation
# as Baltic Dry Index in eu_monitor). Ingest pattern mirrors
# BalticDryIngestor in eu_monitor_downloaders.py: validate -> copy ->
# SHA256 -> audit entry. Source: https://rigcount.bakerhughes.com
# (download the "North America Rig Count" state-level XLSX/CSV export).

RIG_COUNT = {
    "dataset_id":  "industry.rig_count.state",
    "label":       "Baker Hughes North America Rig Count (by state)",
    "source":      "Baker Hughes",
    "frequency":   "weekly",
    "unit":        "active rigs",
    "fetch_mode":  "manual_csv",
    "output_dir":  RAW_MANUAL_RIGS,
    "file_prefix": "rig_count",
    "manual_note": (
        "Rig count has no free API. Download the state-level export from "
        "https://rigcount.bakerhughes.com and ingest with "
        "USManualIngestor().ingest('path/to/file.csv', dataset=RIG_COUNT)."
    ),
}

# ============================================================
# AUDIT RECORD SCHEMA  (identical shape to eu_monitor's)
# ============================================================

AUDIT_SCHEMA = {
    "dataset_id":   None,
    "source":       None,
    "source_url":   None,
    "retrieved_at": None,
    "period_start": None,
    "period_end":   None,
    "local_path":   None,
    "raw_hash":     None,
    "row_count":    None,
    "unit":         None,
    "notes":        "",
}
