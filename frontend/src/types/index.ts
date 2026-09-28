/**
 * TypeScript types synchronized with Backend Pydantic v2 schemas.
 * (backend/app/schemas/job.py, processing.py, profile.py)
 */

export type UserRole = "COMERCIAL" | "OPERADOR" | "ADMIN";

export interface CurrentUser {
  id: string;
  email: string;
  name: string;
  role: UserRole;
}

export type JobStatus =
  | "UPLOADED"
  | "VALIDATING"
  | "READY_FOR_REVIEW"
  | "NEEDS_CORRECTION"
  | "APPROVED"
  | "PROCESSING"
  | "COMPLETED"
  | "FAILED"
  | "CANCELLED";

export interface JobCreateRequest {
  profile_id: string;
  source_system?: string | null;
  description?: string | null;
  options?: Record<string, unknown>;
}

export interface JobResponse {
  id: string;
  job_number?: number | null;
  profile_id: string;
  created_by_id: string;
  approved_by_id?: string | null;
  status: JobStatus;
  source_system?: string | null;
  description?: string | null;
  options: Record<string, unknown>;
  summary?: {
    total?: number;
    updated?: number;
    new?: number;
    ignored?: number;
    blocked?: number;
    [key: string]: unknown;
  } | null;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
}

export interface JobListResponse {
  items: JobResponse[];
  total: number;
}

export interface ApprovalRequest {
  comment?: string | null;
}

export interface ApprovalResponse {
  id: string;
  job_id: string;
  action: string;
  actor_id: string;
  comment?: string | null;
  created_at: string;
}

export interface JobItemResponse {
  id: string;
  job_id: string;
  reference_original: string;
  reference_normalized: string;
  old_price?: number | null;
  new_price?: number | null;
  old_stock?: number | null;
  new_stock?: number | null;
  price_variation_pct?: number | null;
  decision: "UPDATE" | "NEW" | "IGNORED" | "BLOCKED" | string;
  decision_code: string;
  details?: Record<string, unknown> | null;
  created_at: string;
}

export interface ValidationIssueResponse {
  id: string;
  job_id: string;
  severity: "BLOCKER" | "ERROR" | "WARNING" | "INFO" | string;
  code: string;
  message: string;
  field?: string | null;
  row_number?: number | null;
  details?: Record<string, unknown> | null;
  resolved: boolean;
  created_at: string;
}

export interface JobSummaryResponse {
  job_id: string;
  status: JobStatus;
  summary?: {
    total?: number;
    updated?: number;
    new?: number;
    ignored?: number;
    blocked?: number;
    [key: string]: unknown;
  } | null;
  issues_by_severity: Record<string, number>;
}

export interface ProfileResponse {
  id: string;
  code: string;
  name: string;
  type: string;
  description?: string | null;
  active: boolean;
  config: {
    price_guard_threshold_pct?: number;
    new_product_min_stock?: number;
    [key: string]: unknown;
  };
  rules_version: number;
  created_at: string;
  updated_at: string;
}

export interface ProfileListResponse {
  items: ProfileResponse[];
  total: number;
}
