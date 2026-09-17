#!/usr/bin/env python3
"""
Capex → 밸류체인 전파 워터폴 차트 데이터 생성 스크립트

contracts 테이블과 earnings_reports(capex)를 결합하여
레이어 간 자금 흐름 JSON을 생성한다.

사용법:
    python3 scripts/export_capex_waterfall.py
"""

import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "memory_claude.db"
RATIOS_PATH = BASE_DIR / "data" / "capex_allocation_ratios.json"
OUTPUT_PATH = BASE_DIR / "data" / "capex_waterfall.json"


def main():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    with open(RATIOS_PATH, "r", encoding="utf-8") as f:
        ratios_config = json.load(f)

    cur = conn.cursor()

    # ── 1) 하이퍼스케일러 Capex 데이터 조회 ─────────────
    hyperscaler_capex = {}
    for hs in ratios_config["hyperscalers"]:
        cur.execute("""
            SELECT period, capex FROM earnings_reports
            WHERE entity_id = ? AND is_forecast = 0 AND capex IS NOT NULL
            ORDER BY period
        """, (hs,))
        rows = [dict(r) for r in cur.fetchall()]
        if rows:
            hyperscaler_capex[hs] = {
                "quarters": rows,
                "latest_q": rows[-1]["period"],
                "latest_capex": rows[-1]["capex"],
                "annual_est": round(rows[-1]["capex"] * 4, 2),
            }

    # ── 2) 계약 데이터에서 레이어 간 흐름 추출 ──────────
    cur.execute("""
        SELECT c.contract_id, c.buyer_id, c.seller_id,
               c.value_b, c.contract_type, c.description,
               b.layer as buyer_layer, b.name_en as buyer_name,
               s.layer as seller_layer, s.name_en as seller_name
        FROM contracts c
        JOIN entities b ON c.buyer_id = b.entity_id
        JOIN entities s ON c.seller_id = s.entity_id
        WHERE c.value_b IS NOT NULL
        ORDER BY c.value_b DESC
    """)
    contracts = [dict(r) for r in cur.fetchall()]

    # 레이어 간 흐름 집계
    layer_flows = {}
    for c in contracts:
        key = f"{c['buyer_layer']}→{c['seller_layer']}"
        if key not in layer_flows:
            layer_flows[key] = {"total_b": 0, "contracts": [], "label": key}
        layer_flows[key]["total_b"] += c["value_b"]
        layer_flows[key]["contracts"].append({
            "id": c["contract_id"],
            "buyer": c["buyer_name"],
            "seller": c["seller_name"],
            "value_b": c["value_b"],
            "type": c["contract_type"],
            "desc": c["description"],
        })

    # ── 3) 워터폴 노드 구성 ─────────────────────────────
    dr = ratios_config["default_ratios"]
    waterfall_nodes = []

    # Root node
    waterfall_nodes.append({
        "id": "capex_total",
        "label": "하이퍼스케일러 Capex",
        "layer": "L2_HYPERSCALER",
        "pct": 100,
        "depth": 0,
        "source": "input",
        "children": ["L3_COMPUTE", "L6_OPTICAL", "L7L8_INFRA", "L4_EQUIPMENT", "OTHER"],
    })

    # L3 Compute
    l3 = dr["L3_COMPUTE"]
    waterfall_nodes.append({
        "id": "L3_COMPUTE",
        "label": l3["label"],
        "layer": "L3_COMPUTE",
        "pct": l3["pct"],
        "depth": 1,
        "source": l3["source"],
        "children": ["L4_FOUNDRY_WAFER", "L5_MEMORY_HBM"],
        "contracts_flow": layer_flows.get("L2_HYPERSCALER→L3_COMPUTE", {}).get("contracts", []),
    })

    # L3 sub-layers
    for sub_key in ["L4_FOUNDRY_WAFER", "L5_MEMORY_HBM"]:
        sub = l3["sub"][sub_key]
        actual_pct = round(l3["pct"] * sub["pct"] / 100, 1)
        flow_key = "L3_COMPUTE→L4_FOUNDRY" if "FOUNDRY" in sub_key else "L3_COMPUTE→L5_MEMORY"
        waterfall_nodes.append({
            "id": sub_key,
            "label": sub["label"],
            "layer": sub_key.split("_")[0] + "_" + sub_key.split("_")[1],
            "pct": actual_pct,
            "parent_pct": sub["pct"],
            "depth": 2,
            "source": sub["source"],
            "children": [],
            "contracts_flow": layer_flows.get(flow_key, {}).get("contracts", []),
        })

    # Other top-level nodes
    for key in ["L6_OPTICAL", "L7L8_INFRA", "L4_EQUIPMENT", "OTHER"]:
        node = dr[key]
        waterfall_nodes.append({
            "id": key,
            "label": node["label"],
            "layer": key,
            "pct": node["pct"],
            "depth": 1,
            "source": node["source"],
            "children": [],
        })

    # ── 4) 레이어별 기업 매출 비중 ──────────────────────
    company_shares = {}
    for layer_key, companies in ratios_config["layer_companies"].items():
        shares = []
        for comp in companies:
            cur.execute("""
                SELECT revenue FROM earnings_reports
                WHERE entity_id = ? AND is_forecast = 0
                ORDER BY period DESC LIMIT 1
            """, (comp,))
            row = cur.fetchone()
            rev = row["revenue"] if row else 0
            cur.execute("SELECT name_en FROM entities WHERE entity_id = ?", (comp,))
            name = cur.fetchone()["name_en"] if cur.fetchone is not None else comp
            try:
                cur.execute("SELECT name_en FROM entities WHERE entity_id = ?", (comp,))
                name_row = cur.fetchone()
                name = name_row["name_en"] if name_row else comp
            except:
                name = comp
            shares.append({"entity_id": comp, "name": name, "latest_revenue": rev})

        total_rev = sum(s["latest_revenue"] for s in shares)
        for s in shares:
            s["share_pct"] = round(s["latest_revenue"] / total_rev * 100, 1) if total_rev > 0 else 0
        company_shares[layer_key] = sorted(shares, key=lambda x: x["latest_revenue"], reverse=True)

    conn.close()

    # ── 출력 ────────────────────────────────────────────
    output = {
        "generated_at": "2026-09-17",
        "waterfall_nodes": waterfall_nodes,
        "layer_flows": {k: {"total_b": v["total_b"], "count": len(v["contracts"]), "contracts": v["contracts"]}
                        for k, v in layer_flows.items()},
        "hyperscaler_capex": hyperscaler_capex,
        "company_shares": company_shares,
        "default_capex_b": 100,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✅ Capex 워터폴 JSON 생성 완료: {OUTPUT_PATH}")
    print(f"   워터폴 노드: {len(waterfall_nodes)}개")
    print(f"   레이어 간 흐름: {len(layer_flows)}건")
    print(f"   하이퍼스케일러 Capex 보유: {len(hyperscaler_capex)}사")


if __name__ == "__main__":
    main()
