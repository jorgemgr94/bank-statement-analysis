from decimal import Decimal

from bank_analysis.utils import parse_amount, categorize, clean_description


class TestParseAmount:
    def test_with_dollar_and_commas(self):
        assert parse_amount("$1,234.56") == Decimal("1234.56")

    def test_without_dollar(self):
        assert parse_amount("1234.56") == Decimal("1234.56")

    def test_zero(self):
        assert parse_amount("$0.00") == Decimal("0")

    def test_large_number(self):
        assert parse_amount("$12,345,678.90") == Decimal("12345678.90")

    def test_small_decimal(self):
        assert parse_amount("$0.99") == Decimal("0.99")

    def test_no_commas(self):
        assert parse_amount("$999.99") == Decimal("999.99")


class TestCategorize:
    def test_amazon_returns_compras_online(self):
        assert categorize("AMAZON") == "Compras Online"

    def test_netflix_returns_suscripciones(self):
        assert categorize("NETFLIX") == "Suscripciones"

    def test_case_insensitive(self):
        assert categorize("amazon") == "Compras Online"

    def test_partial_match(self):
        assert categorize("payment to AMAZON PRIME") == "Compras Online"

    def test_unknown_returns_otros(self):
        assert categorize("TIENDA DESCONOCIDA") == "Otros"

    def test_empty_string_returns_otros(self):
        assert categorize("") == "Otros"

    def test_heb_returns_supermercado(self):
        assert categorize("HEB") == "Supermercado"

    def test_uber_eats_returns_comida_delivery(self):
        assert categorize("UBER EATS") == "Comida / Delivery"

    def test_cfe_returns_servicios(self):
        assert categorize("CFE") == "Servicios"

    def test_hyphen_normalized(self):
        assert categorize("H-E-B") == "Supermercado"

    def test_dots_normalized(self):
        assert categorize("C.F.E.") == "Servicios"

    def test_mixed_punctuation(self):
        assert categorize("WAL-MART #42") == "Supermercado"

    def test_asterisk_in_description(self):
        assert categorize("PAYPAL *NATURGYMEXI") == "Servicios"

    def test_extra_spaces_normalized(self):
        assert categorize("  AMAZON  ") == "Compras Online"


class TestCleanDescription:
    def test_removes_rfc_suffix(self):
        assert clean_description("PAY PAL*LIVERPOOL; RFC: OPM150323DI1") == "PAY PAL*LIVERPOOL"

    def test_removes_ref_suffix(self):
        assert clean_description("AMAZON MX; REF: 123456789") == "AMAZON MX"

    def test_removes_trailing_asterisk_ref(self):
        assert clean_description("SAMSENLINEA *1234") == "SAMSENLINEA"

    def test_no_cleanup_needed(self):
        assert clean_description("NETFLIX") == "NETFLIX"

    def test_cleanup_empty(self):
        assert clean_description("") == ""
