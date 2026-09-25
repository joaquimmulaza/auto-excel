-- =============================================================================
-- Migration 003 — Seed: Commercial Profiles
-- Cotarco Commercial Manager
-- =============================================================================
-- Inserts the initial set of commercial profiles used in the MVP.
-- Uses ON CONFLICT DO UPDATE (upsert) so it is safe to re-run.
--
-- Profiles seeded:
--   1. MANO       — Marketplace Mano (Excel export; stock >= 3; price variation 30%)
--   2. WOOCOMMERCE — Loja Online Cotarco (WooCommerce API future; stock > 0; variation 30%)
--   3. BFA        — Parceiro corporativo BFA (Excel export; price variation 10%)
--   4. KERO       — Revendedor Kero (Excel export; reseller margin rules)
--   5. SIAC       — Revendedor SIAC (Excel export; reseller price rules)
--
-- NOTE: Rule parameters for BFA, Kero, and SIAC are placeholder values.
--       Exact commercial terms must be confirmed with the business before
--       being changed in production. Registered as a requirement in
--       docs/requirements.md before any update.
-- =============================================================================

INSERT INTO commercial_profiles
  (code, name, type, description, active, config, rules_version)
VALUES
  -- -------------------------------------------------------------------------
  -- 1. Marketplace Mano
  -- -------------------------------------------------------------------------
  (
    'MANO',
    'Marketplace Mano',
    'MARKETPLACE',
    'Tabela para publicação no Marketplace Mano Angola. '
    'Exportação Excel. Stock mínimo 3 unidades para ativação. '
    'Variação máxima de preço 30%.',
    TRUE,
    '{
      "integration_type": "EXCEL_EXPORT",
      "stock_min_activation": 3,
      "price_variation_threshold": 0.30,
      "allow_zero_price": false,
      "allow_negative_stock": false,
      "price_guard_enabled": true,
      "woocommerce_enabled": false
    }'::jsonb,
    1
  ),

  -- -------------------------------------------------------------------------
  -- 2. Loja Online (WooCommerce)
  -- -------------------------------------------------------------------------
  (
    'WOOCOMMERCE',
    'Loja Online Cotarco',
    'STORE',
    'Tabela para atualização da loja online Cotarco. '
    'WooCommerce API (integração futura ativada por feature flag). '
    'Stock positivo obrigatório para ativação. Variação máxima 30%.',
    TRUE,
    '{
      "integration_type": "EXCEL_EXPORT",
      "stock_min_activation": 1,
      "price_variation_threshold": 0.30,
      "allow_zero_price": false,
      "allow_negative_stock": false,
      "price_guard_enabled": true,
      "woocommerce_enabled": false,
      "woocommerce_api_version": "v3",
      "feature_flags": {
        "woocommerce_live_push": false
      }
    }'::jsonb,
    1
  ),

  -- -------------------------------------------------------------------------
  -- 3. BFA (Parceiro Corporativo)
  -- -------------------------------------------------------------------------
  (
    'BFA',
    'BFA Parceiro Corporativo',
    'PARTNER',
    'Tabela para o parceiro corporativo BFA. '
    'Exportação Excel. Variação máxima de preço 10% (política conservadora). '
    'AVISO: Regras comerciais exactas a confirmar com a gestão antes de produção.',
    TRUE,
    '{
      "integration_type": "EXCEL_EXPORT",
      "stock_min_activation": 0,
      "price_variation_threshold": 0.10,
      "allow_zero_price": false,
      "allow_negative_stock": false,
      "price_guard_enabled": true,
      "woocommerce_enabled": false,
      "business_rules_confirmed": false,
      "notes": "Parametros placeholder — confirmar com gestao antes de producao."
    }'::jsonb,
    1
  ),

  -- -------------------------------------------------------------------------
  -- 4. Kero (Revendedor)
  -- -------------------------------------------------------------------------
  (
    'KERO',
    'Kero Revendedor',
    'RESELLER',
    'Tabela para o revendedor Kero. '
    'Exportação Excel. Regras de margem/preço a confirmar com gestão.',
    TRUE,
    '{
      "integration_type": "EXCEL_EXPORT",
      "stock_min_activation": 0,
      "price_variation_threshold": 0.30,
      "allow_zero_price": false,
      "allow_negative_stock": false,
      "price_guard_enabled": true,
      "woocommerce_enabled": false,
      "business_rules_confirmed": false,
      "notes": "Parametros placeholder — confirmar margem e politica de preco com gestao."
    }'::jsonb,
    1
  ),

  -- -------------------------------------------------------------------------
  -- 5. SIAC (Revendedor)
  -- -------------------------------------------------------------------------
  (
    'SIAC',
    'SIAC Revendedor',
    'RESELLER',
    'Tabela para o revendedor SIAC. '
    'Exportação Excel. Regras de margem/preço a confirmar com gestão.',
    TRUE,
    '{
      "integration_type": "EXCEL_EXPORT",
      "stock_min_activation": 0,
      "price_variation_threshold": 0.30,
      "allow_zero_price": false,
      "allow_negative_stock": false,
      "price_guard_enabled": true,
      "woocommerce_enabled": false,
      "business_rules_confirmed": false,
      "notes": "Parametros placeholder — confirmar margem e politica de preco com gestao."
    }'::jsonb,
    1
  )

