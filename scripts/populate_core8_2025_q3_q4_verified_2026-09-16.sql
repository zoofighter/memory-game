-- Fill the 16 missing 2025-Q3/Q4 earnings rows for the project's core 8.
-- GAAP/K-IFRS actuals only; analysis amounts are B_USD.
-- KRW FX: Federal Reserve Board DEXKOUS quarterly averages already validated
-- by scripts/convert_krw_earnings_to_usd_2026-09-16.sql.

BEGIN IMMEDIATE;

INSERT INTO earnings_reports (
    entity_id, period, report_date, revenue, op_income, net_income, unit,
    reported_revenue, reported_op_income, reported_net_income,
    reported_currency, reported_unit, fx_rate, fx_rate_type, fx_source, fx_as_of_date,
    eps_actual, gross_margin_pct, op_margin_pct, capex,
    key_takeaways, source, is_forecast
) VALUES
-- NVIDIA FY2026 Q3/Q4, mapped to calendar 2025-Q3/Q4 in this database.
('NVIDIA','2025-Q3','2025-11-19',57.006,36.010,31.910,'B_USD',
 NULL,NULL,NULL,'USD','B_USD',NULL,NULL,NULL,NULL,
 1.30,73.4,ROUND(36.010/57.006*100,2),NULL,
 'GAAP actual; Blackwell demand drove record quarterly revenue.',
 'https://investor.nvidia.com/news/press-release-details/2025/NVIDIA-Announces-Financial-Results-for-Third-Quarter-Fiscal-2026/',0),
('NVIDIA','2025-Q4','2026-02-25',68.127,44.299,42.960,'B_USD',
 NULL,NULL,NULL,'USD','B_USD',NULL,NULL,NULL,NULL,
 1.76,75.0,ROUND(44.299/68.127*100,2),NULL,
 'GAAP actual; fiscal 2026 fourth-quarter record revenue.',
 'https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-Fourth-Quarter-and-Fiscal-2026/',0),

-- Microsoft FY2026 Q1/Q2 correspond to quarters ended Sep/Dec 2025.
('MICROSOFT','2025-Q3','2025-10-29',77.673,37.961,27.747,'B_USD',
 NULL,NULL,NULL,'USD','B_USD',NULL,NULL,NULL,NULL,
 3.72,ROUND((77.673-24.043)/77.673*100,2),ROUND(37.961/77.673*100,2),NULL,
 'GAAP actual for the quarter ended September 30, 2025.',
 'https://www.microsoft.com/en-us/Investor/earnings/FY-2026-Q1/income-statements',0),
('MICROSOFT','2025-Q4','2026-01-28',81.273,38.275,38.458,'B_USD',
 NULL,NULL,NULL,'USD','B_USD',NULL,NULL,NULL,NULL,
 5.16,ROUND((81.273-25.978)/81.273*100,2),ROUND(38.275/81.273*100,2),NULL,
 'GAAP actual; net income includes gains from OpenAI investments.',
 'https://www.microsoft.com/en-us/Investor/earnings/FY-2026-Q2/income-statements',0),

('GOOGLE','2025-Q3','2025-10-29',102.346,31.228,34.979,'B_USD',
 NULL,NULL,NULL,'USD','B_USD',NULL,NULL,NULL,NULL,
 2.87,NULL,ROUND(31.228/102.346*100,2),23.953,
 'GAAP actual; first quarter above $100B revenue.',
 'https://abc.xyz/investor/events/event-details/2025/2025-Q3-Earnings-Call-2025-4OI4Bac_Q9/default.aspx',0),
('GOOGLE','2025-Q4','2026-02-04',113.828,35.934,34.455,'B_USD',
 NULL,NULL,NULL,'USD','B_USD',NULL,NULL,NULL,NULL,
 2.82,NULL,ROUND(35.934/113.828*100,2),27.851,
 'GAAP actual; Google Cloud revenue grew 48% year over year.',
 'https://s206.q4cdn.com/479360582/files/doc_news/2026/Feb/04/attachments/2025q4-alphabet-earnings-release.pdf',0),

('META','2025-Q3','2025-10-29',51.242,20.535,2.709,'B_USD',
 NULL,NULL,NULL,'USD','B_USD',NULL,NULL,NULL,NULL,
 1.05,ROUND((51.242-9.206)/51.242*100,2),40.0,NULL,
 'GAAP actual; net income includes a one-time non-cash $15.93B tax charge.',
 'https://investor.atmeta.com/investor-news/press-release-details/2025/Meta-Reports-Third-Quarter-2025-Results/',0),
('META','2025-Q4','2026-01-28',59.893,24.745,22.768,'B_USD',
 NULL,NULL,NULL,'USD','B_USD',NULL,NULL,NULL,NULL,
 8.88,NULL,41.0,22.14,
 'GAAP actual for the quarter ended December 31, 2025.',
 'https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-Fourth-Quarter-and-Full-Year-2025-Results/',0),

