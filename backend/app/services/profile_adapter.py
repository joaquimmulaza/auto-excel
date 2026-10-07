"""Map ORM commercial_profiles.config → domain CommercialProfile."""
from __future__ import annotations

from typing import Any

from backend.app.domain.models import CommercialProfile, PriceRule, StockRule
from backend.app.infra.db.models import CommercialProfileOrm


def _as_fraction(value: Any, default: float = 0.30) -> float:
    if value is None:
        return default
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    # Accept both 30 and 0.30
    if number > 1:
        return number / 100.0
    return number


def orm_profile_to_domain(profile: CommercialProfileOrm) -> CommercialProfile:
    config: dict[str, Any] = profile.config or {}
    threshold = config.get("price_variation_threshold")
    if threshold is None:
        threshold = config.get("price_guard_threshold_pct")
    min_stock = config.get("stock_min_activation")
    if min_stock is None:
        min_stock = config.get("new_product_min_stock", 3)
    allow_zero = bool(config.get("allow_zero_price", False))
    allow_negative = bool(config.get("allow_negative_stock", False))
    column_mapping = config.get("column_mapping") or {}

    return CommercialProfile(
        code=profile.code,
        name=profile.name,
        description=profile.description,
        price_rule=PriceRule(
            max_variation_threshold=_as_fraction(threshold, 0.30),
            allow_zero_price=allow_zero,
            reject_negative=True,
        ),
        stock_rule=StockRule(
            min_stock_activation=int(min_stock or 3),
            allow_negative=allow_negative,
        ),
        column_mapping=column_mapping,
    )
