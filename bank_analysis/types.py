from decimal import Decimal
from typing import Literal, TypedDict

TransactionType = Literal[
    "previous_balance",
    "charge",
    "msi",
    "refund",
    "payment",
]


class Transaction(TypedDict):
    date: str
    description: str
    amount: Decimal
    category: str
    type: TransactionType


class TableRow(TypedDict):
    cat: str
    total: Decimal
    pct: float
    color: str
    count: int
