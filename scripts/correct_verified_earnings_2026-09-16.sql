-- First official-source correction batch.
-- Scope: rows whose GAAP values were checked against first-party IR releases.

BEGIN IMMEDIATE;

INSERT INTO earnings_correction_audit (
    entity_id, period, correction_batch,
    old_report_date, old_revenue, old_op_income, old_net_income,
    old_eps_actual, old_gross_margin_pct, old_op_margin_pct,
    old_beat_miss_status, old_source,
    source_url, correction_note
)
SELECT entity_id, period, '2026-09-16_OFFICIAL_IR_BATCH_1',
       report_date, revenue, op_income, net_income,
       eps_actual, gross_margin_pct, op_margin_pct,
       beat_miss_status, source,
       CASE entity_id || ':' || period
         WHEN 'GOOGLE:2025-Q2' THEN 'https://abc.xyz/assets/cc/27/3ada14014efbadd7a58472f1f3f4/2025q2-alphabet-earnings-release.pdf'
         WHEN 'META:2025-Q2' THEN 'https://investor.atmeta.com/investor-news/press-release-details/2025/Meta-Reports-Second-Quarter-2025-Results/'
         WHEN 'MICROSOFT:2025-Q2' THEN 'https://www.microsoft.com/en-us/Investor/earnings/FY-2025-Q4/press-release-webcast'
         WHEN 'NVIDIA:2025-Q2' THEN 'https://investor.nvidia.com/news/press-release-details/2025/NVIDIA-Announces-Financial-Results-for-Second-Quarter-Fiscal-2026/default.aspx'
         WHEN 'MICROSOFT:2026-Q2' THEN 'https://www.microsoft.com/en-us/investor/earnings/fy-2026-q4/press-release-webcast'
         WHEN 'NVIDIA:2026-Q2' THEN 'https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-Second-Quarter-Fiscal-2027/default.aspx'
         WHEN 'SAMSUNG:2026-Q2' THEN 'https://news.samsung.com/kr/삼성전자-2026년-2분기-실적-발표'
       END,
       'Official GAAP result correction; unverified ancillary fields were left unchanged.'
FROM earnings_reports
WHERE (entity_id, period) IN (
    ('GOOGLE','2025-Q2'), ('META','2025-Q2'),
    ('MICROSOFT','2025-Q2'), ('NVIDIA','2025-Q2'),
    ('MICROSOFT','2026-Q2'), ('NVIDIA','2026-Q2'),
    ('SAMSUNG','2026-Q2')
);

UPDATE earnings_reports
SET report_date='2025-07-23', revenue=96.428, op_income=31.271,
    net_income=28.196, eps_actual=2.31, op_margin_pct=32.4,
    source='Alphabet 2025-Q2 official earnings release'
WHERE entity_id='GOOGLE' AND period='2025-Q2';

UPDATE earnings_reports
SET report_date='2025-07-30', revenue=47.516, op_income=20.441,
    op_margin_pct=43.0,
    source='Meta 2025-Q2 official earnings release'
WHERE entity_id='META' AND period='2025-Q2';

UPDATE earnings_reports
SET report_date='2025-07-30', revenue=76.441, op_income=34.323,
    net_income=27.233, eps_actual=3.65, op_margin_pct=44.9,
    source='Microsoft FY2025-Q4 official earnings release'
WHERE entity_id='MICROSOFT' AND period='2025-Q2';

UPDATE earnings_reports
SET revenue=46.743, op_income=28.440, net_income=26.422,
    eps_actual=1.08, gross_margin_pct=72.4, op_margin_pct=60.8,
    source='NVIDIA FY2026-Q2 official GAAP earnings release'
WHERE entity_id='NVIDIA' AND period='2025-Q2';

UPDATE earnings_reports
SET revenue=90.0, op_income=40.6, net_income=35.766,
    eps_actual=4.81, op_margin_pct=45.1,
    source='Microsoft FY2026-Q4 official GAAP earnings release'
WHERE entity_id='MICROSOFT' AND period='2026-Q2';

UPDATE earnings_reports
SET report_date='2026-08-26', revenue=96.221, op_income=63.734,
    net_income=59.688, eps_actual=2.46, gross_margin_pct=75.0,
    op_margin_pct=66.2,
    source='NVIDIA FY2027-Q2 official GAAP earnings release'
WHERE entity_id='NVIDIA' AND period='2026-Q2';

UPDATE earnings_reports
SET report_date='2026-07-30', revenue=171.5, op_income=89.5,
    op_margin_pct=52.2,
    source='Samsung Electronics 2026-Q2 official K-IFRS earnings release'
WHERE entity_id='SAMSUNG' AND period='2026-Q2';

UPDATE earnings_reports
SET beat_miss_status=NULL
WHERE is_forecast=1;

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
WHERE correction_batch='2026-09-16_OFFICIAL_IR_BATCH_1';

COMMIT;
