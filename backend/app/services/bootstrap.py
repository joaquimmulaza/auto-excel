"""Seed users and commercial profiles for local / file-backed databases."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.app.api.v1.auth import ensure_demo_users
from backend.app.core.settings import get_settings
from backend.app.infra.db.models import CommercialProfileOrm


SEED_PROFILES = [
    (
        uuid.UUID("11111111-1111-1111-1111-111111111111"),
        "MANO",
        "Marketplace Mano",
        "MARKETPLACE",
        "Exportação Excel. Stock mínimo 3. Variação máxima 30%.",
        {
            "integration_type": "EXCEL_EXPORT",
            "stock_min_activation": 3,
            "price_variation_threshold": 0.30,
            "price_guard_threshold_pct": 30,
            "new_product_min_stock": 3,
            "allow_zero_price": False,
            "allow_negative_stock": False,
            "price_guard_enabled": True,
        },
    ),
    (
        uuid.UUID("22222222-2222-2222-2222-222222222222"),
        "WOOCOMMERCE",
        "Loja Online Cotarco",
        "STORE",
        "Catálogo e-commerce Cotarco. Stock mínimo 1. Variação 30%.",
        {
            "integration_type": "EXCEL_EXPORT",
            "stock_min_activation": 1,
            "price_variation_threshold": 0.30,
            "price_guard_threshold_pct": 30,
            "new_product_min_stock": 1,
            "allow_zero_price": False,
            "woocommerce_enabled": False,
            "feature_flags": {"woocommerce_live_push": False},
        },
    ),
    (
        uuid.UUID("33333333-3333-3333-3333-333333333333"),
        "BFA",
        "BFA Wholesale",
        "PARTNER",
        "Parceiro BFA. Limiar placeholder — confirmar com negócio.",
        {
            "integration_type": "EXCEL_EXPORT",
            "stock_min_activation": 5,
            "price_variation_threshold": 0.10,
            "price_guard_threshold_pct": 10,
            "new_product_min_stock": 5,
            "allow_zero_price": False,
            "business_rules_confirmed": False,
        },
    ),
    (
        uuid.UUID("44444444-4444-4444-4444-444444444444"),
        "KERO",
        "Revendedor Kero",
        "RESELLER",
        "Revendedor Kero. Limiares placeholder — confirmar com negócio.",
        {
            "integration_type": "EXCEL_EXPORT",
            "stock_min_activation": 2,
            "price_variation_threshold": 0.20,
            "price_guard_threshold_pct": 20,
            "new_product_min_stock": 2,
            "business_rules_confirmed": False,
        },
    ),
    (
        uuid.UUID("55555555-5555-5555-5555-555555555555"),
        "SIAC",
        "Revendedor SIAC",
        "RESELLER",
        "Revendedor SIAC. Limiares placeholder — confirmar com negócio.",
        {
            "integration_type": "EXCEL_EXPORT",
            "stock_min_activation": 2,
            "price_variation_threshold": 0.15,
            "price_guard_threshold_pct": 15,
            "new_product_min_stock": 2,
            "business_rules_confirmed": False,
        },
    ),
]


def ensure_seed_profiles(db: Session) -> None:
    now = datetime.now(timezone.utc)
    for pid, code, name, ptype, description, config in SEED_PROFILES:
        existing = db.get(CommercialProfileOrm, pid)
        if existing:
            continue
        by_code = (
            db.query(CommercialProfileOrm)
            .filter(CommercialProfileOrm.code == code)
            .first()
        )
        if by_code:
            continue
        db.add(
            CommercialProfileOrm(
                id=pid,
                code=code,
                name=name,
                type=ptype,
                description=description,
                active=True,
                config=config,
                rules_version=1,
                created_at=now,
                updated_at=now,
            )
        )
    db.flush()


def bootstrap_database(db: Session) -> None:
    settings = get_settings()
    if settings.auth_mode == "local":
        ensure_demo_users(db)
    if settings.environment in {"local", "test"} or settings.is_sqlite:
        ensure_seed_profiles(db)
    db.commit()
