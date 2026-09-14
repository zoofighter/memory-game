-- add_datacenter_table.sql
-- 하이퍼스케일러 및 빅테크 AI 데이터센터 전력/클러스터 용량 추적 테이블

CREATE TABLE IF NOT EXISTS datacenter_capacity (
    dc_id               TEXT PRIMARY KEY,
    entity_id           TEXT NOT NULL REFERENCES entities(entity_id),
    dc_name             TEXT NOT NULL,
    location_state      TEXT,
    location_country    TEXT DEFAULT 'USA',
    power_mw_current    REAL,               -- 현재 가동 전력 (MW)
    power_mw_target     REAL,               -- 최종 목표 전력 (MW)
    power_source        TEXT,               -- 전력원 (원전 PPA, 그리드, 천연가스, SMR 등)
    cooling_type        TEXT,               -- 냉각 방식 (Liquid Cooling 수랭식, 공랭식 등)
    gpu_cluster_target  INTEGER,            -- 탑재 목표 가속기(GPU/TPU) 수량 (단위: 대)
    primary_chips       TEXT,               -- 주력 탑재 가속기 (Blackwell, GB200, TPU v6, Trainium2 등)
    online_date         TEXT,               -- 본격 가동(예정) 시점 (YYYY-QN)
    status              TEXT DEFAULT 'CONSTRUCTION', -- OPERATING, CONSTRUCTION, PLANNED
    capex_est_b         REAL,               -- 추정 투자 규모 (USD Billion)
    key_notes           TEXT,
    source              TEXT,
    created_at          TEXT DEFAULT (datetime('now')),
    updated_at          TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_dc_entity ON datacenter_capacity(entity_id);
CREATE INDEX IF NOT EXISTS idx_dc_status ON datacenter_capacity(status);
CREATE INDEX IF NOT EXISTS idx_dc_online ON datacenter_capacity(online_date);

-- 데이터센터 요약 뷰 생성
CREATE VIEW IF NOT EXISTS v_datacenter_summary AS
SELECT 
    e.name_ko AS 기업,
    d.dc_name AS 데이터센터명,
    d.location_state || ' (' || d.location_country || ')' AS 위치,
    d.power_mw_current AS 현재전력_MW,
    d.power_mw_target AS 목표전력_MW,
    d.power_source AS 전력원,
    COALESCE(printf('%,d대', d.gpu_cluster_target), '-') AS 목표가속기수,
    d.primary_chips AS 주력칩,
    d.online_date AS 가동목표,
    d.status AS 상태
FROM datacenter_capacity d
JOIN entities e ON d.entity_id = e.entity_id
ORDER BY e.layer, d.power_mw_target DESC;
