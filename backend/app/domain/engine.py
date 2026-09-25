"""Domain processing engine for Cotarco Commercial Manager.

Fully deterministic, pure Python execution.
No CLI calls (no argparse, sys.exit, prints).
No external database or network dependencies.
"""

from __future__ import annotations

import copy
from typing import Any, Optional

from backend.app.domain.models import (
    CommercialProfile,
    DecisionCode,
    IssueSeverity,
    JobItemResult,
    PriceRule,
    ProcessResult,
    ProcessSummary,
    StockRule,
    ValidationIssue,
)
from backend.app.domain.normalization import (
    calcular_variacao,
    limpar_preco,
    normalize_col,
    ultra_clean,
)

# Standard alias candidates for source columns
DEFAULT_SOURCE_REF_ALIASES = [
    "REFERENCIA", "REFERÊNCIA", "REF", "REFERENCE", "CODIGO", "CÓDIGO",
    "COD", "SKU", "MODELO", "INTERNAL_IDENTIFIER", "IDENTIFIER",
]
DEFAULT_SOURCE_PRICE_ALIASES = [
    "PRECO COM IVA", "PREÇO COM IVA", "PRECO", "PREÇO", "PRICE", "PVP",
    "VALOR", "PRECO_FINAL", "ORIGINAL_PRICE", "PRECO_1", "PRICE1",
]
DEFAULT_SOURCE_STOCK_ALIASES = [
    "STOCK", "ESTOQUE", "QTY", "QUANTIDADE", "QUANTITY", "QNT",
]
DEFAULT_SOURCE_NAME_ALIASES = [
    "DESIGNACAO", "DESIGNAÇÃO", "DESCRICAO", "DESCRIÇÃO", "DESCRIPTION",
    "NOME", "NAME", "PRODUTO", "TITLE", "TITLE_PT",
]

# Standard alias candidates for target catalog columns
DEFAULT_TARGET_REF_ALIASES = [
    "internal_identifier", "identifier", "referencia", "referência",
    "ref", "sku", "codigo", "código",
]
DEFAULT_TARGET_PRICE_ALIASES = [
    "original_price", "price", "preco", "preço", "pvp",
]
DEFAULT_TARGET_STOCK_ALIASES = [
    "quantity", "stock", "estoque", "quantidade", "qty",
]


def _find_field_value(record: dict[str, Any], candidate_aliases: list[str], default: Any = None) -> Any:
    """Finds a field value in a dict using a list of case/accent-insensitive candidate aliases."""
    if not record:
        return default

    # 1. Exact match
    for alias in candidate_aliases:
        if alias in record:
            return record[alias]

    # 2. Case-insensitive / normalized match
    norm_record_keys = {normalize_col(k): k for k in record.keys()}
    for alias in candidate_aliases:
        norm_alias = normalize_col(alias)
        if norm_alias in norm_record_keys:
            orig_key = norm_record_keys[norm_alias]
            return record[orig_key]

    return default


def _find_target_key(record: dict[str, Any], candidate_aliases: list[str], default: str) -> str:
    """Finds the actual key name present in target record matching candidate aliases."""
    if not record:
        return default

    for alias in candidate_aliases:
        if alias in record:
            return alias

    norm_record_keys = {normalize_col(k): k for k in record.keys()}
    for alias in candidate_aliases:
        norm_alias = normalize_col(alias)
        if norm_alias in norm_record_keys:
            return norm_record_keys[norm_alias]

    return default


