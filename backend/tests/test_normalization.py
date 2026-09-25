"""Unit tests for domain normalization and cleaning utilities."""

import math
import pytest

from backend.app.domain.normalization import (
    calcular_variacao,
    limpar_preco,
    normalize_col,
    ultra_clean,
)


class TestNormalizeCol:
    """Tests for normalize_col utility function."""

    def test_removes_accents_and_uppercases(self):
        assert normalize_col("REFERÊNCIA") == "REFERENCIA"
        assert normalize_col("preço com iva") == "PRECO COM IVA"
        assert normalize_col("DesigNaçãO") == "DESIGNACAO"
        assert normalize_col("CÓDIGO DE BARRAS") == "CODIGO DE BARRAS"

    def test_strips_surrounding_whitespace(self):
        assert normalize_col("  referencia  ") == "REFERENCIA"
        assert normalize_col("\t stock \n") == "STOCK"

    def test_handles_empty_and_null_inputs(self):
        assert normalize_col(None) == ""
        assert normalize_col("") == ""
        assert normalize_col("   ") == ""
        assert normalize_col(float("nan")) == ""


class TestUltraClean:
    """Tests for ultra_clean reference sanitization."""

    def test_preserves_alphanumeric_and_hyphens(self):
        assert ultra_clean("SM-A125F") == "SM-A125F"
        assert ultra_clean("ABC-123-XYZ") == "ABC-123-XYZ"

    def test_removes_special_characters_and_spaces(self):
        # Keeps only A-Z, 0-9 and hyphens
        assert ultra_clean("SM-A125F/DS") == "SM-A125FDS"
        assert ultra_clean("REF. 123-AB_45") == "REF123-AB45"
        assert ultra_clean("  samsung  galaxy-s21  ") == "SAMSUNGGALAXY-S21"

    def test_removes_accents(self):
        assert ultra_clean("PROD-ÚLTIMO") == "PROD-ULTIMO"
        assert ultra_clean("PEÇA-AÇÃO-01") == "PECA-ACAO-01"

    def test_handles_empty_and_null_inputs(self):
        assert ultra_clean(None) == ""
        assert ultra_clean("") == ""
        assert ultra_clean("   ") == ""
        assert ultra_clean(float("nan")) == ""
        assert ultra_clean("nan") == ""


class TestLimparPreco:
    """Tests for limpar_preco robust price parser."""

    def test_parses_european_format(self):
        # Dots as thousands separators, comma as decimal
        assert limpar_preco("2.614.035,09") == 2614035.09
        assert limpar_preco("1.250,50") == 1250.50
        assert limpar_preco("45,90") == 45.90

    def test_parses_standard_decimal_format(self):
        assert limpar_preco("2614035.09") == 2614035.09
        assert limpar_preco("99.95") == 99.95
        assert limpar_preco("150.0") == 150.0

    def test_handles_currency_symbols_and_spaces(self):
        assert limpar_preco("€ 1.250,50") == 1250.50
        assert limpar_preco("1250,50 EUR") == 1250.50
        assert limpar_preco("R$ 30,00") == 30.00
        assert limpar_preco("  100 $  ") == 100.00

    def test_accepts_direct_numeric_types(self):
        assert limpar_preco(100) == 100.00
        assert limpar_preco(123.456) == 123.46
        assert limpar_preco(0) == 0.00

    def test_handles_invalid_and_empty_values(self):
        assert limpar_preco(None) == 0.00
        assert limpar_preco("") == 0.00
        assert limpar_preco("   ") == 0.00
        assert limpar_preco("N/A") == 0.00
        assert limpar_preco("nan") == 0.00
        assert limpar_preco("-") == 0.00
        assert limpar_preco("invalid_price") == 0.00


class TestCalcularVariacao:
    """Tests for calcular_variacao calculation and zero-division protection."""

    def test_calculates_positive_variation(self):
        # 100 -> 130 is +30% (+0.30)
        var = calcular_variacao(100.0, 130.0)
        assert var is not None
        assert math.isclose(var, 0.30, rel_tol=1e-3)

    def test_calculates_negative_variation(self):
        # 100 -> 70 is -30% (-0.30)
        var = calcular_variacao(100.0, 70.0)
        assert var is not None
        assert math.isclose(var, -0.30, rel_tol=1e-3)

    def test_calculates_zero_variation(self):
        var = calcular_variacao(50.0, 50.0)
        assert var == 0.0

    def test_protection_against_division_by_zero(self):
        # Zero old price should not raise ZeroDivisionError
        assert calcular_variacao(0.0, 100.0) is None
        assert calcular_variacao(None, 100.0) is None
        assert calcular_variacao(-50.0, 100.0) is None
