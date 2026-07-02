import os
import tempfile
from decimal import Decimal

import pytest
from bank_analysis.reporter import generate_html_report


SAMPLE_ITEMS = [
    {
        "date": "2026-01-01",
        "description": "Adeudo del periodo anterior",
        "amount": Decimal("5000"),
        "category": "Balance",
        "type": "previous_balance",
    },
    {
        "date": "2026-01-02",
        "description": "AMAZON",
        "amount": Decimal("500"),
        "category": "Compras Online",
        "type": "charge",
    },
    {
        "date": "2026-01-03",
        "description": "HEB",
        "amount": Decimal("300"),
        "category": "Supermercado",
        "type": "charge",
    },
    {
        "date": "2026-01-04",
        "description": "NETFLIX",
        "amount": Decimal("200"),
        "category": "Suscripciones",
        "type": "charge",
    },
    {
        "date": "2026-01-05",
        "description": "PAGO POR SPEI",
        "amount": Decimal("-6000"),
        "category": "Pagos y Bonificaciones",
        "type": "payment",
    },
    {
        "date": "2026-01-06",
        "description": "LIVERPOOL (Mensualidad)",
        "amount": Decimal("382.36"),
        "category": "Compras Online",
        "type": "msi",
    },
    {
        "date": "2026-01-07",
        "description": "CASHBACK",
        "amount": Decimal("-50"),
        "category": "Pagos y Bonificaciones",
        "type": "refund",
    },
]


@pytest.fixture
def temp_output():
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
        path = f.name
    yield path
    if os.path.exists(path):
        os.unlink(path)


class TestGenerateHTMLReport:
    def test_generates_html_file(self, temp_output):
        generate_html_report(SAMPLE_ITEMS, temp_output)
        assert os.path.exists(temp_output)
        with open(temp_output) as f:
            content = f.read()
        assert "<!DOCTYPE html>" in content
        assert "Dashboard Financiero" in content

    def test_contains_transaction_data(self, temp_output):
        generate_html_report(SAMPLE_ITEMS, temp_output)
        with open(temp_output) as f:
            content = f.read()
        assert "AMAZON" in content
        assert "500.00" in content
        assert "HEB" in content
        assert "NETFLIX" in content

    def test_contains_category_breakdown(self, temp_output):
        generate_html_report(SAMPLE_ITEMS, temp_output)
        with open(temp_output) as f:
            content = f.read()
        assert "Compras Online" in content
        assert "Supermercado" in content
        assert "Suscripciones" in content

    def test_contains_summary_widgets(self, temp_output):
        generate_html_report(SAMPLE_ITEMS, temp_output)
        with open(temp_output) as f:
            content = f.read()
        assert "Adeudo Anterior" in content
        assert "Cargos Mes" in content
        assert "Mensualidades" in content
        assert "Pagos / Abonos" in content
        assert "Total a Pagar" in content

    def test_contains_tabs_and_search(self, temp_output):
        generate_html_report(SAMPLE_ITEMS, temp_output)
        with open(temp_output) as f:
            content = f.read()
        assert "tab-panel-categories" in content
        assert "tab-panel-concepts" in content
        assert "concept-search" in content
        assert "categoryChart" not in content

    def test_handles_empty_items(self, temp_output):
        generate_html_report([], temp_output)
        with open(temp_output) as f:
            content = f.read()
        assert "<!DOCTYPE html>" in content
        assert "Dashboard Financiero" in content

    def test_single_transaction(self, temp_output):
        items = [
            {
                "date": "2026-01-01",
                "description": "Test",
                "amount": Decimal("100"),
                "category": "Test",
                "type": "charge",
            }
        ]
        generate_html_report(items, temp_output)
        with open(temp_output) as f:
            content = f.read()
        assert "Test" in content
        assert "100.00" in content

    def test_copy_buttons_exist(self, temp_output):
        generate_html_report(SAMPLE_ITEMS, temp_output)
        with open(temp_output) as f:
            content = f.read()
        assert "copyToClipboard" in content

    def test_modal_logic_included(self, temp_output):
        generate_html_report(SAMPLE_ITEMS, temp_output)
        with open(temp_output) as f:
            content = f.read()
        assert "openModal" in content
        assert "closeModal" in content