ON CONFLICT (code) DO UPDATE SET
  name          = EXCLUDED.name,
  type          = EXCLUDED.type,
  description   = EXCLUDED.description,
  config        = EXCLUDED.config,
  rules_version = EXCLUDED.rules_version,
  updated_at    = NOW();


-- ---------------------------------------------------------------------------
-- Seed profile_rules for MANO (version 1)
-- ---------------------------------------------------------------------------

INSERT INTO profile_rules (profile_id, version, rule_code, rule_config, active)
SELECT
  cp.id,
  1,
  rules.rule_code,
  rules.rule_config,
  TRUE
FROM commercial_profiles cp
CROSS JOIN (VALUES
  (
    'PRICE_VARIATION_THRESHOLD',
    '{"max_variation_pct": 30, "action": "BLOCK"}'::jsonb
  ),
  (
    'MIN_STOCK_ACTIVATION',
    '{"min_stock": 3, "action": "IGNORE_NEW_PRODUCT"}'::jsonb
  ),
  (
    'ZERO_PRICE',
    '{"allow": false, "action": "BLOCK"}'::jsonb
  ),
  (
    'NEGATIVE_STOCK',
    '{"allow": false, "action": "IGNORE"}'::jsonb
  )
) AS rules(rule_code, rule_config)
WHERE cp.code = 'MANO'
ON CONFLICT ON CONSTRAINT uq_profile_rules_profile_version_code DO UPDATE SET
  rule_config = EXCLUDED.rule_config,
  active      = EXCLUDED.active;


-- ---------------------------------------------------------------------------
-- Seed profile_rules for WOOCOMMERCE (version 1)
-- ---------------------------------------------------------------------------

INSERT INTO profile_rules (profile_id, version, rule_code, rule_config, active)
SELECT
  cp.id,
  1,
  rules.rule_code,
  rules.rule_config,
  TRUE
FROM commercial_profiles cp
CROSS JOIN (VALUES
  (
    'PRICE_VARIATION_THRESHOLD',
    '{"max_variation_pct": 30, "action": "BLOCK"}'::jsonb
  ),
  (
    'MIN_STOCK_ACTIVATION',
    '{"min_stock": 1, "action": "IGNORE_NEW_PRODUCT"}'::jsonb
  ),
  (
    'ZERO_PRICE',
    '{"allow": false, "action": "BLOCK"}'::jsonb
  ),
  (
    'WOOCOMMERCE_INTEGRATION',
    '{"enabled": false, "api_version": "v3", "reason": "feature_flag_disabled"}'::jsonb
  )
) AS rules(rule_code, rule_config)
WHERE cp.code = 'WOOCOMMERCE'
ON CONFLICT ON CONSTRAINT uq_profile_rules_profile_version_code DO UPDATE SET
  rule_config = EXCLUDED.rule_config,
  active      = EXCLUDED.active;


-- ---------------------------------------------------------------------------
-- Seed profile_rules for BFA (version 1)
-- ---------------------------------------------------------------------------

INSERT INTO profile_rules (profile_id, version, rule_code, rule_config, active)
SELECT
  cp.id,
  1,
  rules.rule_code,
  rules.rule_config,
  TRUE
FROM commercial_profiles cp
CROSS JOIN (VALUES
  (
    'PRICE_VARIATION_THRESHOLD',
    '{"max_variation_pct": 10, "action": "BLOCK", "note": "conservative_partner_policy"}'::jsonb
  ),
  (
    'ZERO_PRICE',
    '{"allow": false, "action": "BLOCK"}'::jsonb
  )
) AS rules(rule_code, rule_config)
WHERE cp.code = 'BFA'
ON CONFLICT ON CONSTRAINT uq_profile_rules_profile_version_code DO UPDATE SET
  rule_config = EXCLUDED.rule_config,
  active      = EXCLUDED.active;


-- ---------------------------------------------------------------------------
-- Verification: display seeded profiles
-- ---------------------------------------------------------------------------

SELECT code, name, type, active, rules_version,
       config->>'integration_type' AS integration,
       config->>'price_variation_threshold' AS price_var_threshold
FROM commercial_profiles
ORDER BY type, code;

-- =============================================================================
-- END OF MIGRATION 003
-- =============================================================================
