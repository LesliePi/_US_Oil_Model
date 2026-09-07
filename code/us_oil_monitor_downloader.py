# US Oil Allocation Law Monitor — Unified Downloader
# us_oil_monitor_downloader.py
# Version: v0.1  (2026-08-30)
# Author: László Tatai / BarefootRealism Labs (sibling of eu_monitor_* family)
# License: Apache License 2.0 WITH Commons Clause v1.0
# -*- coding: utf-8 -*-

"""
Downloads real EIA data for the US Oil Allocation Law test.

  1. EIADownloader        - crude oil production by state, WTI spot,
                             and the v0.7 flow layer (SPR / commercial
                             stocks / imports / exports) -- all via the
                             EIA v2 API /seriesid/ v1-compatibility route
  2. USManualIngestor      - rig count (Baker Hughes, no free API;
                             same manual-ingest pattern as eu_monitor's
                             BalticDryIngestor), and (session 4) PADD3
                             heavy-crude imports (EIA "Company Level
                             Imports" / Form EIA-814 -- no bulk API,
                             one xlsx/xls per year or month, ingested
                             in bulk via ingest_directory())

Design mirrors eu_monitor_downloaders.py on purpose: skip-if-exists,
SHA256 hash per file, JSON-lines audit log, retry with backoff.
This file is self-contained (does not import eu_monitor_config) so it
can be dropped in and run independently.

Flow layer (v0.7, brief §17.3/§17.5): SPR stock level, commercial
stock level, total stock incl. SPR (cross-check only), crude imports,
crude exports -- all weekly. Feeds R_effective(t) = R_prod(t) +
R_import(t) + Delta_SPR(t) - R_export(t) and alpha_eff(t) in
us_oil_monitor_processor.py. SPR and commercial stocks are downloaded
as separate series and must stay separate -- see config comments.

EIA API key:
  export EIA_API_KEY="your_key_here"     (free registration required:
  https://www.eia.gov/opendata/)

Usage:
    python us_oil_monitor_downloader.py --verify        # check all series IDs resolve (incl. flow layer), no full pull
    python us_oil_monitor_downloader.py                 # download production + WTI price + flow layer
    python us_oil_monitor_downloader.py --no-flows       # old v0.6 behaviour: production + WTI price only
    python us_oil_monitor_downloader.py --production-only
    python us_oil_monitor_downloader.py --flows-only     # SPR/commercial/imports/exports only
    python us_oil_monitor_downloader.py --ingest-rigs path/to/rig_count.csv
    python us_oil_monitor_downloader.py --ingest-padd3-heavy-dir path/to/downloaded_eia_files/
"""

import os
import sys
import json
import time
import hashlib
import argparse
import datetime
import requests

from us_oil_monitor_config import (
    CRUDE_PRODUCTION, WTI_SPOT, RIG_COUNT,
    SPR_STOCKS, COMMERCIAL_STOCKS, TOTAL_STOCKS_INCL_SPR,
    CRUDE_IMPORTS, CRUDE_EXPORTS, FLOW_LAYER_SERIES,
    PADD3_HEAVY_CRUDE_IMPORTS, TIGHT_OIL_PRODUCTION,
    EIA_API_BASE, HTTP_TIMEOUT, HTTP_SLEEP, HTTP_RETRIES,
    AUDIT_DIR, AUDIT_LOG,
    RAW_EIA_PRODUCTION, RAW_EIA_PRICE, RAW_EIA_STOCKS, RAW_EIA_TRADE,
    RAW_MANUAL_RIGS, RAW_MANUAL_PADD3_HEAVY,
    AUDIT_SCHEMA,
)

for _d in [AUDIT_DIR, RAW_EIA_PRODUCTION, RAW_EIA_PRICE, RAW_EIA_STOCKS,
           RAW_EIA_TRADE, RAW_MANUAL_RIGS, RAW_MANUAL_PADD3_HEAVY]:
    os.makedirs(_d, exist_ok=True)

# Load .env if present (same convenience as eu_monitor_downloaders.py)
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_env_path):
    with open(_env_path) as _ef:
        for _line in _ef:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())


# ============================================================
# SHARED UTILITIES  (identical contract to eu_monitor_downloaders.py)
# ============================================================

