"""Pure domain business rules and validation logic for Cotarco Commercial Manager.

These functions are strictly 100% isolated from any I/O, database, API, or CLI dependencies.
They receive inputs and return structured results and domain issues.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Optional

from backend.app.domain.models import (
    DecisionCode,
    IssueSeverity,
    PriceRule,
    StockRule,
    ValidationIssue,
)


def normalize_reference(text: Any) -> str:
    """Normalizes catalog reference string deterministically.

    Removes accents, spaces, and non-alphanumeric characters except hyphens,
    and converts to uppercase.
    """
    if text is None:
        return ""
    s = str(text).strip().upper()
    if not s or s.lower() == "nan":
        return ""
    # Strip accents
    normalized = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("ASCII")
    # Keep only letters, digits, and hyphens
    cleaned = re.sub(r"[^A-Z0-9-]", "", normalized)
    return cleaned.strip()


def clean_price_value(value: Any) -> float:
    """Cleans and parses price value into a rounded 2-decimal float.

    Handles varied number formatting (Portuguese/European comma separators,
    thousand separators, currency symbols).
    """
    if value is None:
        return 0.0
    s = str(value).strip().upper()
    if not s or s == "NAN" or s == "NONE":
        return 0.0

    # Remove all non-digits, non-dots, non-commas, non-minus
    s = re.sub(r"[^\d.,-]", "", s)
    if not s or s == "-":
        return 0.0

    # Normalize decimal separator
    s = s.replace(",", ".")
    # If multiple dots (e.g. 1.234.56), remove all except the last
    parts = s.split(".")
    if len(parts) > 2:
        s = "".join(parts[:-1]) + "." + parts[-1]

    try:
        parsed = float(s)
        return round(parsed, 2)
    except (ValueError, TypeError):
        return 0.0


def calculate_price_variation(
    old_price: Optional[float],
    new_price: float,
) -> tuple[Optional[float], Optional[float]]:
    """Calculates price difference and percentage variation.

    Returns:
        (delta_abs, variation_pct) where variation_pct is in % (e.g. 25.0 for 25%).
        If old_price is None or <= 0, variation_pct is None.
    """
    if old_price is None or old_price <= 0.0:
        return None, None

    delta = new_price - old_price
    variation_pct = round((delta / old_price) * 100.0, 2)
    return round(delta, 2), variation_pct


def evaluate_price_guard(
    ref: str,
    old_price: Optional[float],
    new_price: float,
    rule: PriceRule,
    row_number: Optional[int] = None,
) -> tuple[bool, Optional[float], Optional[ValidationIssue]]:
    """Evaluates price guard rules against price changes.

    Returns:
        tuple (is_blocked, variation_pct, issue)
        - is_blocked: True if the price change must be blocked.
        - variation_pct: calculated variation percentage or None.
        - issue: ValidationIssue if a violation or block occurred, else None.
    """
    # 1. Negative price check
    if rule.reject_negative and new_price < 0.0:
        issue = ValidationIssue(
            severity=IssueSeverity.BLOCKER,
            code="BLOCKED_NEGATIVE_PRICE",
            message=f"Referência '{ref}': Preço negativo ({new_price:.2f} EUR) rejeitado por regra de segurança.",
            field="price",
            row_number=row_number,
            details={"reference": ref, "new_price": new_price, "old_price": old_price},
        )
        return True, None, issue

    # 2. Zero price check
    if not rule.allow_zero_price and new_price == 0.0:
        issue = ValidationIssue(
            severity=IssueSeverity.BLOCKER,
            code="BLOCKED_ZERO_PRICE",
            message=f"Referência '{ref}': Preço zero (0.00 EUR) não permitido pelas regras do perfil.",
            field="price",
            row_number=row_number,
            details={"reference": ref, "new_price": new_price, "old_price": old_price},
        )
        return True, None, issue

    # 3. Price variation threshold check
    _, variation_pct = calculate_price_variation(old_price, new_price)

    if (
        variation_pct is not None
        and rule.max_variation_threshold is not None
        and rule.max_variation_threshold > 0.0
    ):
        threshold_pct = rule.max_variation_threshold * 100.0
        if abs(variation_pct) > threshold_pct:
            issue = ValidationIssue(
                severity=IssueSeverity.BLOCKER,
                code="BLOCKED_PRICE_VARIATION",
                message=(
                    f"Referência '{ref}': Variação de preço de {variation_pct:+.1f}% "
                    f"({old_price:.2f} EUR -> {new_price:.2f} EUR) excede o limiar de segurança de {threshold_pct:.0f}%."
                ),
                field="price",
                row_number=row_number,
                details={
                    "reference": ref,
                    "old_price": old_price,
                    "new_price": new_price,
                    "variation_pct": variation_pct,
                    "threshold_pct": threshold_pct,
                },
            )
            return True, variation_pct, issue

    return False, variation_pct, None


def evaluate_stock_activation(stock: int, rule: StockRule) -> tuple[bool, bool]:
    """Evaluates product activation and sold_out status based on stock quantity.

    Returns:
        tuple (is_active, sold_out)
    """
    if stock >= rule.min_stock_activation:
        return True, False
    return False, True


def evaluate_new_product_eligibility(
    ref_orig: str,
    ref_normalized: str,
    stock: int,
    price: float,
    exists_in_target: bool,
    price_rule: PriceRule,
    stock_rule: StockRule,
    row_number: Optional[int] = None,
) -> tuple[DecisionCode, str, Optional[ValidationIssue]]:
    """Evaluates whether an item from source should be added as a new product or skipped.

    Returns:
        tuple (decision_code, decision_description, issue)
    """
    if exists_in_target:
        return (
            DecisionCode.IGNORED_EXISTS,
            "IGNORADO: Já existe no catálogo de destino (gerenciado na atualização).",
            None,
        )

    if not ref_normalized:
        issue = ValidationIssue(
            severity=IssueSeverity.WARNING,
            code="IGNORED_EMPTY_REF",
            message=f"Linha ignorada: Referência vazia ou inválida ('{ref_orig}').",
            field="reference",
            row_number=row_number,
            details={"original_reference": ref_orig},
        )
        return (
            DecisionCode.IGNORED_EMPTY_REF,
            "IGNORADO: Referência vazia ou inválida.",
            issue,
        )

    if not price_rule.allow_zero_price and price == 0.0:
        issue = ValidationIssue(
            severity=IssueSeverity.INFO,
            code="IGNORED_ZERO_PRICE",
            message=f"Referência '{ref_orig}': Produto ignorado pois o preço é zero (0.00 EUR).",
            field="price",
            row_number=row_number,
            details={"reference": ref_orig, "price": price},
        )
        return (
            DecisionCode.IGNORED_ZERO_PRICE,
            "IGNORADO: Preço igual a zero.",
            issue,
        )

    if stock < stock_rule.min_stock_activation:
        issue = ValidationIssue(
            severity=IssueSeverity.INFO,
            code="IGNORED_STOCK",
            message=(
                f"Referência '{ref_orig}': Stock insuficiente ({stock} < {stock_rule.min_stock_activation})."
            ),
            field="stock",
            row_number=row_number,
            details={
                "reference": ref_orig,
                "stock": stock,
                "min_stock": stock_rule.min_stock_activation,
            },
        )
        return (
            DecisionCode.IGNORED_STOCK,
            f"IGNORADO: Stock insuficiente ({stock} < {stock_rule.min_stock_activation}).",
            issue,
        )

    return (
        DecisionCode.NEW_PRODUCT,
        "ADICIONADO: Produto novo com stock suficiente e preço válido.",
        None,
    )
