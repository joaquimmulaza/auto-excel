#!/usr/bin/env python3
"""Generate Excel fixtures for Cotarco Commercial Manager demos and tests."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "fixtures" / "excel"
OUT.mkdir(parents=True, exist_ok=True)

# Column names match common Samsung-style tables consumed by the domain engine.
INPUT_ROWS = [
    {"REF": "RS64R53112A/EU", "PRECO": 2614035, "STOCK": 3, "DESCRICAO": "Side-by-side"},
    {"REF": "RF71A967532UT", "PRECO": 3491228, "STOCK": 9, "DESCRICAO": "French door"},
    {"REF": "RB34T602FSA", "PRECO": 850000, "STOCK": 22, "DESCRICAO": "Combi"},
    {"REF": "WW90T554DAN", "PRECO": 649900, "STOCK": 8, "DESCRICAO": "Lavadora"},
    {"REF": "DV90T6240LK", "PRECO": 520000, "STOCK": 1, "DESCRICAO": "Secadora stock baixo"},
    {"REF": "XXX-ANOMALY-REF", "PRECO": 5500000, "STOCK": 5, "DESCRICAO": "Anomalia preço"},
    {"REF": "ZERO-PRICE-SKU", "PRECO": 0, "STOCK": 4, "DESCRICAO": "Preço zero"},
]

CATALOG_ROWS = [
    {"REF": "RS64R53112A/EU", "PRECO": 2393787, "STOCK": 0, "DESCRICAO": "Side-by-side"},
    {"REF": "RF71A967532UT", "PRECO": 3980000, "STOCK": 8, "DESCRICAO": "French door"},
    {"REF": "RB34T602FSA", "PRECO": 850000, "STOCK": 14, "DESCRICAO": "Combi"},
    {"REF": "XXX-ANOMALY-REF", "PRECO": 2000000, "STOCK": 5, "DESCRICAO": "Anomalia preço"},
]


def main() -> None:
    input_path = OUT / "sample_input_samsung.xlsx"
    catalog_path = OUT / "sample_catalog.xlsx"
    pd.DataFrame(INPUT_ROWS).to_excel(input_path, index=False)
    pd.DataFrame(CATALOG_ROWS).to_excel(catalog_path, index=False)
    print(f"Wrote {input_path}")
    print(f"Wrote {catalog_path}")


if __name__ == "__main__":
    main()
