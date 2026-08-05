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

    def test_convenience_stores_return_supermercado(self):
        assert categorize("OXXO TORREMOLINOS") == "Supermercado"
        assert categorize("7 ELEVEN") == "Supermercado"

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

    def test_longest_match_wins_amazon_prime(self):
        # 'AMAZONPRIMESUBS' (15 chars) should win over 'AMAZON' (6 chars)
        assert categorize("STR*AMAZONPRIMESUBS") == "Suscripciones"

    def test_longest_match_wins_uber_eats_vs_uber(self):
        # 'UBER EATS' should win over 'UBER'
        assert categorize("UBER EATS MX") == "Comida / Delivery"

    def test_longest_match_cinepolis_dulceria(self):
        # 'CINEPOLIS DULCERIA' should win over 'CINEPOLIS'
        assert categorize("CINEPOLIS DULCERIA MX") == "Vacaciones / Entretenimiento"

    def test_new_supermarket_merchants(self):
        assert categorize("ZUMA ABTS MERCO LIN VI") == "Supermercado"
        assert categorize("PAYPAL*BODAURRERA") == "Supermercado"
        assert categorize("CARNES JA CARLOS") == "Supermercado"

    def test_school_merchants(self):
        assert categorize("ANGEL COLOR") == "Escuela"
        assert categorize("DEL SOL 1112 MP") == "Escuela"
        assert categorize("DEL SOL 1188 MP") == "Escuela"
        assert categorize("TIEND INT SUC MATRIZ") == "Escuela"

    def test_new_food_merchants(self):
        merchants = (
            "COM RAP P LOCO SUC PLA",
            "CAFET GABY S HIDAL",
            "KK PASEO DE LA FE",
            "ROCK&BILLY CITADEL",
            "PANADERIA LEO 1",
            "FENGFA COMIDA CANTONES",
            "COMERC ALIMENTOS GOOL",
        )
        for merchant in merchants:
            assert categorize(merchant) == "Comida / Delivery"

    def test_new_transport_merchants(self):
        merchants = (
            "PAY PAL*KIGO",
            "PAYPAL*KIGO",
            "OPENPAY*KIGO PARKIMOVI",
            "CONEKTA*URBANI",
        )
        for merchant in merchants:
            assert categorize(merchant) == "Transporte"

    def test_new_entertainment_merchants(self):
        merchants = (
            "PAYPAL *EPIC GAMES",
            "SULTANES BEBIDAS MU",
            "ZUMA*EPIK LINDA VISTA",
            "PINPEO*RAA FESTIVALES",
        )
        for merchant in merchants:
            assert categorize(merchant) == "Vacaciones / Entretenimiento"

    def test_new_services_and_shopping_merchants(self):
        assert categorize("MERPAGO*RENTAMOVISTAR") == "Servicios"
        assert categorize("PAYPAL*MICROSOFT") == "Compras Online"
        assert categorize("HOME DEPOT M ALEMAN") == "Hogar / Mantenimiento"
        assert categorize("BENAVI 330603 CITADEL") == "Salud"

    def test_reviewed_merchants_that_remain_otros(self):
        merchants = (
            "PAYPAL",
            "PY *INK D STORES",
            "MERPAGO*ADALBERTOGUAD",
            "GRUPO TTA ZEMAT",
        )
        for merchant in merchants:
            assert categorize(merchant) == "Otros"


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
