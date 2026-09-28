/**
 * API client connected to Cotarco Commercial Manager FastAPI backend.
 * Base URL: http://localhost:8000/api/v1
 */

import {
  JobResponse,
  JobListResponse,
  JobCreateRequest,
  JobItemResponse,
  ValidationIssueResponse,
  JobSummaryResponse,
  ProfileListResponse,
  ApprovalResponse, AIExplainIssueRequest, AIAnomalyExplanation, AIResponse,
} from "@/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Fallback demo data for immediate testing and resilience
export const DEMO_PROFILES = [
  {
    id: "11111111-1111-1111-1111-111111111111",
    code: "MANO",
    name: "Marketplace Mano",
    type: "MARKETPLACE",
    description: "ExportaÃ§Ã£o de preÃ§os e stocks com limiar de variaÃ§Ã£o de 30% e stock mÃ­nimo de 3 unidades para produtos novos.",
    active: true,
    config: { price_guard_threshold_pct: 30, new_product_min_stock: 3 },
    rules_version: 1,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: "22222222-2222-2222-2222-222222222222",
    code: "LOJA_ONLINE",
    name: "Loja Online Cotarco",
    type: "ECOMMERCE",
    description: "AtualizaÃ§Ã£o direta de catÃ¡logo do e-commerce Cotarco com regras de margem comercial.",
    active: true,
    config: { price_guard_threshold_pct: 25, new_product_min_stock: 1 },
    rules_version: 1,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: "33333333-3333-3333-3333-333333333333",
    code: "BFA",
    name: "BFA Wholesale",
    type: "PARTNER",
    description: "Tabela institucional de fornecimento e parcerias com preÃ§os especiais.",
    active: true,
    config: { price_guard_threshold_pct: 20, new_product_min_stock: 5 },
    rules_version: 1,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

export const DEMO_JOBS: JobResponse[] = [
  {
    id: "00000000-0000-0000-0000-000000000184",
    job_number: 184,
    profile_id: DEMO_PROFILES[0].id,
    created_by_id: "00000000-0000-0000-0000-000000000001",
    status: "READY_FOR_REVIEW",
    source_system: "SAMSUNG",
    description: "Tabela de PreÃ§os e Stocks Linha Branca Setembro 2026",
    options: {},
    summary: {
      total: 1248,
      updated: 843,
      new: 102,
      ignored: 271,
      blocked: 20,
    },
    created_at: new Date(Date.now() - 3600000 * 2).toISOString(),
    updated_at: new Date(Date.now() - 1800000).toISOString(),
  },
  {
    id: "00000000-0000-0000-0000-000000000183",
    job_number: 183,
    profile_id: DEMO_PROFILES[1].id,
    created_by_id: "00000000-0000-0000-0000-000000000001",
    status: "COMPLETED",
    source_system: "LG",
    description: "AtualizaÃ§Ã£o Televisores e Ãudio",
    options: {},
    summary: {
      total: 936,
      updated: 710,
      new: 180,
      ignored: 46,
      blocked: 0,
    },
    created_at: new Date(Date.now() - 86400000).toISOString(),
    updated_at: new Date(Date.now() - 82000000).toISOString(),
  },
  {
    id: "00000000-0000-0000-0000-000000000182",
    job_number: 182,
    profile_id: DEMO_PROFILES[0].id,
    created_by_id: "00000000-0000-0000-0000-000000000001",
    status: "NEEDS_CORRECTION",
    source_system: "SAMSUNG",
    description: "Lote Inicial Smartphone Galaxy SÃ©rie S",
    options: {},
    summary: {
      total: 1421,
      updated: 620,
      new: 210,
      ignored: 400,
      blocked: 191,
    },
    created_at: new Date(Date.now() - 86400000 * 3).toISOString(),
    updated_at: new Date(Date.now() - 86400000 * 3 + 3600000).toISOString(),
  },
];

export const DEMO_ITEMS: JobItemResponse[] = [
  {
    id: "item-1",
    job_id: "00000000-0000-0000-0000-000000000184",
    reference_original: "RS64R53112A/EU",
    reference_normalized: "RS64R53112A",
    old_price: 2393787,
    new_price: 2614035,
    old_stock: 0,
    new_stock: 3,
    price_variation_pct: 9.2,
    decision: "UPDATE",
    decision_code: "PRICE_AND_STOCK_UPDATE",
    created_at: new Date().toISOString(),
  },
  {
    id: "item-2",
    job_id: "00000000-0000-0000-0000-000000000184",
    reference_original: "RF71A967532UT",
    reference_normalized: "RF71A967532UT",
    old_price: 3980000,
    new_price: 3491228,
    old_stock: 8,
    new_stock: 9,
    price_variation_pct: -12.3,
    decision: "UPDATE",
    decision_code: "PRICE_AND_STOCK_UPDATE",
    created_at: new Date().toISOString(),
  },
  {
    id: "item-3",
    job_id: "00000000-0000-0000-0000-000000000184",
    reference_original: "RB34T602FSA",
    reference_normalized: "RB34T602FSA",
    old_price: 850000,
    new_price: 850000,
    old_stock: 14,
    new_stock: 22,
    price_variation_pct: 0.0,
    decision: "UPDATE",
    decision_code: "STOCK_UPDATE",
    created_at: new Date().toISOString(),
  },
  {
    id: "item-4",
    job_id: "00000000-0000-0000-0000-000000000184",
    reference_original: "WW90T554DAN",
    reference_normalized: "WW90T554DAN",
    old_price: null,
    new_price: 649900,
    old_stock: null,
    new_stock: 8,
    price_variation_pct: null,
    decision: "NEW",
    decision_code: "NEW_PRODUCT_CREATED",
    created_at: new Date().toISOString(),
  },
  {
    id: "item-5",
    job_id: "00000000-0000-0000-0000-000000000184",
    reference_original: "DV90T6240LK",
    reference_normalized: "DV90T6240LK",
    old_price: null,
    new_price: 520000,
    old_stock: null,
    new_stock: 1,
    price_variation_pct: null,
    decision: "IGNORED",
    decision_code: "STOCK_BELOW_MINIMUM",
    created_at: new Date().toISOString(),
  },
  {
    id: "item-6",
    job_id: "00000000-0000-0000-0000-000000000184",
    reference_original: "XXX-ANOMALY-REF",
    reference_normalized: "XXX_ANOMALY_REF",
    old_price: 2000000,
    new_price: 5500000,
    old_stock: 5,
    new_stock: 5,
    price_variation_pct: 175.0,
    decision: "BLOCKED",
    decision_code: "PRICE_VARIATION_BLOCKED",
    created_at: new Date().toISOString(),
  },
];

export const DEMO_ISSUES: ValidationIssueResponse[] = [
  {
    id: "issue-1",
    job_id: "00000000-0000-0000-0000-000000000184",
    severity: "BLOCKER",
    code: "PRICE_VARIATION_BLOCKED",
    message: "A variaÃ§Ã£o de preÃ§o (+175.0%) ultrapassa o limite de 30% configurado para o Marketplace Mano. Verifique a referÃªncia XXX_ANOMALY_REF.",
    field: "price",
    row_number: 142,
    resolved: false,
    created_at: new Date().toISOString(),
  },
  {
    id: "issue-2",
    job_id: "00000000-0000-0000-0000-000000000184",
    severity: "WARNING",
    code: "STOCK_THRESHOLD_IGNORED",
    message: "O produto DV90T6240LK foi ignorado porque o stock (1) Ã© inferior ao mÃ­nimo configurado (3).",
    field: "stock",
    row_number: 89,
    resolved: true,
    created_at: new Date().toISOString(),
  },
];

export async function fetchProfiles(): Promise<ProfileListResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/profiles`, { cache: "no-store" });
    if (!res.ok) throw new Error("API offline");
    return await res.json();
  } catch {
    return { items: DEMO_PROFILES, total: DEMO_PROFILES.length };
  }
}

export async function fetchJobs(): Promise<JobListResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/jobs`, { cache: "no-store" });
    if (!res.ok) throw new Error("API offline");
    return await res.json();
  } catch {
    return { items: DEMO_JOBS, total: DEMO_JOBS.length };
  }
}

