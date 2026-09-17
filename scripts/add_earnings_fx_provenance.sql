-- Memory Claude earnings FX provenance migration
-- 분석 금액은 B_USD로 통일하고, 비USD 원천 자료에만 환율/원값을 기록한다.
-- fx_rate 방향: reported currency units per 1 USD (예: 1350 KRW/USD).

BEGIN IMMEDIATE;

ALTER TABLE earnings_reports ADD COLUMN reported_revenue REAL;
ALTER TABLE earnings_reports ADD COLUMN reported_op_income REAL;
ALTER TABLE earnings_reports ADD COLUMN reported_net_income REAL;
ALTER TABLE earnings_reports ADD COLUMN reported_currency TEXT;
ALTER TABLE earnings_reports ADD COLUMN reported_unit TEXT;
ALTER TABLE earnings_reports ADD COLUMN fx_rate REAL;
ALTER TABLE earnings_reports ADD COLUMN fx_rate_type TEXT;
ALTER TABLE earnings_reports ADD COLUMN fx_source TEXT;
ALTER TABLE earnings_reports ADD COLUMN fx_as_of_date TEXT;

-- USD 원천 자료는 환산 대상이 아니므로 환율을 NULL로 둔다.
UPDATE earnings_reports
SET reported_currency = 'USD',
    reported_unit = 'B_USD'
WHERE unit = 'B_USD';

-- 기존 KRW 자료는 아직 검증된 분기 평균 환율이 연결되지 않았으므로
-- 원 단위를 표시하되 B_USD로 잘못 간주하거나 임의 환산하지 않는다.
UPDATE earnings_reports
SET reported_currency = 'KRW',
    reported_unit = 'T_KRW',
    reported_revenue = revenue,
    reported_op_income = op_income,
    reported_net_income = net_income
WHERE unit = 'T_KRW';

-- 공시 환율과 원값이 적재 스크립트에 명시된 검증 완료 데이터.
UPDATE earnings_reports SET
    reported_revenue = 342.799, reported_op_income = 44.899,
    reported_net_income = 18.284, reported_currency = 'JPY',
    reported_unit = 'B_JPY', fx_rate = 145.0,
    fx_rate_type = 'QUARTER_AVG', fx_source = source,
    fx_as_of_date = report_date
WHERE entity_id = 'KIOXIA' AND period = '2025-Q2';

UPDATE earnings_reports SET
    reported_revenue = 1002.9, reported_op_income = 596.8,
    reported_net_income = 407.7, reported_currency = 'JPY',
    reported_unit = 'B_JPY', fx_rate = 155.0,
    fx_rate_type = 'QUARTER_AVG', fx_source = source,
    fx_as_of_date = report_date
WHERE entity_id = 'KIOXIA' AND period = '2026-Q1';

UPDATE earnings_reports SET
    reported_revenue = 1767.117, reported_op_income = 1270.017,
    reported_net_income = 842.165, reported_currency = 'JPY',
    reported_unit = 'B_JPY', fx_rate = 160.0,
    fx_rate_type = 'QUARTER_AVG', fx_source = source,
    fx_as_of_date = report_date
WHERE entity_id = 'KIOXIA' AND period = '2026-Q2';

UPDATE earnings_reports SET
    reported_revenue = 2390.0, reported_op_income = 1890.0,
    reported_net_income = 1270.0, reported_currency = 'JPY',
    reported_unit = 'B_JPY', fx_rate = 162.0,
    fx_rate_type = 'GUIDANCE', fx_source = source,
    fx_as_of_date = report_date
WHERE entity_id = 'KIOXIA' AND period = '2026-Q3';

UPDATE earnings_reports SET
    reported_revenue = 150750.0, reported_op_income = 10193.0,
    reported_net_income = 7521.0, reported_currency = 'TWD',
    reported_unit = 'M_TWD', fx_rate = 31.18,
    fx_rate_type = 'QUARTER_AVG', fx_source = source,
    fx_as_of_date = report_date
WHERE entity_id = 'ASE' AND period = '2025-Q2';

UPDATE earnings_reports SET
    reported_revenue = 173662.0, reported_op_income = 17493.0,
    reported_net_income = 14132.0, reported_currency = 'TWD',
    reported_unit = 'M_TWD', fx_rate = 31.53,
    fx_rate_type = 'QUARTER_AVG', fx_source = source,
    fx_as_of_date = report_date
WHERE entity_id = 'ASE' AND period = '2026-Q1';

UPDATE earnings_reports SET
    reported_revenue = 191064.0, reported_op_income = 21134.0,
    reported_net_income = 21068.0, reported_currency = 'TWD',
    reported_unit = 'M_TWD', fx_rate = 31.59,
    fx_rate_type = 'QUARTER_AVG', fx_source = source,
    fx_as_of_date = report_date
WHERE entity_id = 'ASE' AND period = '2026-Q2';

CREATE INDEX IF NOT EXISTS idx_er_reported_currency
    ON earnings_reports(reported_currency);

COMMIT;
