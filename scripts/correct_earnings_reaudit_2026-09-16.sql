-- Memory Claude earnings re-audit correction batch.
-- Scope: Samsung 2026-Q1/Q2, NVIDIA 2026-Q1/Q3, and deterministic
-- revenue-consensus BEAT/MISS normalization.

BEGIN IMMEDIATE;

INSERT OR IGNORE INTO earnings_correction_audit (
    entity_id, period, correction_batch,
    old_report_date, old_revenue, old_op_income, old_net_income,
    old_eps_actual, old_gross_margin_pct, old_op_margin_pct,
    old_beat_miss_status, old_source, source_url, correction_note
)
SELECT entity_id, period, '2026-09-16_REAUDIT_BATCH_2',
       report_date, revenue, op_income, net_income,
       eps_actual, gross_margin_pct, op_margin_pct,
       beat_miss_status, source,
       CASE entity_id || ':' || period
         WHEN 'SAMSUNG:2026-Q1' THEN 'https://news.samsung.com/kr/삼성전자-2026년-1분기-실적-발표'
         WHEN 'SAMSUNG:2026-Q2' THEN 'https://news.samsung.com/kr/삼성전자-2026년-2분기-실적-발표'
         WHEN 'NVIDIA:2026-Q1' THEN 'https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-Second-Quarter-Fiscal-2027/default.aspx'
         WHEN 'NVIDIA:2026-Q3' THEN 'https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-Second-Quarter-Fiscal-2027/default.aspx'
       END,
       CASE
         WHEN entity_id='NVIDIA' AND period='2026-Q3'
           THEN 'Replaced stale consensus with company Q3 FY2027 revenue guidance; unverified profit estimates cleared.'
         ELSE 'Re-audited against first-party release; stale ancillary values not supported by the cited release were cleared.'
       END
FROM earnings_reports
WHERE (entity_id, period) IN (
    ('SAMSUNG','2026-Q1'), ('SAMSUNG','2026-Q2'),
    ('NVIDIA','2026-Q1'), ('NVIDIA','2026-Q3')
);

-- Samsung official reported values are KRW trillions. Analysis values remain B_USD.
UPDATE earnings_reports
SET report_date = '2026-04-30',
    reported_revenue = 133.9,
    reported_op_income = 57.2,
    reported_net_income = NULL,
    revenue = 133.9 * 1000.0 / fx_rate,
    op_income = 57.2 * 1000.0 / fx_rate,
    net_income = NULL,
    consensus_revenue = NULL,
    reported_consensus_revenue = NULL,
    gross_margin_pct = NULL,
    op_margin_pct = ROUND(57.2 / 133.9 * 100.0, 2),
    beat_miss_status = NULL,
    source = 'https://news.samsung.com/kr/삼성전자-2026년-1분기-실적-발표'
WHERE entity_id = 'SAMSUNG' AND period = '2026-Q1';

UPDATE earnings_reports
SET reported_revenue = 171.5,
    reported_op_income = 89.5,
    reported_net_income = NULL,
    revenue = 171.5 * 1000.0 / fx_rate,
    op_income = 89.5 * 1000.0 / fx_rate,
    net_income = NULL,
    consensus_revenue = NULL,
    reported_consensus_revenue = NULL,
    gross_margin_pct = NULL,
    op_margin_pct = ROUND(89.5 / 171.5 * 100.0, 2),
    beat_miss_status = NULL,
    source = 'https://news.samsung.com/kr/삼성전자-2026년-2분기-실적-발표'
WHERE entity_id = 'SAMSUNG' AND period = '2026-Q2';

-- NVIDIA Q1 FY2027 comparative figures disclosed in the Q2 FY2027 release.
UPDATE earnings_reports
SET revenue = 81.615,
    op_income = 53.536,
    net_income = 58.321,
    eps_actual = 2.39,
    consensus_revenue = NULL,
    gross_margin_pct = 74.9,
    op_margin_pct = ROUND(53.536 / 81.615 * 100.0, 2),
    beat_miss_status = NULL,
    source = 'https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-Second-Quarter-Fiscal-2027/default.aspx'
WHERE entity_id = 'NVIDIA' AND period = '2026-Q1';

-- Q3 FY2027 company outlook: revenue $108B +/-2%, GAAP GM 74.0% +/-0.5pt.
UPDATE earnings_reports
SET revenue = 108.0,
    op_income = NULL,
    net_income = NULL,
    eps_actual = NULL,
    eps_consensus = NULL,
    consensus_revenue = NULL,
    gross_margin_pct = 74.0,
    op_margin_pct = NULL,
    beat_miss_status = NULL,
    guidance_next_q = 'Q3 FY2027 revenue guidance $108.0B ±2%; GAAP gross margin 74.0% ±0.5pt.',
    key_takeaways = 'Company guidance; no China Data Center compute revenue assumed.',
    source = 'https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-Second-Quarter-Fiscal-2027/default.aspx'
WHERE entity_id = 'NVIDIA' AND period = '2026-Q3';

-- Deterministic status definition: revenue actual vs revenue consensus.
-- Within +/-0.1% is INLINE. Forecast rows never receive a realized status.
UPDATE earnings_reports
SET beat_miss_status = CASE
    WHEN consensus_revenue IS NULL THEN NULL
    WHEN revenue > consensus_revenue * 1.001 THEN 'BEAT'
    WHEN revenue < consensus_revenue * 0.999 THEN 'MISS'
    ELSE 'INLINE'
END
WHERE is_forecast = 0;

UPDATE earnings_reports SET beat_miss_status = NULL WHERE is_forecast = 1;

UPDATE earnings_correction_audit AS a
SET new_report_date=(SELECT report_date FROM earnings_reports r WHERE r.entity_id=a.entity_id AND r.period=a.period),
    new_revenue=(SELECT revenue FROM earnings_reports r WHERE r.entity_id=a.entity_id AND r.period=a.period),
    new_op_income=(SELECT op_income FROM earnings_reports r WHERE r.entity_id=a.entity_id AND r.period=a.period),
    new_net_income=(SELECT net_income FROM earnings_reports r WHERE r.entity_id=a.entity_id AND r.period=a.period),
    new_eps_actual=(SELECT eps_actual FROM earnings_reports r WHERE r.entity_id=a.entity_id AND r.period=a.period),
    new_gross_margin_pct=(SELECT gross_margin_pct FROM earnings_reports r WHERE r.entity_id=a.entity_id AND r.period=a.period),
    new_op_margin_pct=(SELECT op_margin_pct FROM earnings_reports r WHERE r.entity_id=a.entity_id AND r.period=a.period),
    new_beat_miss_status=(SELECT beat_miss_status FROM earnings_reports r WHERE r.entity_id=a.entity_id AND r.period=a.period),
    new_source=(SELECT source FROM earnings_reports r WHERE r.entity_id=a.entity_id AND r.period=a.period)
WHERE correction_batch='2026-09-16_REAUDIT_BATCH_2';

COMMIT;