export async function fetchJob(jobId: string): Promise<JobResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/jobs/${jobId}`, { cache: "no-store" });
    if (!res.ok) throw new Error("API offline");
    return await res.json();
  } catch {
    const found = DEMO_JOBS.find((j) => j.id === jobId) || DEMO_JOBS[0];
    return found;
  }
}

export async function createJob(data: JobCreateRequest): Promise<JobResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/jobs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("API offline");
    return await res.json();
  } catch {
    // Return created mock job
    const newJob: JobResponse = {
      id: `job-${Date.now()}`,
      job_number: Math.floor(Math.random() * 1000) + 185,
      profile_id: data.profile_id,
      created_by_id: "00000000-0000-0000-0000-000000000001",
      status: "VALIDATING",
      source_system: data.source_system || "SAMSUNG",
      description: data.description || "Novo Lote",
      options: data.options || {},
      summary: {
        total: 1248,
        updated: 843,
        new: 102,
        ignored: 271,
        blocked: 20,
      },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    DEMO_JOBS.unshift(newJob);
    return newJob;
  }
}

export async function fetchJobSummary(jobId: string): Promise<JobSummaryResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/jobs/${jobId}/summary`, { cache: "no-store" });
    if (!res.ok) throw new Error("API offline");
    return await res.json();
  } catch {
    return {
      job_id: jobId,
      status: "READY_FOR_REVIEW",
      summary: {
        total: 1248,
        updated: 843,
        new: 102,
        ignored: 271,
        blocked: 20,
      },
      issues_by_severity: { BLOCKER: 20, WARNING: 12 },
    };
  }
}

export async function fetchJobItems(jobId: string): Promise<JobItemResponse[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/jobs/${jobId}/items`, { cache: "no-store" });
    if (!res.ok) throw new Error("API offline");
    return await res.json();
  } catch {
    return DEMO_ITEMS;
  }
}

export async function fetchJobIssues(jobId: string): Promise<ValidationIssueResponse[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/jobs/${jobId}/issues`, { cache: "no-store" });
    if (!res.ok) throw new Error("API offline");
    return await res.json();
  } catch {
    return DEMO_ISSUES;
  }
}

export async function approveJob(jobId: string, comment?: string): Promise<ApprovalResponse> {
  const res = await fetch(`${API_BASE_URL}/jobs/${jobId}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ comment }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const message = errorData?.detail?.error?.message || "Erro ao aprovar processamento";
    throw new Error(message);
  }
  return await res.json();
}

export async function explainIssueWithAi(jobId: string, payload: AIExplainIssueRequest): Promise<AIResponse<AIAnomalyExplanation>> {
  const res = await fetch(API_BASE_URL + '/jobs/' + jobId + '/ai/explain-issue', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData?.detail?.error?.message || 'Falha ao obter explicação da IA');
  }
  return await res.json();
}


