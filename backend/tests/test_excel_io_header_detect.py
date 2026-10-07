"""Regression: Excel header/sheet detection for Samsung-style workbooks."""
from __future__ import annotations

from pathlib import Path

from backend.app.domain.engine import (
    DEFAULT_SOURCE_PRICE_ALIASES,
    DEFAULT_SOURCE_REF_ALIASES,
    DEFAULT_SOURCE_STOCK_ALIASES,
    _find_field_value,
)
from backend.app.domain.normalization import ultra_clean
from backend.app.services.excel_io import auto_detect_header, read_excel_records

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "fixtures" / "excel"


def test_sample_input_samsung_still_reads_with_header_on_row_zero():
    content = (FIXTURES / "sample_input_samsung.xlsx").read_bytes()
    sheet, skip = auto_detect_header(content)
    assert skip == 0

    records = read_excel_records(content)
    assert len(records) >= 1
    cols = {str(c).strip().upper() for c in records[0].keys()}
    assert "REF" in cols or "REFERÊNCIA" in {c.upper() for c in records[0].keys()} or any(
        "REF" in c.upper() for c in records[0].keys()
    )


def test_samsung_banner_workbook_detects_header_row_two():
    content = (FIXTURES / "cotarco_samsung_preco_atualizado.xlsx").read_bytes()
    sheet, skip = auto_detect_header(content)
    assert skip == 2
    assert "Tabela" in str(sheet) or sheet == "Tabela Preços "

    records = read_excel_records(content)
    assert len(records) >= 100

    keys = {str(k).strip() for k in records[0].keys()}
    assert "REFERÊNCIA" in keys
    assert "Preço com IVA" in keys
    assert any(k.strip().upper().startswith("STOCK") for k in keys)

    ok_refs = 0
    for row in records:
        raw_ref = str(_find_field_value(row, DEFAULT_SOURCE_REF_ALIASES, default="") or "")
        if ultra_clean(raw_ref):
            ok_refs += 1
            price = _find_field_value(row, DEFAULT_SOURCE_PRICE_ALIASES, default=0.0)
            stock = _find_field_value(row, DEFAULT_SOURCE_STOCK_ALIASES, default=0)
            assert price is not None
            assert stock is not None

    # Production bug had 187/187 empty; after fix almost all rows resolve.
    assert ok_refs >= 170
    assert ok_refs / len(records) > 0.9


def test_samsung_catalog_workbook_also_detects_real_header():
    content = (FIXTURES / "cotarco_samsung_tabela_cf.xlsx").read_bytes()
    _sheet, skip = auto_detect_header(content)
    assert skip == 2
    records = read_excel_records(content)
    assert "REFERÊNCIA" in {str(k).strip() for k in records[0].keys()}
    first_ref = _find_field_value(records[0], DEFAULT_SOURCE_REF_ALIASES, default="")
    assert ultra_clean(str(first_ref or ""))
