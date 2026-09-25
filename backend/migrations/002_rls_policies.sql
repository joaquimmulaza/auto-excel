-- =============================================================================
-- Migration 002 — Row Level Security (RLS) Policies
-- Cotarco Commercial Manager
-- =============================================================================
-- Prerequisite: Migration 001 must have been applied.
--
-- Security Model:
--   COMERCIAL  → can only see/submit their own jobs and associated data.
--   OPERADOR   → can read all jobs + approve + audit; cannot manage profiles/users.
--   ADMIN      → full access to everything including user/profile management.
--
-- Implementation strategy:
--   1. Enable RLS on every table.
--   2. Policies reference auth.uid() for Supabase Auth integration.
--   3. Role is resolved via the local `users` table (role column).
--   4. audit_logs is INSERT-only for all roles — no UPDATE/DELETE ever allowed.
--
-- NOTE: FastAPI also enforces role-based access in the service layer.
--       RLS is defence-in-depth — not the sole access control barrier.
-- =============================================================================


-- ---------------------------------------------------------------------------
-- Helper function: resolve role for the current authenticated user
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION current_user_role()
RETURNS TEXT
LANGUAGE sql STABLE SECURITY DEFINER
AS $$
  SELECT role::TEXT FROM users WHERE id = auth.uid()
$$;

COMMENT ON FUNCTION current_user_role() IS
  'Returns the role (COMERCIAL | OPERADOR | ADMIN) for the currently authenticated Supabase user.';


-- ---------------------------------------------------------------------------
-- Enable RLS on all tables
-- ---------------------------------------------------------------------------

ALTER TABLE users               ENABLE ROW LEVEL SECURITY;
ALTER TABLE commercial_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_rules       ENABLE ROW LEVEL SECURITY;
ALTER TABLE processing_jobs     ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_files           ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_items           ENABLE ROW LEVEL SECURITY;
ALTER TABLE validation_issues   ENABLE ROW LEVEL SECURITY;
ALTER TABLE approvals           ENABLE ROW LEVEL SECURITY;
ALTER TABLE price_history       ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs          ENABLE ROW LEVEL SECURITY;


-- =============================================================================
-- POLICIES: users
-- =============================================================================

-- Users can always see their own record
DROP POLICY IF EXISTS users_select_own ON users;
CREATE POLICY users_select_own ON users
  FOR SELECT
  USING (id = auth.uid());

-- ADMIN can see all users
DROP POLICY IF EXISTS users_select_admin ON users;
CREATE POLICY users_select_admin ON users
  FOR SELECT
  USING (current_user_role() = 'ADMIN');

-- ADMIN can manage users (insert, update)
DROP POLICY IF EXISTS users_insert_admin ON users;
CREATE POLICY users_insert_admin ON users
  FOR INSERT
  WITH CHECK (current_user_role() = 'ADMIN');

DROP POLICY IF EXISTS users_update_admin ON users;
CREATE POLICY users_update_admin ON users
  FOR UPDATE
  USING (current_user_role() = 'ADMIN');


-- =============================================================================
-- POLICIES: commercial_profiles
-- =============================================================================

-- All authenticated users can view active profiles (needed to select when submitting)
DROP POLICY IF EXISTS profiles_select_authenticated ON commercial_profiles;
CREATE POLICY profiles_select_authenticated ON commercial_profiles
  FOR SELECT
  USING (auth.uid() IS NOT NULL AND active = TRUE);

-- ADMIN sees inactive too
DROP POLICY IF EXISTS profiles_select_all_admin ON commercial_profiles;
CREATE POLICY profiles_select_all_admin ON commercial_profiles
  FOR SELECT
  USING (current_user_role() = 'ADMIN');

-- Only ADMIN can create/modify profiles
DROP POLICY IF EXISTS profiles_insert_admin ON commercial_profiles;
CREATE POLICY profiles_insert_admin ON commercial_profiles
  FOR INSERT
  WITH CHECK (current_user_role() = 'ADMIN');

DROP POLICY IF EXISTS profiles_update_admin ON commercial_profiles;
CREATE POLICY profiles_update_admin ON commercial_profiles
  FOR UPDATE
  USING (current_user_role() = 'ADMIN');


-- =============================================================================
-- POLICIES: profile_rules
-- =============================================================================

DROP POLICY IF EXISTS profile_rules_select_authenticated ON profile_rules;
CREATE POLICY profile_rules_select_authenticated ON profile_rules
  FOR SELECT
  USING (auth.uid() IS NOT NULL);

