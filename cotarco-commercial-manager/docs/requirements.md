# Documento de Requisitos — Cotarco Commercial Manager

**Versão:** 1.0 — 23/09/2026  
**Status:** Base para MVP / requisitos ainda sujeitos a validação com Comercial

## 1. Visão do produto

O Cotarco Commercial Manager (CCM) é uma aplicação interna destinada a apoiar o ciclo de vida de tabelas comerciais de preços e stock.

O sistema deve abstrair o destino da tabela. Loja online, Marketplace Mano, BFA, Kero, SIAC, revendedores e futuros parceiros são **perfis/destinos configuráveis**, não o núcleo do sistema.

## 2. Objetivos

### O1 — Eliminar dependência do terminal

Permitir que utilizadores da Comercial submetam ficheiros através de uma interface web.

### O2 — Reduzir erros manuais

Validar estrutura, referências, preços, stock e regras de negócio antes de qualquer processamento crítico.

### O3 — Aumentar rastreabilidade

Registar utilizador, ficheiro, perfil, decisões, alertas, aprovação e outputs.

### O4 — Reutilizar o motor `auto-excel`

Transformar o script existente em engine testável e reutilizável.

### O5 — Preparar integrações

Permitir adapters para WooCommerce e outros destinos sem acoplar o domínio.

## 3. Personas

### P1 — Comercial

Prepara tabelas, envia, analisa erros e corrige.

### P2 — Operador

Revê, aprova e executa processamento/integrações externas.

### P3 — Administrador

Configura perfis, templates, regras e utilizadores.

## 4. Requisitos funcionais

### RF-001 — Login

O sistema deve permitir autenticação.

**Aceitação:** utilizador autenticado vê apenas funcionalidades permitidas pelo seu papel.

### RF-002 — Gestão de perfis

O sistema deve permitir selecionar um perfil comercial.

**Perfis iniciais conhecidos:** Loja Online, Marketplace Mano, BFA, Kero, SIAC, Revendedores, Outros.

**Nota:** regras específicas de cada parceiro precisam de levantamento adicional antes de serem consideradas definitivas.

### RF-003 — Novo processamento

Utilizador pode iniciar um job, selecionar perfil, indicar descrição/opcional e submeter ficheiro.

### RF-004 — Upload

MVP aceita `.xlsx` com limite configurável de tamanho.

O sistema deve:

- validar extensão;
- calcular hash SHA-256;
- guardar original sem alteração;
- registar metadata;
- impedir ficheiros corrompidos/ilegíveis.

### RF-005 — Deteção de estrutura

O sistema deve localizar folha e cabeçalho de acordo com o perfil/adapter.

### RF-006 — Normalização

Aplicar limpeza e normalização de referências, preços e campos necessários.

### RF-007 — Validações

Suportar, no mínimo:

- colunas obrigatórias ausentes;
- referência vazia;
- referência duplicada;
- stock inválido;
- stock negativo;
- preço inválido;
- preço zero quando obrigatório;
- referência não encontrada na base de comparação;
- variação de preço acima do limiar;
- ficheiro antigo quando a política do perfil exigir;
- linhas inconsistentes.

### RF-008 — Preview/Diff

Mostrar antes da aplicação:

- atualizações;
- novos;
- ignorados;
- bloqueados;
- diferenças de preço;
- diferenças de stock;
- motivos de cada decisão.

### RF-009 — Estados do job

Estados mínimos:

`UPLOADED`, `VALIDATING`, `READY_FOR_REVIEW`, `NEEDS_CORRECTION`, `APPROVED`, `PROCESSING`, `COMPLETED`, `FAILED`, `CANCELLED`.

### RF-010 — Correção/reenvio

Comercial deve conseguir substituir a tabela antes de aprovação, criando nova versão do ficheiro dentro do mesmo job ou novo job conforme decisão de produto.

### RF-011 — Aprovação

Operador/Admin pode aprovar um job apto para execução.

### RF-012 — Processamento

Executar o engine adequado ao perfil e gerar outputs.

### RF-013 — Exportação

MVP deve gerar Excel final e relatório/log quando o perfil usa `EXCEL_EXPORT`.

### RF-014 — Histórico

Pesquisar e consultar jobs passados e alterações de preço/stock quando aplicável.

### RF-015 — Auditoria

Guardar ações críticas de autenticação, upload, validação, aprovação, execução, download e alteração de configuração.

### RF-016 — Gemini Assist

Permitir pedir ao Gemini:

- resumo;
- explicação de alertas;
- análise de anomalias;
- sugestão de mapeamento.

A resposta deve ser claramente marcada como assistiva.

### RF-017 — Integração WooCommerce (fase posterior)

Criar adapter e endpoints de preparação, mas manter execução atrás de feature flag no MVP.

### RF-018 — Mano (MVP)

Exportação compatível com o processo atual. Não assumir API.

## 5. Requisitos não funcionais

### RNF-001 — Segurança

- TLS em trânsito;
- secrets exclusivamente no backend/secret manager;
- RBAC;
- validação de upload;
- auditoria;
- princípio do menor privilégio;
- RLS como defesa adicional quando aplicável.

### RNF-002 — Performance

A validação de tabelas deve fornecer feedback de progresso/estado para processamentos que ultrapassem alguns segundos.

### RNF-003 — Confiabilidade

Uma falha de processamento não deve deixar um output parcial marcado como concluído.

### RNF-004 — Idempotência

Repetir uma execução com o mesmo job/version não deve produzir duplicações ou mutações externas duplicadas.

### RNF-005 — Observabilidade

Logs estruturados e correlation/job id em todas as operações relevantes.

### RNF-006 — Acessibilidade

Componentes interativos devem possuir teclado, foco visível, labels e contraste aceitável.

### RNF-007 — Manutenibilidade

Domínio testável sem depender da web, da base ou do Excel físico sempre que possível.

## 6. Regras ainda pendentes de levantamento de negócio

Antes do release do MVP, validar com Comercial/Operador:

- todos os destinos/parceiros utilizados pela equipa;
- campos específicos por parceiro;
- fórmulas de preço/margem/desconto;
- regras de validade de preço;
- regras por marca/categoria;
- necessidade de histórico por parceiro;
- templates oficiais de cada parceiro;
- nomenclatura de ficheiros;
- quem pode aprovar cada tipo de tabela;
- política de retenção dos Excel.

## 7. Fora do escopo do MVP

- integração automática com Mano;
- publicação automática universal para todos os parceiros;
- regras desconhecidas inventadas pelo sistema;
- chat aberto de IA sem contexto do job;
- multi-empresa/multi-tenant completo;
- ERP integration genérica.

## 8. MVP Definition of Done

O MVP só está pronto para demonstração quando:

1. Comercial faz login;
2. seleciona um perfil;
3. envia uma tabela;
4. sistema valida;
5. sistema mostra diff realista;
6. bloqueios são explicados;
7. Operador aprova;
8. engine gera Excel/log;
9. histórico regista o processamento;
10. auditoria mostra quem fez cada ação;
11. testes backend/frontend/E2E passam;
12. CI passa;
13. documentação está atualizada;
14. não existem secrets no repositório.
