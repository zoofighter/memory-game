#!/usr/bin/env python3
"""
populate_datacenter_capacity.py
--------------------------------------------------
Memory Claude 데이터베이스에 빅테크 하이퍼스케일러의
핵심 AI 데이터센터 전력/클러스터 용량(datacenter_capacity) 데이터를 적재하는 스크립트.

- 기준 시점: 2026년 9월 10일
- 전력 단위: MW (Megawatts), GW = 1,000 MW
- 통화 단위: USD Billion
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "memory_claude.db")

DC_DATA = [
    # ── Microsoft ──
    (
        "DC-MSFT-MT-PLEASANT", "MICROSOFT", "마운트 플레전트 AI 슈퍼캠퍼스",
        "Wisconsin", "USA", 200.0, 1000.0, "Grid + 전력사 가스/신재생",
        "Direct Liquid Cooling (액체 냉각)", 100000,
        "NVIDIA Blackwell (GB200 NVL72)", "2026-Q4", "CONSTRUCTION", 3.3,
        "오픈AI 및 자체 AI 서비스 구동을 위한 기가와트(1GW)급 초대형 데이터센터.",
        "Microsoft Corporate Announcements & Local Filings"
    ),
    (
        "DC-MSFT-THREE-MILE", "MICROSOFT", "3마일 원전(Crane Clean Energy) 직결 캠퍼스",
        "Pennsylvania", "USA", 0.0, 835.0, "Nuclear PPA (100% 원자력 직결)",
        "Direct Liquid Cooling", 150000,
        "Blackwell Ultra / Rubin R100", "2028-Q1", "PLANNED", 1.6,
        "콘스텔레이션 에너지와 20년 PPA 계약 체결. 퇴역 3마일 원전 1호기를 재가동하여 835MW 전량을 MS 전용으로 공급받는 프로젝트.",
        "Constellation Energy & MSFT PPA Contract (2024)"
    ),
    (
        "DC-MSFT-BOYDTON", "MICROSOFT", "보이드턴 버지니아 메가 캠퍼스",
        "Virginia", "USA", 350.0, 600.0, "PJM Grid + 원전 전력 PPA",
        "Hybrid Cooling (공랭+수랭)", 80000,
        "NVIDIA H100 / H200 / B200", "2025-Q4", "OPERATING", 2.5,
        "미국 동부 최대 규모의 애저(Azure) 핵심 가속기 클러스터 거점.",
        "Virginia State Corporate Commission Filings"
    ),

    # ── Amazon (AWS) ──
    (
        "DC-AMZN-CUMULUS", "AMAZON", "서스퀘하나 원전 직결 캠퍼스 (Cumulus Data Center)",
        "Pennsylvania", "USA", 120.0, 960.0, "Susquehanna Nuclear (탈렌 에너지 100% 원전 PPA)",
        "Direct-to-Chip Liquid Cooling", 150000,
        "AWS Trainium2 / NVIDIA Blackwell", "2026-Q4", "CONSTRUCTION", 1.2,
        "탈렌 에너지 원자력 발전소 부지 내 직접 연결된 960MW 캠퍼스 인수. 전력망 거치지 않는 무탄소 기저부하 확보.",
        "AWS Talen Energy Deal Filing (2024)"
    ),
    (
        "DC-AMZN-OHIO-AI", "AMAZON", "오하이오 뉴올버니 AI 메가 허브 (Project Rainier)",
        "Ohio", "USA", 400.0, 1200.0, "AEP Grid + 전용 가스 발전 백업",
        "Direct Liquid Cooling", 200000,
        "Trainium2 / Inferentia2 / B200", "2026-Q3", "CONSTRUCTION", 7.8,
        "앤트로픽 전용 초대형 AI 학습 클러스터(Project Rainier)의 핵심 물리적 인프라 거점.",
        "Amazon 10-Q & Ohio Development Dept"
    ),
    (
        "DC-AMZN-VIRGINIA", "AMAZON", "북부 버지니아 데이터센터 클러스터",
        "Virginia", "USA", 800.0, 1500.0, "Dominion Energy Grid + 신재생 PPA",
        "Air & Liquid Hybrid", 120000,
        "NVIDIA Hopper / Blackwell", "2025-Q3", "OPERATING", 10.0,
        "글로벌 인터넷 트래픽의 핵심 관문이자 AWS의 최대 규모 상용 AI 클러스터.",
        "AWS Global Infrastructure Reports"
    ),

    # ── Alphabet (Google) ──
    (
        "DC-GOOGL-COUNCIL", "ALPHABET", "아이오와 카운실 블러프스 AI 허브",
        "Iowa", "USA", 500.0, 900.0, "MidAmerican 풍력/원자력 + 그리드",
        "Direct Liquid Cooling", 120000,
        "Google TPU v5p / TPU v6 (Trillium)", "2026-Q2", "OPERATING", 4.0,
        "구글의 핵심 자체 TPU 기반 초거대 제미나이(Gemini) 모델 훈련 및 추론 전용 캠퍼스.",
        "Google Environmental Report & Iowa EDC"
    ),
    (
        "DC-GOOGL-KAIROS", "ALPHABET", "카이로스 파워 SMR 연계 AI 캠퍼스",
        "Tennessee/TBD", "USA", 0.0, 500.0, "Kairos Power SMR (소형 모듈 원전 7기, 총 500MW)",
        "Closed-loop Liquid Cooling", 100000,
        "TPU v6 / TPU v7 (Ironwood)", "2027-Q4", "PLANNED", 3.0,
        "빅테크 최초의 SMR 직구매 계약. 2027년 첫 SMR 가동을 시작으로 2030년까지 500MW 전량 AI 데이터센터 투입.",
        "Google Kairos Power Agreement (2024)"
    ),
    (
        "DC-GOOGL-HENDERSON", "ALPHABET", "네바다 헨더슨 AI 인프라 캠퍼스",
        "Nevada", "USA", 250.0, 650.0, "태양광 + Fervo 지열발전 + NV Energy Grid",
        "Advanced Closed Loop Cooling", 80000,
        "TPU v5e / NVIDIA Blackwell", "2026-Q4", "RAMP_UP", 2.2,
        "차세대 청정 지열 발전 및 태양광 결합 24/7 무탄소 데이터센터 실험 거점.",
        "Nevada Governor's Office of Economic Development"
    ),

    # ── Meta ──
    (
        "DC-META-JEFFERSON", "META", "인디애나 제퍼슨빌 AI 데이터센터",
        "Indiana", "USA", 150.0, 800.0, "Duke Energy Grid + 솔라 PPA",
        "Direct-to-Chip Liquid Cooling", 150000,
        "Meta MTIA v2 / NVIDIA B200", "2026-Q4", "CONSTRUCTION", 0.8,
        "자체 AI 추천 엔진(MTIA)과 Llama 시리즈 차세대 모델 서빙을 위해 설계된 차세대 액체 냉각 캠퍼스.",
        "Meta Infrastructure Press Releases"
    ),
    (
        "DC-META-LOUISIANA", "META", "루이지애나 리치랜드 패리시 AI 슈퍼캠퍼스",
        "Louisiana", "USA", 0.0, 1500.0, "Entergy Grid + 원자력/가스 복합",
        "Next-gen Liquid Submersion Cooling", 250000,
        "NVIDIA Rubin R100 / MTIA v3", "2027-Q3", "PLANNED", 10.0,
        "메타 역사상 최대 규모의 1.5GW 초대형 AI 허브 계획. 2027년 Llama 5 이후 초거대 모델 학습용.",
        "Louisiana Economic Development Official Release"
    ),

    # ── Oracle / xAI ──
    (
        "DC-ORCL-MEMPHIS", "ORACLE", "멤피스 '콜로서스(Colossus)' 클러스터 (xAI 파트너십)",
        "Tennessee", "USA", 150.0, 300.0, "TVA Grid + 현장 이동형 천연가스 터빈 발전",
        "Supermicro Direct Liquid Cooling", 100000,
        "NVIDIA H100 (10만장) → H200/GB200 (30만장)", "2026-Q2", "OPERATING", 2.0,
        "xAI(일론 머스크)와 오라클이 구축한 세계 최대 단일 가속기 훈련 클러스터. 122일 만에 10만 장 가동.",
        "xAI & Oracle Public Disclosures (2024)"
    ),
    (
        "DC-ORCL-SMR-HUB", "ORACLE", "기가와트(GW)급 소형원전(SMR) 데이터센터 캠퍼스",
        "Location Pending", "USA", 0.0, 1000.0, "SMR 소형 원자로 3기 (총 1GW)",
        "Advanced Liquid Cooling", 200000,
        "Blackwell / Rubin / Custom ASIC", "2028-Q2", "PLANNED", 5.0,
        "오라클 래리 엘리슨 회장이 발표한 1GW 규모 SMR 직결 AI 데이터센터. 허가 및 착공 준비 단계.",
        "Oracle Q1-FY2025 Earnings Call"
    )
]

def populate():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print(f"Connecting to DB: {DB_PATH}")
    print("\n[1/1] Populating 'datacenter_capacity' table...")
    cur.execute("DELETE FROM datacenter_capacity;")

    insert_sql = """
    INSERT INTO datacenter_capacity (
        dc_id, entity_id, dc_name, location_state, location_country,
        power_mw_current, power_mw_target, power_source, cooling_type,
        gpu_cluster_target, primary_chips, online_date, status,
        capex_est_b, key_notes, source
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    cur.executemany(insert_sql, DC_DATA)
    conn.commit()

    cur.execute("SELECT count(*), sum(power_mw_current), sum(power_mw_target), sum(gpu_cluster_target) FROM datacenter_capacity;")
    cnt, p_curr, p_tgt, gpu_total = cur.fetchone()

    print("\n" + "="*50)
    print("Datacenter Capacity Verification Results:")
    print(f" - 데이터센터 수: {cnt}개 캠퍼스 등록 완료")
    print(f" - 현재 전력 용량: {p_curr:,.0f} MW ({p_curr/1000:.2f} GW)")
    print(f" - 최종 목표 전력: {p_tgt:,.0f} MW ({p_tgt/1000:.2f} GW)")
    print(f" - 탑재 목표 GPU/가속기 합계: {gpu_total:,.0f}대")
    print("="*50)

    conn.close()

if __name__ == "__main__":
    populate()
