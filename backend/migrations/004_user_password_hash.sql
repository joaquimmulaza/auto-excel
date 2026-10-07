-- Add local password hash for JWT login (dev/local auth bridge).
-- Supabase Auth remains the production identity source; this column
-- supports the local FastAPI login until Auth is wired end-to-end.

ALTER TABLE users
  ADD COLUMN IF NOT EXISTS password_hash TEXT;

COMMENT ON COLUMN users.password_hash IS
  'Optional bcrypt hash for local JWT login. Null when using Supabase Auth only.';
