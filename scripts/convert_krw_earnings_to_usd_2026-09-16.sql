-- Convert Samsung and SK hynix earnings from T_KRW to B_USD.
-- FX source: Federal Reserve Board series DEXKOUS via FRED.
-- Rate direction: KRW per 1 USD. Full-quarter daily observations are averaged.
-- 2026-Q3 is a partial-quarter average through 2026-09-11.
-- 2026-Q4 is a forecast assumption using the 2026-09-11 spot observation.

BEGIN IMMEDIATE;

ALTER TABLE earnings_reports ADD COLUMN reported_consensus_revenue REAL;
ALTER TABLE earnings_reports ADD COLUMN reported_capex REAL;

CREATE TEMP TABLE krw_quarterly_fx (
    period TEXT PRIMARY KEY,
    fx_rate REAL NOT NULL,
    fx_rate_type TEXT NOT NULL,
    fx_as_of_date TEXT NOT NULL
);

INSERT INTO krw_quarterly_fx VALUES
('2020-Q1',1194.005968,'QUARTER_AVG','2020-03-31'),
('2020-Q2',1219.130781,'QUARTER_AVG','2020-06-30'),
('2020-Q3',1187.620156,'QUARTER_AVG','2020-09-30'),
('2020-Q4',1117.973833,'QUARTER_AVG','2020-12-31'),
('2021-Q1',1114.809500,'QUARTER_AVG','2021-03-31'),
('2021-Q2',1121.301719,'QUARTER_AVG','2021-06-30'),
('2021-Q3',1160.083906,'QUARTER_AVG','2021-09-30'),
('2021-Q4',1183.289016,'QUARTER_AVG','2021-12-31'),
('2022-Q1',1206.183226,'QUARTER_AVG','2022-03-31'),
('2022-Q2',1260.455714,'QUARTER_AVG','2022-06-30'),
('2022-Q3',1341.107812,'QUARTER_AVG','2022-09-30'),
('2022-Q4',1359.375738,'QUARTER_AVG','2022-12-31'),
('2023-Q1',1276.335000,'QUARTER_AVG','2023-03-31'),
('2023-Q2',1315.682222,'QUARTER_AVG','2023-06-30'),
('2023-Q3',1313.187302,'QUARTER_AVG','2023-09-30'),
('2023-Q4',1321.846230,'QUARTER_AVG','2023-12-31'),
('2024-Q1',1329.613226,'QUARTER_AVG','2024-03-31'),
('2024-Q2',1370.138889,'QUARTER_AVG','2024-06-30'),
('2024-Q3',1355.480781,'QUARTER_AVG','2024-09-30'),
('2024-Q4',1398.668226,'QUARTER_AVG','2024-12-31'),
('2025-Q1',1452.005738,'QUARTER_AVG','2025-03-31'),
('2025-Q2',1399.823016,'QUARTER_AVG','2025-06-30'),
('2025-Q3',1386.945312,'QUARTER_AVG','2025-09-30'),
('2025-Q4',1448.764194,'QUARTER_AVG','2025-12-31'),
('2026-Q1',1465.569508,'QUARTER_AVG','2026-03-31'),
('2026-Q2',1500.478889,'QUARTER_AVG','2026-06-30'),
('2026-Q3',1430.604902,'PARTIAL_QUARTER_AVG','2026-09-11'),
('2026-Q4',1340.300000,'SPOT_FORECAST_ASSUMPTION','2026-09-11');

UPDATE earnings_reports AS e
SET reported_revenue = e.revenue,
    reported_op_income = e.op_income,
    reported_net_income = e.net_income,
    reported_consensus_revenue = e.consensus_revenue,
    reported_capex = e.capex,
    reported_currency = 'KRW',
    reported_unit = 'T_KRW',
    fx_rate = (SELECT f.fx_rate FROM krw_quarterly_fx f WHERE f.period=e.period),
    fx_rate_type = (SELECT f.fx_rate_type FROM krw_quarterly_fx f WHERE f.period=e.period),
    fx_source = 'Federal Reserve Board DEXKOUS via FRED: https://fred.stlouisfed.org/series/DEXKOUS',
    fx_as_of_date = (SELECT f.fx_as_of_date FROM krw_quarterly_fx f WHERE f.period=e.period),
    revenue = e.revenue * 1000.0 / (SELECT f.fx_rate FROM krw_quarterly_fx f WHERE f.period=e.period),
    op_income = e.op_income * 1000.0 / (SELECT f.fx_rate FROM krw_quarterly_fx f WHERE f.period=e.period),
    net_income = e.net_income * 1000.0 / (SELECT f.fx_rate FROM krw_quarterly_fx f WHERE f.period=e.period),
    consensus_revenue = e.consensus_revenue * 1000.0 / (SELECT f.fx_rate FROM krw_quarterly_fx f WHERE f.period=e.period),
    capex = e.capex * 1000.0 / (SELECT f.fx_rate FROM krw_quarterly_fx f WHERE f.period=e.period),
    unit = 'B_USD'
WHERE e.unit = 'T_KRW'
  AND e.entity_id IN ('SAMSUNG','SK_HYNIX')
  AND EXISTS (SELECT 1 FROM krw_quarterly_fx f WHERE f.period=e.period);

COMMIT;
