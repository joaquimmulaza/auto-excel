"""Excel read/write helpers for job processing."""
from __future__ import annotations

from io import BytesIO
from typing import Any

import pandas as pd


def dataframe_to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    cleaned = df.where(pd.notnull(df), None)
    return cleaned.to_dict(orient="records")


def read_excel_records(content: bytes) -> list[dict[str, Any]]:
    df = pd.read_excel(BytesIO(content))
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