def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _section(title: str):
    print(f"\n{'='*60}\n  {title}\n{'='*60}")


def _write_audit(entry: dict):
    os.makedirs(AUDIT_DIR, exist_ok=True)
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _make_audit_entry(**kwargs) -> dict:
    entry = dict(AUDIT_SCHEMA)
    entry.update(kwargs)
    return entry


def _save_json(data, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _request_with_retry(url, params=None, retries=HTTP_RETRIES,
                         timeout=HTTP_TIMEOUT, sleep_s=HTTP_SLEEP):
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params or {}, timeout=timeout)
            r.raise_for_status()
            time.sleep(sleep_s)
            return r
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "?"
            print(f"    [HTTP {status}] {url}  (attempt {attempt+1}/{retries})")
            if status == 429:
                print("    Rate limited. Waiting 60s ...")
                time.sleep(60)
            elif attempt < retries - 1:
                time.sleep(5 * (attempt + 1))
        except Exception as e:
            print(f"    [ERROR] {url}: {e}  (attempt {attempt+1}/{retries})")
            if attempt < retries - 1:
                time.sleep(5 * (attempt + 1))
    print(f"    [FAILED] {url} - all {retries} attempts exhausted")
    return None


# ============================================================
# EIA DOWNLOADER
# ============================================================

