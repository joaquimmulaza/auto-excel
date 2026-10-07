/**
 * API client for Cotarco Commercial Manager FastAPI backend.
 */
import {
  JobResponse,
  JobListResponse,
  JobCreateRequest,
  JobItemResponse,
  ValidationIssueResponse,
  JobSummaryResponse,
  ProfileListResponse,
  ProfileResponse,
  ApprovalResponse,
  AIExplainIssueRequest,
  AIAnomalyExplanation,
  AIResponse,
  CurrentUser,
} from "@/types";

const TOKEN_KEY = "ccm_access_token";

/**
 * Resolve API base URL.
 * - Explicit NEXT_PUBLIC_API_URL wins
 * - On Vercel / non-localhost hosts, use same-origin `/api/v1` (Vercel Services rewrite)
 * - Local dev defaults to FastAPI on :8000
 */
export function getApiBaseUrl(): string {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, "");
  }
  if (typeof window !== "undefined") {
    const host = window.location.hostname;
    if (host !== "localhost" && host !== "127.0.0.1") {
      return `${window.location.origin}/api/v1`;
    }
  }
  return "http://localhost:8000/api/v1";
}

export function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token: string | null): void {
  if (typeof window === "undefined") return;
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

export function getAuthHeaders(extra?: HeadersInit): HeadersInit {
  const headers: Record<string, string> = {
    ...(extra as Record<string, string>),
  };
  const token = getStoredToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

type ApiError = Error & { code?: string; status?: number };

async function parseError(res: Response): Promise<ApiError> {
  const data = await res.json().catch(() => ({}));
  const nested = data?.error || data?.detail?.error || {};
  const message =
    nested.message ||
    nested.code ||
    (typeof data?.detail === "string" ? data.detail : null) ||
    `Erro HTTP ${res.status}`;
  const err = new Error(message) as ApiError;
  err.code = nested.code;
  err.status = res.status;
  return err;
}

function networkError(err: unknown): ApiError {
  const raw = err instanceof Error ? err.message : String(err);
  const friendly =
    raw === "Load failed" ||
    raw === "Failed to fetch" ||
    raw.includes("NetworkError") ||
    raw.includes("fetch")
      ? "Não foi possível contactar a API. Confirme que o backend está a correr (local: :8000) ou que o deploy Vercel inclui o serviço backend."
      : raw;
  const e = new Error(friendly) as ApiError;
  e.code = "NETWORK_ERROR";
  return e;
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  try {
    const res = await fetch(`${getApiBaseUrl()}${path}`, {
      ...init,
      headers: getAuthHeaders(init?.headers),
      cache: "no-store",
    });
    if (!res.ok) throw await parseError(res);
    if (res.status === 204) return undefined as T;
    return res.json();
  } catch (err) {
    if (err instanceof Error && (err as ApiError).status) throw err;
    throw networkError(err);
  }
}

export async function login(
  email: string,
  password: string
): Promise<{ access_token: string; user: CurrentUser }> {
  try {
    const res = await fetch(`${getApiBaseUrl()}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) throw await parseError(res);
    const data = await res.json();
    setStoredToken(data.access_token);
    return {
      access_token: data.access_token,
      user: {
        id: data.user.id,
        email: data.user.email,
        name: data.user.name || data.user.email,
        role: data.user.role,
      },
    };
  } catch (err) {
    if (err instanceof Error && (err as ApiError).status) throw err;
    throw networkError(err);
  }
}

export async function fetchMe(): Promise<CurrentUser> {
  const data = await apiFetch<{ id: string; email: string; name: string | null; role: string }>(
    "/auth/me"
  );
  return {
    id: data.id,
    email: data.email,
    name: data.name || data.email,
    role: data.role as CurrentUser["role"],
  };
}

export async function fetchProfiles(): Promise<ProfileListResponse> {
  return apiFetch<ProfileListResponse>("/profiles");
}

export async function fetchProfile(id: string): Promise<ProfileResponse> {
  return apiFetch<ProfileResponse>(`/profiles/${id}`);
}

export async function updateProfile(
  id: string,
  payload: { name?: string; description?: string; active?: boolean; config?: Record<string, unknown> }
): Promise<ProfileResponse> {
  return apiFetch<ProfileResponse>(`/profiles/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function fetchJobs(): Promise<JobListResponse> {
  return apiFetch<JobListResponse>("/jobs");
}

export async function fetchJob(jobId: string): Promise<JobResponse> {
  return apiFetch<JobResponse>(`/jobs/${jobId}`);
}

export async function createJob(data: JobCreateRequest): Promise<JobResponse> {
  return apiFetch<JobResponse>("/jobs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function uploadJobFile(
  jobId: string,
  file: File,
  kind: "INPUT" | "CATALOG" = "INPUT"
): Promise<{ id: string; kind: string; original_name: string; sha256: string }> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(
    `${getApiBaseUrl()}/jobs/${jobId}/files?kind=${encodeURIComponent(kind)}`,
    {
      method: "POST",
      headers: getAuthHeaders(),
      body: form,
    }
  );
  if (!res.ok) throw await parseError(res);
  return res.json();
}

export async function listJobFiles(
  jobId: string
): Promise<{ items: Array<{ id: string; kind: string; original_name: string; sha256: string; size_bytes: number }> }> {
  return apiFetch(`/jobs/${jobId}/files`);
}

export async function downloadJobFile(jobId: string, fileId: string, filename: string): Promise<void> {
  const res = await fetch(`${getApiBaseUrl()}/jobs/${jobId}/files/${fileId}/download`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw await parseError(res);
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export async function validateJob(
  jobId: string,
  dryRun?: boolean
): Promise<{ job_id: string; status: string; summary: Record<string, unknown>; dry_run: boolean }> {
  const qs = dryRun === undefined ? "" : `?dry_run=${dryRun ? "true" : "false"}`;
  return apiFetch(`/jobs/${jobId}/validate${qs}`, { method: "POST" });
}

export async function fetchJobSummary(jobId: string): Promise<JobSummaryResponse> {
  return apiFetch<JobSummaryResponse>(`/jobs/${jobId}/summary`);
}

export async function fetchJobItems(jobId: string): Promise<JobItemResponse[]> {
  return apiFetch<JobItemResponse[]>(`/jobs/${jobId}/items`);
}

export async function fetchJobIssues(jobId: string): Promise<ValidationIssueResponse[]> {
  return apiFetch<ValidationIssueResponse[]>(`/jobs/${jobId}/issues`);
}

export async function approveJob(jobId: string, comment?: string): Promise<ApprovalResponse> {
  return apiFetch<ApprovalResponse>(`/jobs/${jobId}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ comment }),
  });
}

export async function rejectJob(jobId: string, comment?: string): Promise<ApprovalResponse> {
  return apiFetch<ApprovalResponse>(`/jobs/${jobId}/reject`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ comment }),
  });
}

export async function processJob(jobId: string): Promise<{
  job_id: string;
  status: string;
  output_sha256: string;
  log_sha256: string;
  summary: Record<string, unknown>;
}> {
  return apiFetch(`/jobs/${jobId}/process`, { method: "POST" });
}

export async function fetchReceipt(jobId: string): Promise<Record<string, unknown>> {
  return apiFetch(`/jobs/${jobId}/receipt`);
}

export async function fetchExceptions(): Promise<{
  items: Array<Record<string, unknown>>;
  total: number;
}> {
  return apiFetch("/exceptions");
}

export async function fetchPriceHistory(
  reference: string
): Promise<{ items: Array<Record<string, unknown>> }> {
  return apiFetch(`/history/prices?reference=${encodeURIComponent(reference)}`);
}

export async function explainIssueWithAi(
  jobId: string,
  payload: AIExplainIssueRequest
): Promise<AIResponse<AIAnomalyExplanation>> {
  try {
    return await apiFetch<AIResponse<AIAnomalyExplanation>>(
      `/jobs/${jobId}/ai/explain-issue`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }
    );
  } catch {
    const isBlocker = payload.severity === "BLOCKER";
    return {
      is_ai_generated: false,
      fallback_used: true,
      data: {
        title: `Problema detectado: ${payload.issue_code}`,
        plain_explanation: payload.issue_message,
        likely_cause: explainBlockCode(payload.issue_code),
        suggested_action:
          "Reveja a referência no Excel de origem, corrija o valor e volte a validar o lote.",
        is_blocker: isBlocker,
      },
    };
  }
}

/** Deterministic Portuguese explanation for decision / issue codes. */
export function explainBlockCode(code: string): string {
  const map: Record<string, string> = {
    PRICE_VARIATION_BLOCKED:
      "A variação de preço ultrapassa o limiar do Price Guard do perfil comercial.",
    BLOCKED_PRICE_VARIATION:
      "A variação de preço ultrapassa o limiar do Price Guard do perfil comercial.",
    BLOQUEADO_VARIACAO_EXCESSIVA:
      "A variação de preço ultrapassa o limiar do Price Guard do perfil comercial.",
    BLOCKED_ZERO_PRICE: "Preço zero não é permitido para este perfil.",
    ZERO_PRICE_REJECTED: "Preço zero não é permitido para este perfil.",
    BLOCKED_DUPLICATE_REF: "Referência duplicada no ficheiro de origem.",
    DUPLICATE_REFERENCE: "Referência duplicada no ficheiro de origem.",
    STOCK_BELOW_MINIMUM:
      "Stock abaixo do mínimo configurado para ativação de produto novo.",
    IGNORED_STOCK: "Ignorado por stock insuficiente segundo as regras do perfil.",
    STOCK_THRESHOLD_IGNORED:
      "Ignorado por stock insuficiente segundo as regras do perfil.",
  };
  return map[code] || `Regra de negócio aplicada: ${code}.`;
}
