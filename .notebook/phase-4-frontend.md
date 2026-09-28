# Fase 4 — Frontend & Google Stitch Loop

## 1. Visão Geral
Execução da **Fase 4 (Frontend & Google Stitch Loop)** do Cotarco Commercial Manager (CCM), cobrindo a prototipagem visual via Stitch MCP, criação da base Next.js (App Router), aplicação do Design System com tokens corporativos estritos e implementação da primeira fatia vertical completa conectada aos endpoints da API FastAPI.

---

## 2. Orquestração de Subagentes & Portões de Qualidade
A execução seguiu a matriz de isolamento e governança de design:
- **`stitch-designer` (Skills: `stitch-design`, `taste-design`)**:
  - Execução do **Portão 1 (Pré-Stitch)**: Refinamento dos prompts de `prompts/stitch/` com especificações `DESIGN SYSTEM (REQUIRED)` e `Page Structure`.
  - Acionamento do **Stitch MCP** para criar o projeto oficial e gerar os ecrãs desktop de alta densidade.
- **`frontend-agent` (Skills: `shadcn-ui`, `frontend-blueprint`, `taste-design`)**:
  - Bootstrap do Next.js 14 App Router em `frontend/`.
  - Configuração do Tailwind CSS com a paleta institucional da Cotarco.
  - Implementação dos componentes base shadcn/ui e da camada de integração HTTP com tipagem Pydantic v2 sincronizada.
  - Implementação do isolamento RBAC reativo no cliente (`UserSwitcher`).
- **`ui-qa-agent` (Skills: `web-quality-audit`, `core-web-vitals`, `tlc-spec-driven`)**:
  - Auditoria do **Portão 2 (Pré/Pós-Implementação)**: Conformidade com touch targets $\ge 44\times 44\text{px}$, `:focus-visible`, `tabular-nums` e feedback textual em badges.
  - Verificação de compilação: `npm run build` e `tsc --noEmit` aprovados com 0 erros.

---

## 3. Stitch MCP Loop & Ecrãs Criados
- **Projeto Stitch:** `projects/8549647647361663165` (*Cotarco Commercial Manager*)
- **Design System Asset:** `assets/8e4297416fdb403281fd966d51fe4e17` (*Precision Enterprise Commercial*)
- **Ecrãs Gerados:**
  1. **Dashboard Corporativo:**
     - Screen ID: `1001d8525c084ec48281b065416727a8`
     - Estrutura: KPIs operacionais, tabela de processamentos recentes e card de governança.
  2. **Novo Processamento (Upload):**
     - Screen ID: `a19e430400974a47beed6083d389f8fe`
     - Estrutura: Seletor de Perfil Comercial com regras contextuais, Dropzone Excel `.xlsx` e stepper de 3 fases.
  3. **Revisão e Tabela de Diff:**
     - Screen ID: `289841099180452aba6254a88f5aabd0`
     - Estrutura: Header de job, 5 Summary Cards, Diff Table de alta densidade com paginação e barra de aprovação RBAC.

---

## 4. Tokens Corporativos e Design Engineering
- **Tokens Institucionais:**
  - `brand`: `#FF3C1D` (Cotarco Red para CTAs primários e alertas críticos)
  - `secondary`: `#6B6363` (Slate Gray para legendas, bordas e metadados)
  - `surface`: `#FFFFFF` (Superfície limpa para cartões e tabelas)
  - `ink`: `#000000` (Texto principal de alto contraste)
  - `canvas`: `#F8F9FA` (Fundo neutro suave para longas jornadas de trabalho)
  - `border`: `#E5E7EB` (Delineação precisa de 1px)
- **Acessibilidade e Dados:**
  - `font-variant-numeric: tabular-nums` em todas as colunas de preços, percentagens e quantidades.
  - Alinhamento numérico estritamente à direita nas tabelas.
  - Touch targets acessíveis e anéis de foco com `ring-brand`.
  - Badges de estado sempre combinando ícone + texto semântico + contraste WCAG AA.

