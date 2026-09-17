-- ============================================================
-- scripts/add_entities_l8_expansion.sql
-- 작성일: 2026-09-16
-- 목적: L8_POWER 신설 및 xAI의 SpaceX 통합, 
--       P0/P1 핵심 기업(네오클라우드, 장비, 패키징, 전력 등) 안전한 UPSERT
-- ============================================================

BEGIN TRANSACTION;

-- 1. SpaceX 엔티티에 xAI 통합 업데이트
INSERT INTO entities (entity_id, name_en, name_ko, layer, country, ticker, is_public, description, updated_at)
VALUES (
    'SPACEX',
    'SpaceX / xAI',
    '스페이스X / xAI',
    'L7_INFRA',
    'US',
    NULL,
    0,
    'Starlink 저궤도 위성 통신망 + xAI Colossus 100k GPU 슈퍼컴퓨터 및 자체 가스터빈 전력 인프라',
    datetime('now')
)
ON CONFLICT(entity_id) DO UPDATE SET
    name_en=excluded.name_en,
    name_ko=excluded.name_ko,
    description=excluded.description,
    updated_at=datetime('now');

-- 2. xAI 관련 별칭(alias)을 SPACEX로 매핑
INSERT INTO entity_aliases (alias, entity_id) VALUES
    ('xAI', 'SPACEX'),
    ('XAI', 'SPACEX'),
    ('xai', 'SPACEX'),
    ('엑스에이아이', 'SPACEX'),
    ('Colossus', 'SPACEX'),
    ('콜로서스', 'SPACEX'),
    ('Grok', 'SPACEX')
ON CONFLICT(alias) DO UPDATE SET
    entity_id=excluded.entity_id;

-- 3. 신규 확장 엔티티 UPSERT (L1~L7 유지 + L8_POWER 신설)
INSERT INTO entities (entity_id, name_en, name_ko, layer, country, ticker, is_public, description, updated_at) VALUES
-- L2: 네오클라우드 (GPU 특화 클라우드)
('COREWEAVE', 'CoreWeave', '코어위브', 'L2_HYPERSCALER', 'US', NULL, 0, '엔비디아 전략 투자 GPU 특화 네오클라우드, 앤트로픽 $518B 공급 파트너', datetime('now')),
('NEBIUS', 'Nebius Group', '네비우스', 'L2_HYPERSCALER', 'NL', 'NBIS', 1, '나스닥 상장 대규모 AI 인프라 및 GPU 네오클라우드', datetime('now')),

-- L3: 컴퓨팅 & 가속기
('ARM', 'Arm Holdings', 'Arm', 'L3_COMPUTE', 'UK', 'ARM', 1, '빅테크 자체 가속기(Axion, Graviton) CPU 아키텍처 독점 라이선스', datetime('now')),
('INTEL', 'Intel', '인텔', 'L3_COMPUTE', 'US', 'INTC', 1, '데이터센터 x86 제온 CPU 및 파운드리', datetime('now')),

-- L4: 파운드리, 장비 & 첨단 패키징
('APPLIED_MATERIALS', 'Applied Materials', '어플라이드', 'L4_FOUNDRY', 'US', 'AMAT', 1, '반도체 증착·배선 및 첨단 패키징 장비 1위', datetime('now')),
('LAM_RESEARCH', 'Lam Research', '램리서치', 'L4_FOUNDRY', 'US', 'LRCX', 1, 'HBM 3D 적층 및 고단화 DRAM 식각 장비 독점', datetime('now')),
('KLA', 'KLA Corporation', 'KLA', 'L4_FOUNDRY', 'US', 'KLAC', 1, '선단공정 및 패키징 수율 검사·계측 장비 독점', datetime('now')),
('ASE', 'ASE Technology', 'ASE', 'L4_FOUNDRY', 'TW', 'ASX', 1, '글로벌 1위 OSAT, TSMC CoWoS 패키징 외주 파트너', datetime('now')),
('AMKOR', 'Amkor Technology', '앰코', 'L4_FOUNDRY', 'US', 'AMKR', 1, '미국 애리조나 첨단 2.5D 패키징 협력사', datetime('now')),

