#!/usr/bin/env python3
"""
scripts/export_earnings_data.py
--------------------------------------------------
SQLite 데이터베이스(data/memory_claude.db)에서
전체 기업의 분기 실적(earnings_reports) 데이터를 추출하여
CSV 및 JSON 파일로 저장합니다.

출력 파일:
  - data/earnings_reports_export.csv (Excel 호환 UTF-8 BOM)
  - data/earnings_reports_export.json (구조화된 JSON)

사용법:
  python3 scripts/export_earnings_data.py
"""

import os
import sqlite3
import csv
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "memory_claude.db")
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_PATH = os.path.join(DATA_DIR, "earnings_reports_export.csv")
JSON_PATH = os.path.join(DATA_DIR, "earnings_reports_export.json")

def export_earnings():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"데이터베이스 파일을 찾을 수 없습니다: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    sql = """
        SELECT 
            r.id,
            r.entity_id,
            e.name_ko,
            e.name_en,
            e.layer,
            e.ticker,
            e.country,
            e.is_public,
            r.period,
            r.report_date,
            r.revenue,
            r.op_income,
            r.net_income,
            r.unit,
            r.reported_revenue,
            r.reported_op_income,
            r.reported_net_income,
            r.reported_consensus_revenue,
            r.reported_capex,
            r.reported_currency,
            r.reported_unit,
            r.fx_rate,
            r.fx_rate_type,
            r.fx_source,
            r.fx_as_of_date,
            r.eps_actual,
            r.eps_consensus,
            r.consensus_revenue,
            r.beat_miss_status,
            r.gross_margin_pct,
            r.op_margin_pct,
            r.capex,
            r.revenue_breakdown,
            r.guidance_next_q,
            r.key_takeaways,
            r.source,
            r.is_forecast,
            CASE WHEN r.is_forecast = 1 THEN '전망' ELSE '확정' END AS data_type,
            r.created_at
        FROM earnings_reports r
        JOIN entities e ON r.entity_id = e.entity_id
        ORDER BY e.layer, r.entity_id, r.period ASC;
    """

    cur.execute(sql)
    rows = cur.fetchall()
    data = [dict(row) for row in rows]
    conn.close()

    total_count = len(data)
    actual_count = sum(1 for d in data if d['is_forecast'] == 0)
    forecast_count = sum(1 for d in data if d['is_forecast'] == 1)
    entity_count = len(set(d['entity_id'] for d in data))

    # 1. CSV 저장 (utf-8-sig: 엑셀에서 한글 깨짐 방지)
    if data:
        headers = list(data[0].keys())
        with open(CSV_PATH, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

    # 2. JSON 저장 (인덴트 포함 가독성 확보)
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"==================================================")
    print(f" [DB ➔ 파일 저장 완료]")
    print(f" - 전체 실적 건수: {total_count}건")
    print(f" - 대상 기업 수:   {entity_count}개사")
    print(f" - 확정 실적(0):   {actual_count}건 (2020-Q1 ~ 2026-Q2)")
    print(f" - 전망 데이터(1): {forecast_count}건 (2026-Q3 ~ 2026-Q4)")
    print(f"--------------------------------------------------")
    print(f" CSV 저장 경로:  {CSV_PATH}")
    print(f" JSON 저장 경로: {JSON_PATH}")
    print(f"==================================================")

if __name__ == "__main__":
    export_earnings()