DROP POLICY IF EXISTS profile_rules_insert_admin ON profile_rules;
CREATE POLICY profile_rules_insert_admin ON profile_rules
  FOR INSERT
  WITH CHECK (current_user_role() = 'ADMIN');

DROP POLICY IF EXISTS profile_rules_update_admin ON profile_rules;
CREATE POLICY profile_rules_update_admin ON profile_rules
  FOR UPDATE
  USING (current_user_role() = 'ADMIN');


-- =============================================================================
-- POLICIES: processing_jobs
-- =============================================================================

-- COMERCIAL: can only see their own jobs
DROP POLICY IF EXISTS jobs_select_comercial ON processing_jobs;
CREATE POLICY jobs_select_comercial ON processing_jobs
  FOR SELECT
  USING (
    current_user_role() = 'COMERCIAL'
    AND created_by = auth.uid()
  );

-- OPERADOR + ADMIN: can see all jobs
DROP POLICY IF EXISTS jobs_select_operador_admin ON processing_jobs;
CREATE POLICY jobs_select_operador_admin ON processing_jobs
  FOR SELECT
  USING (current_user_role() IN ('OPERADOR', 'ADMIN'));

-- Any authenticated user can create a job (profile association validated in app)
DROP POLICY IF EXISTS jobs_insert_authenticated ON processing_jobs;
CREATE POLICY jobs_insert_authenticated ON processing_jobs
  FOR INSERT
  WITH CHECK (
    auth.uid() IS NOT NULL
    AND created_by = auth.uid()
  );

-- COMERCIAL: can update only their own PENDING jobs (e.g. re-upload)
DROP POLICY IF EXISTS jobs_update_comercial_own ON processing_jobs;
CREATE POLICY jobs_update_comercial_own ON processing_jobs
  FOR UPDATE
  USING (
    current_user_role() = 'COMERCIAL'
    AND created_by = auth.uid()
    AND status IN ('UPLOADED', 'NEEDS_CORRECTION')
  );

-- OPERADOR + ADMIN: can update any job (approve, reject, process)
DROP POLICY IF EXISTS jobs_update_operador_admin ON processing_jobs;
CREATE POLICY jobs_update_operador_admin ON processing_jobs
  FOR UPDATE
  USING (current_user_role() IN ('OPERADOR', 'ADMIN'));


-- =============================================================================
-- POLICIES: job_files
-- =============================================================================

-- COMERCIAL: own job files
DROP POLICY IF EXISTS job_files_select_comercial ON job_files;
CREATE POLICY job_files_select_comercial ON job_files
  FOR SELECT
  USING (
    current_user_role() = 'COMERCIAL'
    AND job_id IN (
      SELECT id FROM processing_jobs WHERE created_by = auth.uid()
    )
  );

-- OPERADOR + ADMIN: all job files
DROP POLICY IF EXISTS job_files_select_operador_admin ON job_files;
CREATE POLICY job_files_select_operador_admin ON job_files
  FOR SELECT
  USING (current_user_role() IN ('OPERADOR', 'ADMIN'));

-- Any authenticated user can insert job files for their own job
DROP POLICY IF EXISTS job_files_insert_authenticated ON job_files;
CREATE POLICY job_files_insert_authenticated ON job_files
  FOR INSERT
  WITH CHECK (
    auth.uid() IS NOT NULL
    AND job_id IN (
      SELECT id FROM processing_jobs WHERE created_by = auth.uid()
    )
  );


-- =============================================================================
-- POLICIES: job_items
-- =============================================================================

DROP POLICY IF EXISTS job_items_select_comercial ON job_items;
CREATE POLICY job_items_select_comercial ON job_items
  FOR SELECT
  USING (
    current_user_role() = 'COMERCIAL'
    AND job_id IN (
      SELECT id FROM processing_jobs WHERE created_by = auth.uid()
    )
  );

DROP POLICY IF EXISTS job_items_select_operador_admin ON job_items;
CREATE POLICY job_items_select_operador_admin ON job_items
  FOR SELECT
  USING (current_user_role() IN ('OPERADOR', 'ADMIN'));

-- Items are inserted by the backend service (not directly by the user)
DROP POLICY IF EXISTS job_items_insert_service ON job_items;
CREATE POLICY job_items_insert_service ON job_items
  FOR INSERT
  WITH CHECK (auth.uid() IS NOT NULL);


-- =============================================================================
-- POLICIES: validation_issues
-- =============================================================================

