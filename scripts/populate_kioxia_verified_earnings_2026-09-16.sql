-- Kioxia official IFRS results converted from JPY billion to USD billion.
-- FX rates are the quarterly average USD/JPY rates disclosed in the source.

BEGIN IMMEDIATE;

INSERT OR IGNORE INTO earnings_reports (
    entity_id, period, report_date, revenue, op_income, net_income, unit,
    reported_revenue, reported_op_income, reported_net_income,
    reported_currency, reported_unit, fx_rate, fx_rate_type, fx_source, fx_as_of_date,
    gross_margin_pct, op_margin_pct, guidance_next_q, key_takeaways,
    source, is_forecast
) VALUES
(
    'KIOXIA', '2025-Q2', '2025-08-08',
    342.799 / 145.0, 44.899 / 145.0, 18.284 / 145.0, 'B_USD',
    342.799, 44.899, 18.284, 'JPY', 'B_JPY', 145.0, 'QUARTER_AVG',
    'https://ssl4.eir-parts.net/doc/285A/tdnet/2859905/00.pdf', '2025-08-08',
    NULL, ROUND(44.899 / 342.799 * 100.0, 2), NULL,
    'Official IFRS result; JPY values converted at disclosed quarterly average USD/JPY 145.',
    'https://ssl4.eir-parts.net/doc/285A/tdnet/2859905/00.pdf', 0
),
(
    'KIOXIA', '2026-Q1', '2026-05-15',
    1002.9 / 155.0, 596.8 / 155.0, 407.7 / 155.0, 'B_USD',
    1002.9, 596.8, 407.7, 'JPY', 'B_JPY', 155.0, 'QUARTER_AVG',
    'https://ssl4.eir-parts.net/doc/285A/tdnet/2815552/00.pdf', '2026-05-15',
    NULL, ROUND(596.8 / 1002.9 * 100.0, 2), NULL,
    'Official IFRS result; JPY values converted at disclosed quarterly average USD/JPY 155.',
    'https://ssl4.eir-parts.net/doc/285A/tdnet/2815552/00.pdf', 0
),
(
    'KIOXIA', '2026-Q2', '2026-07-31',
    1767.117 / 160.0, 1270.017 / 160.0, 842.165 / 160.0, 'B_USD',
    1767.117, 1270.017, 842.165, 'JPY', 'B_JPY', 160.0, 'QUARTER_AVG',
    'https://ssl4.eir-parts.net/doc/285A/tdnet/2859905/00.pdf', '2026-07-31',
    NULL, ROUND(1270.017 / 1767.117 * 100.0, 2),
    'FY2026 calendar Q3 guidance: revenue JPY 2,390B, operating profit JPY 1,890B.',
    'Official IFRS result; JPY values converted at disclosed quarterly average USD/JPY 160.',
    'https://ssl4.eir-parts.net/doc/285A/tdnet/2859905/00.pdf', 0
),
(
    'KIOXIA', '2026-Q3', NULL,
    2390.0 / 162.0, 1890.0 / 162.0, 1270.0 / 162.0, 'B_USD',
    2390.0, 1890.0, 1270.0, 'JPY', 'B_JPY', 162.0, 'GUIDANCE',
    'https://ssl4.eir-parts.net/doc/285A/tdnet/2859905/00.pdf', NULL,
    NULL, ROUND(1890.0 / 2390.0 * 100.0, 2), NULL,
    'Company guidance for Jul-Sep 2026; converted at company USD/JPY assumption 162.',
    'https://ssl4.eir-parts.net/doc/285A/tdnet/2859905/00.pdf', 1
);

COMMIT;
