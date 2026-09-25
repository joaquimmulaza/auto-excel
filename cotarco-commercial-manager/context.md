# CONTEXT.md — Cotarco Commercial Manager

> **Documento obrigatório para qualquer agente de IA antes de alterar o código.**

## 1. O que estamos a construir

Uma plataforma web interna para a Cotarco destinada a **receber, validar, comparar, processar, gerar e auditar tabelas comerciais de preços e stock** para múltiplos canais, parceiros e operações.

O produto nasceu de um problema real: o processo de preparação das tabelas é feito pela Comercial, enquanto o processamento/atualização final dos dados na loja online e no Marketplace Mano é atualmente executado por um operador técnico. O primeiro motor automatizado foi o repositório `auto-excel`.

### Não confundir o produto com:

- um gestor exclusivo do Marketplace Mano;
- um gestor exclusivo da loja Cotarco;
- um simples visualizador de Excel;
- um chatbot de IA.

Excel é um formato de entrada/saída. O domínio é **gestão de tabelas comerciais**.

## 2. Papéis

### COMERCIAL

Responsável por preparar/submeter tabelas e corrigir problemas apontados pelo sistema.

Pode:

- criar processamento;
- selecionar perfil de tabela;
- fazer upload;
- ver validações e preview;
- corrigir/reenviar;
- consultar os próprios processamentos;
- gerar/exportar quando o perfil permitir.

Não pode, no MVP:

- executar publicação no WooCommerce;
- alterar credenciais de integração;
- aprovar/publicar uma operação crítica em nome do Operador.

### OPERADOR

Responsável pela revisão final e execução das operações que alteram sistemas externos.

Pode tudo do Comercial e, adicionalmente:

- aprovar;
- executar processamento final;
- gerar ficheiro final;
- visualizar processamentos globais;
- consultar histórico/auditoria;
- preparar integrações futuras.

### ADMIN

Responsável por configuração do sistema.

Pode:

- gerir utilizadores/papéis;
- gerir perfis de tabela;
- gerir regras/configurações;
- gerir templates;
- gerir integrações;
- consultar auditoria global.

## 3. Domínio

### Source (fonte)

Origem dos dados: Samsung, Comercial, fornecedor, ERP etc.

### Commercial Profile (perfil de tabela)

Define para que finalidade uma tabela está a ser criada e quais regras/formato deve seguir.

Exemplos conhecidos:

- Loja Online;
- Marketplace Mano;
- BFA;
- Kero;
- SIAC;
- Revendedores;
- Outros.

Os exemplos acima **não são uma lista exaustiva**. Novos perfis devem ser configuráveis, sem criar `if/elif` espalhados pelo código.

### Processing Job

Uma execução auditável associada a um perfil, utilizador, ficheiro de entrada, validações, aprovação e outputs.

### Destination / Integration

A forma como o resultado chega ao destino:

- `EXCEL_EXPORT` no MVP para a maioria dos destinos;
- `WOOCOMMERCE_API` posteriormente;
- outros adapters futuros.

## 4. Motor existente

O `auto-excel` atual possui lógica de:

- deteção automática de cabeçalho;
- mapeamento tolerante de colunas;
- limpeza/normalização de referências;
- limpeza de preços;
- regras de stock;
- filtro de produtos novos;
- price guard;
- dry-run;
- histórico;
- backup;
- log de decisão.

A refatoração deve **preservar comportamentos corretos**, mas separar domínio, infraestrutura, API e apresentação.

## 5. Regras de negócio conhecidas

1. Referências precisam ser normalizadas para comparação.
2. Produtos existentes podem ter preço/stock atualizados conforme o perfil.
3. Produtos novos dependem das regras do perfil; o limiar `stock >= 3` é uma regra do processamento atual de Loja/Mano, não uma verdade universal para todos os perfis.
4. `preço = 0` é inválido para os cenários em que preço é obrigatório.
5. Variações de preço acima do limite configurado devem gerar bloqueio/alerta conforme o profile.
6. Regras financeiras críticas são determinísticas e codificadas/configuradas; IA não substitui essas regras.
7. Nenhuma alteração externa deve ocorrer sem aprovação explícita quando a operação for classificada como crítica.
8. O ficheiro original submetido nunca é sobrescrito.
9. Cada processamento deve ser auditável.
10. Toda integração externa deve ser implementada atrás de uma interface/adapter e feature flag.

## 6. IA

Gemini é **assistente**, não fonte de verdade.

Usos aprovados:

- explicar anomalias;
- resumir um processamento;
- sugerir mapeamento de colunas desconhecidas;
- ajudar a interpretar erros;
- responder perguntas sobre o resultado do processamento.

Usos proibidos:

- decidir sozinho preço final;
- aprovar operações financeiras;
- ignorar Price Guard;
- publicar alterações externas sem aprovação determinística.

Quando gerar dados estruturados, preferir schema JSON/Pydantic/Zod.

## 7. Stack alvo

### Frontend

- Next.js;
- TypeScript strict;
- Tailwind CSS;
- shadcn/ui;
- TanStack Query;
- TanStack Table;
- React Hook Form + Zod;
- Vitest + React Testing Library;
- Playwright.

### Backend

- Python;
- FastAPI;
- Pydantic;
- Pandas;
- OpenPyXL;
- SQLAlchemy 2;
- Alembic;
- pytest;
- Ruff;
- mypy (ou pyright quando aprovado).

### Plataforma

- Supabase PostgreSQL;
- Supabase Auth;
- Supabase Storage;
- Vercel para frontend;
- Cloud Run para backend;
- GitHub Actions para CI.

### IA

- Gemini API / Google GenAI SDK no backend.

### Design

Paleta base obrigatória:

- `#FF3C1D` — brand/action;
- `#6B6363` — secondary/muted;
- `#FFFFFF` — surface/light;
- `#000000` — text/dark/high contrast.

Cores semânticas adicionais podem existir apenas para estados (success, warning, error, info) e devem ser definidas no design system; não inventar cores diretamente em componentes.

## 8. UX

A interface deve ser:

- empresarial;
- moderna;
- limpa;
- rápida;
- com foco em tabelas e dados;
- responsiva, mas desktop-first para utilização interna;
- acessível;
- sem excesso de animações.

Padrões esperados:

- skeleton no carregamento inicial;
- spinner apenas em refetch/ações curtas;
- estados vazios claros;
- confirmação explícita antes de operações críticas;
- toasts apenas para feedback de ações, nunca como único local de um erro importante.

## 9. O que ainda NÃO sabemos

Não inventar regras dos parceiros BFA, Kero, SIAC ou outros.

Antes de codificar regras específicas, criar um requisito/configuração ou uma pergunta de negócio e registrar a decisão em `docs/requirements.md` ou ADR.

## 10. Critério geral de sucesso do MVP

Um colega da Comercial deve conseguir preparar/enviar uma tabela sem abrir terminal, receber feedback de qualidade sobre problemas, corrigir a tabela e acompanhar o estado do processamento. O Operador deve conseguir revisar, aprovar, executar o motor existente e obter o output final e o histórico de auditoria.
