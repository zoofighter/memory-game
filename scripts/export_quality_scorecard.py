#!/usr/bin/env python3
"""
데이터 품질 스코어카드 JSON 생성 스크립트

earnings_reports 테이블에서 36개사 × 7개 필드의 입력 완결도를 집계하여
data/quality_scorecard.json 으로 출력한다.

사용법:
    python3 scripts/export_quality_scorecard.py
"""

import json
import os
import sqlite3
from pathlib import Path

# ── 경로 설정 ──────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "memory_claude.db"
OUTPUT_PATH = BASE_DIR / "data" / "quality_scorecard.json"

# ── 측정 대상 필드 ──────────────────────────────────────
FIELDS = [
    {"key": "revenue",            "label": "매출",        "label_en": "Revenue"},
    {"key": "op_margin_pct",      "label": "OPM",         "label_en": "OPM"},
    {"key": "capex",              "label": "Capex",       "label_en": "Capex"},
    {"key": "beat_miss_status",   "label": "Beat/Miss",   "label_en": "Beat/Miss"},
    {"key": "guidance_next_q",    "label": "가이던스",    "label_en": "Guidance"},
    {"key": "eps_actual",         "label": "EPS",         "label_en": "EPS"},
    {"key": "consensus_revenue",  "label": "컨센서스매출", "label_en": "Cons.Rev"},
]

# 기대 분기 수: 2020-Q1 ~ 2026-Q2 = 26분기
EXPECTED_QUARTERS = 26


