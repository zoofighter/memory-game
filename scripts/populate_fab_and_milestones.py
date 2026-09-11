#!/usr/bin/env python3
"""
populate_fab_and_milestones.py
--------------------------------------------------
Memory Claude 데이터베이스에 핵심 반도체 Fab 생산 캐파(fab_capacity)와
기술·공급망 마일스톤(milestones) 데이터를 적재하는 스크립트.

- 기준 시점: 2026년 9월 10일
- is_forecast 규칙:
  - 2026-Q2 이전 (확정 사건/수치) : is_forecast = 0
  - 2026-Q3 이후 (로드맵/목표치) : is_forecast = 1
"""

import sqlite3
import os
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "memory_claude.db")

FAB_DATA = [
    # TSMC
    (
        "FAB-TSMC-COWOS", "TSMC", "TSMC CoWoS Advanced Packaging (Tonglu/Chiayi)",
        "Chiayi", "Taiwan", "CoWoS-S / CoWoS-L", "PACKAGING",
        75000.0, 120000.0, "2024-Q1", "2026-Q4", 6.5, 92.0, 88.0,
        "OPERATING", "NVIDIA (B200/GB200/Rubin), AMD, Broadcom",
        "AI 가속기 칩 병목의 핵심 거점. 2024년 월 3.5만장에서 2026년 말 월 12만장으로 증설 진행.",
        "TSMC Quarterly Earnings & Supply Chain Reports"
    ),
    (
        "FAB-TSMC-F18", "TSMC", "Fab 18 (P6/P7/P8)",
        "Tainan", "Taiwan", "3nm (N3/N3E/N3P)", "FAB",
        60000.0, 85000.0, "2023-Q1", "2026-Q2", 15.0, 95.0, 85.0,
        "OPERATING", "Apple, NVIDIA (Blackwell), Qualcomm, AMD",
        "선단 3nm 주력 양산 기지. 엔비디아 블랙웰 GPU 다이 주력 생산.",
        "TSMC IR Presentation"
    ),
    (
        "FAB-TSMC-F20", "TSMC", "Fab 20 (P1~P4)",
        "Hsinchu", "Taiwan", "2nm (N2 / A16)", "FAB",
        15000.0, 65000.0, "2025-Q3", "2026-Q4", 20.0, 75.0, 70.0,
        "RAMP_UP", "Apple, NVIDIA (Rubin), AMD",
        "GAA(Gate-All-Around) 구조 첫 도입 차세대 2nm 팹. 2026년 하반기 리스크 프로덕션 및 양산 전환.",
        "Taiwan Commercial Times, TSMC Roadmap"
    ),
    (
        "FAB-TSMC-F21", "TSMC", "Arizona Fab 21 (Phase 1)",
        "Phoenix", "USA", "4nm (N4/N4P)", "FAB",
        8000.0, 25000.0, "2024-Q4", "2027-Q2", 12.0, 80.0, 78.0,
        "RAMP_UP", "Apple, NVIDIA, AMD, US DoD",
        "미국 현지 칩스법 보조금 지원 거점. 4nm 양산 안착 후 Phase 2 2nm 증설 추진.",
        "US CHIPS Act Filings"
    ),
    (
        "FAB-TSMC-F23", "TSMC", "Kumamoto Fab 23 (JASM Phase 1/2)",
        "Kumamoto", "Japan", "12nm / 6nm", "FAB",
        25000.0, 45000.0, "2024-Q2", "2027-Q1", 8.6, 90.0, 88.0,
        "OPERATING", "Sony, Automotive (Denso), Industrial",
        "소니 이미지센서 및 자동차용 마이크로컨트롤러/특수 AI 칩 생산.",
        "JASM Corporate Disclosures"
    ),

    # SK하이닉스
    (
        "FAB-SKH-M16", "SK_HYNIX", "이천 M16 팹",
        "Icheon", "South Korea", "1b nm (10nm급 5세대) DRAM", "FAB",
        55000.0, 75000.0, "2023-Q2", "2025-Q4", 5.8, 96.0, 90.0,
        "OPERATING", "NVIDIA (HBM3E), Apple, Global Server",
        "EUV 기반 HBM3E용 1b nm 코어 다이 핵심 생산 팹.",
        "SK hynix IR Disclosures"
    ),
    (
        "FAB-SKH-M15X", "SK_HYNIX", "청주 M15X 팹",
        "Cheongju", "South Korea", "HBM 패키징 및 차세대 DRAM", "PACKAGING",
        15000.0, 50000.0, "2025-Q2", "2026-Q3", 5.3, 85.0, 86.0,
        "CONSTRUCTION", "NVIDIA, CSPs (AWS, Google, MSFT)",
        "HBM 수요 급증에 맞춰 청주에 건설 중인 HBM 특화 생산기지. 2026년 가동 예정.",
        "SK hynix Board Resolution 2024"
    ),
    (
        "FAB-SKH-YONGIN", "SK_HYNIX", "용인 반도체 클러스터 1기",
        "Yongin", "South Korea", "1c nm DRAM / HBM4", "FAB",
        0.0, 85000.0, "2026-Q4", "2027-Q3", 9.4, 0.0, 0.0,
        "CONSTRUCTION", "NVIDIA (Rubin), Major AI Accelerator OEMs",
        "총 120조원 투자 메가 클러스터 1단계 팹. HBM4 16단 대량 양산 핵심 기지.",
        "Ministry of Trade, Industry and Energy Press Release"
    ),

    # 삼성전자
    (
        "FAB-SEC-P3", "SAMSUNG", "평택 P3 라인",
        "Pyeongtaek", "South Korea", "1b nm DRAM / V-NAND / Foundry 4nm", "FAB",
        70000.0, 90000.0, "2023-Q1", "2025-Q3", 14.0, 92.0, 87.0,
        "OPERATING", "NVIDIA, AMD, Broadcom, Samsung Mobile",
        "메모리와 파운드리가 공존하는 복합 팹. HBM3E 양산 공급 라인.",
        "Samsung Electronics IR"
    ),
    (
        "FAB-SEC-P4", "SAMSUNG", "평택 P4 라인",
        "Pyeongtaek", "South Korea", "1c nm DRAM / HBM4 / 2nm Foundry", "FAB",
        20000.0, 80000.0, "2025-Q1", "2026-Q4", 16.0, 78.0, 75.0,
        "RAMP_UP", "Global Big Tech, NVIDIA, Google TPU",
        "차세대 HBM4 턴키(메모리+파운드리+어드밴스드 패키징 원스톱) 생산 기지.",
        "Samsung Electronics Earnings Call"
    ),
    (
        "FAB-SEC-TAYLOR", "SAMSUNG", "미국 테일러 파운드리 팹",
        "Taylor", "USA", "4nm / 2nm 파운드리", "FAB",
        0.0, 30000.0, "2025-Q4", "2026-Q4", 17.0, 60.0, 65.0,
        "CONSTRUCTION", "US Fabless, Groq, AI Startups",
        "미국 텍사스 테일러 시 신규 파운드리 거점. 고객사 확보 및 2nm 전환 준비.",
        "US CHIPS Act Agreement"
    )
]

