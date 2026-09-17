-- Earnings correction audit trail.
-- Apply before official-results corrections so every previous value is retained.

CREATE TABLE IF NOT EXISTS earnings_correction_audit (
    audit_id               INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id              TEXT NOT NULL REFERENCES entities(entity_id),
    period                 TEXT NOT NULL,
    correction_batch       TEXT NOT NULL,
    old_report_date        TEXT,
    old_revenue            REAL,
    old_op_income          REAL,
    old_net_income         REAL,
    old_eps_actual         REAL,
    old_gross_margin_pct   REAL,
    old_op_margin_pct      REAL,
    old_beat_miss_status   TEXT,
    old_source             TEXT,
    new_report_date        TEXT,
    new_revenue            REAL,
    new_op_income          REAL,
    new_net_income         REAL,
    new_eps_actual         REAL,
    new_gross_margin_pct   REAL,
    new_op_margin_pct      REAL,
    new_beat_miss_status   TEXT,
    new_source             TEXT,
    source_url             TEXT NOT NULL,
    correction_note        TEXT,
    corrected_at           TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(entity_id, period, correction_batch)
);

CREATE INDEX IF NOT EXISTS idx_earnings_correction_entity_period
    ON earnings_correction_audit(entity_id, period);