def main():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # ── 1) 전체 기업 목록 조회 ──────────────────────────
    cur.execute("""
        SELECT entity_id, name_en, name_ko, layer, ticker, is_public
        FROM entities
        ORDER BY layer, entity_id
    """)
    entities = [dict(row) for row in cur.fetchall()]

    # ── 2) 기업별 × 필드별 입력 건수 집계 ───────────────
    results = []
    for ent in entities:
        eid = ent["entity_id"]
        field_scores = {}
        total_filled = 0

        for f in FIELDS:
            col = f["key"]
            cur.execute(f"""
                SELECT COUNT(*) as cnt
                FROM earnings_reports
                WHERE entity_id = ?
                  AND is_forecast = 0
                  AND {col} IS NOT NULL
                  AND TRIM(CAST({col} AS TEXT)) != ''
            """, (eid,))
            filled = cur.fetchone()["cnt"]
            field_scores[col] = {
                "filled": filled,
                "total": EXPECTED_QUARTERS,
                "pct": round(filled / EXPECTED_QUARTERS * 100, 1) if EXPECTED_QUARTERS > 0 else 0,
            }
            total_filled += filled

        max_possible = len(FIELDS) * EXPECTED_QUARTERS
        results.append({
            "entity_id": eid,
            "name_en": ent["name_en"],
            "name_ko": ent["name_ko"],
            "layer": ent["layer"],
            "ticker": ent["ticker"],
            "is_public": ent["is_public"],
            "fields": field_scores,
            "total_filled": total_filled,
            "total_possible": max_possible,
            "total_pct": round(total_filled / max_possible * 100, 1) if max_possible > 0 else 0,
        })

    # ── 3) 필드별 전체 요약 통계 ─────────────────────────
    field_summary = {}
    for f in FIELDS:
        col = f["key"]
        cur.execute(f"""
            SELECT COUNT(DISTINCT entity_id) as entities_with_data
            FROM earnings_reports
            WHERE is_forecast = 0
              AND {col} IS NOT NULL
              AND TRIM(CAST({col} AS TEXT)) != ''
        """)
        entities_with = cur.fetchone()["entities_with_data"]

        cur.execute(f"""
            SELECT COUNT(*) as total_filled
            FROM earnings_reports
            WHERE is_forecast = 0
              AND {col} IS NOT NULL
              AND TRIM(CAST({col} AS TEXT)) != ''
        """)
        total_filled_field = cur.fetchone()["total_filled"]

        total_possible_field = len(entities) * EXPECTED_QUARTERS
        field_summary[col] = {
            "label": f["label"],
            "label_en": f["label_en"],
            "entities_with_data": entities_with,
            "total_entities": len(entities),
            "total_filled": total_filled_field,
            "total_possible": total_possible_field,
            "coverage_pct": round(total_filled_field / total_possible_field * 100, 1) if total_possible_field > 0 else 0,
        }

    # ── 4) 전체 시스템 요약 ──────────────────────────────
    grand_total_filled = sum(r["total_filled"] for r in results)
    grand_total_possible = sum(r["total_possible"] for r in results)

    # ── 5) 추가 테이블별 커버리지 ────────────────────────
    cur.execute("SELECT COUNT(*) as cnt FROM contracts")
    contracts_count = cur.fetchone()["cnt"]
    cur.execute("SELECT COUNT(*) as cnt FROM milestones")
    milestones_count = cur.fetchone()["cnt"]
    cur.execute("SELECT COUNT(*) as cnt FROM fab_capacity")
    fab_count = cur.fetchone()["cnt"]
    cur.execute("""
        SELECT COUNT(DISTINCT eid) as cnt FROM (
            SELECT buyer_id as eid FROM contracts
            UNION
            SELECT seller_id as eid FROM contracts
        )
    """)
    entities_with_contracts = cur.fetchone()["cnt"]

    # ── 6) 경고 메시지 생성 ──────────────────────────────
    alerts = []
    for col, info in field_summary.items():
        if info["coverage_pct"] < 15:
            alerts.append({
                "level": "critical",
                "field": info["label"],
                "message": f"{info['label']}: {info['entities_with_data']}/{info['total_entities']}사만 입력 ({info['coverage_pct']}%)"
            })
        elif info["coverage_pct"] < 40:
            alerts.append({
                "level": "warning",
                "field": info["label"],
                "message": f"{info['label']}: 커버리지 {info['coverage_pct']}% — 보강 필요"
            })

    # 비상장 기업 경고
    unlisted = [r for r in results if r["is_public"] == 0 or r["total_filled"] == 0]
    if unlisted:
        alerts.append({
            "level": "info",
            "field": "general",
            "message": f"비상장/미수집 {len(unlisted)}사: 실적 0건"
        })

    # ── 출력 구성 ────────────────────────────────────────
    output = {
        "generated_at": "2026-09-17",
        "project_baseline": "2026-09-10",
        "expected_quarters": EXPECTED_QUARTERS,
        "period_range": "2020-Q1 ~ 2026-Q2",
        "fields": [{"key": f["key"], "label": f["label"], "label_en": f["label_en"]} for f in FIELDS],
        "entities": sorted(results, key=lambda x: x["total_pct"], reverse=True),
        "field_summary": field_summary,
        "system_summary": {
            "total_entities": len(entities),
            "entities_with_earnings": sum(1 for r in results if r["total_filled"] > 0),
            "grand_total_filled": grand_total_filled,
            "grand_total_possible": grand_total_possible,
            "overall_pct": round(grand_total_filled / grand_total_possible * 100, 1) if grand_total_possible > 0 else 0,
            "contracts_count": contracts_count,
            "milestones_count": milestones_count,
            "fab_count": fab_count,
        },
        "alerts": alerts,
    }

    conn.close()

    # ── JSON 저장 ────────────────────────────────────────
    with open(OUTPUT_PATH, "w", encoding="utf-8") as fp:
        json.dump(output, fp, ensure_ascii=False, indent=2)

    print(f"✅ 스코어카드 JSON 생성 완료: {OUTPUT_PATH}")
    print(f"   기업 수: {len(entities)}사")
    print(f"   전체 완결도: {output['system_summary']['overall_pct']}%")
    print(f"   경고 {len(alerts)}건")


if __name__ == "__main__":
    main()
