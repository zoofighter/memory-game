#!/usr/bin/env python3
"""
기업별 원페이저 (Entity One-Pager) 자동 생성 스크립트

DB 데이터를 기반으로 각 기업의 투자 노트 1장 분량 마크다운을 생성한다.

사용법:
    python3 scripts/generate_entity_one_pager.py --entity SK_HYNIX
    python3 scripts/generate_entity_one_pager.py --all
    python3 scripts/generate_entity_one_pager.py --layer L5_MEMORY
    python3 scripts/generate_entity_one_pager.py --all --output-dir docs/generated/entity_profiles/
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# ── 경로 설정 ──────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "memory_claude.db"
DEFAULT_OUTPUT_DIR = BASE_DIR / "docs" / "generated" / "entity_profiles"

# ── 레이어 라벨 ────────────────────────────────────────
LAYER_LABELS = {
    "L1_AI_LAB":      "L1 AI 프론티어 랩",
    "L2_HYPERSCALER": "L2 하이퍼스케일러 & 네오클라우드",
    "L3_COMPUTE":     "L3 컴퓨팅/가속기",
    "L4_FOUNDRY":     "L4 파운드리/장비/패키징",
    "L5_MEMORY":      "L5 메모리/스토리지",
    "L6_OPTICAL":     "L6 광통신/네트워킹",
    "L7_INFRA":       "L7 인프라/특수 플랫폼",
    "L8_POWER":       "L8 전력 & 에너지 인프라",
}

EXPECTED_QUARTERS = 26  # 2020-Q1 ~ 2026-Q2

# ── 측정 필드 (데이터 품질 스코어카드 연동) ────────────
QUALITY_FIELDS = [
    ("revenue",           "매출"),
    ("op_margin_pct",     "OPM"),
    ("capex",             "Capex"),
    ("beat_miss_status",  "Beat/Miss"),
    ("guidance_next_q",   "가이던스"),
    ("eps_actual",        "EPS"),
    ("consensus_revenue", "컨센서스매출"),
]


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def fetch_entity(conn, entity_id):
    """기업 메타데이터 조회"""
    cur = conn.cursor()
    cur.execute("SELECT * FROM entities WHERE entity_id = ?", (entity_id,))
    row = cur.fetchone()
    if not row:
        return None
    return dict(row)


def fetch_earnings(conn, entity_id):
    """확정 실적 조회 (시간순)"""
    cur = conn.cursor()
    cur.execute("""
        SELECT period, revenue, op_income, net_income,
               op_margin_pct, gross_margin_pct, capex,
               eps_actual, eps_consensus, consensus_revenue,
               beat_miss_status, guidance_next_q, report_date, source
        FROM earnings_reports
        WHERE entity_id = ? AND is_forecast = 0
        ORDER BY period
    """, (entity_id,))
    return [dict(r) for r in cur.fetchall()]


def fetch_contracts(conn, entity_id):
    """해당 기업이 참여한 계약 조회"""
    cur = conn.cursor()
    cur.execute("""
        SELECT c.contract_id, c.buyer_id, c.seller_id, c.contract_type,
               c.value_b, c.description, c.product_type, c.announced_date,
               c.confidence,
               b.name_en as buyer_name, s.name_en as seller_name
        FROM contracts c
        JOIN entities b ON c.buyer_id = b.entity_id
        JOIN entities s ON c.seller_id = s.entity_id
        WHERE c.buyer_id = ? OR c.seller_id = ?
        ORDER BY c.value_b DESC NULLS LAST
    """, (entity_id, entity_id))
    return [dict(r) for r in cur.fetchall()]


def fetch_milestones(conn, entity_id):
    """마일스톤 조회"""
    cur = conn.cursor()
    cur.execute("""
        SELECT event_id, event_date, category, description,
               impact_level, is_forecast, confidence
        FROM milestones
        WHERE entity_id = ?
        ORDER BY event_date
    """, (entity_id,))
    return [dict(r) for r in cur.fetchall()]


def fetch_fabs(conn, entity_id):
    """Fab 현황 조회"""
    cur = conn.cursor()
    cur.execute("""
        SELECT fab_id, fab_name, location_city, location_country,
               process_node, fab_type, wspm_current, wspm_target,
               ramp_start_date, status, capex_invested_b,
               utilization_pct, key_customers, key_notes
        FROM fab_capacity
        WHERE entity_id = ?
        ORDER BY status, ramp_start_date
    """, (entity_id,))
    return [dict(r) for r in cur.fetchall()]


def compute_quality_score(conn, entity_id):
    """데이터 품질 스코어 계산"""
    cur = conn.cursor()
    scores = {}
    total_filled = 0
    for col, label in QUALITY_FIELDS:
        cur.execute(f"""
            SELECT COUNT(*) as cnt FROM earnings_reports
            WHERE entity_id = ? AND is_forecast = 0
              AND {col} IS NOT NULL AND TRIM(CAST({col} AS TEXT)) != ''
        """, (entity_id,))
        filled = cur.fetchone()["cnt"]
        pct = round(filled / EXPECTED_QUARTERS * 100, 1) if EXPECTED_QUARTERS > 0 else 0
        scores[col] = {"filled": filled, "total": EXPECTED_QUARTERS, "pct": pct, "label": label}
        total_filled += filled

    max_possible = len(QUALITY_FIELDS) * EXPECTED_QUARTERS
    return {
        "fields": scores,
        "total_filled": total_filled,
        "total_possible": max_possible,
        "total_pct": round(total_filled / max_possible * 100, 1) if max_possible > 0 else 0,
    }


# ── 자동 하이라이트 규칙 ───────────────────────────────

def generate_watchpoints(entity, earnings, contracts, milestones, quality):
    """규칙 기반 Key Watchpoints 자동 생성"""
    points = []

    if not earnings:
        points.append("❌ 비상장 기업 — 공개 실적 없음, 제한적 분석만 가능")
        return points

    latest = earnings[-1]
    recent_4 = earnings[-4:] if len(earnings) >= 4 else earnings

    # W1: 높은 OPM
    if latest.get("op_margin_pct") and latest["op_margin_pct"] >= 50:
        points.append(f"⚡ OPM {latest['op_margin_pct']:.1f}%는 동종 레이어 평균 대비 상위권")

    # W2: 연속 매출 성장
    if len(recent_4) >= 2:
        growth_streak = 0
        for i in range(len(earnings)-1, 0, -1):
            if earnings[i]["revenue"] > earnings[i-1]["revenue"]:
                growth_streak += 1
            else:
                break
        if growth_streak >= 4:
            points.append(f"📈 {growth_streak}분기 연속 매출 성장 중 (QoQ)")

    # W3: Beat 연속 스트릭
    beat_streak = 0
    for e in reversed(earnings):
        if e.get("beat_miss_status") and "BEAT" in str(e["beat_miss_status"]).upper():
            beat_streak += 1
        elif e.get("beat_miss_status"):
            break
    if beat_streak >= 4:
        points.append(f"🎯 {beat_streak}분기 연속 컨센서스 Beat")

    # W4/W5: YoY 매출 성장률
    if len(earnings) >= 5:
        current_rev = latest["revenue"]
        yoy_period = earnings[-5]["period"] if len(earnings) >= 5 else None
        yoy_rev = earnings[-5]["revenue"] if len(earnings) >= 5 else None
        if yoy_rev and yoy_rev > 0:
            yoy_growth = ((current_rev - yoy_rev) / yoy_rev) * 100
            if yoy_growth >= 50:
                points.append(f"🚀 YoY 매출 성장률 {yoy_growth:.0f}% — 고성장 구간")
            elif yoy_growth <= -20:
                points.append(f"⚠️ YoY 매출 {yoy_growth:.0f}% 역성장 — 다운사이클 주의")

    # W6: 대규모 계약
    if contracts:
        valued = [c for c in contracts if c.get("value_b")]
        total_contract_value = sum(c["value_b"] for c in valued)
        if total_contract_value >= 10:
            points.append(f"🔗 대규모 계약 {len(valued)}건, 총 ${total_contract_value:.1f}B")

    # W7: CRITICAL 마일스톤
    critical_ms = [m for m in milestones if m.get("impact_level") == "CRITICAL"]
    for m in critical_ms[:3]:
        points.append(f"🎯 주요 마일스톤: {m['description']} ({m['event_date']})")

    # W8: Capex 데이터 없음
    capex_filled = sum(1 for e in earnings if e.get("capex") is not None)
    if capex_filled == 0:
        points.append("⚠️ Capex 데이터 미입력 — 투자 규모 파악 불가")

    return points


# ── 마크다운 생성 ──────────────────────────────────────

def generate_one_pager(conn, entity_id):
    """단일 기업 원페이저 마크다운 생성"""
    entity = fetch_entity(conn, entity_id)
    if not entity:
        return None, f"❌ entity_id '{entity_id}' 를 찾을 수 없습니다."

    earnings = fetch_earnings(conn, entity_id)
    contracts_data = fetch_contracts(conn, entity_id)
    milestones_data = fetch_milestones(conn, entity_id)
    fabs = fetch_fabs(conn, entity_id)
    quality = compute_quality_score(conn, entity_id)
    watchpoints = generate_watchpoints(entity, earnings, contracts_data, milestones_data, quality)

    layer_label = LAYER_LABELS.get(entity["layer"], entity["layer"])
    ticker_info = entity.get("ticker") or "비상장"
    country = entity.get("country") or ""
    desc = entity.get("description") or ""

    lines = []
    lines.append(f"# {entity['name_en']} ({entity_id}) — {layer_label}")
    lines.append(f"> {ticker_info} | {country} | {desc}")
    lines.append("")
    lines.append(f"*자동 생성: {datetime.now().strftime('%Y-%m-%d %H:%M')} · 기준: 2026-09-10*")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── §1: 최근 실적 추이 ─────────────────────────────
    lines.append("## 1️⃣ 최근 실적 추이 (Recent Earnings)")
    lines.append("")
    if not earnings:
        lines.append("> ⚠️ 실적 데이터 없음 (비상장 또는 미수집)")
        lines.append("")
    else:
        recent = earnings[-8:] if len(earnings) >= 8 else earnings
        lines.append("| 분기 | 매출($B) | 영업이익($B) | OPM(%) | Beat/Miss |")
        lines.append("|:---|---:|---:|---:|:---:|")
        for e in recent:
            rev = f"{e['revenue']:.2f}" if e.get("revenue") else "—"
            opi = f"{e['op_income']:.2f}" if e.get("op_income") else "—"
            opm = f"{e['op_margin_pct']:.1f}" if e.get("op_margin_pct") else "—"
            beat = e.get("beat_miss_status") or "—"
            lines.append(f"| {e['period']} | {rev} | {opi} | {opm} | {beat} |")
        lines.append("")

    # ── §2: 실적 트렌드 (Sparkline) ────────────────────
    lines.append("## 2️⃣ 실적 트렌드")
    lines.append("")
    if earnings and len(earnings) >= 4:
        # ASCII sparkline for revenue
        revs = [e["revenue"] for e in earnings if e.get("revenue")]
        if revs:
            min_r, max_r = min(revs), max(revs)
            span = max_r - min_r if max_r != min_r else 1
            blocks = "▁▂▃▄▅▆▇█"
            spark = ""
            for r in revs:
                idx = min(int((r - min_r) / span * (len(blocks)-1)), len(blocks)-1)
                spark += blocks[idx]
            lines.append(f"**매출 추이** ({earnings[0]['period']} → {earnings[-1]['period']}): `{spark}`")
            lines.append(f"  범위: ${min_r:.2f}B ~ ${max_r:.2f}B")
            lines.append("")

        # OPM sparkline
        opms = [(e["period"], e["op_margin_pct"]) for e in earnings if e.get("op_margin_pct") is not None]
        if opms:
            vals = [o[1] for o in opms]
            min_o, max_o = min(vals), max(vals)
            span = max_o - min_o if max_o != min_o else 1
            spark_o = ""
            for v in vals:
                idx = min(int((v - min_o) / span * (len(blocks)-1)), len(blocks)-1)
                spark_o += blocks[idx]
            lines.append(f"**OPM 추이**: `{spark_o}`")
            lines.append(f"  범위: {min_o:.1f}% ~ {max_o:.1f}%")
            lines.append("")
    else:
        lines.append("> 트렌드 표시를 위한 충분한 데이터 없음")
        lines.append("")

    # ── §3: Capex 현황 ─────────────────────────────────
    lines.append("## 3️⃣ Capex 현황")
    lines.append("")
    capex_data = [(e["period"], e["capex"]) for e in earnings if e.get("capex") is not None]
    if capex_data:
        lines.append("| 분기 | Capex ($B) |")
        lines.append("|:---|---:|")
        for period, capex in capex_data[-8:]:
            lines.append(f"| {period} | {capex:.2f} |")
        lines.append("")
    else:
        lines.append("> ⚠️ Capex 데이터 미입력")
        lines.append("")

    # ── §4: 주요 계약 ──────────────────────────────────
    lines.append("## 4️⃣ 주요 계약 (Key Contracts)")
    lines.append("")
    if contracts_data:
        for c in contracts_data:
            role = "구매" if c["buyer_id"] == entity_id else "공급"
            counterpart = c["seller_name"] if c["buyer_id"] == entity_id else c["buyer_name"]
            val = f"${c['value_b']:.1f}B" if c.get("value_b") else "금액 미공개"
            desc_text = c.get("description") or c.get("product_type") or c["contract_type"]
            lines.append(f"- **{val}** — {role}: {counterpart} ({desc_text})")
        lines.append("")
    else:
        lines.append("> 등록된 계약 없음")
        lines.append("")

    # ── §5: 마일스톤 ───────────────────────────────────
    lines.append("## 5️⃣ 마일스톤 (Key Milestones)")
    lines.append("")
    if milestones_data:
        for m in milestones_data:
            impact = "🔴" if m["impact_level"] == "CRITICAL" else "🟡" if m["impact_level"] == "HIGH" else "⚪"
            forecast = " *(전망)*" if m["is_forecast"] else ""
            lines.append(f"- {impact} **{m['event_date']}** — {m['description']}{forecast}")
        lines.append("")
    else:
        lines.append("> 등록된 마일스톤 없음")
        lines.append("")

    # ── §6: Fab/인프라 현황 ────────────────────────────
    lines.append("## 6️⃣ Fab / 인프라 현황")
    lines.append("")
    if fabs:
        for f in fabs:
            status_icon = "🟢" if f["status"] == "OPERATING" else "🔵" if f["status"] == "UNDER_CONSTRUCTION" else "⚪"
            location = f"{f.get('location_city', '')} {f.get('location_country', '')}".strip()
            node = f.get("process_node") or ""
            capex_f = f"(투자 ${f['capex_invested_b']:.1f}B)" if f.get("capex_invested_b") else ""
            lines.append(f"- {status_icon} **{f['fab_name']}** — {location} | {node} | {f['status']} {capex_f}")
            if f.get("key_notes"):
                lines.append(f"  - {f['key_notes']}")
        lines.append("")
    else:
        lines.append("> 등록된 Fab/인프라 없음")
        lines.append("")

    # ── §7: 핵심 관전 포인트 ───────────────────────────
    lines.append("## 7️⃣ 핵심 관전 포인트 (Key Watchpoints)")
    lines.append("")
    if watchpoints:
        for wp in watchpoints:
            lines.append(f"- {wp}")
    else:
        lines.append("> 자동 생성된 관전 포인트 없음")
    lines.append("")

    # ── §8: 데이터 커버리지 노트 ───────────────────────
    lines.append("## 8️⃣ 데이터 커버리지 노트")
    lines.append("")
    lines.append(f"**전체 완결도: {quality['total_pct']}%** ({quality['total_filled']}/{quality['total_possible']})")
    lines.append("")
    lines.append("| 필드 | 입력 | 비율 |")
    lines.append("|:---|:---:|:---:|")
    for col, label in QUALITY_FIELDS:
        q = quality["fields"][col]
        bar_full = "█" * int(q["pct"] / 10)
        bar_empty = "░" * (10 - len(bar_full))
        lines.append(f"| {label} | {q['filled']}/{q['total']} | {bar_full}{bar_empty} {q['pct']}% |")
    lines.append("")

    lines.append("---")
    lines.append(f"*Generated by Memory Claude · generate_entity_one_pager.py*")

    return "\n".join(lines), None


def generate_index(output_dir, generated_entities):
    """INDEX.md 생성"""
    lines = [
        "# Entity Profiles — 기업별 원페이저 인덱스",
        "",
        f"*자동 생성: {datetime.now().strftime('%Y-%m-%d %H:%M')} · 총 {len(generated_entities)}사*",
        "",
        "---",
        "",
    ]

    # 레이어별 그룹핑
    by_layer = {}
    for eid, name, layer in generated_entities:
        if layer not in by_layer:
            by_layer[layer] = []
        by_layer[layer].append((eid, name))

    for layer in sorted(by_layer.keys()):
        label = LAYER_LABELS.get(layer, layer)
        lines.append(f"## {label}")
        lines.append("")
        for eid, name in sorted(by_layer[layer], key=lambda x: x[1]):
            lines.append(f"- [{name} ({eid})](./{eid}.md)")
        lines.append("")

    index_path = output_dir / "INDEX.md"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return index_path


def main():
    parser = argparse.ArgumentParser(description="기업별 원페이저 자동 생성")
    parser.add_argument("--entity", type=str, help="단일 기업 entity_id (예: SK_HYNIX)")
    parser.add_argument("--all", action="store_true", help="전체 36개사 일괄 생성")
    parser.add_argument("--layer", type=str, help="특정 레이어만 생성 (예: L5_MEMORY)")
    parser.add_argument("--output-dir", type=str, default=str(DEFAULT_OUTPUT_DIR), help="출력 디렉토리")
    args = parser.parse_args()

    if not args.entity and not args.all and not args.layer:
        parser.error("--entity, --all, --layer 중 하나를 지정하세요.")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    conn = get_db()

    # 대상 기업 목록 결정
    if args.entity:
        targets = [args.entity]
    elif args.layer:
        cur = conn.cursor()
        cur.execute("SELECT entity_id FROM entities WHERE layer = ? ORDER BY entity_id", (args.layer,))
        targets = [r["entity_id"] for r in cur.fetchall()]
        if not targets:
            print(f"❌ 레이어 '{args.layer}'에 해당하는 기업이 없습니다.")
            sys.exit(1)
    else:  # --all
        cur = conn.cursor()
        cur.execute("SELECT entity_id FROM entities ORDER BY layer, entity_id")
        targets = [r["entity_id"] for r in cur.fetchall()]

    generated = []
    errors = []

    for eid in targets:
        md_content, err = generate_one_pager(conn, eid)
        if err:
            errors.append(err)
            print(f"  ⚠️ {eid}: {err}")
            continue

        filepath = output_dir / f"{eid}.md"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)

        # 기업 이름과 레이어 조회
        ent = fetch_entity(conn, eid)
        generated.append((eid, ent["name_en"], ent["layer"]))
        print(f"  ✅ {eid:20s} → {filepath.name}")

    # INDEX.md 생성
    if len(generated) > 1:
        idx_path = generate_index(output_dir, generated)
        print(f"\n  📋 INDEX.md → {idx_path}")

    conn.close()

    print(f"\n{'='*50}")
    print(f"✅ 완료: {len(generated)}사 생성, {len(errors)}건 오류")
    print(f"   출력: {output_dir}")


if __name__ == "__main__":
    main()
