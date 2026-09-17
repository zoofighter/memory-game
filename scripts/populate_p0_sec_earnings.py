#!/usr/bin/env python3
"""Load official SEC XBRL quarterly earnings for P0 public entities.

The script downloads SEC Company Facts JSON into 99.raw/financials/sec_companyfacts,
extracts reported quarterly values, derives Q4 from FY minus Q1-Q3 when necessary,
and inserts only confirmed periods through 2026-Q2. It never creates consensus data.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import time
import urllib.request
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "memory_claude.db"
RAW_DIR = ROOT / "99.raw" / "financials" / "sec_companyfacts"
USER_AGENT = "MemoryClaude earnings research contact@example.com"

COMPANIES = {
    "ARM": "0001973239",
    "INTEL": "0000050863",
    "ASE": "0001122411",
    "AMKOR": "0001047127",
    "APPLIED_MATERIALS": "0000006951",
    "LAM_RESEARCH": "0000707549",
    "KLA": "0000319201",
    "ARISTA": "0001596532",
    "VERTIV": "0001674101",
}

METRIC_TAGS = {
    "revenue": (
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "SalesRevenueNet",
        "Revenues",
        "Revenue",
    ),
    "op_income": (
        "OperatingIncomeLoss",
        "ProfitLossFromOperatingActivities",
    ),
    "net_income": (
        "NetIncomeLoss",
        "ProfitLoss",
        "ProfitLossAttributableToOwnersOfParent",
    ),
    "gross_profit": ("GrossProfit",),
    "eps_actual": ("EarningsPerShareDiluted", "DilutedEarningsLossPerShare"),
}

FORMS = {"10-Q", "10-K", "20-F", "40-F", "6-K"}
ACTUAL_CUTOFF = "2026-Q2"
ACTUAL_START = "2020-Q1"


@dataclass
class Point:
    value: float
    filed: str
    accession: str
    fy: int | None
    fp: str | None
    end: str
    derived: bool = False


def download(entity_id: str, cik: str, refresh: bool) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"{entity_id.lower()}_{cik}.json"
    if path.exists() and not refresh:
        return path
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read()
    path.write_bytes(payload)
    time.sleep(0.15)
    return path


def duration_days(item: dict) -> int | None:
    if not item.get("start") or not item.get("end"):
        return None
    return (date.fromisoformat(item["end"]) - date.fromisoformat(item["start"])).days


def namespace(data: dict) -> dict:
    facts = data.get("facts", {})
    merged = {}
    merged.update(facts.get("us-gaap", {}))
    merged.update(facts.get("ifrs-full", {}))
    return merged


def choose_tag(facts: dict, tags: tuple[str, ...], unit: str) -> tuple[str | None, list[dict]]:
    best_tag = None
    best_items: list[dict] = []
    for tag in tags:
        items = facts.get(tag, {}).get("units", {}).get(unit, [])
        eligible = [item for item in items if item.get("form") in FORMS]
        direct = [item for item in eligible if (duration_days(item) or 0) in range(60, 121)]
        score = (max((item.get("end", "") for item in direct), default=""), len(direct))
        best_score = (max((item.get("end", "") for item in best_items), default=""), len(best_items))
        if score > best_score:
            best_tag = tag
            best_items = direct
    return best_tag, best_items


def extract_metric(data: dict, metric: str) -> tuple[str | None, dict[str, Point]]:
    facts = namespace(data)
    unit = "USD/shares" if metric == "eps_actual" else "USD"
    tag, direct_items = choose_tag(facts, METRIC_TAGS[metric], unit)
    if not tag:
        return None, {}

    all_items = [
        item
        for item in facts[tag].get("units", {}).get(unit, [])
        if item.get("form") in FORMS and item.get("end") and item.get("filed")
    ]

    # Keep the latest filing for duplicated comparative facts.
    direct_by_end_fp: dict[tuple[str, str], dict] = {}
    for item in direct_items:
        fp = item.get("fp")
        if fp not in {"Q1", "Q2", "Q3", "Q4"}:
            continue
        key = (item["end"], fp)
        if key not in direct_by_end_fp or item["filed"] > direct_by_end_fp[key]["filed"]:
            direct_by_end_fp[key] = item

    points: dict[str, Point] = {}
    for (_, fp), item in direct_by_end_fp.items():
        period = f"{item['end'][:4]}-{fp}"
        if ACTUAL_START <= period <= ACTUAL_CUTOFF:
            points[period] = Point(
                float(item["val"]), item["filed"], item.get("accn", ""),
                item.get("fy"), fp, item["end"], False,
            )

    # Annual EPS minus quarterly EPS is not a valid weighted-share calculation.
    if metric == "eps_actual":
        return tag, points

    # Most issuers do not tag a standalone Q4. Derive it from the annual fact.
    annual_by_end: dict[str, dict] = {}
    for item in all_items:
        days = duration_days(item)
        if item.get("fp") != "FY" or not days or not 300 <= days <= 380:
            continue
        key = item["end"]
        if key not in annual_by_end or item["filed"] > annual_by_end[key]["filed"]:
            annual_by_end[key] = item

    for _, annual in annual_by_end.items():
        candidates = [
            item for item in direct_by_end_fp.values()
            if annual["start"] <= item.get("start", "")
            and item["end"] <= annual["end"]
            and item.get("fp") in {"Q1", "Q2", "Q3"}
        ]
        quarters = {}
        for item in candidates:
            fp = item["fp"]
            if fp not in quarters or item["end"] > quarters[fp]["end"]:
                quarters[fp] = item
        if set(quarters) != {"Q1", "Q2", "Q3"}:
            continue
        period = f"{annual['end'][:4]}-Q4"
        if not ACTUAL_START <= period <= ACTUAL_CUTOFF:
            continue
        q4_value = float(annual["val"]) - sum(float(q["val"]) for q in quarters.values())
        points[period] = Point(
            q4_value, annual["filed"], annual.get("accn", ""),
            annual.get("fy"), "Q4", annual["end"], True,
        )
    return tag, points


def accession_url(cik: str, accession: str) -> str:
    cik_plain = str(int(cik))
    accession_plain = accession.replace("-", "")
    return f"https://www.sec.gov/Archives/edgar/data/{cik_plain}/{accession_plain}/"


def build_rows(entity_id: str, cik: str, data: dict, raw_path: Path) -> list[dict]:
    tags = {}
    metrics = {}
    for metric in METRIC_TAGS:
        tags[metric], metrics[metric] = extract_metric(data, metric)

    rows = []
    for period, revenue_point in sorted(metrics["revenue"].items()):
        revenue = revenue_point.value / 1_000_000_000
        if revenue <= 0:
            continue
        values = {}
        for metric in ("op_income", "net_income", "gross_profit"):
            point = metrics[metric].get(period)
            values[metric] = point.value / 1_000_000_000 if point else None
        eps_point = metrics["eps_actual"].get(period)
        gross_margin = (
            round(values["gross_profit"] / revenue * 100, 2)
            if values["gross_profit"] is not None else None
        )
        op_margin = (
            round(values["op_income"] / revenue * 100, 2)
            if values["op_income"] is not None else None
        )
        derived_metrics = [
            metric for metric, points in metrics.items()
            if period in points and points[period].derived
        ]
        tags_used = ", ".join(f"{key}={value}" for key, value in tags.items() if value)
        note = "SEC XBRL official filing"
        if derived_metrics:
            note += "; Q4 derived as FY minus Q1-Q3 for " + ", ".join(derived_metrics)
        rows.append({
            "entity_id": entity_id,
            "period": period,
            "report_date": revenue_point.filed,
            "revenue": round(revenue, 6),
            "op_income": round(values["op_income"], 6) if values["op_income"] is not None else None,
            "net_income": round(values["net_income"], 6) if values["net_income"] is not None else None,
            "eps_actual": round(eps_point.value, 6) if eps_point else None,
            "gross_margin_pct": gross_margin,
            "op_margin_pct": op_margin,
            "key_takeaways": note,
            "source": accession_url(cik, revenue_point.accession),
            "raw_source": str(raw_path.relative_to(ROOT)),
            "tags_used": tags_used,
        })
    return rows


def apply_rows(connection: sqlite3.Connection, rows: list[dict]) -> tuple[int, int]:
    inserted = 0
    updated = 0
    for row in rows:
        existing = connection.execute(
            "SELECT id FROM earnings_reports WHERE entity_id=? AND period=?",
            (row["entity_id"], row["period"]),
        ).fetchone()
        values = (
            row["report_date"], row["revenue"], row["op_income"], row["net_income"],
            "B_USD", row["eps_actual"], row["gross_margin_pct"], row["op_margin_pct"],
            row["key_takeaways"], row["source"], 0,
        )
        if existing:
            connection.execute(
                """
                UPDATE earnings_reports
                SET report_date=?, revenue=?, op_income=?, net_income=?, unit=?,
                    eps_actual=?, gross_margin_pct=?, op_margin_pct=?,
                    key_takeaways=?, source=?, is_forecast=?
                WHERE id=?
                """,
                values + (existing[0],),
            )
            updated += 1
        else:
            connection.execute(
                """
                INSERT INTO earnings_reports (
                    entity_id, period, report_date, revenue, op_income, net_income,
                    unit, eps_actual, gross_margin_pct, op_margin_pct,
                    key_takeaways, source, is_forecast
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (row["entity_id"], row["period"]) + values,
            )
            inserted += 1
    return inserted, updated


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write extracted rows to SQLite")
    parser.add_argument("--refresh", action="store_true", help="redownload SEC JSON")
    parser.add_argument("--entities", nargs="*", choices=sorted(COMPANIES), default=sorted(COMPANIES))
    args = parser.parse_args()

    all_rows: list[dict] = []
    for entity_id in args.entities:
        cik = COMPANIES[entity_id]
        raw_path = download(entity_id, cik, args.refresh)
        data = json.loads(raw_path.read_text(encoding="utf-8"))
        rows = build_rows(entity_id, cik, data, raw_path)
        all_rows.extend(rows)
        print(f"{entity_id}: {len(rows)} confirmed quarters")

    preview_path = ROOT / "data" / "p0_sec_earnings_preview.json"
    preview_path.write_text(json.dumps(all_rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"total={len(all_rows)} preview={preview_path}")

    if not args.apply:
        print("dry-run only; use --apply after reviewing the preview")
        return

    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys=ON")
    try:
        connection.execute("BEGIN IMMEDIATE")
        inserted, updated = apply_rows(connection, all_rows)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    print(f"inserted={inserted} updated={updated}")


if __name__ == "__main__":
    main()
