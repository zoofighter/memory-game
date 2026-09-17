.mode json
.once /private/tmp/memory_claude_earnings_export/earnings.json
SELECT
  er.id,
  er.entity_id,
  e.name_ko,
  e.name_en,
  e.layer,
  e.ticker,
  er.period,
  CASE WHEN er.is_forecast = 1 THEN '전망' ELSE '확정' END AS data_type,
  er.is_forecast,
  er.report_date,
  er.revenue,
  er.op_income,
  er.net_income,
  er.unit,
  er.eps_actual,
  er.eps_consensus,
  er.consensus_revenue,
  er.beat_miss_status,
  er.gross_margin_pct,
  er.op_margin_pct,
  er.capex,
  er.revenue_breakdown,
  er.guidance_next_q,
  er.key_takeaways,
  er.source,
  er.created_at
FROM earnings_reports er
JOIN entities e ON e.entity_id = er.entity_id
ORDER BY er.entity_id, er.period;

.once /private/tmp/memory_claude_earnings_export/entities.json
SELECT entity_id, name_ko, name_en, layer, country, ticker, is_public,
       description, created_at, updated_at
FROM entities
ORDER BY layer, entity_id;