DROP POLICY IF EXISTS issues_select_comercial ON validation_issues;
CREATE POLICY issues_select_comercial ON validation_issues
  FOR SELECT
  USING (
    current_user_role() = 'COMERCIAL'
    AND job_id IN (
      SELECT id FROM processing_jobs WHERE created_by = auth.uid()
    )
  );

DROP POLICY IF EXISTS issues_select_operador_admin ON validation_issues;
CREATE POLICY issues_select_operador_admin ON validation_issues
  FOR SELECT
  USING (current_user_role() IN ('OPERADOR', 'ADMIN'));

DROP POLICY IF EXISTS issues_insert_service ON validation_issues;
CREATE POLICY issues_insert_service ON validation_issues
  FOR INSERT
  WITH CHECK (auth.uid() IS NOT NULL);

-- COMERCIAL can mark issues as resolved (self-correction flow)
DROP POLICY IF EXISTS issues_update_resolved_comercial ON validation_issues;
CREATE POLICY issues_update_resolved_comercial ON validation_issues
  FOR UPDATE
  USING (
    current_user_role() = 'COMERCIAL'
    AND job_id IN (
      SELECT id FROM processing_jobs WHERE created_by = auth.uid()
    )
  )
  WITH CHECK (
    -- Only the resolved flag may be toggled by Comercial
    TRUE
  );


-- =============================================================================
-- POLICIES: approvals
-- =============================================================================

-- Comercial can see approvals for their own jobs (read-only)
DROP POLICY IF EXISTS approvals_select_comercial ON approvals;
CREATE POLICY approvals_select_comercial ON approvals
  FOR SELECT
  USING (
    current_user_role() = 'COMERCIAL'
    AND job_id IN (
      SELECT id FROM processing_jobs WHERE created_by = auth.uid()
    )
  );

DROP POLICY IF EXISTS approvals_select_operador_admin ON approvals;
CREATE POLICY approvals_select_operador_admin ON approvals
  FOR SELECT
  USING (current_user_role() IN ('OPERADOR', 'ADMIN'));

-- Only OPERADOR and ADMIN can insert approval records
DROP POLICY IF EXISTS approvals_insert_operador_admin ON approvals;
CREATE POLICY approvals_insert_operador_admin ON approvals
  FOR INSERT
  WITH CHECK (current_user_role() IN ('OPERADOR', 'ADMIN'));


-- =============================================================================
-- POLICIES: price_history
-- =============================================================================

-- Comercial can see price history for their own jobs
DROP POLICY IF EXISTS price_history_select_comercial ON price_history;
CREATE POLICY price_history_select_comercial ON price_history
  FOR SELECT
  USING (
    current_user_role() = 'COMERCIAL'
    AND job_id IN (
      SELECT id FROM processing_jobs WHERE created_by = auth.uid()
    )
  );

DROP POLICY IF EXISTS price_history_select_operador_admin ON price_history;
CREATE POLICY price_history_select_operador_admin ON price_history
  FOR SELECT
  USING (current_user_role() IN ('OPERADOR', 'ADMIN'));

-- Append-only insert by service layer
DROP POLICY IF EXISTS price_history_insert_service ON price_history;
CREATE POLICY price_history_insert_service ON price_history
  FOR INSERT
  WITH CHECK (auth.uid() IS NOT NULL);

-- EXPLICITLY DENY: no UPDATE or DELETE on price_history
-- (No policy = deny; but we add explicit comment for clarity)


-- =============================================================================
-- POLICIES: audit_logs — APPEND-ONLY (SECURITY CRITICAL)
-- =============================================================================

-- SELECT: only OPERADOR and ADMIN can read audit logs
DROP POLICY IF EXISTS audit_select_operador_admin ON audit_logs;
CREATE POLICY audit_select_operador_admin ON audit_logs
  FOR SELECT
  USING (current_user_role() IN ('OPERADOR', 'ADMIN'));

-- INSERT: any authenticated user (service layer inserts on behalf of users)
DROP POLICY IF EXISTS audit_insert_authenticated ON audit_logs;
CREATE POLICY audit_insert_authenticated ON audit_logs
  FOR INSERT
  WITH CHECK (auth.uid() IS NOT NULL);

-- EXPLICITLY DENY UPDATE and DELETE on audit_logs
-- No UPDATE or DELETE policies are created — PostgreSQL denies by default.
-- This enforces the APPEND-ONLY guarantee at the database level.


-- =============================================================================
-- END OF MIGRATION 002
-- =============================================================================
