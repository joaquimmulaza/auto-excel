"""Domain layer package for Cotarco Commercial Manager.

Exports domain entities, validation issues, decisions, and pure business rules.
"""

from backend.app.domain.models import (
    CommercialProfile,
    DecisionCode,
    IssueSeverity,
    JobItemResult,
    PriceRule,
    ProcessResult,
    ProcessSummary,
    Product,
    StockRule,
    ValidationIssue,
)
from backend.app.domain.engine import (
    TableProcessor,
    process_price_table,
)
from backend.app.domain.normalization import (
    calcular_variacao,
    limpar_preco,
    normalize_col,
    ultra_clean,
)
from backend.app.domain.rules import (
    calculate_price_variation,
    clean_price_value,
    evaluate_new_product_eligibility,
    evaluate_price_guard,
    evaluate_stock_activation,
    normalize_reference,
)

__all__ = [
    # Models
    "CommercialProfile",
    "DecisionCode",
    "IssueSeverity",
    "JobItemResult",
    "PriceRule",
    "ProcessResult",
    "ProcessSummary",
    "Product",
    "StockRule",
    "ValidationIssue",
    # Engine
    "TableProcessor",
    "process_price_table",
    # Normalization & Helpers
    "calcular_variacao",
    "calculate_price_variation",
    "clean_price_value",
    "evaluate_new_product_eligibility",
    "evaluate_price_guard",
    "evaluate_stock_activation",
    "limpar_preco",
    "normalize_col",
    "normalize_reference",
    "ultra_clean",
]
