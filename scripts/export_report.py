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
    tables = ['entities', 'contracts', 'financials', 'milestones', 'fab_capacity', 'entity_strategy']
    lines.append('| 테이블 | 행 수 |')
    lines.append('| :--- | :---: |')
    for t in tables:
        cnt = conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
        lines.append(f'| `{t}` | {cnt} |')
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
        'L3_COMPUTE': '컴퓨팅·가속기',
        'L4_FOUNDRY': '파운드리·장비',
        'L5_MEMORY': '메모리·스토리지',
        'L6_OPTICAL': '광통신',
        'L7_INFRA': '인프라·특수',
    }
    for r in rows:
        layer_ko = layer_map.get(r['layer'], r['layer'])
        ticker = r['ticker'] or '-'
        lines.append(f"| {layer_ko} | **{r['name_ko']}** | `{r['entity_id']}` | {r['country']} | {ticker} |")
    lines.append('')
    lines.append('---')
    lines.append('')

    # ── 3. 핵심 계약 ──
    lines.append('## 3. 핵심 계약 (금액순)')
    lines.append('')
    lines.append('| # | 구매자 | 판매자 | 유형 | 금액($B) | 대상 | 발표 시점 | 설명 |')
    lines.append('| :---: | :--- | :--- | :--- | :---: | :--- | :--- | :--- |')
    rows = conn.execute('SELECT * FROM v_contract_summary').fetchall()
    for i, r in enumerate(rows, 1):
        val = f"${r['value_b']:.1f}" if r['value_b'] else '-'
        prod = r['product_type'] or '-'
        lines.append(f"| {i} | {r['buyer']} | {r['seller']} | {r['contract_type']} | {val} | {prod} | {r['announced_date']} | {r['description']} |")
    lines.append('')
    lines.append('---')
    lines.append('')

    # ── 4. 하이퍼스케일러 Capex 추이 ──
    lines.append('## 4. 하이퍼스케일러 Capex 추이 ($B)')
    lines.append('')
    lines.append('| 기업 | 2024 | 2025 | 2026 | YoY (25→26) |')
    lines.append('| :--- | :---: | :---: | :---: | :---: |')

    capex_companies = ['GOOGLE', 'AMAZON', 'MICROSOFT', 'META', 'ORACLE']
    for eid in capex_companies:
        name = conn.execute('SELECT name_ko FROM entities WHERE entity_id=?', (eid,)).fetchone()['name_ko']
        vals = {}
        for period in ['2024-FY', '2025-FY', '2026-FY']:
            row = conn.execute(
                'SELECT value FROM financials WHERE entity_id=? AND period=? AND metric=?',
                (eid, period, 'CAPEX')
            ).fetchone()
            vals[period] = row['value'] if row else None

        v24 = f"${vals['2024-FY']:.1f}" if vals['2024-FY'] else '-'
        v25 = f"${vals['2025-FY']:.1f}" if vals['2025-FY'] else '-'
        v26 = f"${vals['2026-FY']:.1f}" if vals['2026-FY'] else '-'

        if vals['2025-FY'] and vals['2026-FY']:
            yoy = ((vals['2026-FY'] - vals['2025-FY']) / vals['2025-FY']) * 100
            yoy_str = f"+{yoy:.0f}%" if yoy > 0 else f"{yoy:.0f}%"
        else:
            yoy_str = '-'

        lines.append(f"| **{name}** | {v24} | {v25} | {v26} | {yoy_str} |")

    # 합계
    totals = {}
    for period in ['2024-FY', '2025-FY', '2026-FY']:
        row = conn.execute('''
            SELECT SUM(value) as total FROM financials
            WHERE entity_id IN ('GOOGLE','AMAZON','MICROSOFT','META','ORACLE')
            AND period=? AND metric='CAPEX'
        ''', (period,)).fetchone()
        totals[period] = row['total'] if row['total'] else 0

    t24 = f"**${totals['2024-FY']:.1f}**" if totals['2024-FY'] else '-'
    t25 = f"**${totals['2025-FY']:.1f}**" if totals['2025-FY'] else '-'
    t26 = f"**${totals['2026-FY']:.1f}**" if totals['2026-FY'] else '-'
    if totals['2025-FY'] and totals['2026-FY']:
        tyoy = ((totals['2026-FY'] - totals['2025-FY']) / totals['2025-FY']) * 100
        tyoy_str = f"+{tyoy:.0f}%" if tyoy > 0 else f"{tyoy:.0f}%"
    else:
        tyoy_str = '-'
    lines.append(f"| **합계** | {t24} | {t25} | {t26} | {tyoy_str} |")

    lines.append('')
    lines.append('---')
    lines.append('')

    # ── 5. 핵심 기업 매출 추이 ──
    lines.append('## 5. 핵심 기업 매출 추이 ($B)')
    lines.append('')
    lines.append('| 기업 | 계층 | 2024 | 2025 | 2026(E) | YoY |')
    lines.append('| :--- | :--- | :---: | :---: | :---: | :---: |')

    rev_companies = ['NVIDIA', 'TSMC', 'SAMSUNG', 'SK_HYNIX', 'BROADCOM']
    for eid in rev_companies:
        row = conn.execute('SELECT name_ko, layer FROM entities WHERE entity_id=?', (eid,)).fetchone()
        name = row['name_ko']
        layer = layer_map.get(row['layer'], row['layer'])
        vals = {}
        for period in ['2024-FY', '2025-FY', '2026-FY']:
            r = conn.execute(
                'SELECT value FROM financials WHERE entity_id=? AND period=? AND metric=?',
                (eid, period, 'REVENUE')
            ).fetchone()
            vals[period] = r['value'] if r else None

        v24 = f"${vals['2024-FY']:.0f}" if vals['2024-FY'] else '-'
        v25 = f"${vals['2025-FY']:.0f}" if vals['2025-FY'] else '-'
        v26 = f"${vals['2026-FY']:.0f}" if vals['2026-FY'] else '-'

        if vals['2025-FY'] and vals['2026-FY']:
            yoy = ((vals['2026-FY'] - vals['2025-FY']) / vals['2025-FY']) * 100
            yoy_str = f"+{yoy:.0f}%" if yoy > 0 else f"{yoy:.0f}%"
        else:
            yoy_str = '-'

        lines.append(f"| **{name}** | {layer} | {v24} | {v25} | {v26} | {yoy_str} |")

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

    # GPU/ASIC 계약 합계
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

    # 파일 출력
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    print(f'✅ 보고서 생성 완료: {OUTPUT_PATH}')
    print(f'   기업: {len([r for r in rows])}개사')


if __name__ == '__main__':
    generate_report()
