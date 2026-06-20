from decimal import Decimal
from unittest.mock import patch, MagicMock
from bank_analysis.parser import extract_data


def make_mock_page(text):
    page = MagicMock()
    page.extract_text.return_value = text
    return page


@patch("bank_analysis.parser.pdfplumber.open")
def test_charge_transaction(mock_open):
    mock_pdf = MagicMock()
    mock_pdf.pages = [make_mock_page("2026-02-16 2026-02-17 AMAZON +$381.00\n")]
    mock_open.return_value.__enter__.return_value = mock_pdf

    result = extract_data("fake.pdf")
    assert len(result) == 1
    assert result[0]["description"] == "AMAZON"
    assert result[0]["amount"] == Decimal("381")
    assert result[0]["type"] == "charge"
    assert result[0]["category"] == "Compras Online"
    assert result[0]["date"] == "2026-02-16"


@patch("bank_analysis.parser.pdfplumber.open")
def test_refund_transaction(mock_open):
    mock_pdf = MagicMock()
    mock_pdf.pages = [
        make_mock_page("2026-02-17 2026-02-17 BONIFICACIÓN CON CASHBACK -$102.33\n")
    ]
    mock_open.return_value.__enter__.return_value = mock_pdf

    result = extract_data("fake.pdf")
    assert len(result) == 1
    assert result[0]["type"] == "refund"
    assert result[0]["amount"] == Decimal("-102.33")


@patch("bank_analysis.parser.pdfplumber.open")
def test_payment_via_spei(mock_open):
    mock_pdf = MagicMock()
    mock_pdf.pages = [
        make_mock_page("2026-03-01 2026-03-01 PAGO POR SPEI -$5,000.00\n")
    ]
    mock_open.return_value.__enter__.return_value = mock_pdf

    result = extract_data("fake.pdf")
    assert len(result) == 1
    assert result[0]["type"] == "payment"
    assert result[0]["amount"] == Decimal("-5000")
    assert result[0]["category"] == "Pagos y Bonificaciones"


@patch("bank_analysis.parser.pdfplumber.open")
def test_msi_transaction(mock_open):
    mock_pdf = MagicMock()
    mock_pdf.pages = [
        make_mock_page(
            "2025-11-24 PAY PAL*LIVERPOOL; RFC: OPM150323DI1 $2,294.15 $764.71 $382.36 4 de 6 0.00%\n"
        )
    ]
    mock_open.return_value.__enter__.return_value = mock_pdf

    result = extract_data("fake.pdf")
    assert len(result) == 1
    assert result[0]["type"] == "msi"
    assert "LIVERPOOL" in result[0]["description"]
    assert "(Mensualidad)" in result[0]["description"]


@patch("bank_analysis.parser.pdfplumber.open")
def test_previous_balance(mock_open):
    mock_pdf = MagicMock()
    mock_pdf.pages = [make_mock_page("Adeudo del periodo anterior = $15,000.00\n")]
    mock_open.return_value.__enter__.return_value = mock_pdf

    result = extract_data("fake.pdf")
    assert len(result) == 1
    assert result[0]["type"] == "previous_balance"
    assert result[0]["amount"] == Decimal("15000")
    assert result[0]["category"] == "Balance"


@patch("bank_analysis.parser.pdfplumber.open")
def test_multiple_transactions(mock_open):
    mock_pdf = MagicMock()
    mock_pdf.pages = [
        make_mock_page(
            "Adeudo del periodo anterior = $15,000.00\n"
            "2026-02-16 2026-02-17 AMAZON +$381.00\n"
            "2026-02-17 2026-02-17 PAGO POR SPEI -$5,000.00\n"
        )
    ]
    mock_open.return_value.__enter__.return_value = mock_pdf

    result = extract_data("fake.pdf")
    assert len(result) == 3
    types = [item["type"] for item in result]
    assert "previous_balance" in types
    assert "charge" in types
    assert "payment" in types


@patch("bank_analysis.parser.pdfplumber.open")
def test_empty_page_returns_empty(mock_open):
    mock_pdf = MagicMock()
    mock_pdf.__enter__.return_value.pages = [make_mock_page("\n")]
    mock_open.return_value.__enter__.return_value = mock_pdf

    result = extract_data("fake.pdf")
    assert result == []


@patch("bank_analysis.parser.pdfplumber.open")
def test_charge_with_dollar_in_description(mock_open):
    mock_pdf = MagicMock()
    mock_pdf.pages = [
        make_mock_page("2026-03-05 2026-03-06 DONA TOTA $N +$381.00\n")
    ]
    mock_open.return_value.__enter__.return_value = mock_pdf

    result = extract_data("fake.pdf")
    assert len(result) == 1
    assert result[0]["description"] == "DONA TOTA $N"
    assert result[0]["amount"] == Decimal("381")
    assert result[0]["type"] == "charge"


@patch("bank_analysis.parser.pdfplumber.open")
def test_description_cleanup_removes_ref(mock_open):
    mock_pdf = MagicMock()
    mock_pdf.pages = [
        make_mock_page("2026-02-16 2026-02-17 AMAZON MX; REF: 123456789 +$500.00\n")
    ]
    mock_open.return_value.__enter__.return_value = mock_pdf

    result = extract_data("fake.pdf")
    assert len(result) == 1
    assert "; REF:" not in result[0]["description"]
    assert result[0]["description"].strip() == "AMAZON MX"


@patch("bank_analysis.parser.pdfplumber.open")
def test_description_cleanup_removes_trailing_asterisk(mock_open):
    mock_pdf = MagicMock()
    mock_pdf.pages = [
        make_mock_page("2026-02-16 2026-02-17 SAMSENLINEA *12345 +$500.00\n")
    ]
    mock_open.return_value.__enter__.return_value = mock_pdf

    result = extract_data("fake.pdf")
    assert len(result) == 1
    assert " *12345" not in result[0]["description"]
    assert result[0]["description"].strip() == "SAMSENLINEA"


@patch("bank_analysis.parser.pdfplumber.open")
def test_description_cleanup_removes_rfc(mock_open):
    mock_pdf = MagicMock()
    mock_pdf.pages = [
        make_mock_page("2026-02-16 2026-02-17 AMAZON MX; RFC: ABC123456XYZ +$500.00\n")
    ]
    mock_open.return_value.__enter__.return_value = mock_pdf

    result = extract_data("fake.pdf")
    assert len(result) == 1
    assert "; RFC:" not in result[0]["description"]
    assert result[0]["description"].strip() == "AMAZON MX"
