-- ASE official 6-K quarterly results converted from TWD million to USD billion.
-- FX rates are disclosed in the same official earnings release.

BEGIN IMMEDIATE;

INSERT OR IGNORE INTO earnings_reports (
    entity_id, period, report_date, revenue, op_income, net_income, unit,
    reported_revenue, reported_op_income, reported_net_income,
    reported_currency, reported_unit, fx_rate, fx_rate_type, fx_source, fx_as_of_date,
    eps_actual, gross_margin_pct, op_margin_pct, key_takeaways, source,
    is_forecast
) VALUES
(
    'ASE', '2025-Q2', '2025-07-31',
    150750.0 / 31.18 / 1000.0,
    10193.0 / 31.18 / 1000.0,
    7521.0 / 31.18 / 1000.0,
    'B_USD', 150750.0, 10193.0, 7521.0, 'TWD', 'M_TWD', 31.18,
    'QUARTER_AVG',
    'https://www.sec.gov/Archives/edgar/data/1122411/000095010326011351/dp250868_6k.htm',
    '2025-07-31', 0.109,
    ROUND(25687.0 / 150750.0 * 100.0, 2),
    ROUND(10193.0 / 150750.0 * 100.0, 2),
    'Official unaudited T-IFRS result; converted at disclosed NTD/USD 31.18. EPS is per ADS in USD.',
    'https://www.sec.gov/Archives/edgar/data/1122411/000095010326011351/dp250868_6k.htm',
    0
),
(
    'ASE', '2026-Q1', '2026-04-29',
    173662.0 / 31.53 / 1000.0,
    17493.0 / 31.53 / 1000.0,
    14132.0 / 31.53 / 1000.0,
    'B_USD', 173662.0, 17493.0, 14132.0, 'TWD', 'M_TWD', 31.53,
    'QUARTER_AVG',
    'https://www.sec.gov/Archives/edgar/data/1122411/000095010326011351/dp250868_6k.htm',
    '2026-04-29', 0.195,
    ROUND(34818.0 / 173662.0 * 100.0, 2),
    ROUND(17493.0 / 173662.0 * 100.0, 2),
    'Official unaudited T-IFRS result, retrospectively adjusted; converted at disclosed NTD/USD 31.53. EPS is per ADS in USD.',
    'https://www.sec.gov/Archives/edgar/data/1122411/000095010326011351/dp250868_6k.htm',
    0
),
(
    'ASE', '2026-Q2', '2026-07-30',
    191064.0 / 31.59 / 1000.0,
    21134.0 / 31.59 / 1000.0,
    21068.0 / 31.59 / 1000.0,
    'B_USD', 191064.0, 21134.0, 21068.0, 'TWD', 'M_TWD', 31.59,
    'QUARTER_AVG',
    'https://www.sec.gov/Archives/edgar/data/1122411/000095010326011351/dp250868_6k.htm',
    '2026-07-30', 0.292,
    ROUND(40150.0 / 191064.0 * 100.0, 2),
    ROUND(21134.0 / 191064.0 * 100.0, 2),
    'Official unaudited T-IFRS result; converted at disclosed NTD/USD 31.59. EPS is per ADS in USD.',
    'https://www.sec.gov/Archives/edgar/data/1122411/000095010326011351/dp250868_6k.htm',
    0
);

COMMIT;
