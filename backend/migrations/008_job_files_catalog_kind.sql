-- Allow CATALOG uploads used by the validate pipeline (optional base catalog).
-- 001_initial_schema only permitted INPUT | OUTPUT | LOG | REPORT.

ALTER TABLE job_files DROP CONSTRAINT IF EXISTS job_files_kind_check;

ALTER TABLE job_files
  ADD CONSTRAINT job_files_kind_check
  CHECK (kind = ANY (ARRAY[
    'INPUT'::text,
    'CATALOG'::text,
    'OUTPUT'::text,
    'LOG'::text,
    'REPORT'::text
  ]));

COMMENT ON COLUMN job_files.kind IS
  'INPUT | CATALOG | OUTPUT | LOG | REPORT. CATALOG is the optional base price table for validation.';
