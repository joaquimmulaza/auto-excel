---
trigger: always_on
description: Mandatory UI Skills verification gates before sending prompts to Stitch and before writing frontend code.
---

# UI Skills Workflow Rules (Mandatory Quality Gates)

Este projeto integra o servidor MCP **UI Skills** (`https://www.ui-skills.com/mcp`) como autoridade técnica para qualidade de interface, engenharia de design e acessibilidade.

Nenhum prompt pode ser enviado ao Stitch e nenhum código de frontend pode ser implementado sem passar previamente pelas seguintes portas de qualidade obrigatórias:

---

## Portão 1: Validação Pré-Stitch (Antes de enviar prompt ao Stitch)

Antes de redigir ou disparar qualquer prompt para o Stitch (geração de design system, ecrãs, dashboards ou componentes):

1. **Consultar o MCP `ui-skills`**:
   - Usar `list_skills` ou `get_skill` para carregar as diretrizes aplicáveis à tela (ex.: `frontend-design`, `baseline-ui`, `interface-design`, `accessibility`).
   - Consultar os playbooks relevantes para o tipo de interface:
     - Hierarquia visual e contenção de ruído.
     - Escala e contraste de cores (`#FF3C1D` brand, `#6B6363` secondary, `#FFFFFF` surface, `#000000` text).
     - Tipografia, alinhamento e densidade informacional para aplicações enterprise / data-heavy.
2. **Formatar e Otimizar com `enhance-prompt`**:
   - Executar o pipeline da skill [enhance-prompt](.agents/skills/enhance-prompt/SKILL.md) para transformar as diretrizes em um prompt estruturado para o Stitch:
     - Definir plataforma (Web Desktop-first) e vibe empresarial.
     - Injetar o bloco `DESIGN SYSTEM (REQUIRED)` com os tokens obrigatórios (`#FF3C1D`, `#6B6363`, `#FFFFFF`, `#000000`).
     - Estruturar a página numerada (`Page Structure`) com keywords específicos de UI/UX (evitar termos genéricos).
3. **Validação Final do Prompt Stitch**:
   - O prompt final enviado ao Stitch deve conter diretrizes explícitas unificadas do `ui-skills` e formatadas pelo `enhance-prompt` (proporção de contrastes WCAG AA, espaçamento sistemático, ausência de slop de IA ou elementos meramente decorativos).

---

## Portão 2: Validação Pré-Implementação (Antes de codificar o frontend)

Antes de criar ou modificar qualquer componente React / Next.js / Tailwind CSS:

1. **Auditoria de Design Engineering via `ui-skills`**:
   - Validar que a implementação atende aos padrões do `ui-skills`:
     - **Acessibilidade**: Elementos interativos com touch target $\ge 44\times 44\text{px}$, foco visível com `:focus-visible`, labels semânticos em formulários, status com texto + cor (nunca cor isolada).
     - **Tabelas e Dados**: Uso obrigatório de `tabular-nums` para alinhamento de preços e quantidades, truncamento suave com fade ou line-clamp.
     - **Tipografia e Espaçamento**: `text-balance` em títulos, `text-pretty` em parágrafos, agrupamento por espaçamento antes de usar linhas divisórias.
     - **Feedback Visual**: Skeletons estruturais em carregamento inicial (sem spinners em ecrãs completos), transições CSS curtas e interrompíveis.
2. **Execução Cirúrgica**:
   - O código deve reproduzir a intenção validada no Stitch e refinada pelo `ui-skills`, sem importar slop ou CSS ad-hoc.
