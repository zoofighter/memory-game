-- ============================================================
-- Memory Claude: add_earnings_table.sql
-- 목적: 분기별 실적 발표(Earnings Reports) 전용 테이블 및 시계열 데이터(2019~2026)
-- ============================================================

CREATE TABLE IF NOT EXISTS earnings_reports (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id           TEXT NOT NULL REFERENCES entities(entity_id),
    period              TEXT NOT NULL,          -- 예: '2019-Q4', '2020-Q4', '2024-Q4', '2025-Q4'
    report_date         TEXT,                   -- 실적 발표일 (YYYY-MM-DD)
    
    -- [1] 주요 손익 실적 (Actuals)
    revenue             REAL NOT NULL,          -- 매출
    op_income           REAL,                   -- 영업이익
    net_income          REAL,                   -- 당기순이익
    unit                TEXT DEFAULT 'B_USD',   -- 단위: B_USD(10억 달러), T_KRW(조 원)
    
    -- [2] 주당순이익 (EPS) & 시장 기대치
    eps_actual          REAL,                   -- 발표된 실제 EPS ($ 또는 원)
    eps_consensus       REAL,                   -- 시장 예상 EPS ($ 또는 원)
    consensus_revenue   REAL,                   -- 시장 예상 매출
    beat_miss_status    TEXT,                   -- 'TRIPLE_BEAT', 'BEAT', 'MISS', 'INLINE'
    
    -- [3] 수익성 및 투자 지표 (반도체/빅테크 핵심)
    gross_margin_pct    REAL,                   -- 매출총이익률 (Gross Margin %)
    op_margin_pct       REAL,                   -- 영업이익률 (Operating Margin %)
    capex               REAL,                   -- 해당 분기 설비투자액
    
    -- [4] 매출 비중 및 차기 가이던스 (텍스트)
    revenue_breakdown   TEXT,                   -- 사업부별 매출 비중 (텍스트)
    guidance_next_q     TEXT,                   -- 다음 분기 가이던스 및 전망
    
    -- [5] 어닝콜 핵심 코멘트 & 출처
    key_takeaways       TEXT,                   -- 실적발표 핵심 코멘트 / CEO 발언
    source              TEXT,                   -- 공시 및 IR 자료 출처
    created_at          TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_earnings_entity ON earnings_reports(entity_id);
CREATE INDEX IF NOT EXISTS idx_earnings_period ON earnings_reports(period);
CREATE INDEX IF NOT EXISTS idx_earnings_date ON earnings_reports(report_date);

-- ============================================================
-- 뷰: 분기 실적 요약 및 어닝 서프라이즈 분석 뷰
-- ============================================================
DROP VIEW IF EXISTS v_earnings_summary;
CREATE VIEW v_earnings_summary AS
SELECT 
    e.name_ko AS 기업,
    r.period AS 분기,
    r.report_date AS 발표일,
    r.revenue || ' ' || r.unit AS 매출,
    r.op_income || ' ' || r.unit AS 영업익,
    CASE 
        WHEN r.consensus_revenue IS NOT NULL 
        THEN ROUND(r.revenue - r.consensus_revenue, 2) || ' ' || r.unit
        ELSE '-' 
    END AS 매출서프라이즈,
    COALESCE('$' || r.eps_actual, '-') AS 실제EPS,
    COALESCE('$' || r.eps_consensus, '-') AS 예상EPS,
    COALESCE(r.gross_margin_pct || '%', '-') AS 매출총이익률,
    COALESCE(r.beat_miss_status, '-') AS 실적판정,
    r.revenue_breakdown AS 매출비중,
    r.guidance_next_q AS 차기가이던스
FROM earnings_reports r
JOIN entities e ON r.entity_id = e.entity_id
ORDER BY r.period DESC, e.layer, e.entity_id;

-- ============================================================
-- 시드 데이터 투입: 2019~2020 (AI 이전) vs 2024~2025/2026 (AI 본격화)
-- ============================================================

-- [1] 엔비디아 (NVIDIA)
-- 2019-Q4 (2020년 2월 13일 발표): 게이밍 중심 시절
INSERT INTO earnings_reports (
    entity_id, period, report_date, revenue, op_income, net_income, unit,
    eps_actual, eps_consensus, consensus_revenue, beat_miss_status,
    gross_margin_pct, op_margin_pct, capex,
    revenue_breakdown, guidance_next_q, key_takeaways, source
) VALUES (
    'NVIDIA', '2019-Q4', '2020-02-13', 3.11, 0.99, 0.95, 'B_USD',
    0.47, 0.41, 3.01, 'BEAT',
    64.9, 31.8, 0.15,
    '게이밍: 48.0% ($1.49B), 데이터센터: 31.0% ($0.97B), 프로비즈: 11.0% ($0.33B), 오토: 5.0% ($0.16B)',
    '1분기 매출 가이던스 $3.00B',
    '데이터센터 매출 분기 첫 $1B 육박, RTX 튜링 게이밍 카드 호조',
    'NVIDIA IR FY2020 Q4 10-K'
);

-- 2020-Q4 (2021년 2월 24일 발표): 언택트 및 멜라녹스 인수 직후
INSERT INTO earnings_reports (
    entity_id, period, report_date, revenue, op_income, net_income, unit,
    eps_actual, eps_consensus, consensus_revenue, beat_miss_status,
    gross_margin_pct, op_margin_pct, capex,
    revenue_breakdown, guidance_next_q, key_takeaways, source
) VALUES (
    'NVIDIA', '2020-Q4', '2021-02-24', 5.00, 1.51, 1.46, 'B_USD',
    0.78, 0.70, 4.82, 'BEAT',
    63.1, 30.2, 0.23,
    '게이밍: 50.0% ($2.50B), 데이터센터: 38.0% ($1.90B), 프로비즈: 6.0% ($0.31B), 오토: 3.0% ($0.15B)',
    '1분기 매출 가이던스 $5.30B',
    'Ampere 아키텍처 GPU(A100 및 RTX 30) 판매 본격 가속',
    'NVIDIA IR FY2021 Q4 10-K'
);

-- 2024-Q4 (2025년 2월 26일 발표): 생성형 AI 대폭발
INSERT INTO earnings_reports (
    entity_id, period, report_date, revenue, op_income, net_income, unit,
    eps_actual, eps_consensus, consensus_revenue, beat_miss_status,
    gross_margin_pct, op_margin_pct, capex,
    revenue_breakdown, guidance_next_q, key_takeaways, source
) VALUES (
    'NVIDIA', '2024-Q4', '2025-02-26', 39.3, 24.2, 22.1, 'B_USD',
    0.89, 0.84, 37.8, 'TRIPLE_BEAT',
    73.5, 61.6, 1.20,
    '데이터센터: 88.0% ($34.6B), 게이밍: 8.5% ($3.3B), 프로비즈: 1.8% ($0.7B), 오토: 1.1% ($0.4B)',
    '1분기 매출 가이던스 $43.0B ±2% (블랙웰 양산 본격화)',
    'Hopper(H100/H200) 수요 여전히 강력, Blackwell 전량 완판 수준',
    'NVIDIA IR FY2025 Q4 10-K'
);

-- 2025-Q4 (2026년 2월 25일 발표): Blackwell 슈퍼사이클
INSERT INTO earnings_reports (
    entity_id, period, report_date, revenue, op_income, net_income, unit,
    eps_actual, eps_consensus, consensus_revenue, beat_miss_status,
    gross_margin_pct, op_margin_pct, capex,
    revenue_breakdown, guidance_next_q, key_takeaways, source
) VALUES (
    'NVIDIA', '2025-Q4', '2026-02-25', 54.0, 35.1, 31.5, 'B_USD',
    1.25, 1.18, 51.5, 'TRIPLE_BEAT',
    75.0, 65.0, 1.80,
    '데이터센터: 91.0% ($49.1B), 게이밍: 6.5% ($3.5B), 기타: 2.5% ($1.4B)',
    '2026-Q1 매출 $58.0B 전망 (Rubin 아키텍처 언급)',
    'GB200 NVL72 랙스케일 납품 가속화, 추론 수요 폭증',
    '2025-Q4 어닝콜'
);

-- [2] TSMC (TSMC)
-- 2019-Q4 (2020년 1월 16일 발표)
INSERT INTO earnings_reports (
    entity_id, period, report_date, revenue, op_income, net_income, unit,
    eps_actual, eps_consensus, consensus_revenue, beat_miss_status,
    gross_margin_pct, op_margin_pct, capex,
    revenue_breakdown, guidance_next_q, key_takeaways, source
) VALUES (
    'TSMC', '2019-Q4', '2020-01-16', 10.39, 4.07, 3.82, 'B_USD',
    0.73, 0.70, 10.20, 'BEAT',
    50.2, 39.2, 3.80,
    '스마트폰: 53%, HPC: 29%, IoT: 8%, 오토: 4%',
    '1분기 매출 $10.2B~$10.3B 가이던스',
    '7nm 공정 풀가동, 5nm 2020년 상반기 양산 순항 발표',
    'TSMC IR 2019-Q4'
);

-- 2024-Q4 (2025년 1월 16일 발표)
INSERT INTO earnings_reports (
    entity_id, period, report_date, revenue, op_income, net_income, unit,
    eps_actual, eps_consensus, consensus_revenue, beat_miss_status,
    gross_margin_pct, op_margin_pct, capex,
    revenue_breakdown, guidance_next_q, key_takeaways, source
) VALUES (
    'TSMC', '2024-Q4', '2025-01-16', 26.88, 12.77, 11.52, 'B_USD',
    1.94, 1.85, 26.10, 'BEAT',
    57.8, 47.5, 9.50,
    'HPC(고성능컴퓨팅/AI): 53%, 스마트폰: 35%, IoT: 5%, 오토: 5%',
    '1분기 매출 $25.0B~$25.8B (전년비 +35% 성장 유지)',
    'CoWoS 패키징 용량 전년 대비 2배 증설 완료, AI 가속기 주문 지속 초과',
    'TSMC IR 2024-Q4'
);

-- [3] SK하이닉스 (SK_HYNIX)
-- 2019-Q4 (2020년 1월 31일 발표): 메모리 다운턴 시기
INSERT INTO earnings_reports (
    entity_id, period, report_date, revenue, op_income, net_income, unit,
    eps_actual, eps_consensus, consensus_revenue, beat_miss_status,
    gross_margin_pct, op_margin_pct, capex,
    revenue_breakdown, guidance_next_q, key_takeaways, source
) VALUES (
    'SK_HYNIX', '2019-Q4', '2020-01-31', 6.92, 0.24, -0.12, 'T_KRW',
    NULL, NULL, 6.75, 'INLINE',
    21.0, 3.4, 2.50,
    'DRAM: 75%, NAND: 22%, 기타: 3%',
    'DRAM 출하량 한 자릿수 중반 성장 목표, 설비투자 보수적 집행',
    '메모리 단가 하락으로 수익성 급감, 재고 소진 주력',
    'SK하이닉스 2019년 4분기 경영실적'
);

-- 2024-Q4 (2025년 1월 23일 발표): HBM 독점 프리미엄
INSERT INTO earnings_reports (
    entity_id, period, report_date, revenue, op_income, net_income, unit,
    eps_actual, eps_consensus, consensus_revenue, beat_miss_status,
    gross_margin_pct, op_margin_pct, capex,
    revenue_breakdown, guidance_next_q, key_takeaways, source
) VALUES (
    'SK_HYNIX', '2024-Q4', '2025-01-23', 19.80, 8.10, 6.20, 'T_KRW',
    NULL, NULL, 19.10, 'TRIPLE_BEAT',
    52.0, 40.9, 4.80,
    'DRAM(HBM 포함): 82% (이 중 HBM이 DRAM 매출의 40% 초과), NAND(eSSD 포함): 16%',
    'HBM3E 12단 본격 확대, 2025년 HBM 물량 이미 전량 솔드아웃',
    '분기 영업이익률 40% 돌파, HBM 시장 1위 입지 재확인',
    'SK하이닉스 2024년 4분기 경영실적'
);

-- [4] 삼성전자 (SAMSUNG)
-- 2019-Q4 (2020년 1월 30일 발표)
INSERT INTO earnings_reports (
    entity_id, period, report_date, revenue, op_income, net_income, unit,
    eps_actual, eps_consensus, consensus_revenue, beat_miss_status,
    gross_margin_pct, op_margin_pct, capex,
    revenue_breakdown, guidance_next_q, key_takeaways, source
) VALUES (
    'SAMSUNG', '2019-Q4', '2020-01-30', 59.88, 7.16, 5.23, 'T_KRW',
    NULL, NULL, 60.50, 'INLINE',
    36.2, 12.0, 8.70,
    '반도체(DS): 28.0% (16.79조), 모바일(IM): 41.6% (24.91조), 디스플레이: 13.4% (8.05조), 가전(CE): 18.4% (11.02조)',
    '1분기 비수기 진입 예상, 5G 스마트폰 및 서버 DRAM 수요 회복 기대',
    '반도체 영업이익 3.45조 원 기록 (메모리 가격 하락 영향)',
    '삼성전자 2019년 4분기 경영실적'
);

-- 2024-Q4 (2025년 1월 31일 발표)
INSERT INTO earnings_reports (
    entity_id, period, report_date, revenue, op_income, net_income, unit,
    eps_actual, eps_consensus, consensus_revenue, beat_miss_status,
    gross_margin_pct, op_margin_pct, capex,
    revenue_breakdown, guidance_next_q, key_takeaways, source
) VALUES (
    'SAMSUNG', '2024-Q4', '2025-01-31', 75.80, 6.50, 5.80, 'T_KRW',
    NULL, NULL, 78.20, 'MISS',
    34.5, 8.6, 12.50,
    '반도체(DS): 38.0% (28.8조), 모바일(MX): 34.0% (25.8조), 디스플레이: 12.0% (9.1조), 가전: 16.0% (12.1조)',
    'HBM3E 공급 확대 및 파운드리 수주 회복 추진',
    'DS 부문 성과급 충당금 및 HBM 주요 고객사 퀄테스트 지연으로 영업익 기대치 하회',
    '삼성전자 2024년 4분기 경영실적'
);

-- [5] 마이크로소프트 (MICROSOFT)
-- 2019-Q4 (2020년 1월 29일 발표)
INSERT INTO earnings_reports (
    entity_id, period, report_date, revenue, op_income, net_income, unit,
    eps_actual, eps_consensus, consensus_revenue, beat_miss_status,
    gross_margin_pct, op_margin_pct, capex,
    revenue_breakdown, guidance_next_q, key_takeaways, source
) VALUES (
    'MICROSOFT', '2019-Q4', '2020-01-29', 36.91, 13.89, 11.65, 'B_USD',
    1.51, 1.32, 35.68, 'BEAT',
    67.0, 37.6, 4.50,
    'Intelligent Cloud(Azure): 32% ($11.9B), Productivity: 32% ($11.8B), Personal Computing: 36% ($13.2B)',
    '클라우드 상업용 매출 지속 견조',
    'Azure 성장률 +62%, 클라우드 전환 초기 가속 단계',
    'Microsoft IR FY20 Q2'
);

-- 2024-Q4 (2025년 1월 29일 발표)
INSERT INTO earnings_reports (
    entity_id, period, report_date, revenue, op_income, net_income, unit,
    eps_actual, eps_consensus, consensus_revenue, beat_miss_status,
    gross_margin_pct, op_margin_pct, capex,
    revenue_breakdown, guidance_next_q, key_takeaways, source
) VALUES (
    'MICROSOFT', '2024-Q4', '2025-01-29', 69.63, 31.64, 24.11, 'B_USD',
    3.23, 3.11, 68.80, 'BEAT',
    69.2, 45.4, 16.50,
    'Intelligent Cloud(Azure): 42% ($29.3B), Productivity: 34% ($23.8B), Personal Computing: 24% ($16.5B)',
    '3분기 Capex 추가 확대 예고 (AI 인프라 투자 지속)',
    'Azure 성장률 중 AI 기여분 12%p 달성, 공급 부족 지속',
    'Microsoft IR FY25 Q2'
);
