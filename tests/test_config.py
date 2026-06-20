from bank_analysis.config import (
    TRANSACTION_PATTERN,
    MSI_PATTERN,
    PREVIOUS_BALANCE_PATTERN,
    CATEGORY_KEYWORDS,
)


class TestTransactionPattern:
    def test_charge(self):
        line = "2026-02-16 2026-02-17 AMAZON +$381.00"
        m = TRANSACTION_PATTERN.match(line)
        assert m is not None
        assert m.group(1) == "2026-02-16"
        assert m.group(3) == "AMAZON"
        assert m.group(4) == "+"
        assert m.group(5) == "381.00"

    def test_payment_or_refund(self):
        line = "2026-02-17 2026-02-17 BONIFICACIÓN CON CASHBACK -$102.33"
        m = TRANSACTION_PATTERN.match(line)
        assert m is not None
        assert m.group(4) == "-"
        assert m.group(5) == "102.33"

    def test_long_description(self):
        line = "2026-03-01 2026-03-02 PAY PAL*LIVERPOOL; RFC: OPM150323DI1 +$500.00"
        m = TRANSACTION_PATTERN.match(line)
        assert m is not None
        assert "LIVERPOOL" in m.group(3)

    def test_no_match_for_invalid(self):
        assert TRANSACTION_PATTERN.match("not a transaction") is None

    def test_no_match_for_empty(self):
        assert TRANSACTION_PATTERN.match("") is None


class TestMSIPattern:
    def test_msi_standard(self):
        line = "2025-11-24 PAY PAL*LIVERPOOL; RFC: OPM150323DI1 $2,294.15 $764.71 $382.36 4 de 6 0.00%"
        m = MSI_PATTERN.match(line)
        assert m is not None
        assert m.group(1) == "2025-11-24"
        assert "LIVERPOOL" in m.group(2)
        assert m.group(4) is not None

    def test_msi_no_rfc(self):
        line = "2026-01-15 AMAZON $5,000.00 $3,000.00 $500.00 6 de 12 0.00%"
        m = MSI_PATTERN.match(line)
        assert m is not None

    def test_no_match_for_regular_transaction(self):
        line = "2026-02-16 2026-02-17 AMAZON +$381.00"
        assert MSI_PATTERN.match(line) is None


class TestPreviousBalancePattern:
    def test_standard(self):
        line = "Adeudo del periodo anterior = $12,345.67"
        m = PREVIOUS_BALANCE_PATTERN.search(line)
        assert m is not None
        assert m.group(1) == "12,345.67"

    def test_zero_balance(self):
        line = "Adeudo del periodo anterior = $0.00"
        m = PREVIOUS_BALANCE_PATTERN.search(line)
        assert m is not None
        assert m.group(1) == "0.00"

    def test_no_match(self):
        assert PREVIOUS_BALANCE_PATTERN.search("not a balance line") is None


class TestCategoryKeywords:
    def test_7eleven_first_match_is_conveniencia(self):
        assert "7ELEVEN" in CATEGORY_KEYWORDS
        assert CATEGORY_KEYWORDS["7ELEVEN"] == "Supermercado"

    def test_no_duplicate_cfe(self):
        keys = [k for k in CATEGORY_KEYWORDS if "CFE" in k]
        assert len(keys) == 1

    def test_amazon_is_present(self):
        assert "AMAZON" in CATEGORY_KEYWORDS
