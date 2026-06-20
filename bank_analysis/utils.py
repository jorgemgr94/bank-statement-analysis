from decimal import Decimal

from .config import CATEGORY_KEYWORDS

def parse_amount(amount_str):
    """Converts '$1,234.56' or '1,234.56' to Decimal('1234.56')"""
    return Decimal(amount_str.replace('$', '').replace(',', ''))

def categorize(description):
    """Categorizes a transaction based on its description."""
    desc_upper = description.upper()
    for keyword, category in CATEGORY_KEYWORDS.items():
        if keyword in desc_upper:
            return category
    return "Otros"
