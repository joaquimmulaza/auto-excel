# Fase 5 — Gemini AI Assistive Integration

**STATUS:** DONE
**TASK:** Phase 5
**SUMMARY:** Criação do serviço de inteligência assistiva no backend FastAPI com SDK `google-genai`. Implementados schemas Pydantic v2 estritos, guardrails determinísticos e três endpoints (explain-issue, summary e suggest-columns). O Gemini apenas explica e assiste, não decide preços, stocks nem aprova processos. Também incluídos fallbacks determinísticos no caso de indisponibilidade ou falhas da API Gemini, rate limit (in-memory) e integração de audit logs para uso da IA. Suite de testes completamente mockada.

**FILES:**
- `c:\up_prices\backend\app\schemas\ai.py` (Criação de schemas Pydantic)
- `c:\up_prices\backend\app\services\ai_service.py` (Lógica e prompts Gemini com SDK `google-genai`)
- `c:\up_prices\backend\app\api\v1\ai.py` (Endpoints protegidos por RBAC)
- `c:\up_prices\backend\app\api\v1\router.py` (Atualização p/ incluir `ai.router`)
- `c:\up_prices\backend\tests\test_api\test_ai_api.py` (Testes TDD completos mockados)

**TESTS:**
```bash
cd c:\up_prices\backend
pytest tests/test_api/test_ai_api.py -v
```

**QA:**
- **Segurança:** GEMINI_API_KEY referenciada apenas no backend (via env var).
- **Acessos:** `suggest-columns` restrito, RBAC verificado. Endpoints verificam propriedade de jobs. Rate limit incluído (20 req/min por utilizador). Fallback garantido; as respostas nunca dependem em absoluto do estado do SDK do Google.
- **Estruturação:** O Gemini devolve JSON mapeado exatamente para os Models do Pydantic (`generate_content` usando `response_mime_type="application/json"` e `system_instruction`).

**RISKS:**
- Rate Limit `in-memory` em `ai.py` perderá o estado se houver reinício do worker/FastAPI. Num cenário produtivo escalado (múltiplas instâncias no Cloud Run), poderá não proteger estritamente contra chamadas agressivas (seria recomendado Redis-backed rate limit futuro).
- A versão do SDK `google-genai==2.25.0` funciona bem, mas a constante migração da Google requer revisões periódicas do schema caso o Gemini altere formatações baseadas na versão do client.

**DOCS_UPDATED:**
- `.notebook/phase-5-gemini.md` (Criado)

**NEXT:** Fase 06 - Testes E2E com Playwright & Demo Final
