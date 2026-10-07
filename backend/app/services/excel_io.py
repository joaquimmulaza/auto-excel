"""Excel read/write helpers for job processing."""
from __future__ import annotations

from io import BytesIO
from typing import Any

import pandas as pd

from backend.app.domain.normalization import normalize_col

# Column-name hints used to prefer real data headers over banner rows.
_HEADER_HINT_ALIASES = (
    "REFERENCIA",
    "REFERÊNCIA",
    "REF",
    "REFERENCE",
    "SKU",
    "CODIGO",
    "CÓDIGO",
    "PRECO COM IVA",
    "PREÇO COM IVA",
    "PRECO",
    "PREÇO",
    "PRICE",
    "PVP",
    "STOCK",
    "ESTOQUE",
    "QUANTIDADE",
    "DESIGNACAO",
    "DESIGNAÇÃO",
)


def dataframe_to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    cleaned = df.where(pd.notnull(df), None)
    return cleaned.to_dict(orient="records")


def _column_header_score(columns: list[Any]) -> int:
    """Score a candidate header row; higher is better."""
    hint_norms = {normalize_col(a) for a in _HEADER_HINT_ALIASES}
    score = 0
    for col in columns:
        if not isinstance(col, str):
            continue
        label = col.strip()
        if len(label) <= 1 or label.isdigit() or label.startswith("Unnamed:"):
            continue
        score += 1
        if normalize_col(label) in hint_norms:
            score += 3
    return score


def auto_detect_header(content: bytes, max_rows: int = 10) -> tuple[Any, int]:
    """Detect the best sheet and header skiprows for an Excel workbook.

    Port of ``main.auto_detect_header``, adapted for in-memory bytes and with
    a bonus when column names match known ref/price/stock aliases.
    """
    best_sheet: Any = 0
    best_row = 0
    best_score = -1

    bio = BytesIO(content)
    try:
        xl = pd.ExcelFile(bio)
        sheets = list(xl.sheet_names)
    except Exception:
        return 0, 0

    for sheet in sheets:
        for skip in range(max_rows):
            try:
                bio.seek(0)
                df_test = pd.read_excel(
                    bio,
                    sheet_name=sheet,
                    skiprows=skip,
                    nrows=1,
                    header=0,
                )
            except Exception:
                break
            score = _column_header_score(list(df_test.columns))
            if score > best_score:
                best_score = score
                best_row = skip
                best_sheet = sheet

    return best_sheet, best_row


def read_excel_records(content: bytes) -> list[dict[str, Any]]:
    sheet, skiprows = auto_detect_header(content)
    bio = BytesIO(content)
    df = pd.read_excel(bio, sheet_name=sheet, skiprows=skiprows, header=0)
    df.columns = [str(c).strip() for c in df.columns]
    return dataframe_to_records(df)


def write_excel_bytes(records: list[dict[str, Any]], sheet_name: str = "Sheet1") -> bytes:
    df = pd.DataFrame(records)
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return buf.getvalue()


def write_decision_log(items: list[dict[str, Any]]) -> bytes:
    rows = [
        {
            "Referência Original": i.get("reference_original"),
            "Referência Limpa (Match)": i.get("reference_normalized"),
            "Preço Anterior": i.get("old_price"),
            "Preço Novo": i.get("new_price"),
            "Stock Anterior": i.get("old_stock"),
            "Stock Novo": i.get("new_stock"),
            "Variação %": i.get("price_variation_pct"),
            "Decisão": i.get("decision"),
            "Código": i.get("decision_code"),
        }
        for i in items
    ]
    return write_excel_bytes(rows, sheet_name="LOG")
