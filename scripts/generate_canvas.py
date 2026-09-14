#!/usr/bin/env python3
"""
generate_canvas.py
--------------------------------------------------
SQLite DB(entities, contracts)의 데이터를 기반으로
옵시디언(Obsidian)에서 바로 열 수 있는 정식 캔버스(.canvas) 파일을 자동 생성합니다.

출력 파일: docs/memory_claude_value_chain.canvas
"""

import json
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "memory_claude.db")
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "memory_claude_value_chain.canvas")

# 계층별 색상 및 Y축 좌표 설정
LAYER_CONFIG = {
    "L1_AI_LAB":      {"y": -300, "color": "6", "title": "AI Frontier Labs (컴퓨트 수요 진원지)"},
    "L2_HYPERSCALER": {"y": -50,  "color": "5", "title": "Hyperscalers (초대형 AI Capex 주도)"},
    "L3_COMPUTE":     {"y": 200,  "color": "4", "title": "AI Accelerators (GPU/ASIC 공급)"},
    "L4_FOUNDRY":     {"y": 450,  "color": "3", "title": "Foundry & Equipment (선단공정 & 패키징)"},
    "L5_MEMORY":      {"y": 700,  "color": "2", "title": "Memory & Storage (HBM3E / HBM4)"},
    "L6_OPTICAL":     {"y": 950,  "color": "1", "title": "Optical & Network (광트랜시버/CPO)"},
    "L7_INFRA":       {"y": 1200, "color": "0", "title": "Infra & Ecosystem (온디바이스/SMR)"},
}

def generate_canvas():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    nodes = []
    edges = []

    # 1. 기업 노드 배치
    cur.execute("SELECT entity_id, name_ko, layer, ticker, country, description FROM entities ORDER BY layer, entity_id;")
    entities = cur.fetchall()

    # 레이어별 X 좌표 배치를 위한 카운터
    layer_counters = {}
    node_id_map = {}

    for row in entities:
        ent_id, name_ko, layer, ticker, country, desc = row
        idx = layer_counters.get(layer, 0)
        layer_counters[layer] = idx + 1

        cfg = LAYER_CONFIG.get(layer, {"y": 0, "color": "1", "title": layer})
        x = idx * 300 - 450
        y = cfg["y"]

        node_id = f"node_{ent_id}"
        node_id_map[ent_id] = node_id

        text_content = f"### {name_ko} ({ent_id})\n- **티커**: `{ticker or '-'}` | **국가**: {country}\n- **설명**: {desc or '-'}"

        nodes.append({
            "id": node_id,
            "x": x,
            "y": y,
            "width": 260,
            "height": 150,
            "type": "text",
            "text": text_content,
            "color": cfg["color"]
        })

    # 2. 계약 기반 엣지(연결선) 생성
    cur.execute("SELECT contract_id, buyer_id, seller_id, contract_type, value_b, product_type, description FROM contracts;")
    contracts = cur.fetchall()

    for idx, c in enumerate(contracts):
        c_id, buyer, seller, c_type, val_b, p_type, desc = c
        from_node = node_id_map.get(buyer)
        to_node = node_id_map.get(seller)

        if from_node and to_node:
            val_str = f"${val_b}B" if val_b else ""
            label_text = f"[{c_type}] {val_str} ({p_type})" if val_str else f"[{c_type}] ({p_type})"

            edges.append({
                "id": f"edge_{idx}_{c_id}",
                "fromNode": from_node,
                "fromSide": "bottom",
                "toNode": to_node,
                "toSide": "top",
                "label": label_text,
                "toEnd": "arrow"
            })

    canvas_data = {
        "nodes": nodes,
        "edges": edges
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(canvas_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Obsidian Canvas 생성 완료: {OUTPUT_PATH}")
    print(f" - 노드 수: {len(nodes)}개 (21개 기업)")
    print(f" - 연결선 수: {len(edges)}개 (10대 계약 자본/공급망 흐름)")

    conn.close()

if __name__ == "__main__":
    generate_canvas()
