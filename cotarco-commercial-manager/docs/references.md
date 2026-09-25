# Referências técnicas consultadas — 23/09/2026

Estas referências suportam as decisões de stack documentadas e devem ser revistas quando o projeto entrar em produção.

## Supabase

Pricing/Free: https://supabase.com/pricing

Para quotas, limites e condições atualizadas da plataforma, consultar a documentação canónica em `cotarco-commercial-manager/docs/stack-and-guardrails.md §8` e o link oficial de pricing acima, evitando duplicação sujeita a drift.

## WooCommerce

REST API v3: https://developer.woocommerce.com/docs/apis/rest-api/v3/

Products: https://developer.woocommerce.com/docs/apis/rest-api/v3/products

A documentação atual indica v3 como versão recomendada para novas integrações e suporta operações de produto, incluindo batch.

## Gemini

Structured Outputs: https://ai.google.dev/gemini-api/docs/structured-output

Usar JSON Schema/Pydantic/Zod para respostas estruturadas.

## Google Stitch

Google Cloud MCP supported products: https://docs.cloud.google.com/mcp/supported-products

O catálogo atual lista Stitch (Beta) em `https://stitch.googleapis.com/mcp`.

Stitch overview: https://developers.googleblog.com/stitch-a-new-way-to-design-uis/

## Nota

Ferramentas e quotas são mutáveis. Agentes devem consultar documentação oficial atual antes de alterar versões, limites, autenticação ou deployment.