-- L5: 메모리 & 스토리지
('KIOXIA', 'Kioxia Holdings', '키옥시아', 'L5_MEMORY', 'JP', '285A', 1, 'NAND 플래시 및 AI 추론용 엔터프라이즈 eSSD 팹 운영', datetime('now')),

-- L6: 광통신 & 네트워킹
('ARISTA', 'Arista Networks', '아리스타', 'L6_OPTICAL', 'US', 'ANET', 1, 'AI 백엔드 클러스터용 800G/1.6T 고속 Ethernet 스위치 패브릭 독점적 지위', datetime('now')),

-- ⚡ L8_POWER (신설: 전력 & 에너지 인프라)
('VERTIV', 'Vertiv Holdings', '버티브', 'L8_POWER', 'US', 'VRT', 1, 'AI 데이터센터 고밀도 액체냉각(Liquid Cooling) 및 전력 분배 인프라 1위', datetime('now')),
('EATON', 'Eaton Corporation', '이튼', 'L8_POWER', 'US', 'ETN', 1, '데이터센터 배전, 변압기, 고전압 UPS 및 전력 관리 솔루션', datetime('now')),
('GE_VERNOVA', 'GE Vernova', 'GE 버노바', 'L8_POWER', 'US', 'GEV', 1, '데이터센터 전력 공급용 가스터빈, 독립 발전 및 전력망 솔루션', datetime('now')),
('SCHNEIDER', 'Schneider Electric', '슈나이더', 'L8_POWER', 'FR', 'SU', 1, '데이터센터 전력 분배 장비, 냉각 및 인프라 자동화 솔루션', datetime('now'))

ON CONFLICT(entity_id) DO UPDATE SET
    name_en=excluded.name_en,
    name_ko=excluded.name_ko,
    layer=excluded.layer,
    country=excluded.country,
    ticker=excluded.ticker,
    is_public=excluded.is_public,
    description=excluded.description,
    updated_at=datetime('now');

-- 4. 신규 기업 별칭(entity_aliases) 등록
INSERT INTO entity_aliases (alias, entity_id) VALUES
    ('코어위브', 'COREWEAVE'),
    ('CoreWeave', 'COREWEAVE'),
    ('CRWV', 'COREWEAVE'),
    ('네비우스', 'NEBIUS'),
    ('Nebius', 'NEBIUS'),
    ('NBIS', 'NEBIUS'),
    ('Arm', 'ARM'),
    ('ARM', 'ARM'),
    ('암', 'ARM'),
    ('인텔', 'INTEL'),
    ('Intel', 'INTEL'),
    ('INTC', 'INTEL'),
    ('어플라이드', 'APPLIED_MATERIALS'),
    ('AMAT', 'APPLIED_MATERIALS'),
    ('Applied Materials', 'APPLIED_MATERIALS'),
    ('램리서치', 'LAM_RESEARCH'),
    ('Lam Research', 'LAM_RESEARCH'),
    ('LRCX', 'LAM_RESEARCH'),
    ('KLA', 'KLA'),
    ('KLAC', 'KLA'),
    ('ASE', 'ASE'),
    ('일월광', 'ASE'),
    ('앰코', 'AMKOR'),
    ('Amkor', 'AMKOR'),
    ('AMKR', 'AMKOR'),
    ('키옥시아', 'KIOXIA'),
    ('Kioxia', 'KIOXIA'),
    ('아리스타', 'ARISTA'),
    ('Arista', 'ARISTA'),
    ('ANET', 'ARISTA'),
    ('버티브', 'VERTIV'),
    ('Vertiv', 'VERTIV'),
    ('VRT', 'VERTIV'),
    ('이튼', 'EATON'),
    ('Eaton', 'EATON'),
    ('ETN', 'EATON'),
    ('GE버노바', 'GE_VERNOVA'),
    ('GE Vernova', 'GE_VERNOVA'),
    ('GEV', 'GE_VERNOVA'),
    ('슈나이더', 'SCHNEIDER'),
    ('Schneider', 'SCHNEIDER')
ON CONFLICT(alias) DO UPDATE SET
    entity_id=excluded.entity_id;

COMMIT;
