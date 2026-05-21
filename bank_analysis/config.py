import re

# New Regex for transaction lines: Date1 Date2 Description Amount
# Example: 2026-02-16 2026-02-17 AMAZON +$381.00
# Example: 2026-02-17 2026-02-17 BONIFICACIÓN CON CASHBACK -$102.33
TRANSACTION_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})\s+(\d{4}-\d{2}-\d{2})\s+(.+?)\s+([+-])\$([\d,]+\.\d{2})$")

# New Regex for MSI (Compras a meses): Date Description Original Pending Payment X de Y Interest%
# Example: 2025-11-24 PAY PAL*LIVERPOOL; RFC: OPM150323DI1 $2,294.15 $764.71 $382.36 4 de 6 0.00%
MSI_PATTERN = re.compile(r"^(\d{4}-\d{2}-(?:\d{2})?)\s*(.+?)\s+\$[\d,]+\.\d{2}\s+\$[\d,]+\.\d{2}\s+\$([\d,]+\.\d{2})\s+(\d+\s+de\s+\d+).*?$")

# Regex for Previous Balance
PREVIOUS_BALANCE_PATTERN = re.compile(r"Adeudo del periodo anterior\s*=\s*\$([\d,]+\.\d{2})")

# Note: Payments and refunds in the new layout just appear as regular transactions with a `-` sign (e.g., PAGO POR SPEI -$35,000.00)
# We use the TRANSACTION_PATTERN to capture them and classify them based on the sign and description.
PAYMENT_PATTERN = None  # No longer needed, handled by TRANSACTION_PATTERN

# Categories mapping (keywords -> category)
CATEGORY_KEYWORDS = {
    "7ELEVEN": "Supermercado",
    "ABACUS.AI": "Trabajo",
    "ABARROTES MISION": "Supermercado", 
    "AGUA": "Servicios",
    "AMAZONPRIMESUBS": "Suscripciones",
    "PAGO MI TELMEX": "Servicios",
    "AMAZON": "Compras Online",
    "BENAVIDES SUC": "Salud",
    "PAYPAL *UBRPAGOSMEX": "Transporte",
    "APODACA EVENTOS": "Vacaciones / Entretenimiento",
    "CAFEBRERIA EL PENDULO": "Comida / Delivery",
    "DIDI FOODS": "Comida / Delivery",
    "BOUT YALIN CHEN": "Comida / Delivery",
    "PAGO POR SPEI": "Pagos y Bonificaciones",
    "BONIFICACIÓN CON CASHBACK": "Pagos y Bonificaciones",
    "CINEPOLIS ": "Vacaciones / Entretenimiento",
    "DEL KING ENTERTAINMENT": "Vacaciones / Entretenimiento",
    "CFE": "Servicios",
    "COM RAPCHINA KING": "Comida / Delivery",
    "ELDENTISTADEMISHIJOS": "Salud",
    "DR HUGO HERNANDEZ": "Salud",
    "EST STA TER MONT II": "Vacaciones / Entretenimiento",
    "LANONNA": "Vacaciones / Entretenimiento",
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
    "KFC P": "Comida / Delivery",
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
    "REST": "Comida / Delivery",
    "COPPEL ": "Compras Online",
    "SORIANA": "Supermercado",
    "SPOTIFY": "Suscripciones",
    "STARBUCKS": "Vacaciones / Entretenimiento",
    "SUP CARNES MURILLO": "Supermercado",
    "SUPERCENTER REF HUINA": "Supermercado",
    "TELCEL": "Servicios",
    "TELMEX CARGO RECURR": "Servicios",
    "TLAYUDAS MANON": "Salidas / Recreación",
    "UBER EATS": "Comida / Delivery",
    "UBER PAGOS MEXICO":"Suscripciones",
    "UBER": "Transporte",
    "VIDEOJUEGOS HAPPYLAND": "Vacaciones / Entretenimiento",
    "WAL MART": "Supermercado",
    "WALMART": "Supermercado",
    "YOUTUBE": "Suscripciones",
    "RENTA DE OFNAS": "Vacaciones / Entretenimiento",
    "AIRBNB *": "Vacaciones / Entretenimiento",
    "7 ELEVEN": "Conveniencia",
    "SAMSENLINEA": "Supermercado",
    "BENA330575": "Salud",
    "MERCADO PAGO": "Compras Online",
    "MC DONALD": "Comida / Delivery"
}
