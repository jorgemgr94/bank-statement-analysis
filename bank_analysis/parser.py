import pdfplumber
from .config import TRANSACTION_PATTERN, MSI_PATTERN, PREVIOUS_BALANCE_PATTERN
from .types import Transaction, TransactionType
from .utils import parse_amount, categorize


def extract_data(pdf_path: str) -> list[Transaction]:
    """
    Extracts transaction data from a PDF bank statement.
    Returns a list of transaction dictionaries with date, description, amount, category, and type.
    """
    transactions: list[Transaction] = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            lines = text.split("\n")

            for line in lines:
                line = line.strip()

                pb_match = PREVIOUS_BALANCE_PATTERN.search(line)
                if pb_match:
                    transactions.append({
                        "date": "N/A",
                        "description": "Adeudo del periodo anterior",
                        "amount": parse_amount(pb_match.group(1)),
                        "category": "Balance",
                        "type": "previous_balance",
                    })
                    continue

                msi_match = MSI_PATTERN.match(line)
                if msi_match:
                    date = msi_match.group(1)
                    desc = msi_match.group(2)
                    amount_str = msi_match.group(3)

                    desc_clean = desc.split(";")[0].strip()

                    transactions.append({
                        "date": date,
                        "description": desc_clean + " (Mensualidad)",
                        "amount": parse_amount(amount_str),
                        "category": categorize(desc_clean),
                        "type": "msi",
                    })
                    continue

                t_match = TRANSACTION_PATTERN.match(line)
                if t_match:
                    date = t_match.group(1)
                    desc = t_match.group(3)
                    sign = t_match.group(4)
                    amount_str = t_match.group(5)

                    amount = parse_amount(amount_str)
                    desc_clean = desc.split(";")[0].strip()

                    if sign == "+":
                        transactions.append({
                            "date": date,
                            "description": desc_clean,
                            "amount": amount,
                            "category": categorize(desc_clean),
                            "type": "charge",
                        })
                    elif sign == "-":
                        amount_val = -amount
                        item_type: TransactionType = "refund"

                        if "SPEI" in desc_clean.upper():
                            item_type = "payment"

                        transactions.append({
                            "date": date,
                            "description": desc_clean,
                            "amount": amount_val,
                            "category": categorize(desc_clean),
                            "type": item_type,
                        })
                    continue

    return transactions
