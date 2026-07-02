import re
from decimal import Decimal

from .config import CATEGORY_KEYWORDS, DESCRIPTION_CLEANUP_PATTERN, TRAILING_REF_PATTERN


def parse_amount(amount_str: str) -> Decimal:
    """Converts '$1,234.56' or '1,234.56' to Decimal('1234.56')"""
    return Decimal(amount_str.replace("$", "").replace(",", ""))


def clean_description(desc: str) -> str:
    """Removes common suffixes from raw transaction descriptions."""
    desc = DESCRIPTION_CLEANUP_PATTERN.sub("", desc)
    desc = TRAILING_REF_PATTERN.sub("", desc)
    return desc.strip()


def _strip_non_alnum(text: str) -> str:
    """Removes non-alphanumeric chars (except spaces) and collapses whitespace."""
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    return re.sub(r"\s+", " ", cleaned).strip()


def categorize(description: str) -> str:
    """Categorizes a transaction based on its description (normalized matching).

    Uses a "longest match wins" strategy: when multiple keywords match the
    description, the most specific (longest) one takes priority.
    Example: 'STR*AMAZONPRIMESUBS' matches both 'AMAZON' and 'AMAZONPRIMESUBS',
    but 'AMAZONPRIMESUBS' wins because it is longer.
    """
    desc_norm = _strip_non_alnum(description.upper())
    best_kw, best_cat = "", "Otros"
    for keyword, category in CATEGORY_KEYWORDS.items():
        kw_norm = _strip_non_alnum(keyword.upper())
        if kw_norm in desc_norm and len(kw_norm) > len(best_kw):
            best_kw, best_cat = kw_norm, category
    return best_cat