def process_price_table(
    source_records: list[dict[str, Any]],
    target_catalog: list[dict[str, Any]],
    profile: CommercialProfile,
) -> ProcessResult:
    """Processes source supplier/marketplace table against a target catalog deterministically.

    Key business fixes:
    1. Zero Price: Non-permissive zero price is never silently applied to update catalog.
       Produces BLOCKED_ZERO_PRICE blocker for existing items and IGNORED_ZERO_PRICE for new items.
    2. Duplicate Detection: Detects repeated references in source and emits DUPLICATE_REFERENCE
       blockers without silent overwrite.
    3. Configurable Price Guard: Evaluates price variation dynamically against
       profile.price_rule.max_variation_threshold. Blocks when exceeded without crashing.
    4. Reference Sanitization: Normalizes references using ultra_clean (A-Z, 0-9, hyphens).
    5. Pure execution: Zero file or CLI side-effects.

    Args:
        source_records: List of dictionaries from incoming source dataset.
        target_catalog: List of dictionaries from current target catalog.
        profile: CommercialProfile with pricing, stock, and mapping rules.

    Returns:
        Structured ProcessResult containing evaluated items, validation issues,
        quantitative summary, and updated output records.
    """
    # Defensive deep copy to guarantee immutability of inputs
    output_records = copy.deepcopy(target_catalog)
    issues: list[ValidationIssue] = []
    items: list[JobItemResult] = []
    summary = ProcessSummary(
        total_source_rows=len(source_records),
        total_target_rows=len(target_catalog),
    )

    # 1. Setup column alias mappings
    custom_map = profile.column_mapping or {}
    src_ref_aliases = custom_map.get("reference") or custom_map.get("REFERENCIA") or DEFAULT_SOURCE_REF_ALIASES
    src_price_aliases = custom_map.get("price") or custom_map.get("PRECO") or DEFAULT_SOURCE_PRICE_ALIASES
    src_stock_aliases = custom_map.get("stock") or custom_map.get("STOCK") or DEFAULT_SOURCE_STOCK_ALIASES
    src_name_aliases = custom_map.get("name") or custom_map.get("DESIGNACAO") or DEFAULT_SOURCE_NAME_ALIASES

    # Detect target field names
    sample_target = output_records[0] if output_records else {}
    target_id_key = _find_target_key(sample_target, DEFAULT_TARGET_REF_ALIASES, "internal_identifier")
    target_price_key = _find_target_key(sample_target, DEFAULT_TARGET_PRICE_ALIASES, "original_price")
    target_stock_key = _find_target_key(sample_target, DEFAULT_TARGET_STOCK_ALIASES, "quantity")

    # Index target catalog by normalized reference
    # Map: normalized_ref -> index in output_records
    target_index: dict[str, int] = {}
    for idx, target_item in enumerate(output_records):
        raw_t_ref = target_item.get(target_id_key, "")
        norm_t_ref = ultra_clean(raw_t_ref)
        if norm_t_ref:
            target_index[norm_t_ref] = idx

    # 2. Pre-scan source records for duplicate references (Bug 2 fix)
    ref_occurrences: dict[str, list[int]] = {}
    for row_idx, src_row in enumerate(source_records, start=1):
        raw_ref = str(_find_field_value(src_row, src_ref_aliases, default="") or "")
        norm_ref = ultra_clean(raw_ref)
        if norm_ref:
            ref_occurrences.setdefault(norm_ref, []).append(row_idx)

    duplicate_refs = {ref: rows for ref, rows in ref_occurrences.items() if len(rows) > 1}

    # Emit DUPLICATE_REFERENCE blocker issues
    for dup_ref, rows in duplicate_refs.items():
        issues.append(
            ValidationIssue(
                severity=IssueSeverity.BLOCKER,
                code="DUPLICATE_REFERENCE",
                message=f"Referência duplicada '{dup_ref}' detectada na tabela de entrada nas linhas {rows}.",
                field="reference",
                row_number=rows[0],
                details={"reference": dup_ref, "rows": rows, "count": len(rows)},
            )
        )
        summary.blocked_duplicates += 1

    # 3. Process each source record
    price_rule = profile.price_rule
    stock_rule = profile.stock_rule

    for row_idx, src_row in enumerate(source_records, start=1):
        raw_ref = str(_find_field_value(src_row, src_ref_aliases, default="") or "")
        norm_ref = ultra_clean(raw_ref)
        raw_price = _find_field_value(src_row, src_price_aliases, default=0.0)
        raw_stock = _find_field_value(src_row, src_stock_aliases, default=0)
        designation = str(_find_field_value(src_row, src_name_aliases, default="") or "")

        new_price = limpar_preco(raw_price)
        try:
            new_stock = int(limpar_preco(raw_stock))
        except (ValueError, TypeError):
            new_stock = 0

        # Handle empty/invalid reference
        if not norm_ref:
            issue = ValidationIssue(
                severity=IssueSeverity.WARNING,
                code="IGNORED_EMPTY_REF",
                message=f"Linha {row_idx}: Referência vazia ou inválida ('{raw_ref}').",
                field="reference",
                row_number=row_idx,
                details={"raw_reference": raw_ref},
            )
            issues.append(issue)
            items.append(
                JobItemResult(
                    reference_original=raw_ref,
                    reference_normalized="",
                    new_price=new_price,
                    new_stock=new_stock,
                    decision="IGNORADO: Referência vazia ou inválida",
                    decision_code=DecisionCode.IGNORED_EMPTY_REF,
                )
            )
            continue

        # Handle duplicate reference
        if norm_ref in duplicate_refs:
            rows = duplicate_refs[norm_ref]
            items.append(
                JobItemResult(
                    reference_original=raw_ref,
                    reference_normalized=norm_ref,
                    new_price=new_price,
                    new_stock=new_stock,
                    decision=f"BLOQUEADO: Referência duplicada na entrada (linhas {rows})",
                    decision_code=DecisionCode.BLOCKED_DUPLICATE_REF,
                    details={"rows": rows},
                )
            )
            continue

        # ─── CASE A: PRODUCT EXISTS IN TARGET CATALOG ───
        if norm_ref in target_index:
            target_idx = target_index[norm_ref]
            target_item = output_records[target_idx]

            raw_old_price = target_item.get(target_price_key)
            old_price = limpar_preco(raw_old_price) if raw_old_price is not None else None
            old_stock = int(target_item.get(target_stock_key) or 0)

            # Security Check 1: Negative Price
            if price_rule.reject_negative and new_price < 0.0:
                issue = ValidationIssue(
                    severity=IssueSeverity.BLOCKER,
                    code="BLOCKED_NEGATIVE_PRICE",
                    message=f"Referência '{norm_ref}': Preço negativo ({new_price:.2f}) rejeitado.",
                    field="price",
                    row_number=row_idx,
                    details={"reference": norm_ref, "new_price": new_price, "old_price": old_price},
                )
                issues.append(issue)
                items.append(
                    JobItemResult(
                        reference_original=raw_ref,
                        reference_normalized=norm_ref,
                        old_price=old_price,
                        new_price=new_price,
                        old_stock=old_stock,
                        new_stock=new_stock,
                        decision="BLOQUEADO: Preço negativo rejeitado",
                        decision_code=DecisionCode.BLOCKED_ZERO_PRICE,
                    )
                )
                continue

            # Security Check 2: Zero Price (Bug 1 fix)
            if not price_rule.allow_zero_price and new_price == 0.0:
                issue = ValidationIssue(
                    severity=IssueSeverity.BLOCKER,
                    code="BLOCKED_ZERO_PRICE",
                    message=f"Referência '{norm_ref}': Preço zero (0.00 EUR) bloqueado pelas regras do perfil.",
                    field="price",
                    row_number=row_idx,
                    details={"reference": norm_ref, "new_price": new_price, "old_price": old_price},
                )
                issues.append(issue)
                summary.blocked_zero_price += 1
                items.append(
                    JobItemResult(
                        reference_original=raw_ref,
                        reference_normalized=norm_ref,
                        old_price=old_price,
                        new_price=new_price,
                        old_stock=old_stock,
                        new_stock=new_stock,
                        decision="BLOQUEADO: Preço zero não permitido",
                        decision_code=DecisionCode.BLOCKED_ZERO_PRICE,
                    )
                )
                continue

            # Security Check 3: Dynamic Configurable Price Guard (Bug 3 fix)
            var_ratio = calcular_variacao(old_price, new_price)
            var_pct = round(var_ratio * 100.0, 2) if var_ratio is not None else None
            threshold_pct = price_rule.max_variation_threshold * 100.0

            if var_pct is not None and abs(var_pct) > threshold_pct:
                issue = ValidationIssue(
                    severity=IssueSeverity.BLOCKER,
                    code="BLOCKED_PRICE_VARIATION",
                    message=(
                        f"Referência '{norm_ref}': Variação de {var_pct:+.1f}% "
                        f"({old_price:.2f} -> {new_price:.2f}) excede o limiar de {threshold_pct:.0f}%."
                    ),
                    field="price",
                    row_number=row_idx,
                    details={
                        "reference": norm_ref,
                        "old_price": old_price,
                        "new_price": new_price,
                        "variation_pct": var_pct,
                        "threshold_pct": threshold_pct,
                    },
                )
                issues.append(issue)
                summary.blocked_price_variation += 1
                items.append(
                    JobItemResult(
                        reference_original=raw_ref,
                        reference_normalized=norm_ref,
                        old_price=old_price,
                        new_price=new_price,
                        old_stock=old_stock,
                        new_stock=new_stock,
                        price_variation_pct=var_pct,
                        decision=f"BLOQUEADO: Variação de preço excessiva ({var_pct:+.1f}% > {threshold_pct:.0f}%)",
                        decision_code=DecisionCode.BLOCKED_PRICE_VARIATION,
                    )
                )
                continue

            # Approved Update
            target_item[target_price_key] = new_price
            target_item[target_stock_key] = new_stock

            if new_stock >= stock_rule.min_stock_activation:
                target_item["is_active"] = True
                target_item["sold_out"] = False
            else:
                target_item["is_active"] = False
                target_item["sold_out"] = True

            summary.updated += 1
            items.append(
                JobItemResult(
                    reference_original=raw_ref,
                    reference_normalized=norm_ref,
                    old_price=old_price,
                    new_price=new_price,
                    old_stock=old_stock,
                    new_stock=new_stock,
                    price_variation_pct=var_pct,
                    decision="ATUALIZADO: Preço e stock atualizados",
                    decision_code=DecisionCode.UPDATE,
                )
            )

        # ─── CASE B: NEW PRODUCT CANDIDATE ───
        else:
            # 1. Zero Price check for new product
            if not price_rule.allow_zero_price and new_price == 0.0:
                issue = ValidationIssue(
                    severity=IssueSeverity.INFO,
                    code="IGNORED_ZERO_PRICE",
                    message=f"Referência '{raw_ref}': Produto novo ignorado devido a preço zero.",
                    field="price",
                    row_number=row_idx,
                    details={"reference": raw_ref, "price": new_price},
                )
                issues.append(issue)
                summary.ignored_zero_price += 1
                items.append(
                    JobItemResult(
                        reference_original=raw_ref,
                        reference_normalized=norm_ref,
                        new_price=new_price,
                        new_stock=new_stock,
                        decision="IGNORADO: Preço igual a zero",
                        decision_code=DecisionCode.IGNORED_ZERO_PRICE,
                    )
                )
                continue

            # 2. Stock threshold check for new product
            if new_stock < stock_rule.min_stock_activation:
                issue = ValidationIssue(
                    severity=IssueSeverity.INFO,
                    code="IGNORED_STOCK",
                    message=(
                        f"Referência '{raw_ref}': Stock insuficiente ({new_stock} < {stock_rule.min_stock_activation})."
                    ),
                    field="stock",
                    row_number=row_idx,
                    details={"reference": raw_ref, "stock": new_stock, "min_stock": stock_rule.min_stock_activation},
                )
                issues.append(issue)
                summary.ignored_stock += 1
                items.append(
                    JobItemResult(
                        reference_original=raw_ref,
                        reference_normalized=norm_ref,
                        new_price=new_price,
                        new_stock=new_stock,
                        decision=f"IGNORADO: Stock insuficiente ({new_stock} < {stock_rule.min_stock_activation})",
                        decision_code=DecisionCode.IGNORED_STOCK,
                    )
                )
                continue

            # 3. Eligible new product - Add to output catalog
            new_record: dict[str, Any] = {}
            if sample_target:
                for k in sample_target.keys():
                    new_record[k] = None
            else:
                new_record = {
                    target_id_key: None,
                    target_price_key: None,
                    target_stock_key: None,
                    "is_active": True,
                    "sold_out": False,
                    "apply_discounted_price": False,
                }

            new_record[target_id_key] = raw_ref
            new_record[target_price_key] = new_price
            new_record[target_stock_key] = new_stock
            new_record["is_active"] = True
            new_record["sold_out"] = False
            new_record["apply_discounted_price"] = False
            if designation and ("title_pt" in new_record or "title" in new_record or "designacao" in new_record):
                for desc_key in ("title_pt", "title", "designacao"):
                    if desc_key in new_record:
                        new_record[desc_key] = designation
                        break

            output_records.append(new_record)
            target_index[norm_ref] = len(output_records) - 1
            summary.new_added += 1

            items.append(
                JobItemResult(
                    reference_original=raw_ref,
                    reference_normalized=norm_ref,
                    new_price=new_price,
                    new_stock=new_stock,
                    decision="ADICIONADO: Produto novo com stock suficiente e preço válido",
                    decision_code=DecisionCode.NEW_PRODUCT,
                )
            )

    summary.total_issues = len(issues)

    return ProcessResult(
        items=items,
        issues=issues,
        summary=summary,
        output_records=output_records,
    )


class TableProcessor:
    """Class wrapper providing a stateless engine processor instance."""

    def __init__(self, profile: CommercialProfile):
        self.profile = profile

    def process(
        self,
        source_records: list[dict[str, Any]],
        target_catalog: list[dict[str, Any]],
    ) -> ProcessResult:
        """Executes table processing using the configured CommercialProfile."""
        return process_price_table(source_records, target_catalog, self.profile)
