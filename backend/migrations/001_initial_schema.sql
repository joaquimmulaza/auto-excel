-- =============================================================================
-- Migration 001 — Initial Schema
-- Cotarco Commercial Manager
-- =============================================================================
-- Idempotent: safe to run multiple times on an existing database.
-- Execute via Supabase SQL Editor or psql.
--
-- Dependencies: PostgreSQL 14+ (pgcrypto / gen_random_uuid built-in via pg 13+)
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Extensions
-- ---------------------------------------------------------------------------

CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- gen_random_uuid() on PG < 13


-- ---------------------------------------------------------------------------
-- ENUM types
-- ---------------------------------------------------------------------------

DO $$ BEGIN
  CREATE TYPE user_role AS ENUM ('COMERCIAL', 'OPERADOR', 'ADMIN');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE job_status AS ENUM (
    'UPLOADED',
    'VALIDATING',
    'READY_FOR_REVIEW',
    'NEEDS_CORRECTION',
    'APPROVED',
    'PROCESSING',
    'COMPLETED',
    'FAILED',
    'CANCELLED'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;


-- ---------------------------------------------------------------------------
-- Table: users
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS users (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email           TEXT UNIQUE NOT NULL,
  display_name    TEXT,
  role            user_role NOT NULL DEFAULT 'COMERCIAL',
  is_active       BOOLEAN NOT NULL DEFAULT TRUE,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE users IS 'Local representation of Supabase Auth users. id aligns with auth.users.id.';
COMMENT ON COLUMN users.role IS 'COMERCIAL: submit/view own jobs. OPERADOR: approve/execute. ADMIN: full config.';


-- ---------------------------------------------------------------------------
-- Table: commercial_profiles
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS commercial_profiles (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code            TEXT UNIQUE NOT NULL,          -- machine key: MANO, BFA, WOOCOMMERCE …
  name            TEXT NOT NULL,
  type            TEXT NOT NULL                  -- STORE | MARKETPLACE | PARTNER | RESELLER | OTHER
                    CHECK (type IN ('STORE', 'MARKETPLACE', 'PARTNER', 'RESELLER', 'OTHER')),
  description     TEXT,
  active          BOOLEAN NOT NULL DEFAULT TRUE,
  config          JSONB NOT NULL DEFAULT '{}',   -- channel-specific options (integration type, feature flags)
  rules_version   INT NOT NULL DEFAULT 1,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE commercial_profiles IS 'Channel/destination configurations. New profiles added via config, not code.';
COMMENT ON COLUMN commercial_profiles.config IS 'Stores: integration_type (EXCEL_EXPORT | WOOCOMMERCE_API), stock_min, price_variation_threshold, feature flags.';


-- ---------------------------------------------------------------------------
-- Table: profile_rules
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS profile_rules (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id      UUID NOT NULL REFERENCES commercial_profiles(id) ON DELETE CASCADE,
  version         INT NOT NULL,
  rule_code       TEXT NOT NULL,   -- e.g. PRICE_VARIATION_THRESHOLD, MIN_STOCK, ALLOW_ZERO_PRICE
  rule_config     JSONB NOT NULL,
  active          BOOLEAN NOT NULL DEFAULT TRUE,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_by      UUID REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT uq_profile_rules_profile_version_code
    UNIQUE (profile_id, version, rule_code)
);

COMMENT ON TABLE profile_rules IS 'Versioned rule configurations per profile. Enables historical replay of decisions.';


-- ---------------------------------------------------------------------------
-- Table: processing_jobs
-- ---------------------------------------------------------------------------

CREATE SEQUENCE IF NOT EXISTS processing_jobs_job_number_seq START 1;

CREATE TABLE IF NOT EXISTS processing_jobs (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_number      BIGINT UNIQUE DEFAULT nextval('processing_jobs_job_number_seq'),
  profile_id      UUID NOT NULL REFERENCES commercial_profiles(id) ON DELETE RESTRICT,
  created_by      UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  approved_by     UUID REFERENCES users(id) ON DELETE SET NULL,
  status          job_status NOT NULL DEFAULT 'UPLOADED',
  source_name     TEXT,                          -- original filename / source label
  source_system   TEXT,                          -- SAMSUNG | COMERCIAL | ERP | …
  description     TEXT,
  options         JSONB NOT NULL DEFAULT '{}',   -- dry_run, overrides, flags
  summary         JSONB,                         -- ProcessSummary serialised post-processing
  error_message   TEXT,
  started_at      TIMESTAMPTZ,
  completed_at    TIMESTAMPTZ,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE processing_jobs IS 'Core operational entity. One job per submitted price/stock table.';
COMMENT ON COLUMN processing_jobs.job_number IS 'Sequential human-friendly reference number (e.g. Job #42).';
COMMENT ON COLUMN processing_jobs.summary IS 'Serialised ProcessSummary: updated, new_added, blocked_*, ignored_* counts.';

CREATE INDEX IF NOT EXISTS idx_jobs_profile_status ON processing_jobs(profile_id, status);
CREATE INDEX IF NOT EXISTS idx_jobs_created_by ON processing_jobs(created_by, created_at DESC);


-- ---------------------------------------------------------------------------
-- Table: job_files
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS job_files (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id          UUID NOT NULL REFERENCES processing_jobs(id) ON DELETE CASCADE,
  kind            TEXT NOT NULL CHECK (kind IN ('INPUT', 'OUTPUT', 'LOG', 'REPORT')),
  original_name   TEXT,
  storage_path    TEXT,                          -- Supabase Storage path (bucket/path/file.xlsx)
  sha256          TEXT NOT NULL,                 -- SHA-256 hex of the binary blob
  size_bytes      BIGINT,
  mime_type       TEXT,
  version         INT NOT NULL DEFAULT 1,
  uploaded_by     UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE job_files IS 'Metadata for files in Supabase Storage. Original files are NEVER overwritten (Guardrail #9).';
COMMENT ON COLUMN job_files.sha256 IS 'Used for duplicate detection and integrity verification.';

CREATE INDEX IF NOT EXISTS idx_job_files_job ON job_files(job_id, created_at DESC);


-- ---------------------------------------------------------------------------
-- Table: job_items
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS job_items (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id                UUID NOT NULL REFERENCES processing_jobs(id) ON DELETE CASCADE,
  reference_original    TEXT NOT NULL,
  reference_normalized  TEXT NOT NULL,
  old_price             NUMERIC(14, 2),
  new_price             NUMERIC(14, 2),
  old_stock             INTEGER,
  new_stock             INTEGER,
  price_variation_pct   NUMERIC(8, 2),
  decision              TEXT NOT NULL,           -- human-readable description
  decision_code         TEXT NOT NULL,           -- enum: UPDATE | NEW_PRODUCT | BLOCKED_* | IGNORED_*
  details               JSONB,                   -- auxiliary metrics
  created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE job_items IS 'Per-reference evaluation result from the domain engine.';
COMMENT ON COLUMN job_items.decision_code IS 'Maps to DecisionCode enum in domain/models.py.';

CREATE INDEX IF NOT EXISTS idx_job_items_job_ref
  ON job_items(job_id, reference_normalized);


-- ---------------------------------------------------------------------------
-- Table: validation_issues
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS validation_issues (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id          UUID NOT NULL REFERENCES processing_jobs(id) ON DELETE CASCADE,
  job_item_id     UUID REFERENCES job_items(id) ON DELETE SET NULL,
  severity        TEXT NOT NULL CHECK (severity IN ('INFO', 'WARNING', 'ERROR', 'BLOCKER')),
  code            TEXT NOT NULL,                 -- e.g. MISSING_COLUMN, PRICE_VARIATION_BLOCKED
  message         TEXT NOT NULL,
  field           TEXT,
  row_number      INTEGER,
  details         JSONB,
  resolved        BOOLEAN NOT NULL DEFAULT FALSE,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE validation_issues IS 'Structured validation/business-rule violations per job.';
COMMENT ON COLUMN validation_issues.resolved IS 'Comercial can mark issues as resolved after correction.';

CREATE INDEX IF NOT EXISTS idx_validation_job_severity
  ON validation_issues(job_id, severity);


-- ---------------------------------------------------------------------------
-- Table: approvals
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS approvals (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id      UUID NOT NULL REFERENCES processing_jobs(id) ON DELETE CASCADE,
  action      TEXT NOT NULL CHECK (action IN ('APPROVED', 'REJECTED', 'CANCELLED')),
  actor_id    UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  comment     TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE approvals IS 'Immutable approval/rejection/cancellation audit trail. Append-only by convention.';


-- ---------------------------------------------------------------------------
-- Table: price_history
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS price_history (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id            UUID REFERENCES commercial_profiles(id) ON DELETE SET NULL,
  job_id                UUID NOT NULL REFERENCES processing_jobs(id) ON DELETE RESTRICT,
  reference_normalized  TEXT NOT NULL,
  old_price             NUMERIC(14, 2),
  new_price             NUMERIC(14, 2),
  variation_pct         NUMERIC(8, 2),
  change_type           TEXT NOT NULL CHECK (change_type IN ('UPDATED', 'NEW', 'BLOCKED')),
  recorded_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  recorded_by           UUID REFERENCES users(id) ON DELETE SET NULL
);

COMMENT ON TABLE price_history IS 'Immutable ledger of price changes — append-only.';

CREATE INDEX IF NOT EXISTS idx_price_history_ref_date
  ON price_history(reference_normalized, recorded_at DESC);


-- ---------------------------------------------------------------------------
-- Table: audit_logs  — APPEND-ONLY
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS audit_logs (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  actor_id      UUID REFERENCES users(id) ON DELETE SET NULL,
  action        TEXT NOT NULL,                   -- e.g. JOB_CREATED, JOB_APPROVED, PROFILE_UPDATED
  entity_type   TEXT NOT NULL,                   -- e.g. processing_job, commercial_profile, user
  entity_id     UUID,
  job_id        UUID REFERENCES processing_jobs(id) ON DELETE SET NULL,
  metadata      JSONB,
  ip_hash       TEXT,                            -- SHA-256 of client IP — NEVER store raw IP
  user_agent    TEXT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE audit_logs IS
  'SECURITY: This table is APPEND-ONLY. No UPDATE or DELETE is permitted. '
  'RLS enforces INSERT-only access. All administrative actions produce a row here.';
COMMENT ON COLUMN audit_logs.ip_hash IS 'One-way SHA-256 hash of client IP. Raw IP is NEVER stored.';

CREATE INDEX IF NOT EXISTS idx_audit_entity
  ON audit_logs(entity_type, entity_id, created_at DESC);


-- ---------------------------------------------------------------------------
-- updated_at auto-update trigger (reusable)
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to tables with updated_at
DO $$
DECLARE
  tbl TEXT;
BEGIN
  FOREACH tbl IN ARRAY ARRAY['users', 'commercial_profiles', 'processing_jobs', 'job_items']
  LOOP
    IF NOT EXISTS (
      SELECT 1 FROM pg_trigger
      WHERE tgname = 'set_updated_at_' || tbl
    ) THEN
      EXECUTE format(
        'CREATE TRIGGER set_updated_at_%I
         BEFORE UPDATE ON %I
         FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at()',
        tbl, tbl
      );
    END IF;
  END LOOP;
END $$;


-- =============================================================================
-- END OF MIGRATION 001
-- =============================================================================
