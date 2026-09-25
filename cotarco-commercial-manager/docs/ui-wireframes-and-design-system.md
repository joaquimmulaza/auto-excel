# UI/UX Wireframes + Design System Base

## 1. Direção visual

**Personalidade:** enterprise moderno, precisão operacional, confiança e velocidade.

Evitar estética "dashboard genérico de SaaS". A UI deve parecer uma ferramenta interna de operações comerciais, com excelente visualização de Excel/differences.

## 2. Paleta base

| Token | Hex | Uso |
|---|---|---|
| `brand` | `#FF3C1D` | CTA principal, highlights, selected states |
| `secondary` | `#6B6363` | texto secundário, ícones muted, borders suaves |
| `surface` | `#FFFFFF` | cards, áreas de conteúdo |
| `ink` | `#000000` | títulos/texto forte |

Estados semânticos devem ser definidos como tokens adicionais:

```text
success / warning / error / info
```

Sem escolher cores arbitrárias dentro de componentes.

## 3. Tipografia

Base recomendada: `Inter` ou stack system equivalente.

Escala mínima:

```text
Display: 32/40
H1: 24/32
H2: 20/28
H3: 16/24
Body: 14/20
Small: 12/16
Label: 12/16 semibold
```

## 4. Spacing

Base 4px:

`4, 8, 12, 16, 20, 24, 32, 40, 48`.

## 5. Radius

- `sm`: 6px;
- `md`: 10px;
- `lg`: 14px;
- `xl`: 18px.

## 6. Sombras

Discretas. Preferir bordas e contraste em vez de sombras pesadas.

## 7. Componentes base

- Button;
- IconButton;
- Badge;
- Card;
- Input;
- Select;
- Combobox;
- Dropzone;
- DataTable;
- Tabs;
- Dialog;
- Drawer;
- Tooltip;
- Toast;
- Alert;
- Empty State;
- Skeleton;
- Progress;
- Timeline;
- Status Badge.

## 8. Wireframe — Dashboard

```text
┌──────────────────────────────────────────────────────────────────────┐
│ LOGO / CCM                Dashboard   Processamentos   Histórico     │
│                                                  Joaquim ▾           │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ Olá, Joaquim                                                        │
│ Acompanhe as últimas atividades comerciais.                         │
│                                                                      │
│ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐          │
│ │ Process.   │ │ Produtos   │ │ Alertas    │ │ Bloqueados │          │
│ │ 47         │ │ 18 420     │ │ 283        │ │ 41         │          │
│ └────────────┘ └────────────┘ └────────────┘ └────────────┘          │
│                                                                      │
│ Processamentos recentes                              [Ver todos]    │
│ ┌──────────────────────────────────────────────────────────────────┐ │
│ │ #000184  BFA             1 248  READY_FOR_REVIEW     23/09      │ │
│ │ #000183  Loja Online       936  COMPLETED             22/09      │ │
│ │ #000182  Mano            1 421  NEEDS_CORRECTION      20/09      │ │
│ └──────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│                                            [ + Novo processamento ]  │
└──────────────────────────────────────────────────────────────────────┘
```

## 9. Wireframe — Novo processamento

```text
┌──────────────────────────────────────────────────────────────┐
│ Novo processamento                                            │
│ Preparar uma nova tabela comercial                            │
├──────────────────────────────────────────────────────────────┤
│ Perfil da tabela                                              │
│ [ Marketplace Mano ▾ ]                                        │
│                                                              │
│ Fonte                                                        │
│ [ Samsung ▾ ]                                                │
│                                                              │
│ Ficheiro                                                     │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │                 Arraste o Excel aqui                     │ │
│ │                    ou [Escolher ficheiro]                │ │
│ │                 .xlsx · até 25 MB                         │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│ Descrição (opcional)                                        │
│ [ Tabela de preços setembro...                           ]   │
│                                                              │
│ [Cancelar]                           [ Validar ficheiro ]    │
└──────────────────────────────────────────────────────────────┘
```

## 10. Wireframe — Review/Diff

```text
┌──────────────────────────────────────────────────────────────────────┐
│ #000184 · Marketplace Mano                     READY FOR REVIEW      │
│ Samsung · 23/09/2026                                               │
├──────────────────────────────────────────────────────────────────────┤
│ 1 248 analisados   843 updates   102 novos   271 ignorados   20 ⛔  │
├──────────────────────────────────────────────────────────────────────┤
│ [Todos] [Atualizações] [Novos] [Ignorados] [Bloqueados]             │
│ Buscar referência: [________________________]                        │
│                                                                      │
│ Referência       Preço atual    Preço novo   Var.    Stock   Estado  │
│ RS64R53112A      2 393 787      2 614 035    +9,2%   0→3     ✓      │
│ RF71A967532UT    3 980 000      3 491 228   -12,3%   8→9     ✓      │
│ XXX              2 000 000      5 500 000  +175,0%   5→5     ⛔     │
│                                                                      │
│ ┌──────────────────────────────────────────────────────────────────┐ │
│ │ Bloqueio: PRICE_VARIATION_BLOCKED                                │ │
│ │ A variação ultrapassa o limite do perfil. Verifique o Excel.     │ │
│ │ [Explicar com IA]                                                 │ │
│ └──────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ [Voltar]                     [Rejeitar]        [ Aprovar ]           │
└──────────────────────────────────────────────────────────────────────┘
```

## 11. Wireframe — Detalhe de processamento

Abas:

`Resumo | Itens | Problemas | Ficheiros | Auditoria | IA`

## 12. Estados obrigatórios

Cada tela relevante deve definir:

- loading;
- empty;
- error;
- success;
- permission denied;
- processing.

## 13. Design de tabelas

- header sticky;
- zebra opcional muito sutil;
- densidade configurável;
- alinhamento numérico à direita;
- referências em fonte monoespaçada ou visualmente distinguível;
- filtros persistentes por sessão;
- paginação/virtualização quando necessário;
- suporte a seleção e ações em lote apenas quando o caso de uso exigir.

## 14. Acessibilidade

- foco visível;
- labels reais;
- atalhos de teclado para tabelas quando necessário;
- `aria-*` apenas quando semântica nativa não resolver;
- contraste funcional;
- mensagens de erro ligadas ao input;
- não depender apenas de cor para indicar estado.

## 15. Stitch Workflow

Para cada tela:

1. agente lê este documento;
2. envia prompt detalhado para Stitch via MCP;
3. Stitch gera proposta;
4. agente executa QA contra os critérios;
5. rejeitar com feedback objetivo quando necessário;
6. após aprovação, implementar a tela com os componentes reais do projeto;
7. executar testes visuais/E2E.

## 16. Critérios de aprovação visual

Uma tela só é aprovada quando:

- parece pertencer ao mesmo produto;
- utiliza corretamente os tokens;
- apresenta hierarquia clara;
- reduz carga cognitiva;
- suporta informação densa;
- estados de erro/blocker são explícitos;
- ações de alto risco são deliberadamente destacadas;
- não cria funcionalidades fora dos requisitos.