MILESTONES_DATA = [
    # 2022~2024 (과거 확정 사실: is_forecast = 0)
    (
        "MS-2022-01", "OPENAI", "2022-11-30", "PRODUCT_LAUNCH",
        "ChatGPT 대중에 공식 공개 — 글로벌 생성형 AI 및 초거대 GPU 인프라 투자 사이클 촉발.",
        "CRITICAL", 0, "C4", "OpenAI Announcement"
    ),
    (
        "MS-2023-01", "NVIDIA", "2023-03-21", "PRODUCT_LAUNCH",
        "Hopper H100 가속기 대량 납품 개시 — 데이터센터 매출 수직 상승 및 공급 부족 심화.",
        "CRITICAL", 0, "C4", "NVIDIA GTC 2023"
    ),
    (
        "MS-2023-02", "SK_HYNIX", "2023-06-15", "PARTNERSHIP",
        "엔비디아 H100향 HBM3 독점 공급권 확보 — AI 고대역폭 메모리 주도권 장악.",
        "HIGH", 0, "C4", "Supply Chain Analysis"
    ),
    (
        "MS-2023-03", "AMAZON", "2023-09-25", "PARTNERSHIP",
        "앤트로픽에 최대 $4B 투자 발표 및 AWS 전용 AI 가속기(Trainium/Inferentia) 파트너십 체결.",
        "HIGH", 0, "C4", "Amazon Corporate Press"
    ),
    (
        "MS-2024-01", "NVIDIA", "2024-03-18", "PRODUCT_LAUNCH",
        "GTC 2024에서 차세대 블랙웰(Blackwell B200 / GB200 NVL72) 아키텍처 공식 발표.",
        "CRITICAL", 0, "C4", "NVIDIA Keynote"
    ),
    (
        "MS-2024-02", "SK_HYNIX", "2024-03-19", "PRODUCT_LAUNCH",
        "세계 최초 8단 HBM3E 양산 개시 및 엔비디아 블랙웰 공급망 납품 착수.",
        "HIGH", 0, "C4", "SK hynix Press Release"
    ),
    (
        "MS-2024-03", "NVIDIA", "2024-06-02", "PRODUCT_LAUNCH",
        "컴퓨텍스(Computex)에서 '1년 주기 신제품 로드맵' 및 2026 루빈(Rubin) 아키텍처 예고.",
        "HIGH", 0, "C4", "NVIDIA Computex Keynote"
    ),
    (
        "MS-2024-04", "SK_HYNIX", "2024-09-26", "PRODUCT_LAUNCH",
        "세계 최초 12단 HBM3E(48GB) 양산 돌입 — Blackwell Ultra 및 대용량 LLM 추론 타깃.",
        "HIGH", 0, "C4", "SK hynix Press Release"
    ),
    (
        "MS-2024-05", "AMAZON", "2024-11-22", "PARTNERSHIP",
        "앤트로픽에 $4B 추가 투자 (누적 $8B) 및 Project Rainier(초대형 Trainium2 클러스터) 가동 합의.",
        "HIGH", 0, "C4", "AWS Press Release"
    ),

    # 2025~2026-Q2 (최근 실적 및 사건: is_forecast = 0)
    (
        "MS-2025-01", "TSMC", "2025-01-15", "FAB_MILESTONE",
        "대만 자이(Chiayi) CoWoS 첨단 패키징 신규 팹 장비 반입 및 시험 가동 개시.",
        "HIGH", 0, "C3", "Taiwan Commercial Times"
    ),
    (
        "MS-2025-02", "NVIDIA", "2025-04-10", "PRODUCT_LAUNCH",
        "Blackwell B200 및 GB200 NVL72 랙스케일 시스템 하이퍼스케일러 데이터센터 본격 출하.",
        "CRITICAL", 0, "C4", "NVIDIA Q1-2025 Earnings Call"
    ),
    (
        "MS-2025-03", "SAMSUNG", "2025-08-20", "PRODUCT_LAUNCH",
        "1b nm 기반 HBM3E 12단 주요 가속기 고객사 퀄 인증 통과 및 양산 공급망 합류.",
        "HIGH", 0, "C3", "Industry Rumors / SEC IR"
    ),
    (
        "MS-2026-01", "ASML", "2026-02-12", "PRODUCT_LAUNCH",
        "차세대 High-NA EUV(EXE:5200) 양산형 노광장비 TSMC 및 삼성전자 팹 인도 완료.",
        "MEDIUM", 0, "C3", "ASML Q4-2025 Earnings Report"
    ),
    (
        "MS-2026-02", "TSMC", "2026-05-18", "FAB_MILESTONE",
        "3nm 풀가동 상태에서 CoWoS-L 월 8만장 달성으로 블랙웰 공급 지연 완전 해소.",
        "HIGH", 0, "C3", "DigiTimes Research"
    ),

    # 2026-Q3 ~ 2028 (미래 전망 및 로드맵: is_forecast = 1)
    (
        "MS-2026-03", "TSMC", "2026-10-15", "FAB_MILESTONE",
        "신주 Fab 20 2nm(N2) 공정 리스크 프로덕션 개시 및 주요 수율 65% 돌파 목표.",
        "HIGH", 1, "C2", "TSMC Technology Symposium 2026"
    ),
    (
        "MS-2026-04", "SK_HYNIX", "2026-11-20", "FAB_MILESTONE",
        "청주 M15X 클린룸 준공 및 차세대 HBM4 어드밴스드 패키징 파일럿 라인 가동.",
        "HIGH", 1, "C2", "SK hynix Capex Outlook"
    ),
    (
        "MS-2027-01", "NVIDIA", "2027-01-10", "PRODUCT_LAUNCH",
        "차세대 Rubin R100 GPU (HBM4 16단 64GB 탑재) 최초 샘플 출하 및 파트너사 제공.",
        "CRITICAL", 1, "C2", "NVIDIA Roadmap Consensus"
    ),
    (
        "MS-2027-02", "SK_HYNIX", "2027-03-30", "PRODUCT_LAUNCH",
        "TSMC 파운드리 베이스 다이 협력 기반 HBM4 16단 대량 양산 및 출하 개시.",
        "CRITICAL", 1, "C2", "Semiconductor Industry Consensus"
    ),
    (
        "MS-2027-03", "SAMSUNG", "2027-06-15", "PRODUCT_LAUNCH",
        "평택 P4 1c nm 기반 HBM4 턴키(메모리+파운드리 4nm 베이스다이 원스톱) 대형 고객사 납품.",
        "HIGH", 1, "C2", "Samsung Semiconductor Strategy"
    ),
    (
        "MS-2027-04", "GOOGLE", "2027-08-20", "PRODUCT_LAUNCH",
        "자체 6세대 TPU(Ironwood) 인프라 비중 50% 돌파 및 외부 GPU 의존도 점진적 분산.",
        "HIGH", 1, "C2", "Google Cloud AI Roadmap"
    ),
    (
        "MS-2028-01", "TSMC", "2028-04-15", "FAB_MILESTONE",
        "미국 애리조나 Fab 21 2단계 2nm 라인 조기 가동 및 미국산 AI 칩 생산 본격화.",
        "MEDIUM", 1, "C1", "CHIPS Program Office"
    )
]

