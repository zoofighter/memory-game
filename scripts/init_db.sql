-- ============================================================
-- Memory Claude: init_db.sql
-- 생성일: 2026-09-11
-- 목적: 6개 핵심 테이블 + 1보조 테이블 + 시드 데이터
-- ============================================================

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ============================================================
-- 1. entities (기업 마스터)
-- ============================================================
CREATE TABLE IF NOT EXISTS entities (
    entity_id       TEXT PRIMARY KEY,
    name_en         TEXT NOT NULL,
    name_ko         TEXT NOT NULL,
    layer           TEXT NOT NULL,
        -- L1_AI_LAB, L2_HYPERSCALER, L3_COMPUTE,
        -- L4_FOUNDRY, L5_MEMORY, L6_OPTICAL, L7_INFRA
    country         TEXT,
    ticker          TEXT,
    is_public       INTEGER DEFAULT 1,
    description     TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

-- ============================================================
-- 2. contracts (계약·투자)
-- ============================================================
CREATE TABLE IF NOT EXISTS contracts (
    contract_id     TEXT PRIMARY KEY,
    buyer_id        TEXT NOT NULL REFERENCES entities(entity_id),
    seller_id       TEXT NOT NULL REFERENCES entities(entity_id),
    contract_type   TEXT NOT NULL,
        -- SUPPLY, INVESTMENT, PARTNERSHIP, LICENSE, SERVICE
    value_b         REAL,
    currency        TEXT DEFAULT 'USD',
    announced_date  TEXT,
    start_date      TEXT,
    end_date        TEXT,
    description     TEXT,
    product_type    TEXT,
    confidence      TEXT DEFAULT 'C3',
    source          TEXT,
    raw_source      TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_contract_buyer ON contracts(buyer_id);
CREATE INDEX IF NOT EXISTS idx_contract_seller ON contracts(seller_id);

-- ============================================================
-- 3. financials (실적·Capex)
-- ============================================================
CREATE TABLE IF NOT EXISTS financials (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id       TEXT NOT NULL REFERENCES entities(entity_id),
    period          TEXT NOT NULL,       -- 2026-Q1, 2026-FY 등
    metric          TEXT NOT NULL,
        -- REVENUE, OP_INCOME, NET_INCOME, CAPEX, GROSS_MARGIN,
        -- OP_MARGIN, HBM_REVENUE, GPU_REVENUE, CLOUD_REVENUE
    value           REAL NOT NULL,
    unit            TEXT DEFAULT 'B_USD',
    is_forecast     INTEGER DEFAULT 0,
    confidence      TEXT DEFAULT 'C3',
    source          TEXT,
    raw_source      TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_fin_entity ON financials(entity_id);
CREATE INDEX IF NOT EXISTS idx_fin_period ON financials(period);
CREATE INDEX IF NOT EXISTS idx_fin_metric ON financials(metric);

-- ============================================================
-- 4. milestones (과거·미래 이벤트)
-- ============================================================
CREATE TABLE IF NOT EXISTS milestones (
    event_id        TEXT PRIMARY KEY,
    entity_id       TEXT NOT NULL REFERENCES entities(entity_id),
    event_date      TEXT NOT NULL,
    category        TEXT NOT NULL,
        -- EARNINGS, PRODUCT_LAUNCH, FAB_MILESTONE, REGULATION,
        -- PARTNERSHIP, RESTRUCTURING, SCENARIO_SIGNAL, PRICE
    description     TEXT NOT NULL,
    impact_level    TEXT DEFAULT 'MEDIUM',
    is_forecast     INTEGER DEFAULT 0,
    confidence      TEXT DEFAULT 'C3',
    source          TEXT,
    raw_source      TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_ms_entity ON milestones(entity_id);
CREATE INDEX IF NOT EXISTS idx_ms_date ON milestones(event_date);

-- ============================================================
-- 5. fab_capacity (공장 증산·수율)
-- ============================================================
CREATE TABLE IF NOT EXISTS fab_capacity (
    fab_id              TEXT PRIMARY KEY,
    entity_id           TEXT NOT NULL REFERENCES entities(entity_id),
    fab_name            TEXT NOT NULL,
    location_city       TEXT,
    location_country    TEXT,
    process_node        TEXT,
    fab_type            TEXT DEFAULT 'FAB',
    wspm_current        REAL,
    wspm_target         REAL,
    ramp_start_date     TEXT,
    ramp_end_date       TEXT,
    capex_invested_b    REAL,
    utilization_pct     REAL,
    yield_pct           REAL,
    status              TEXT DEFAULT 'OPERATING',
    key_customers       TEXT,
    key_notes           TEXT,
    raw_source          TEXT,
    created_at          TEXT DEFAULT (datetime('now')),
    updated_at          TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_fab_entity ON fab_capacity(entity_id);
CREATE INDEX IF NOT EXISTS idx_fab_status ON fab_capacity(status);

-- ============================================================
-- 6. entity_strategy (전략·포지셔닝)
-- ============================================================
CREATE TABLE IF NOT EXISTS entity_strategy (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id       TEXT NOT NULL REFERENCES entities(entity_id),
    dimension       TEXT NOT NULL,
    summary         TEXT NOT NULL,
    detail          TEXT,
    confidence      TEXT DEFAULT 'C3',
    as_of_date      TEXT NOT NULL,
    source          TEXT,
    raw_source      TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_strategy_entity ON entity_strategy(entity_id);
CREATE INDEX IF NOT EXISTS idx_strategy_dimension ON entity_strategy(dimension);

-- ============================================================
-- 보조: entity_aliases (별칭)
-- ============================================================
CREATE TABLE IF NOT EXISTS entity_aliases (
    alias           TEXT PRIMARY KEY,
    entity_id       TEXT NOT NULL REFERENCES entities(entity_id)
);

-- ============================================================
-- 뷰: 기업별 계약 요약
-- ============================================================
CREATE VIEW IF NOT EXISTS v_contract_summary AS
SELECT
    e1.name_ko AS buyer,
    e2.name_ko AS seller,
    c.contract_type,
    c.value_b,
    c.product_type,
    c.announced_date,
    c.description
FROM contracts c
JOIN entities e1 ON c.buyer_id = e1.entity_id
JOIN entities e2 ON c.seller_id = e2.entity_id
ORDER BY c.value_b DESC;

-- ============================================================
-- 뷰: 기업별 실적 매트릭스
-- ============================================================
CREATE VIEW IF NOT EXISTS v_financials_matrix AS
SELECT
    e.name_ko,
    e.layer,
    f.period,
    f.metric,
    f.value,
    f.unit,
    CASE WHEN f.is_forecast = 1 THEN '예측' ELSE '실적' END AS data_type,
    f.confidence
FROM financials f
JOIN entities e ON f.entity_id = e.entity_id
ORDER BY e.layer, e.entity_id, f.period, f.metric;

-- ============================================================
-- SEED DATA: entities (21개사)
-- ============================================================
INSERT INTO entities (entity_id, name_en, name_ko, layer, country, ticker, is_public, description) VALUES
-- L1: AI 프론티어 랩
('ANTHROPIC',          'Anthropic',           '앤트로픽',         'L1_AI_LAB',       'US', NULL,   0, 'Claude AI 개발사, 구글·아마존 투자'),
('OPENAI',             'OpenAI',              '오픈AI',           'L1_AI_LAB',       'US', NULL,   0, 'GPT/ChatGPT 개발사, MS 투자'),
-- L2: 하이퍼스케일러 & 네오클라우드
('GOOGLE',             'Alphabet/Google',     '구글',             'L2_HYPERSCALER',  'US', 'GOOGL', 1, 'GCP + Gemini + TPU'),
('AMAZON',             'Amazon/AWS',          '아마존',           'L2_HYPERSCALER',  'US', 'AMZN',  1, 'AWS + Trainium + Bedrock'),
('MICROSOFT',          'Microsoft',           '마이크로소프트',   'L2_HYPERSCALER',  'US', 'MSFT',  1, 'Azure + OpenAI 파트너'),
('ORACLE',             'Oracle',              '오라클',           'L2_HYPERSCALER',  'US', 'ORCL',  1, 'OCI + AI 인프라 확장'),
('META',               'Meta Platforms',      '메타',             'L2_HYPERSCALER',  'US', 'META',  1, 'Llama 오픈소스 + MTIA ASIC'),
('COREWEAVE',          'CoreWeave',           '코어위브',         'L2_HYPERSCALER',  'US', NULL,    0, '엔비디아 전략 투자 GPU 특화 네오클라우드, 앤트로픽 $518B 공급 파트너'),
('NEBIUS',             'Nebius Group',        '네비우스',         'L2_HYPERSCALER',  'NL', 'NBIS',  1, '나스닥 상장 대규모 AI 인프라 및 GPU 네오클라우드'),
-- L3: 컴퓨팅 & 가속기
('NVIDIA',             'NVIDIA',              '엔비디아',         'L3_COMPUTE',      'US', 'NVDA',  1, 'GPU + CUDA + DGX Cloud'),
('AMD',                'AMD',                 'AMD',              'L3_COMPUTE',      'US', 'AMD',   1, 'MI300/MI400 GPU + EPYC CPU'),
('BROADCOM',           'Broadcom',            '브로드컴',         'L3_COMPUTE',      'US', 'AVGO',  1, 'AI ASIC 설계 + 네트워킹'),
('ARM',                'Arm Holdings',        'Arm',              'L3_COMPUTE',      'UK', 'ARM',   1, '서버 CPU 및 AI ASIC 아키텍처 라이선스'),
('INTEL',              'Intel',               '인텔',             'L3_COMPUTE',      'US', 'INTC',  1, '데이터센터 x86 제온 CPU 및 파운드리'),
-- L4: 파운드리, 장비 & 패키징
('TSMC',               'TSMC',                'TSMC',             'L4_FOUNDRY',      'TW', 'TSM',   1, 'N2/A16 선단공정 + CoWoS'),
('ASML',               'ASML',                'ASML',             'L4_FOUNDRY',      'NL', 'ASML',  1, 'EUV/High-NA EUV 독점'),
('APPLIED_MATERIALS',  'Applied Materials',   '어플라이드',       'L4_FOUNDRY',      'US', 'AMAT',  1, '반도체 증착·배선 및 첨단 패키징 장비 1위'),
('LAM_RESEARCH',       'Lam Research',        '램리서치',         'L4_FOUNDRY',      'US', 'LRCX',  1, 'HBM 3D 적층 및 DRAM 식각 장비 독점'),
('KLA',                'KLA Corporation',     'KLA',              'L4_FOUNDRY',      'US', 'KLAC',  1, '선단공정 및 패키징 수율 검사·계측 장비'),
('ASE',                'ASE Technology',      'ASE',              'L4_FOUNDRY',      'TW', 'ASX',   1, '글로벌 1위 OSAT, CoWoS 패키징 외주 파트너'),
('AMKOR',              'Amkor Technology',    '앰코',             'L4_FOUNDRY',      'US', 'AMKR',  1, '미국 애리조나 첨단 2.5D 패키징 협력사'),
-- L5: 메모리 & 스토리지
('SAMSUNG',            'Samsung Electronics', '삼성전자',         'L5_MEMORY',       'KR', '005930', 1, 'DRAM 1위 + HBM + 파운드리'),
('SK_HYNIX',           'SK hynix',            'SK하이닉스',       'L5_MEMORY',       'KR', '000660', 1, 'HBM 세계 1위 (점유율 50%+)'),
('MICRON',             'Micron Technology',   '마이크론',         'L5_MEMORY',       'US', 'MU',    1, 'HBM 3위 + 미국 유일 메모리'),
('WDC',                'Western Digital',     '샌디스크/WDC',     'L5_MEMORY',       'US', 'WDC',   1, 'NAND + SSD'),
('KIOXIA',             'Kioxia Holdings',     '키옥시아',         'L5_MEMORY',       'JP', '285A',  1, 'NAND 플래시 및 AI 추론용 eSSD'),
-- L6: 광통신 & 네트워킹
('MARVELL',            'Marvell Technology',  '마벨',             'L6_OPTICAL',      'US', 'MRVL',  1, 'AI DC 네트워킹 + 커스텀 ASIC'),
('COHERENT',           'Coherent/Novalit',    '노발리',           'L6_OPTICAL',      'US', 'COHR',  1, '광트랜시버 800G/1.6T'),
('ARISTA',             'Arista Networks',     '아리스타',         'L6_OPTICAL',      'US', 'ANET',  1, 'AI 클러스터 800G/1.6T 고속 Ethernet 스위치'),
-- L7: 인프라 & 특수
('SPACEX',             'SpaceX / xAI',        '스페이스X / xAI',  'L7_INFRA',        'US', NULL,    0, 'Starlink 위성망 + xAI Colossus 100k GPU 슈퍼컴퓨터 & 전력 인프라'),
('SOFTBANK',           'SoftBank Group',      '소프트뱅크',       'L7_INFRA',        'JP', '9984',  1, 'ARM + AI 투자 펀드'),
('APPLE',              'Apple',               '애플',             'L7_INFRA',        'US', 'AAPL',  1, 'TSMC 최대 고객 + 온디바이스 AI'),
-- L8: 전력 & 에너지 인프라
('VERTIV',             'Vertiv Holdings',     '버티브',           'L8_POWER',        'US', 'VRT',   1, 'AI 데이터센터 고밀도 액체냉각 및 배전 인프라 1위'),
('EATON',              'Eaton Corporation',   '이튼',             'L8_POWER',        'US', 'ETN',   1, '데이터센터 배전, 변압기, 고전압 UPS 및 전력 솔루션'),
('GE_VERNOVA',         'GE Vernova',          'GE 버노바',        'L8_POWER',        'US', 'GEV',   1, '데이터센터 가스터빈, 독립 발전 및 전력망 솔루션'),
('SCHNEIDER',          'Schneider Electric',  '슈나이더',         'L8_POWER',        'FR', 'SU',    1, '데이터센터 전력 분배, 냉각 및 인프라 자동화');


-- ============================================================
-- SEED DATA: contracts (핵심 계약 10건)
-- ============================================================
INSERT INTO contracts (contract_id, buyer_id, seller_id, contract_type, value_b, announced_date, description, product_type, confidence, source) VALUES
('CON-GOOG-ANTH-200B',  'GOOGLE',    'ANTHROPIC', 'INVESTMENT',   200.0, '2025-Q4', '구글, 앤트로픽에 $200B 투자 (현금+GCP 크레딧)', 'AI_MODEL', 'C4', '공식 발표'),
('CON-AMZN-ANTH-12B',   'AMAZON',    'ANTHROPIC', 'INVESTMENT',    12.0, '2025-Q1', '아마존, 앤트로픽에 $12B 투자', 'AI_MODEL', 'C4', '공식 발표'),
('CON-AMZN-OPAI',       'AMAZON',    'OPENAI',    'PARTNERSHIP',   NULL, '2026-Q1', '오픈AI, AWS Bedrock 입점 계약', 'AI_MODEL', 'C4', '공식 발표'),
('CON-MSFT-OPAI-13B',   'MICROSOFT', 'OPENAI',    'INVESTMENT',    13.0, '2023-Q1', 'MS, 오픈AI에 $13B 투자 (Azure 크레딧 포함)', 'AI_MODEL', 'C4', '공식 발표'),
('CON-GOOG-NVDA-GPU',   'GOOGLE',    'NVIDIA',    'SUPPLY',        30.0, '2026-Q1', '구글, 엔비디아 Blackwell GPU 대량 공급 계약', 'GPU', 'C3', '업계 추정'),
('CON-META-NVDA-GPU',   'META',      'NVIDIA',    'SUPPLY',        25.0, '2026-Q1', '메타, 엔비디아 GPU 대량 수주 (Llama 학습용)', 'GPU', 'C3', '업계 추정'),
('CON-META-BRCM-ASIC',  'META',      'BROADCOM',  'SUPPLY',        10.0, '2025-Q3', '메타, 브로드컴 MTIA ASIC 공동 개발', 'ASIC', 'C3', '업계 보도'),
('CON-NVDA-SKH-HBM',    'NVIDIA',    'SK_HYNIX',  'SUPPLY',        18.0, '2026-Q1', '엔비디아, SK하이닉스 HBM3E/HBM4 공급 계약', 'HBM', 'C4', '어닝콜'),
('CON-NVDA-SAM-HBM',    'NVIDIA',    'SAMSUNG',   'SUPPLY',        14.0, '2026-Q1', '엔비디아, 삼성전자 HBM4 공급 계약', 'HBM', 'C3', '업계 추정'),
('CON-NVDA-TSMC-FOUND', 'NVIDIA',    'TSMC',      'SUPPLY',        35.0, '2026-FY', '엔비디아, TSMC 파운드리 위탁 (Blackwell/Rubin)', 'FOUNDRY', 'C3', '업계 추정');

-- ============================================================
-- SEED DATA: financials (하이퍼스케일러 + 핵심 기업 실적)
-- ============================================================
INSERT INTO financials (entity_id, period, metric, value, unit, is_forecast, confidence, source) VALUES
-- 구글 Capex
('GOOGLE', '2024-FY', 'CAPEX',   52.5, 'B_USD', 0, 'C4', '10-K 공시'),
('GOOGLE', '2025-FY', 'CAPEX',   65.0, 'B_USD', 0, 'C4', '10-K 공시'),
('GOOGLE', '2026-FY', 'CAPEX',   76.7, 'B_USD', 0, 'C4', '가이던스'),
('GOOGLE', '2026-FY', 'REVENUE', 420.0, 'B_USD', 1, 'C3', '컨센서스'),
-- 아마존 Capex
('AMAZON', '2024-FY', 'CAPEX',   53.0, 'B_USD', 0, 'C4', '10-K 공시'),
('AMAZON', '2025-FY', 'CAPEX',   58.0, 'B_USD', 0, 'C4', '10-K 공시'),
('AMAZON', '2026-FY', 'CAPEX',   65.0, 'B_USD', 1, 'C3', '가이던스'),
-- MS Capex
('MICROSOFT', '2024-FY', 'CAPEX', 44.5, 'B_USD', 0, 'C4', '10-K 공시'),
('MICROSOFT', '2025-FY', 'CAPEX', 55.0, 'B_USD', 0, 'C4', '10-K 공시'),
('MICROSOFT', '2026-FY', 'CAPEX', 62.0, 'B_USD', 1, 'C3', '가이던스'),
-- 메타 Capex
('META', '2024-FY', 'CAPEX',   37.0, 'B_USD', 0, 'C4', '10-K 공시'),
('META', '2025-FY', 'CAPEX',   45.0, 'B_USD', 0, 'C4', '10-K 공시'),
('META', '2026-FY', 'CAPEX',   55.0, 'B_USD', 1, 'C3', '가이던스'),
-- 오라클 Capex
('ORACLE', '2025-FY', 'CAPEX',  16.0, 'B_USD', 0, 'C3', '공시'),
('ORACLE', '2026-FY', 'CAPEX',  22.0, 'B_USD', 1, 'C3', '가이던스'),
-- 엔비디아 실적
('NVIDIA', '2024-FY', 'REVENUE',  61.0, 'B_USD', 0, 'C4', '10-K 공시'),
('NVIDIA', '2025-FY', 'REVENUE', 130.0, 'B_USD', 0, 'C4', '10-K 공시'),
('NVIDIA', '2026-FY', 'REVENUE', 160.0, 'B_USD', 1, 'C3', '컨센서스'),
('NVIDIA', '2025-FY', 'GPU_REVENUE', 105.0, 'B_USD', 0, 'C4', '데이터센터 GPU'),
-- TSMC 실적
('TSMC', '2024-FY', 'REVENUE',  88.0, 'B_USD', 0, 'C4', '공시'),
('TSMC', '2025-FY', 'REVENUE', 105.0, 'B_USD', 0, 'C4', '공시'),
('TSMC', '2026-FY', 'REVENUE', 120.0, 'B_USD', 1, 'C3', '컨센서스'),
('TSMC', '2025-FY', 'CAPEX',    35.0, 'B_USD', 0, 'C4', '공시'),
-- 삼성전자 실적
('SAMSUNG', '2024-FY', 'REVENUE', 230.0, 'B_USD', 0, 'C4', '공시 (KRW→USD 환산)'),
('SAMSUNG', '2025-FY', 'REVENUE', 250.0, 'B_USD', 0, 'C4', '공시'),
('SAMSUNG', '2026-FY', 'REVENUE', 270.0, 'B_USD', 1, 'C3', '컨센서스'),
('SAMSUNG', '2025-FY', 'HBM_REVENUE', 8.0, 'B_USD', 0, 'C3', '추정'),
-- SK하이닉스 실적
('SK_HYNIX', '2024-FY', 'REVENUE', 50.0, 'B_USD', 0, 'C4', '공시'),
('SK_HYNIX', '2025-FY', 'REVENUE', 65.0, 'B_USD', 0, 'C4', '공시'),
('SK_HYNIX', '2026-FY', 'REVENUE', 75.0, 'B_USD', 1, 'C3', '컨센서스'),
('SK_HYNIX', '2025-FY', 'HBM_REVENUE', 20.0, 'B_USD', 0, 'C3', '추정'),
-- 브로드컴 실적
('BROADCOM', '2025-FY', 'REVENUE', 55.0, 'B_USD', 0, 'C4', '공시'),
('BROADCOM', '2026-FY', 'REVENUE', 70.0, 'B_USD', 1, 'C3', '컨센서스');

-- ============================================================
-- SEED DATA: entity_aliases
-- ============================================================
INSERT INTO entity_aliases (alias, entity_id) VALUES
('구글', 'GOOGLE'), ('알파벳', 'GOOGLE'), ('GOOGL', 'GOOGLE'),
('아마존', 'AMAZON'), ('AWS', 'AMAZON'), ('AMZN', 'AMAZON'),
('MS', 'MICROSOFT'), ('마소', 'MICROSOFT'), ('MSFT', 'MICROSOFT'),
('앤트로픽', 'ANTHROPIC'), ('앤쓰로픽', 'ANTHROPIC'),
('오픈AI', 'OPENAI'), ('오픈에이아이', 'OPENAI'),
('엔비디아', 'NVIDIA'), ('NVDA', 'NVIDIA'),
('삼성', 'SAMSUNG'), ('삼성전자', 'SAMSUNG'),
('SK하이닉스', 'SK_HYNIX'), ('하이닉스', 'SK_HYNIX'),
('마이크론', 'MICRON'), ('MU', 'MICRON'),
('브로드컴', 'BROADCOM'), ('AVGO', 'BROADCOM'),
('메타', 'META'), ('페이스북', 'META'),
-- xAI -> SPACEX 매핑
('xAI', 'SPACEX'), ('XAI', 'SPACEX'), ('xai', 'SPACEX'), ('엑스에이아이', 'SPACEX'), ('Colossus', 'SPACEX'), ('콜로서스', 'SPACEX'), ('Grok', 'SPACEX'),
-- 신규 확장 기업
('코어위브', 'COREWEAVE'), ('CoreWeave', 'COREWEAVE'), ('CRWV', 'COREWEAVE'),
('네비우스', 'NEBIUS'), ('Nebius', 'NEBIUS'), ('NBIS', 'NEBIUS'),
('Arm', 'ARM'), ('ARM', 'ARM'), ('암', 'ARM'),
('인텔', 'INTEL'), ('Intel', 'INTEL'), ('INTC', 'INTEL'),
('어플라이드', 'APPLIED_MATERIALS'), ('AMAT', 'APPLIED_MATERIALS'), ('Applied Materials', 'APPLIED_MATERIALS'),
('램리서치', 'LAM_RESEARCH'), ('Lam Research', 'LAM_RESEARCH'), ('LRCX', 'LAM_RESEARCH'),
('KLA', 'KLA'), ('KLAC', 'KLA'),
('ASE', 'ASE'), ('일월광', 'ASE'),
('앰코', 'AMKOR'), ('Amkor', 'AMKOR'), ('AMKR', 'AMKOR'),
('키옥시아', 'KIOXIA'), ('Kioxia', 'KIOXIA'),
('아리스타', 'ARISTA'), ('Arista', 'ARISTA'), ('ANET', 'ARISTA'),
('버티브', 'VERTIV'), ('Vertiv', 'VERTIV'), ('VRT', 'VERTIV'),
('이튼', 'EATON'), ('Eaton', 'EATON'), ('ETN', 'EATON'),
('GE버노바', 'GE_VERNOVA'), ('GE Vernova', 'GE_VERNOVA'), ('GEV', 'GE_VERNOVA'),
('슈나이더', 'SCHNEIDER'), ('Schneider', 'SCHNEIDER');

-- 완료 확인
SELECT '=== DB 초기화 완료 ===' AS status;
SELECT '기업 수: ' || COUNT(*) FROM entities;
SELECT '계약 수: ' || COUNT(*) FROM contracts;
SELECT '실적 데이터: ' || COUNT(*) FROM financials;
