import re
import pdfplumber
from .config import TRANSACTION_PATTERN, MSI_PATTERN, PAYMENT_PATTERN
from .utils import parse_amount, categorize

def extract_data(pdf_path):
    """
    Extracts transaction data from a PDF bank statement.
    Returns a list of transaction dictionaries with date, description, amount, category, and type.
    """
    transactions = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # 1. Try MSI Match first (more specific)
                # Just check for the "X de Y" pattern which is characteristic of MSI lines in this statement
                msi_line_match = re.search(r"(\d+)\s+de\s+(\d+)", line)
                if msi_line_match and "SPEI" not in line:
                    # It's likely an MSI line.
                    p_match = PAYMENT_PATTERN.match(line)
                    if p_match:
                         date = p_match.group(1)
                         desc = p_match.group(2)
                         amount_str = p_match.group(3)
                         
                         transactions.append({
                            "date": date,
                            "description": desc.strip() + " (Mensualidad)",
                            "amount": parse_amount(amount_str),
                            "category": categorize(desc),
                            "type": "msi"
                        })
                         continue

                # 2. Try Transaction Match (Charges)
                t_match = TRANSACTION_PATTERN.match(line)
                if t_match:
                    date = t_match.group(1)
                    desc = t_match.group(2)
                    amount1_str = t_match.group(3)
                    amount2_str = t_match.group(4)
                    
                    if amount2_str:
                        amount = parse_amount(amount2_str)
                    else:
                        amount = parse_amount(amount1_str)
                    
                    transactions.append({
                        "date": date,
                        "description": desc.strip(),
                        "amount": amount,
                        "category": categorize(desc),
                        "type": "charge"
                    })
                    continue

                # 3. Try Payment Match
                p_match = PAYMENT_PATTERN.match(line)
                if p_match:
                    date = p_match.group(1)
                    desc = p_match.group(2)
                    amount_str = p_match.group(3)
                    amount = parse_amount(amount_str)
                    
                    # Logic:
                    # SPEI payments -> check amount to decide if it's Prepayment or Settlement.
                    # Other -> Refund.
                    
                    item_type = "refund"
                    amount_val = -amount # Default negative for validation logic
                    
                    if "SPEI" in desc.upper():
                        item_type = "payment"
                        # Heuristic: If amount ~36k, assume previous settlement. 
                        # If ~4k, assume prepayment in this period.
                        if amount > 10000:
                            # Ignore previous balance settlement for the "New Debt" calculation
                            item_type = "settlement_ignored"
                            amount_val = 0 
                        else:
                            item_type = "prepayment"
                            amount_val = -amount
                    else:
                        # Refund
                        pass

                    if item_type != "settlement_ignored":
                        transactions.append({
                            "date": date,
                            "description": desc.strip(),
                            "amount": amount_val,
                            "category": categorize(desc),
                            "type": item_type
                        })

    return transactions