def populate_database():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print(f"Connecting to DB: {DB_PATH}")

    # 1. fab_capacity 데이터 적재
    print("\n[1/2] Populating 'fab_capacity' table...")
    cur.execute("DELETE FROM fab_capacity;")  # 초기화 후 클린 적재
    insert_fab_sql = """
    INSERT INTO fab_capacity (
        fab_id, entity_id, fab_name, location_city, location_country,
        process_node, fab_type, wspm_current, wspm_target, ramp_start_date,
        ramp_end_date, capex_invested_b, utilization_pct, yield_pct,
        status, key_customers, key_notes, raw_source
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    cur.executemany(insert_fab_sql, FAB_DATA)
    print(f" -> Inserted {len(FAB_DATA)} records into 'fab_capacity'.")

    # 2. milestones 데이터 적재
    print("\n[2/2] Populating 'milestones' table...")
    cur.execute("DELETE FROM milestones;")  # 초기화 후 클린 적재
    insert_ms_sql = """
    INSERT INTO milestones (
        event_id, entity_id, event_date, category, description,
        impact_level, is_forecast, confidence, source
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    cur.executemany(insert_ms_sql, MILESTONES_DATA)
    print(f" -> Inserted {len(MILESTONES_DATA)} records into 'milestones'.")

    conn.commit()

    # 정합성 검증
    cur.execute("SELECT count(*) FROM fab_capacity;")
    fab_cnt = cur.fetchone()[0]
    cur.execute("SELECT count(*), sum(case when is_forecast=0 then 1 else 0 end), sum(case when is_forecast=1 then 1 else 0 end) FROM milestones;")
    ms_cnt, ms_actual, ms_forecast = cur.fetchone()

    print("\n" + "="*50)
    print("Verification Results:")
    print(f" - fab_capacity: {fab_cnt} fabs loaded")
    print(f" - milestones:   {ms_cnt} events (Actual: {ms_actual}, Forecast: {ms_forecast})")
    print("="*50)

    conn.close()

if __name__ == "__main__":
    populate_database()