---

## 5. Ficheiros Criados no Frontend
```text
frontend/
├── package.json               # Dependências Next.js, TanStack Query/Table, Lucide, Tailwind
├── tsconfig.json              # Configuração TypeScript strict com path alias @/*
├── tailwind.config.ts         # Tokens de cor corporativos e mapping shadcn
├── postcss.config.js          # PostCSS para Tailwind e Autoprefixer
├── next.config.mjs            # NextConfig com build rigoroso
└── src/
    ├── app/
    │   ├── globals.css        # CSS base, variáveis HSL e utilitários
    │   ├── layout.tsx         # RootLayout com metadados e estrutura desktop
    │   ├── page.tsx           # Dashboard com KPIs, Jobs recentes e guia
    │   ├── providers.tsx      # QueryClientProvider e AuthProvider
    │   └── jobs/
    │       ├── new/page.tsx   # Criação de Lote, Dropzone e Seleção de Perfil
    │       └── [id]/page.tsx  # Revisão do Diff, Diagnóstico IA e RBAC Guard
    ├── components/
    │   ├── ui/
    │   │   ├── alert.tsx      # Callout semântico de erros e avisos
    │   │   ├── badge.tsx      # Badges com estados de Price Guard e conformidade
    │   │   ├── button.tsx     # Botões acessíveis com variantes corporativas
    │   │   ├── card.tsx       # Content containers de precisão
    │   │   ├── dialog.tsx     # Modal com foco e acessibilidade
    │   │   ├── input.tsx      # Inputs corporativos com foco #FF3C1D
    │   │   ├── select.tsx     # Seletores estilizados
    │   │   ├── skeleton.tsx   # Loading placeholders estruturais
    │   │   ├── table.tsx      # Tabela corporativa de alta densidade
    │   │   └── tabs.tsx       # Navegação por abas acessíveis
    │   ├── layout/
    │   │   ├── Header.tsx     # Barra de navegação com marca CCM e status
    │   │   └── UserSwitcher.tsx# Alternador dinâmico Comercial vs Operador
    │   └── jobs/
    │       ├── DiffViewer.tsx # Tabela de Diff com filtros (Todos, Update, Novo, Bloqueado)
    │       ├── JobTable.tsx   # Lista de processamentos recentes
    │       ├── UploadZone.tsx # Dropzone para arquivos .xlsx
    │       └── ValidationIssueList.tsx # Lista de anomalias com modal Gemini IA
    ├── context/
    │   └── AuthContext.tsx    # Contexto reativo de sessão e permissões RBAC
    ├── lib/
    │   ├── api.ts             # Cliente HTTP para FastAPI com mock data resiliente
    │   └── utils.ts           # Formatadores Kwanza (Kz), percentagens e datas
    └── types/
        └── index.ts           # Interfaces TypeScript sincronizadas com schemas Pydantic
```

---

## 6. Validação e Qualidade (Evidências de Execução)
- **Compilação Next.js:**
  ```text
  > npm run build
  ✓ Compiled successfully
  ✓ Checking validity of types
  ✓ Generating static pages (5/5)
  Finalizing page optimization ...
  Route (app)                              Size     First Load JS
  ┌ ○ /                                    4 kB            119 kB
  ├ ○ /_not-found                          873 B          88.1 kB
  ├ ƒ /jobs/[id]                           8.84 kB         124 kB
  └ ○ /jobs/new                            7.57 kB         118 kB
  + First Load JS shared by all            87.2 kB
  ```
- **Typecheck TypeScript:**
  ```text
  > npm run typecheck
  tsc --noEmit -> Exit code 0
  ```
- **Backend & Regressão de Domínio:**
  ```text
  > uv run pytest
  ============================= 96 passed in 2.74s ==============================
  ```