('AMAZON','2025-Q3','2025-10-30',180.169,17.422,21.187,'B_USD',
 NULL,NULL,NULL,'USD','B_USD',NULL,NULL,NULL,NULL,
 1.95,NULL,ROUND(17.422/180.169*100,2),NULL,
 'GAAP actual; net income includes $9.5B pre-tax gains from Anthropic investments.',
 'https://ir.aboutamazon.com/news-release/news-release-details/2025/Amazon-com-Announces-Third-Quarter-Results/',0),
('AMAZON','2025-Q4','2026-02-05',213.386,24.977,21.192,'B_USD',
 NULL,NULL,NULL,'USD','B_USD',NULL,NULL,NULL,NULL,
 1.95,NULL,ROUND(24.977/213.386*100,2),NULL,
 'GAAP actual; operating income includes $2.44B of disclosed special charges.',
 'https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Fourth-Quarter-Results/',0),

-- TSMC original values are NT$ billions; fx_rate is NTD per USD.
('TSMC','2025-Q3','2025-10-16',989.92/33.10,(989.92*0.506)/33.10,452.30/33.10,'B_USD',
 989.92,989.92*0.506,452.30,'TWD','B_TWD',33.10,'QUARTER_AVG',
 'https://investor.tsmc.com/english/quarterly-results/2025/q3','2025-09-30',
 2.92,59.5,50.6,NULL,
 'Official IFRS result; original NT$ values converted using disclosed quarterly average NTD/USD.',
 'https://www.sec.gov/Archives/edgar/data/1046179/000104617925000116/a3q25e_withguidancexfinal.htm',0),
('TSMC','2025-Q4','2026-01-15',1046.09/31.01,(1046.09*0.54)/31.01,505.74/31.01,'B_USD',
 1046.09,1046.09*0.54,505.74,'TWD','B_TWD',31.01,'QUARTER_AVG',
 'https://investor.tsmc.com/english/quarterly-results/2025/q4','2025-12-31',
 3.14,62.3,54.0,NULL,
 'Official IFRS result; original NT$ values converted using disclosed quarterly average NTD/USD.',
 'https://investor.tsmc.com/english/encrypt/files/encrypt_file/reports/2026-01/3e49621566a3ca53bdf8aee2586929b666c17fd6/4Q25EarningsRelease.pdf',0),

-- Samsung original values are KRW trillions; official newsroom does not state net income.
('SAMSUNG','2025-Q3','2025-10-30',86.1*1000/1386.945312,12.2*1000/1386.945312,NULL,'B_USD',
 86.1,12.2,NULL,'KRW','T_KRW',1386.945312,'QUARTER_AVG',
 'Federal Reserve Board DEXKOUS via FRED: https://fred.stlouisfed.org/series/DEXKOUS','2025-09-30',
 NULL,NULL,ROUND(12.2/86.1*100,2),NULL,
 'Official K-IFRS headline actual; net income not stated in cited release.',
 'https://news.samsung.com/kr/삼성전자-2025년-3분기-실적-발표',0),
('SAMSUNG','2025-Q4','2026-01-29',93.8*1000/1448.764194,20.1*1000/1448.764194,NULL,'B_USD',
 93.8,20.1,NULL,'KRW','T_KRW',1448.764194,'QUARTER_AVG',
 'Federal Reserve Board DEXKOUS via FRED: https://fred.stlouisfed.org/series/DEXKOUS','2025-12-31',
 NULL,NULL,ROUND(20.1/93.8*100,2),NULL,
 'Official K-IFRS headline actual; net income not stated in cited release.',
 'https://news.samsung.com/kr/삼성전자-2025년-4분기-실적-발표',0),

-- SK hynix original values are KRW trillions.
('SK_HYNIX','2025-Q3','2025-10-29',24.4489*1000/1386.945312,11.3834*1000/1386.945312,12.5975*1000/1386.945312,'B_USD',
 24.4489,11.3834,12.5975,'KRW','T_KRW',1386.945312,'QUARTER_AVG',
 'Federal Reserve Board DEXKOUS via FRED: https://fred.stlouisfed.org/series/DEXKOUS','2025-09-30',
 NULL,NULL,ROUND(11.3834/24.4489*100,2),NULL,
 'Official K-IFRS actual; record quarterly revenue and operating profit.',
 'https://news.skhynix.co.kr/3q-2025-business-results/',0),
('SK_HYNIX','2025-Q4','2026-01-28',32.8267*1000/1448.764194,19.1696*1000/1448.764194,15.2460*1000/1448.764194,'B_USD',
 32.8267,19.1696,15.2460,'KRW','T_KRW',1448.764194,'QUARTER_AVG',
 'Federal Reserve Board DEXKOUS via FRED: https://fred.stlouisfed.org/series/DEXKOUS','2025-12-31',
 NULL,NULL,ROUND(19.1696/32.8267*100,2),NULL,
 'Official K-IFRS actual; record full-year and fourth-quarter performance.',
 'https://news.skhynix.co.kr/2025-business-results/',0);

COMMIT;
