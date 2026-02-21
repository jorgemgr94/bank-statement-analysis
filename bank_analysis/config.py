import re

# Regex for transaction lines: Date (YYYY-MM-DD) Description Amount
# Example: 2026-01-15 HELADOS SULTANA $0.00 $136.00
TRANSACTION_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})\s+(.+?)\s+\$([\d,]+\.\d{2})(?:\s+\$([\d,]+\.\d{2}))?$")

# Regex for MSI (Compras a meses): Date Description ... # de # ... Amount
# Example: 2025-11-24 PAY PAL*LIVERPOOL $ 2,294.15 $ 1,147.07 $ 0.00 3 de 6 $ 382.36
MSI_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})\s+(.+?)\s+\$\s*.*?(\d+\s+de\s+\d+).*?\$([\d,]+\.\d{2})$")

# Regex for payments: Date Description Amount
# Example: 2026-01-21 PAGO POR SPEI 36,130.72
PAYMENT_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})\s+(.+?)\s+([\d,]+\.\d{2})$")

# Categories mapping (keywords -> category)
CATEGORY_KEYWORDS = {
    "7 ELEV": "Conveniencia",
    "ABACUS.AI": "Trabajo",
    "ABARROTES MISION": "Supermercado", 
    "AGUA": "Servicios",
    "AMAZON": "Compras Online",
    "BENAVIDES SUC": "Salud",
    "BOUT YALIN CHEN": "Comida / Delivery",
    "CFE": "Servicios",
    "COM RAP CHINA KING": "Comida / Delivery",
    "DOMINOS P": "Comida / Delivery",
    "DONA TOTA SN": "Comida / Delivery",
    "DREAMLANDPFSA": "Salidas / Recreación",
    "ENVIAFLORES": "Regalos",
    "ESTAC PARCO KIOSKO": "Salidas / Recreación",
    "FARM GUADALAJARA": "Salud",
    "GAS": "Gasolina",
    "GINECO OBSTETRICIA": "Salud",
    "GM SUPERCARNES": "Supermercado",
    "H E B SA DE CV": "Supermercado",
    "HEB": "Supermercado",
    "HELADOS SULTANA": "Comida / Delivery",
    "LIVERPOOL": "Compras Online",
    "MERCADOLIBRE": "Compras Online",
    "NATURAL FRUIT": "Supermercado",
    "NATURGY": "Servicios",
    "NETFLIX": "Suscripciones",
    "OXXO": "Conveniencia",
    "PAY PAL*FEVER": "Recreación",
    "PAYPAL *NATURGYMEXI": "Servicios",
    "PAYPAL *SAMSENLINEA": "Supermercado",
    "PETRO7": "Gasolina",
    "RAPPI": "Comida / Delivery",
    "REST POLLO FEL": "Comida / Delivery",
    "SORIANA": "Supermercado",
    "SPOTIFY": "Suscripciones",
    "STARBUCKS": "Cafe",
    "STR*AMAZONPRIMESUBS": "Suscripciones",
    "SUP CARNES MURILLO": "Supermercado",
    "SUPERCENTER REF HUINA": "Supermercado",
    "TELCEL": "Servicios",
    "TELMEX CARGO RECURR": "Servicios",
    "TLAYUDAS MANON": "Salidas / Recreación",
    "UBER EATS": "Comida / Delivery",
    "UBER PAGOS MEXICO":"Suscripciones",
    "UBER": "Transporte",
    "WAL MART": "Supermercado",
    "WALMART": "Supermercado",
    "YOUTUBE": "Suscripciones",
}
