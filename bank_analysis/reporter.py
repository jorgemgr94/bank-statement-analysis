import os
import shutil
import logging
from decimal import Decimal
from collections import defaultdict

from jinja2 import Environment, FileSystemLoader

from .types import Transaction, TableRow


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

CHART_COLORS: list[str] = [
    "#f43f5e", "#ec4899", "#d946ef", "#a855f7", "#8b5cf6",
    "#6366f1", "#3b82f6", "#0ea5e9", "#06b6d4", "#14b8a6",
    "#10b981", "#22c55e", "#84cc16", "#eab308",
]


def generate_html_report(items: list[Transaction], output_file: str = "output/output.html") -> None:
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    category_totals: dict[str, Decimal] = defaultdict(Decimal)
    category_items: dict[str, list[Transaction]] = defaultdict(list)

    total_charges = Decimal("0")
    total_msi = Decimal("0")
    total_refunds = Decimal("0")
    total_prepayments = Decimal("0")
    previous_balance = Decimal("0")

    for item in items:
        amt = item["amount"]
        if item["type"] == "previous_balance":
            previous_balance += amt
        elif item["type"] == "charge":
            total_charges += amt
        elif item["type"] == "msi":
            total_msi += amt
        elif item["type"] == "refund":
            total_refunds += amt
        elif item["type"] in ("payment", "prepayment"):
            total_prepayments += amt

    total_net_calc = previous_balance + total_charges + total_msi + total_refunds + total_prepayments

    for item in items:
        if item["type"] == "previous_balance":
            continue

        cat = item["category"]
        category_totals[cat] += item["amount"]
        category_items[cat].append(item)

    sorted_categories_desc = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)

    chart_labels: list[str] = []
    chart_data: list[float] = []
    total_expenses_for_chart = sum(t for _, t in sorted_categories_desc if t > 0)

    table_rows: list[TableRow] = []
    color_index = 0

    for cat, total in sorted_categories_desc:
        if total > 0:
            chart_labels.append(cat)
            chart_data.append(float(round(total, 2)))

        color = CHART_COLORS[color_index % len(CHART_COLORS)] if total > 0 else "#cbd5e1"
        if total > 0:
            color_index += 1

        pct = float(total / total_expenses_for_chart * 100) if (total > 0 and total_expenses_for_chart) else 0.0

        table_rows.append({
            "cat": cat,
            "total": total,
            "pct": pct,
            "color": color,
            "count": len(category_items[cat]),
        })

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("report.html.j2")

    static_output_dir = os.path.join(output_dir, "static")
    os.makedirs(static_output_dir, exist_ok=True)
    for fname in ("tailwind-play.js", "chart.umd.min.js"):
        shutil.copy2(os.path.join(STATIC_DIR, fname), os.path.join(static_output_dir, fname))

    html_content = template.render(
        total_net_calc=total_net_calc,
        previous_balance=previous_balance,
        total_charges=total_charges,
        total_msi=total_msi,
        total_payments=abs(total_refunds + total_prepayments),
        chart_labels=chart_labels,
        chart_data=chart_data,
        chart_colors=CHART_COLORS,
        table_rows=table_rows,
        category_items=dict(category_items),
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    logging.info("Reporte HTML generado en: %s", output_file)