class EIADownloader:
    """
    Downloads one or more EIA series via the v2 /seriesid/ route, which
    accepts classic v1-style series IDs (e.g. "PET.MCRFPTX2.M") directly
    -- no need to guess v2 facet codes (duoarea, product, etc.).

    API docs: https://www.eia.gov/opendata/documentation.php
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("EIA_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "EIA API key not found. Set the EIA_API_KEY environment "
                "variable.\nRegister free at https://www.eia.gov/opendata/"
            )

    # --------------------------------------------------------
    def fetch_series(self, series_id: str) -> dict | None:
        """Fetch one full series. Returns the raw EIA JSON response body."""
        url = f"{EIA_API_BASE}/seriesid/{series_id}"
        r = _request_with_retry(url, params={"api_key": self.api_key})
        if r is None:
            return None
        return r.json()

    # --------------------------------------------------------
    def verify(self, series_map: dict):
        """
        Resolve every series ID in series_map without saving anything.
        Prints row count + date range, or a clear FAILED marker, per entry.
        Use this BEFORE a real pull to catch any wrong/renamed series ID.
        """
        _section("VERIFY MODE — resolving series IDs only, nothing saved")
        results = {}
        for key, meta in series_map.items():
            sid = meta["series_id"] if "series_id" in meta else meta
            label = meta.get("label", key) if isinstance(meta, dict) else key
            print(f"  [{key}] {label} -> {sid}")
            body = self.fetch_series(sid)
            if body is None or "response" not in body or not body["response"].get("data"):
                print(f"    ✗ FAILED — series did not resolve, check the ID")
                results[key] = False
                continue
            rows = body["response"]["data"]
            periods = sorted(row["period"] for row in rows)
            print(f"    ✓ OK — {len(rows)} rows, {periods[0]} .. {periods[-1]}")
            results[key] = True
        n_ok = sum(results.values())
        print(f"\n  {n_ok}/{len(results)} series resolved correctly.")
        return results

    # --------------------------------------------------------
    def download_dataset(self, dataset_cfg: dict, entities: dict = None):
        """
        Download every series in `entities` (or dataset_cfg['entities'] if
        entities not given) and save one raw JSON per entity, with a full
        audit trail. Skips a series if its output file already exists
        (idempotent — safe to re-run).
        """
        label = dataset_cfg["label"]
        _section(label)

        ents = entities or dataset_cfg.get("entities")
        if ents is None:
            # single-series dataset (e.g. WTI_SPOT)
            ents = {dataset_cfg["dataset_id"]: {
                "series_id": dataset_cfg["series_id"], "label": label}}

        out_dir = dataset_cfg["output_dir"]
        os.makedirs(out_dir, exist_ok=True)

        for key, meta in ents.items():
            sid = meta["series_id"]
            fname = f"{dataset_cfg['file_prefix']}_{key.lower()}.json"
            path = os.path.join(out_dir, fname)

            if os.path.exists(path) and os.path.getsize(path) > 0:
                print(f"  [SKIP] {key} ({sid}) — already downloaded -> {fname}")
                continue

            print(f"  [FETCH] {key} ({sid}) ...")
            retrieved_at = _utc_now()
            body = self.fetch_series(sid)
            if body is None or "response" not in body or not body["response"].get("data"):
                print(f"    ✗ FAILED — {key} did not resolve, skipping")
                continue

            rows = body["response"]["data"]
            periods = sorted(row["period"] for row in rows)
            _save_json(body, path)
            file_hash = _sha256(path)

            print(f"    ✓ SAVED {fname}  ({len(rows)} rows, "
                  f"{periods[0]}..{periods[-1]})")

            _write_audit(_make_audit_entry(
                dataset_id   = f"{dataset_cfg['dataset_id']}.{key.lower()}",
                source       = dataset_cfg["source"],
                source_url   = f"{EIA_API_BASE}/seriesid/{sid}",
                retrieved_at = retrieved_at,
                period_start = periods[0],
                period_end   = periods[-1],
                local_path   = path,
                raw_hash     = file_hash,
                row_count    = len(rows),
                unit         = dataset_cfg["unit"],
                notes        = f"series_id={sid}",
            ))

        print(f"\n[{label}] Complete.")


# ============================================================
# MANUAL INGEST — Rig count (no free API, same pattern as
# eu_monitor's BalticDryIngestor)
# ============================================================

class USManualIngestor:
    """
    Ingests a manually downloaded CSV (e.g. Baker Hughes rig count).
    Validates -> copies with a timestamped name -> SHA256 -> audit entry.
    Does NOT download from the internet.
    """

    def __init__(self):
        pass

    def _validate_csv(self, path: str, required_columns: set) -> tuple[bool, str, int]:
        try:
            import csv
            with open(path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                headers = set(reader.fieldnames or [])
                missing = required_columns - headers
                if missing:
                    return False, f"Missing columns: {missing}", 0
                rows = list(reader)
                if not rows:
                    return False, "CSV has no data rows", 0
                return True, "OK", len(rows)
        except Exception as e:
            return False, str(e), 0

    def _validate_xlsx(self, path: str, required_columns: set, sheet_name: str = None) -> tuple[bool, str, int]:
        """
        Same contract as _validate_csv but for xlsx/xls. Uses pandas so
        legacy .xls (xlrd engine) and modern .xlsx (openpyxl engine) are
        both handled by extension, per the project's file-reading
        convention. Row count is len(df), i.e. data rows excluding the
        header -- consistent with _validate_csv's DictReader-based count.
        """
        try:
            import pandas as pd
            ext = os.path.splitext(path)[1].lower()
            engine = "xlrd" if ext == ".xls" else "openpyxl"
            xls = pd.ExcelFile(path, engine=engine)
            sn = sheet_name if sheet_name in xls.sheet_names else xls.sheet_names[0]
            if sheet_name and sn != sheet_name:
                print(f"    [NOTE] sheet '{sheet_name}' not found in {os.path.basename(path)}, "
                      f"using first sheet '{sn}' instead — check this vintage's schema by hand.")
            df = xls.parse(sn)
            headers = set(df.columns)
            missing = required_columns - headers
            if missing:
                return False, f"Missing columns: {missing} (found: {sorted(headers)})", 0
            if df.empty:
                return False, "Sheet has no data rows", 0
            return True, "OK", len(df)
        except Exception as e:
            return False, str(e), 0

    def ingest(self, source_path: str, dataset: dict,
               required_columns=("Date",), notes: str = ""):
        _section(f"MANUAL INGEST — {dataset['label']}")

        if not os.path.exists(source_path):
            print(f"  [ERROR] File not found: {source_path}")
            return

        ext = os.path.splitext(source_path)[1].lower()
        if ext in (".xlsx", ".xls", ".xlsm"):
            ok, msg, row_count = self._validate_xlsx(
                source_path, set(required_columns), sheet_name=dataset.get("sheet_name"))
        else:
            ok, msg, row_count = self._validate_csv(source_path, set(required_columns))
        if not ok:
            print(f"  [INVALID] {msg}")
            return
        print(f"  [OK] {row_count} data rows, columns validated")

        out_dir = dataset["output_dir"]
        os.makedirs(out_dir, exist_ok=True)
        retrieved_at = _utc_now()
        timestamp = retrieved_at.replace(":", "").replace("-", "")[:15]
        # Keep the original filename stem (e.g. "impa25d" or "2026_06_import")
        # ahead of the timestamp -- for a 17-file batch this is the only
        # thing that lets a human tell the ingested copies apart later;
        # the timestamp alone (as the rig-count single-file case uses)
        # would make all of them look identical.
        stem = os.path.splitext(os.path.basename(source_path))[0]
        dest_fname = f"{dataset['file_prefix']}_{stem}_{timestamp}{ext}"
        dest_path = os.path.join(out_dir, dest_fname)

        import shutil
        shutil.copy2(source_path, dest_path)
        file_hash = _sha256(dest_path)
        print(f"  [SAVED]  {dest_fname}\n  SHA256:  {file_hash}")

        full_notes = dataset.get("manual_note", "")
        if notes:
            full_notes = f"{full_notes} | {notes}" if full_notes else notes

        _write_audit(_make_audit_entry(
            dataset_id   = dataset["dataset_id"],
            source       = dataset["source"],
            source_url   = "manual_download",
            retrieved_at = retrieved_at,
            local_path   = dest_path,
            raw_hash     = file_hash,
            row_count    = row_count,
            unit         = dataset["unit"],
            notes        = full_notes,
        ))
        print("\n  Ingest complete. Audit entry written.")

    def ingest_directory(self, source_dir: str, dataset: dict,
                          required_columns=("RPT_PERIOD",), pattern: str = "*.xls*"):
        """
        Bulk version of ingest() for a whole folder of files at once --
        built for the PADD3 heavy-crude case, where the owner downloads
        17+ annual/monthly Company Level Imports files by hand and does
        not want to call ingest() once per file. Each matching file goes
        through the exact same validate -> copy -> SHA256 -> audit-entry
        path as a single ingest() call; failures on one file are printed
        and skipped, not fatal to the batch.
        """
        import glob
        _section(f"BULK MANUAL INGEST — {dataset['label']}")
        if not os.path.isdir(source_dir):
            print(f"  [ERROR] Not a directory: {source_dir}")
            return
        paths = sorted(glob.glob(os.path.join(source_dir, pattern)))
        if not paths:
            print(f"  [ERROR] No files matching '{pattern}' in {source_dir}")
            return
        print(f"  Found {len(paths)} candidate file(s).")
        ok_count = 0
        for p in paths:
            self.ingest(p, dataset=dataset, required_columns=required_columns)
            ok_count += 1
        print(f"\n  Bulk ingest pass complete: {ok_count}/{len(paths)} files attempted "
              f"(see per-file [OK]/[INVALID] lines above for the actual outcome of each).")


# ============================================================
# MASTER RUNNER
# ============================================================

def run_flow_layer_downloads(api_key: str = None):
    """
    Downloads the SPR / commercial stocks / imports / exports series
    (brief v0.7 §17.3, §17.5) needed to compute R_effective(t) and
    alpha_eff(t). Each is a single-series dataset, same shape as
    WTI_SPOT, so download_dataset() handles them without changes.

    IMPORTANT: entities is passed explicitly, keyed by the
    FLOW_LAYER_SERIES dict key (e.g. "SPR_STOCKS"), NOT left to
    download_dataset()'s single-series fallback. The fallback builds
    the filename from dataset_cfg["dataset_id"] (e.g.
    "petroleum.stocks.spr"), which does not match what
    us_oil_monitor_processor.py looks for and silently produces an
    unfindable file. Bug found and fixed 2026-08-30 after a real run
    reproduced exactly this symptom (files downloaded, processor
    reported them as missing).
    """
    _section("FLOW LAYER — SPR, commercial stocks, imports, exports")
    dl = EIADownloader(api_key=api_key)
    for key, cfg in FLOW_LAYER_SERIES.items():
        dl.download_dataset(cfg, entities={key: {"series_id": cfg["series_id"],
                                                    "label": cfg["label"]}})


def run_all_downloads(production: bool = True, price: bool = True,
                       flows: bool = True, api_key: str = None):
    print("\n" + "="*60)
    print("  US Oil Allocation Law Monitor - Unified Download")
    print(f"  {_utc_now()}")
    print("="*60)

    dl = EIADownloader(api_key=api_key)

    if production:
        dl.download_dataset(CRUDE_PRODUCTION)
    if price:
        dl.download_dataset(WTI_SPOT)
    if flows:
        run_flow_layer_downloads(api_key=api_key)

    print("\n" + "="*60)
    print("  All downloads complete.")
    print(f"  Audit log: {AUDIT_LOG}")
    print("="*60)


def _parse_args():
    p = argparse.ArgumentParser(description="US Oil Allocation Law Monitor - Downloader")
    p.add_argument("--verify", action="store_true",
                    help="Resolve all configured series IDs, save nothing")
    p.add_argument("--production-only", action="store_true",
                    help="Download crude production only, skip WTI price and flow layer")
    p.add_argument("--price-only", action="store_true",
                    help="Download WTI price only, skip production and flow layer")
    p.add_argument("--flows-only", action="store_true",
                    help="Download SPR/commercial stocks + imports/exports only "
                         "(brief v0.7 flow layer), skip production and WTI price")
    p.add_argument("--tight-oil-only", action="store_true",
                    help="Download STEO Table 10b tight-oil-by-formation series only "
                         "(Session Handoff #6 item #2). Run --verify first -- most of "
                         "these series IDs are unconfirmed guesses, see config comments.")
    p.add_argument("--no-flows", action="store_true",
                    help="Skip the flow layer on a full run "
                         "(production + WTI price only, old v0.6 behaviour)")
    p.add_argument("--ingest-rigs", metavar="CSV_PATH",
                    help="Ingest a manually downloaded Baker Hughes rig count CSV")
    p.add_argument("--ingest-padd3-heavy-dir", metavar="FOLDER",
                    help="Bulk-ingest a folder of manually downloaded EIA 'Company Level "
                         "Imports' xlsx/xls files (annual archives and/or current-year "
                         "monthly files) — copies each into "
                         f"{RAW_MANUAL_PADD3_HEAVY} with SHA256 + audit entry, "
                         "same as --ingest-rigs but for the whole folder at once. "
                         "Optional — us_oil_monitor_processor.py --company-imports-dir "
                         "can also read the folder directly without this step.")
    p.add_argument("--api-key", metavar="KEY",
                    help="EIA API key (overrides EIA_API_KEY env var)")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()

    if args.ingest_rigs:
        USManualIngestor().ingest(
            args.ingest_rigs, dataset=RIG_COUNT,
            required_columns=("Date",),
        )
        sys.exit(0)

    if args.ingest_padd3_heavy_dir:
        USManualIngestor().ingest_directory(
            args.ingest_padd3_heavy_dir, dataset=PADD3_HEAVY_CRUDE_IMPORTS,
            required_columns=tuple(PADD3_HEAVY_CRUDE_IMPORTS["required_columns"]),
        )
        sys.exit(0)

    if args.verify:
        dl = EIADownloader(api_key=args.api_key)
        all_series = {k: v for k, v in CRUDE_PRODUCTION["entities"].items()}
        all_series["WTI_SPOT"] = {"series_id": WTI_SPOT["series_id"], "label": WTI_SPOT["label"]}
        for key, cfg in FLOW_LAYER_SERIES.items():
            all_series[key] = {"series_id": cfg["series_id"], "label": cfg["label"]}
        for key, meta in TIGHT_OIL_PRODUCTION["entities"].items():
            all_series[f"TIGHT_OIL_{key}"] = meta
        dl.verify(all_series)
        sys.exit(0)

    if args.flows_only:
        run_flow_layer_downloads(api_key=args.api_key)
        sys.exit(0)

    if args.tight_oil_only:
        _section("TIGHT-OIL PRODUCTION — STEO Table 10b (Session Handoff #6 item #2)")
        EIADownloader(api_key=args.api_key).download_dataset(TIGHT_OIL_PRODUCTION)
        sys.exit(0)

    run_all_downloads(
        production = not args.price_only,
        price      = not args.production_only,
        flows      = not (args.production_only or args.price_only or args.no_flows),
        api_key    = args.api_key,
    )
