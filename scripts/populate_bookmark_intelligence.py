#!/usr/bin/env python3
"""
scripts/populate_bookmark_intelligence.py
북마크 10_실적 ~ 40_계약에서 추출된 핵심 정량 데이터
(오픈AI-브로드컴 10GW 칩 계약, 앤트로픽 $518B 컴퓨트, 마이크론 100k HBM 캐파, 메리츠 2028 HBM 수요 등)를
SQLite 데이터베이스(data/memory_claude.db)에 적재하는 스크립트.
"""

import sqlite3
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = WORKSPACE_ROOT / "data" / "memory_claude.db"

def populate_intelligence():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. 신규 대형 계약 (contracts)
    contracts = [
        (
            'CON-2026-OPAI-BRCM',
            'OPENAI',
            'BROADCOM',
            'PARTNERSHIP',
            65.0,
            'USD',
            '2026-09-10',
            '2026-10-01',
            '2030-12-31',
            '오픈AI-브로드컴 10GW 커스텀 AI 칩 개발 및 공급 계약 체결 (누적 확보 용량 26GW로 확대)',
            'CUSTOM_ASIC',
            'C4',
            'AI타임스 (2026-09)',
            '99.raw/contracts/bookmarks_index.json'
        ),
        (
            'CON-2026-ANTH-AWS',
            'ANTHROPIC',
            'AMAZON',
            'INFRA_COMPUTE',
            280.0,
            'USD',
            '2026-09-08',
            '2026-10-01',
            '2036-09-30',
            '앤트로픽, AWS와 10년 장기 컴퓨트 약정 (총 $518B/14.8~15GW 규모 컴퓨팅 조달 패키지 중 최대 비중)',
            'CLOUD_COMPUTE',
            'C4',
            'The Information / StockSavvyShay',
            '99.raw/contracts/bookmarks_index.json'
        ),
        (
            'CON-2026-ANTH-GOOG',
            'ANTHROPIC',
            'GOOGLE',
            'INFRA_COMPUTE',
            150.0,
            'USD',
            '2026-09-08',
            '2026-10-01',
            '2036-09-30',
            '앤트로픽, 구글 클라우드 TPU 및 인프라 장기 약정 (15GW 조달 패키지 파트너십)',
            'TPU_CLOUD',
            'C4',
            'The Information / StockSavvyShay',
            '99.raw/contracts/bookmarks_index.json'
        ),
        (
            'CON-2026-ANTH-SKH',
            'ANTHROPIC',
            'SK_HYNIX',
            'SUPPLY',
            15.0,
            'USD',
            '2026-09-12',
            '2027-01-01',
            '2028-12-31',
            '앤트로픽 메모리 직납(Direct Buy) 계약 — CY27 메모리 수요의 20% 직납 개시, CY28 엔비디아 규모 구매력 도달 전망',
            'HBM_DRAM',
            'C3',
            'Edgewater Research / Sean',
            '99.raw/contracts/bookmarks_index.json'
        ),
        (
            'CON-2026-ANTH-MU',
            'ANTHROPIC',
            'MICRON',
            'SUPPLY',
            10.0,
            'USD',
            '2026-09-12',
            '2027-01-01',
            '2028-12-31',
            '앤트로픽-마이크론 메모리 직접 조달 및 공급 다변화 파트너십',
            'HBM_DRAM',
            'C3',
            'Edgewater Research / P Equity Research',
            '99.raw/contracts/bookmarks_index.json'
        )
    ]

    for c in contracts:
        cur.execute("""
            INSERT INTO contracts (
                contract_id, buyer_id, seller_id, contract_type, value_b,
                currency, announced_date, start_date, end_date, description,
                product_type, confidence, source, raw_source, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(contract_id) DO UPDATE SET
                value_b=excluded.value_b,
                description=excluded.description,
                product_type=excluded.product_type,
                source=excluded.source,
                raw_source=excluded.raw_source,
                updated_at=datetime('now');
        """, c)
    print(f"[SUCCESS] contracts 테이블 {len(contracts)}건 반영 완료")

    # 2. 팹 캐파 증설 (fab_capacity) — 마이크론 HBM 증설 추가
    fabs = [
        (
            'FAB-MU-TAICHUNG',
            'MICRON',
            '마이크론 타이중/히로시마 HBM 패키징 라인',
            '타이중',
            '대만/일본',
            '1-beta / HBM3E',
            'HBM_PACKAGING',
            45000.0,
            100000.0,
            '2025-Q4',
            '2026-Q4',
            6.5,
            92.0,
            88.0,
            'RAMPING',
            'NVIDIA, AMD, ANTHROPIC',
            '월 6만 장 증설하여 연말까지 총 10만 장(100k wspm) 캐파 도달 계획 (기존 대비 2배 증설)',
            '99.raw/contracts/bookmarks_index.json'
        )
    ]

    for f in fabs:
        cur.execute("""
            INSERT INTO fab_capacity (
                fab_id, entity_id, fab_name, location_city, location_country,
                process_node, fab_type, wspm_current, wspm_target, ramp_start_date,
                ramp_end_date, capex_invested_b, utilization_pct, yield_pct,
                status, key_customers, key_notes, raw_source, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(fab_id) DO UPDATE SET
                wspm_current=excluded.wspm_current,
                wspm_target=excluded.wspm_target,
                ramp_end_date=excluded.ramp_end_date,
                key_notes=excluded.key_notes,
                status=excluded.status,
                updated_at=datetime('now');
        """, f)
    print(f"[SUCCESS] fab_capacity 테이블 {len(fabs)}건 반영 완료")

    # 3. 기술 마일스톤 및 시나리오 신호 (milestones)
    milestones = [
        (
            'MS-2026-09-BRCM-HBM',
            'BROADCOM',
            '2026-09-05',
            'SCENARIO_SIGNAL',
            '메리츠증권 분석: 2028년 기업별 HBM 수요 전망에서 브로드컴(35~40bn Gb)이 엔비디아(30bn Gb)를 제치고 최대 수요처 등극 전망.',
            'HIGH',
            1,
            'C4',
            'Meritz Securities / Jukan',
            '99.raw/contracts/bookmarks_index.json'
        ),
        (
            'MS-2026-09-GOOG-RSI',
            'GOOGLE',
            '2026-09-08',
            'PRODUCT_LAUNCH',
            '구글 딥마인드, AGI 이후 ASI로 향하는 핵심 경로로 재귀적 자기개선(RSI: Recursive Self-Improvement) 공식 연구 및 파이프라인 공개.',
            'HIGH',
            0,
            'C4',
            'Google DeepMind / ByungJun Ahn',
            '99.raw/milestones/bookmarks_index.json'
        ),
        (
            'MS-2026-09-NOMURA-2030',
            'MICRON',
            '2026-09-06',
            'SCENARIO_SIGNAL',
            '노무라 증권: 2030년 글로벌 메모리 시장 매출 ~$3.7조 달러 전망 (데이터센터 비중 83%, 2026년 대비 3.5배 이상 폭증).',
            'MEDIUM',
            1,
            'C3',
            'Nomura Securities / P Equity Research',
            '99.raw/financials/bookmarks_index.json'
        ),
        (
            'MS-2026-09-DRAM-TIGHT',
            'SK_HYNIX',
            '2026-09-07',
            'SCENARIO_SIGNAL',
            '블룸버그·트렌드포스·HSBC: DRAM 공급 부족률(Sufficiency Ratio) 2028년까지 음(-)의 영역에 머물며 낸드 대비 구조적 타이트 국면 지속 전망.',
            'HIGH',
            1,
            'C4',
            'TrendForce / Bloomberg / HSBC / SemiconductorsX',
            '99.raw/financials/bookmarks_index.json'
        )
    ]

    for m in milestones:
        cur.execute("""
            INSERT INTO milestones (
                event_id, entity_id, event_date, category, description,
                impact_level, is_forecast, confidence, source, raw_source, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(event_id) DO UPDATE SET
                description=excluded.description,
                impact_level=excluded.impact_level,
                is_forecast=excluded.is_forecast,
                source=excluded.source,
                raw_source=excluded.raw_source,
                updated_at=datetime('now');
        """, m)
    print(f"[SUCCESS] milestones 테이블 {len(milestones)}건 반영 완료")

    conn.commit()
    conn.close()
    print("[SUCCESS] 전체 북마크 기반 인텔리전스 DB 적재 완료!")

if __name__ == "__main__":
    populate_intelligence()
