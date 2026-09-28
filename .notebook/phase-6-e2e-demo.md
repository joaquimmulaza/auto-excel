# Fase 6 - E2E Demo e Ajustes da Inteligência Artificial

## Resumo Executivo
A Fase 6 incidiu na validação final ponta-a-ponta de toda a aplicação Cotarco Commercial Manager e da configuração da integração entre Frontend (Next.js), Backend (FastAPI), Supabase e o Assistente de Inteligência Artificial Gemini (assistência contextual). 

A suíte de testes (118 testes originais backend + novos testes E2E em Playwright) corre na totalidade com sucesso, sem qualquer regressão, e garante a qualidade e resiliência da aplicação.

## Ajustes da Inteligência Artificial
Para garantir a fiabilidade da assistência contextual (explicações, resumos, sugestões de colunas) fornecida pelo Google Gemini, e mantendo o controlo de custos na API (Free Tier), foram efetuadas as seguintes calibrações no backend:
1. **Calibração do Rate-Limiter:** Ajustado in-memory de 20 RPM para **12 RPM** (`_RATE_LIMIT = 12` em `ai.py`), acomodando assim a limitação de 15 RPM da versão gratuita da API.
2. **Implementação de Cache:** Adicionada uma estrutura de _cache_ por chave (`job_id:issue_code:language`) no serviço `explain_issue` em `ai_service.py` para prevenir chamadas redundantes quando um utilizador solicita repetidamente a explicação para o mesmo erro.

## Testes End-to-End (E2E) com Playwright
Foram implementados testes essenciais validando a experiência de utilizador:

### 1. `test_commercial_job_submission_and_diff.spec.ts`
Garante a estabilidade no fluxo do Comercial:
- Mock do "Comercial" e carregamento da ferramenta de upload na interface com verificação de ficheiro `.xlsx`.
- Envio de ficheiro de preço simulado ("Mano-preco-desatualizado.xlsx").
- Redirecionamento e visualização na grelha do `DiffViewer`.
- Aplicação de diferentes filtros ("Todos", "Atualizados", "Bloqueados").
- Interação e acionamento do "Explicar com IA" sobre uma anomalia, validando a abertura do modal sem erros com o conselho da IA.
- Verificação da segurança da UI (RBAC), assegurando que o Comercial não pode "Aprovar Processamento".

### 2. `test_operator_approval_workflow.spec.ts`
Valida o fluxo crítico do Operador de negócio:
- Mudança para papel "Operador" na interface (destaque `#FF3C1D`).
- Acesso à grelha de tarefas pendentes.
- Botão de "Aprovar Processamento" disponível e não desabilitado.
- Execução do clique de aprovação, simulando a transformação para a mudança de estado para "Aprovado".

### 3. `test_accessibility_and_responsive_audit.spec.ts`
Auditoria de UX de base focada na acessibilidade e performance (Core Web Vitals):
- Verificação do contraste e presença da cor primária da marca (`#FF3C1D`).
- Dimensão dos botões e botões com _touch targets_ conformes para navegação (>= 44px).
- Simulação de leitura de `layout-shift` (CLS < 0.1).

## Declaração de Prontidão (MVP Completion Statement)
> O sistema (Frontend + Backend + IA Assistiva + Base de Dados) encontra-se funcional, sincronizado no Grafo de Conhecimento local, sem erros na suíte de testes automática e completamente livre de regressões. Todos os testes passam (118 testes de backend + 3 de E2E em Playwright).
>
> A plataforma está apta a avançar para as sessões de Homologação / User Acceptance Testing (UAT) finais com o Diretor Comercial e os utilizadores do Backoffice.
