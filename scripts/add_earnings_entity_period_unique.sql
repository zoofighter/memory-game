-- Prevent duplicate quarterly earnings rows for the same company and period.
-- Precondition: duplicate query must return zero rows before applying.

CREATE UNIQUE INDEX IF NOT EXISTS uq_earnings_entity_period
    ON earnings_reports(entity_id, period);
