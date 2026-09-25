"""Domain normalization and data cleaning utilities for Cotarco Commercial Manager.

Fully deterministic pure Python functions for text, reference, price, and variation calculations.
No CLI or external dependencies.
"""

from __future__ import annotations

import math
import re
import unicodedata
from typing import Any, Optional


def normalize_col(txt: Any) -> str:
    """Normalizes column names and header text.

    Removes accents, strips leading/trailing whitespace, and converts to uppercase.
    Handles None and NaN gracefully by returning an empty string.
    """
    if txt is None:
        return ""
    if isinstance(txt, float) and math.isnan(txt):
        return ""

    s = str(txt).strip()
    if not s or s.lower() == "nan":
        return ""

    # NFKD ASCII normalization to strip accents
    normalized = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("ASCII")
    return normalized.strip().upper()


def ultra_clean(text: Any) -> str:
    """Sanitizes catalog references deterministically.

    Retains strictly uppercase alphanumeric characters (A-Z, 0-9) and hyphens (-).
    Removes accents, spaces, slashes, punctuation, and all other symbols.
    Returns empty string for None, NaN, or blank values.
    """
    if text is None:
        return ""
    if isinstance(text, float) and math.isnan(text):
        return ""

    s = str(text).strip()
    if not s or s.lower() == "nan":
        return ""

    # Normalize accents first
    normalized = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("ASCII").upper()
    # Retain only letters, digits, and hyphens
    cleaned = re.sub(r"[^A-Z0-9-]", "", normalized)
    return cleaned.strip()


def limpar_preco(val: Any) -> float:
    """Cleans and parses price value into a rounded 2-decimal float.

    Robust against:
    - European formats with dot thousands and comma decimal ('2.614.035,09' -> 2614035.09)
    - Anglo-Saxon formats ('1,250.50' -> 1250.50)
    - Currency symbols ('€ 1.250,50', '1250,50 EUR', 'R$ 30,00', '100 $')
    - Direct numeric floats and integers
    - Nulls, blanks, NaN, and corrupt strings -> 0.0
    """
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        if isinstance(val, float) and math.isnan(val):
            return 0.0
        return round(float(val), 2)

    s = str(val).strip().upper()
    if not s or s in ("NAN", "NONE", "NULL", "N/A", "-"):
        return 0.0

    # Retain digits, '.', ',', and '-'
    s = re.sub(r"[^\d.,-]", "", s)
    if not s or s in ("-", ".", ","):
        return 0.0

    # Handle thousands and decimal separators
    has_dot = "." in s
    has_comma = "," in s

    if has_dot and has_comma:
        last_dot = s.rfind(".")
        last_comma = s.rfind(",")
        if last_comma > last_dot:
            # European: '1.250,50' or '2.614.035,09'
            s = s.replace(".", "").replace(",", ".")
        else:
            # Anglo-Saxon: '1,250.50'
            s = s.replace(",", "")
    elif has_comma:
        # Only comma: '45,90'
        s = s.replace(",", ".")
    elif has_dot:
        # Only dot(s): '150.00' or multiple dots '1.234.567'
        parts = s.split(".")
        if len(parts) > 2:
            s = "".join(parts[:-1]) + "." + parts[-1]

    try:
        parsed = float(s)
        return round(parsed, 2)
    except (ValueError, TypeError):
        return 0.0


def calcular_variacao(old_price: Optional[float], new_price: float) -> Optional[float]:
    """Safely calculates relative price variation without division by zero.

    Returns:
        float representing relative variation (e.g. 0.30 for +30%, -0.20 for -20%),
        or None if old_price is None, <= 0.0, or invalid.
    """
    if old_price is None or old_price <= 0.0:
        return None

    delta = new_price - old_price
    return round(delta / old_price, 4)
