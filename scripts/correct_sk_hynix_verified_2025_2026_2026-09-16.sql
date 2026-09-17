-- Correct SK hynix 2025-Q1 through 2026-Q2 with official K-IFRS results.
-- Remove two stale 2026-Q3/Q4 consensus rows that were invalidated by Q2 actuals.

BEGIN IMMEDIATE;

INSERT OR IGNORE INTO earnings_correction_audit (
    entity_id, period, correction_batch,
    old_report_date, old_revenue, old_op_income, old_net_income,
    old_eps_actual, old_gross_margin_pct, old_op_margin_pct,
    old_beat_miss_status, old_source, source_url, correction_note
)
SELECT entity_id, period, '2026-09-16_SK_HYNIX_OFFICIAL_REAUDIT',
       report_date, revenue, op_income, net_income,
       eps_actual, gross_margin_pct, op_margin_pct,
       beat_miss_status, source,
       CASE period
         WHEN '2025-Q1' THEN 'https://news.skhynix.co.kr/1q-2025-business-results/'
         WHEN '2025-Q2' THEN 'https://news.skhynix.co.kr/2q-2025-business-results/'
         WHEN '2026-Q1' THEN 'https://news.skhynix.co.kr/q1-2026-business-results/'
         WHEN '2026-Q2' THEN 'https://news.skhynix.co.kr/q2-2026-business-results/'
       END,
       'Replaced rounded/stale values with official K-IFRS revenue, operating income, and net income.'
FROM earnings_reports
WHERE entity_id='SK_HYNIX' AND period IN ('2025-Q1','2025-Q2','2026-Q1','2026-Q2');

UPDATE earnings_reports
SET reported_revenue=17.6391, reported_op_income=7.4405, reported_net_income=8.1082,
    revenue=17.6391*1000.0/fx_rate, op_income=7.4405*1000.0/fx_rate,
    net_income=8.1082*1000.0/fx_rate, op_margin_pct=ROUND(7.4405/17.6391*100,2),
    gross_margin_pct=NULL, consensus_revenue=NULL, reported_consensus_revenue=NULL,
    beat_miss_status=NULL,
    source='https://news.skhynix.co.kr/1q-2025-business-results/'
WHERE entity_id='SK_HYNIX' AND period='2025-Q1';

UPDATE earnings_reports
SET reported_revenue=22.2320, reported_op_income=9.2129, reported_net_income=6.9962,
    revenue=22.2320*1000.0/fx_rate, op_income=9.2129*1000.0/fx_rate,
    net_income=6.9962*1000.0/fx_rate, op_margin_pct=ROUND(9.2129/22.2320*100,2),
    gross_margin_pct=NULL, consensus_revenue=NULL, reported_consensus_revenue=NULL,
    beat_miss_status=NULL,
    source='https://news.skhynix.co.kr/2q-2025-business-results/'
WHERE entity_id='SK_HYNIX' AND period='2025-Q2';

UPDATE earnings_reports
SET reported_revenue=52.5763, reported_op_income=37.6103, reported_net_income=40.3459,
    revenue=52.5763*1000.0/fx_rate, op_income=37.6103*1000.0/fx_rate,
    net_income=40.3459*1000.0/fx_rate, op_margin_pct=ROUND(37.6103/52.5763*100,2),
    gross_margin_pct=NULL, consensus_revenue=NULL, reported_consensus_revenue=NULL,
    beat_miss_status=NULL,
    source='https://news.skhynix.co.kr/q1-2026-business-results/'
WHERE entity_id='SK_HYNIX' AND period='2026-Q1';

UPDATE earnings_reports
SET report_date='2026-07-29',
    reported_revenue=79.3187, reported_op_income=60.5426, reported_net_income=93.9226,
    revenue=79.3187*1000.0/fx_rate, op_income=60.5426*1000.0/fx_rate,
    net_income=93.9226*1000.0/fx_rate, op_margin_pct=ROUND(60.5426/79.3187*100,2),
    gross_margin_pct=NULL, consensus_revenue=NULL, reported_consensus_revenue=NULL,
    beat_miss_status=NULL,
    source='https://news.skhynix.co.kr/q2-2026-business-results/'
WHERE entity_id='SK_HYNIX' AND period='2026-Q2';

UPDATE earnings_correction_audit AS a
SET new_report_date=(SELECT report_date FROM earnings_reports r WHERE r.entity_id=a.entity_id AND r.period=a.period),
    new_revenue=(SELECT revenue FROM earnings_reports r WHERE r.entity_id=a.entity_id AND r.period=a.period),
    new_op_income=(SELECT op_income FROM earnings_reports r WHERE r.entity_id=a.entity_id AND r.period=a.period),
    new_net_income=(SELECT net_income FROM earnings_reports r WHERE r.entity_id=a.entity_id AND r.period=a.period),
    new_op_margin_pct=(SELECT op_margin_pct FROM earnings_reports r WHERE r.entity_id=a.entity_id AND r.period=a.period),
    new_beat_miss_status=(SELECT beat_miss_status FROM earnings_reports r WHERE r.entity_id=a.entity_id AND r.period=a.period),
    new_source=(SELECT source FROM earnings_reports r WHERE r.entity_id=a.entity_id AND r.period=a.period)
WHERE correction_batch='2026-09-16_SK_HYNIX_OFFICIAL_REAUDIT';

DELETE FROM earnings_reports
WHERE entity_id='SK_HYNIX' AND period IN ('2026-Q3','2026-Q4') AND is_forecast=1;

COMMIT;
