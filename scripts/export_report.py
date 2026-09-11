#!/usr/bin/env python3
"""
Memory Claude: DB → 마크다운 보고서 생성
사용법: python scripts/export_report.py
출력: docs/generated/report_summary.md
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'memory_claude.db')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs', 'generated')
OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'report_summary.md')


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def generate_report():
    conn = get_conn()
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = []

    # ── 헤더 ──
    lines.append(f'# Memory Claude 데이터 보고서')
    lines.append(f'**자동 생성**: {now}  ')
    lines.append(f'**DB 경로**: `data/memory_claude.db`')
    lines.append('')
    lines.append('---')
    lines.append('')

    # ── 1. DB 현황 요약 ──
    lines.append('## 1. DB 현황 요약')
    lines.append('')
    tables = ['entities', 'contracts', 'financials', 'earnings_reports', 'milestones', 'fab_capacity', 'entity_strategy']
    lines.append('| 테이블 | 행 수 | 설명 |')
    lines.append('| :--- | :---: | :--- |')
    table_desc = {
        'entities': '21개 AI/반도체 핵심 기업 마스터',
        'contracts': '기업 간 공급·투자·파트너십 계약',
        'financials': '시계열 재무 지표 및 거시 Capex',
        'earnings_reports': '분기별 실적발표 (매출/영업익/순익/EPS/가이던스/비중)',
        'milestones': '공장 가동, 제품 출시 등 마일스톤',
        'fab_capacity': '파운드리/메모리 Fab Capa 및 공정',
        'entity_strategy': '기업별 전략 및 AI 로드맵'
    }
    for t in tables:
        cnt = conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
        lines.append(f'| `{t}` | {cnt} | {table_desc.get(t, "-")} |')
    lines.append('')
    lines.append('---')
    lines.append('')

    # ── 2. 기업 목록 ──
    lines.append('## 2. 등록 기업 (21개사)')
    lines.append('')
    lines.append('| 계층 | 기업명 | ID | 국가 | 티커 |')
    lines.append('| :--- | :--- | :--- | :---: | :---: |')
    rows = conn.execute('''
        SELECT entity_id, name_ko, layer, country, ticker
        FROM entities ORDER BY layer, entity_id
    ''').fetchall()
    layer_map = {
        'L1_AI_LAB': 'AI 프론티어 랩',
        'L2_HYPERSCALER': '하이퍼스케일러',
        'L3_DESIGN': '칩셋 설계/가속기',
        'L4_FOUNDRY': '파운드리',
        'L5_EQUIPMENT': '반도체 장비',
        'L6_MEMORY': '메모리 반도체',
        'L7_SYSTEM': '서버/인프라'
    }
    for r in rows:
        layer_name = layer_map.get(r['layer'], r['layer'])
        ticker = r['ticker'] if r['ticker'] else '-'
        lines.append(f"| {layer_name} | **{r['name_ko']}** | `{r['entity_id']}` | {r['country']} | {ticker} |")
    lines.append('')
    lines.append('---')
    lines.append('')

    # ── 3. 분기별 실적 발표 및 AI 전후 비교 (신규) ──
    lines.append('## 3. 분기별 실적 발표 (어닝콜 데이터 & AI 전후 비교)')
    lines.append('')
    lines.append('> **2019-Q4 (AI 붐 이전)**과 **2024-Q4 (생성형 AI 슈퍼사이클)**의 실적 및 마진 변화 비교')
    lines.append('')
    lines.append('| 기업 | 분기 | 발표일 | 매출 | 영업이익 | 실제 EPS | Gross Margin | 실적 판정 |')
    lines.append('| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |')
    
    earnings = conn.execute('''
        SELECT 
            e.name_ko, r.period, r.report_date, r.revenue, r.op_income, r.unit,
            r.eps_actual, r.gross_margin_pct, r.beat_miss_status, r.revenue_breakdown, r.guidance_next_q
        FROM earnings_reports r
        JOIN entities e ON r.entity_id = e.entity_id
        ORDER BY e.layer, e.entity_id, r.period ASC
    ''').fetchall()

    for er in earnings:
        eps_str = f"${er['eps_actual']:.2f}" if er['eps_actual'] is not None else '-'
        gm_str = f"{er['gross_margin_pct']:.1f}%" if er['gross_margin_pct'] is not None else '-'
        status = er['beat_miss_status'] if er['beat_miss_status'] else '-'
        rep_date = er['report_date'] if er['report_date'] else '-'
        lines.append(f"| **{er['name_ko']}** | {er['period']} | {rep_date} | {er['revenue']} {er['unit']} | {er['op_income']} {er['unit']} | {eps_str} | {gm_str} | {status} |")
    
    lines.append('')
    lines.append('### 3-1. 주요 기업 사업부문별 매출 비중 및 차기 가이던스')
    lines.append('')
    for er in earnings:
        if er['revenue_breakdown'] or er['guidance_next_q']:
            lines.append(f"#### 📌 {er['name_ko']} ({er['period']})")
            if er['revenue_breakdown']:
                lines.append(f"- **매출 비중**: {er['revenue_breakdown']}")
            if er['guidance_next_q']:
                lines.append(f"- **차기 가이던스**: {er['guidance_next_q']}")
            lines.append('')

    lines.append('---')
    lines.append('')

    # ── 4. 핵심 계약 목록 ──
    lines.append('## 4. 핵심 계약 및 파트너십 (10건)')
    lines.append('')
    lines.append('| # | 구매자/투자자 | 공급자/대상 | 계약 유형 | 규모 | 제품군 | 발표 시점 | 내용 |')
    lines.append('| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :--- |')
    contracts = conn.execute('''
        SELECT * FROM v_contract_summary ORDER BY value_b DESC NULLS LAST
    ''').fetchall()
    for i, c in enumerate(contracts, 1):
        val = f"${c['value_b']:.1f}" if c['value_b'] else '-'
        date = c['announced_date'] if c['announced_date'] else '-'
        desc = c['description'] if c['description'] else '-'
        lines.append(f"| {i} | {c['buyer']} | {c['seller']} | {c['contract_type']} | {val} | {c['product_type']} | {date} | {desc} |")
    lines.append('')
    lines.append('---')
    lines.append('')

    # ── 5. 하이퍼스케일러 Capex 추이 ──
    lines.append('## 5. 하이퍼스케일러 Capex 추이 ($B)')
    lines.append('')
    lines.append('| 기업 | 2024 | 2025 | 2026 | YoY (25→26) |')
    lines.append('| :--- | :---: | :---: | :---: | :---: |')

    capex_rows = conn.execute('''
        SELECT
            e.name_ko,
            e.entity_id,
            MAX(CASE WHEN f.period = '2024-FY' THEN f.value END) AS c2024,
            MAX(CASE WHEN f.period = '2025-FY' THEN f.value END) AS c2025,
            MAX(CASE WHEN f.period = '2026-FY' THEN f.value END) AS c2026
        FROM financials f
        JOIN entities e ON f.entity_id = e.entity_id
        WHERE f.metric = 'CAPEX'
        GROUP BY e.entity_id
        ORDER BY c2026 DESC NULLS LAST
    ''').fetchall()

    c24_total = 0
    c25_total = 0
    c26_total = 0

    for r in capex_rows:
        v24 = f"${r['c2024']:.1f}" if r['c2024'] else '-'
        v25 = f"${r['c2025']:.1f}" if r['c2025'] else '-'
        v26 = f"${r['c2026']:.1f}" if r['c2026'] else '-'
        yoy = ''
        if r['c2025'] and r['c2026']:
            pct = ((r['c2026'] - r['c2025']) / r['c2025']) * 100
            yoy = f"+{pct:.0f}%" if pct > 0 else f"{pct:.0f}%"
        lines.append(f"| **{r['name_ko']}** | {v24} | {v25} | {v26} | {yoy} |")
        if r['c2024']: c24_total += r['c2024']
        if r['c2025']: c25_total += r['c2025']
        if r['c2026']: c26_total += r['c2026']

    total_yoy = f"+{((c26_total - c25_total) / c25_total) * 100:.0f}%"
    lines.append(f"| **합계** | **${c24_total:.1f}** | **${c25_total:.1f}** | **${c26_total:.1f}** | **{total_yoy}** |")
    lines.append('')
    lines.append('---')
    lines.append('')

    # ── 6. 자본 흐름 요약 ──
    lines.append('## 6. 자본 흐름 요약 (계약 기반)')
    lines.append('')
    lines.append('```')
    lines.append('하이퍼스케일러 → 엔비디아/브로드컴 → TSMC → ASML')
    lines.append('     │                │')
    lines.append('     │                └──→ SK하이닉스 / 삼성 (HBM)')
    lines.append('     │')
    lines.append('     └──→ 앤트로픽 / 오픈AI (AI 모델)')
    lines.append('')

    gpu_total = conn.execute('''
        SELECT SUM(value_b) FROM contracts WHERE product_type IN ('GPU', 'ASIC') AND value_b IS NOT NULL
    ''').fetchone()[0] or 0

    hbm_total = conn.execute('''
        SELECT SUM(value_b) FROM contracts WHERE product_type = 'HBM' AND value_b IS NOT NULL
    ''').fetchone()[0] or 0

    invest_total = conn.execute('''
        SELECT SUM(value_b) FROM contracts WHERE contract_type = 'INVESTMENT' AND value_b IS NOT NULL
    ''').fetchone()[0] or 0

    lines.append(f'  GPU/ASIC 수주 합계: ${gpu_total:.0f}B')
    lines.append(f'  HBM 공급 계약 합계: ${hbm_total:.0f}B')
    lines.append(f'  AI 랩 투자 합계:    ${invest_total:.0f}B')
    lines.append('```')
    lines.append('')
    lines.append('---')
    lines.append('')

    # ── 푸터 ──
    lines.append(f'> 이 보고서는 `python scripts/export_report.py` 실행으로 자동 생성되었습니다.  ')
    lines.append(f'> DB 데이터를 추가/수정 후 재실행하면 보고서가 갱신됩니다.')

    conn.close()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    print(f'✅ 보고서 생성 완료: {OUTPUT_PATH}')


if __name__ == '__main__':
    generate_report()
