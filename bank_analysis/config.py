import re

# New Regex for transaction lines: Date1 Date2 Description Amount
# Example: 2026-02-16 2026-02-17 AMAZON +$381.00
# Example: 2026-02-17 2026-02-17 BONIFICACIÓN CON CASHBACK -$102.33
TRANSACTION_PATTERN = re.compile(
    r"^(\d{4}-\d{2}-\d{2})\s+(\d{4}-\d{2}-\d{2})\s+(.+)\s+([+-])\$([\d,]+\.\d{2})$"
)

# New Regex for MSI (Compras a meses): Date Description Original Pending Payment X de Y Interest%
# Example: 2025-11-24 PAY PAL*LIVERPOOL; RFC: OPM150323DI1 $2,294.15 $764.71 $382.36 4 de 6 0.00%
MSI_PATTERN = re.compile(
    r"^(\d{4}-\d{2}-(?:\d{2})?)\s*(.+)\s+\$[\d,]+\.\d{2}\s+\$[\d,]+\.\d{2}\s+\$([\d,]+\.\d{2})\s+(\d+\s+de\s+\d+).*$"
)

# Regex for Previous Balance
PREVIOUS_BALANCE_PATTERN = re.compile(
    r"Adeudo del periodo anterior\s*=\s*\$([\d,]+\.\d{2})"
)

# Note: Payments and refunds in the new layout just appear as regular transactions with a `-` sign (e.g., PAGO POR SPEI -$35,000.00)
# We use the TRANSACTION_PATTERN to capture them and classify them based on the sign and description.
PAYMENT_PATTERN = None  # No longer needed, handled by TRANSACTION_PATTERN

# Categories mapping (keywords -> category)
CATEGORY_KEYWORDS = {
    "7 ELEVEN": "Conveniencia",
    "ABACUS.AI": "Trabajo",
    "ABARROTES MISION": "Supermercado",
    "BOSTON PIZZA CUMBRES": "Comida / Delivery",
    "CINEPOLIS DULCERIA": "Vacaciones / Entretenimiento",
    "TACOS AL CARBON SANTIA": "Comida / Delivery",
    "AGUA": "Servicios",
    "AIRBNB *": "Vacaciones / Entretenimiento",
    "AMAZON": "Compras Online",
    "AMAZONPRIMESUBS": "Suscripciones",
    "APODACA EVENTOS": "Vacaciones / Entretenimiento",
    "BENA330575": "Salud",
    "BENAVIDES SUC": "Salud",
    "BONIFICACIÓN CON CASHBACK": "Pagos y Bonificaciones",
    "BOUT YALIN CHEN": "Comida / Delivery",
    "CAFEBRERIA EL PENDULO": "Comida / Delivery",
    "CFE": "Servicios",
    "CINEPOLIS ": "Vacaciones / Entretenimiento",
    "COM RAPCHINA KING": "Comida / Delivery",
    "COPPEL ": "Compras Online",
    "DEL KING ENTERTAINMENT": "Vacaciones / Entretenimiento",
    "DIDI FOODS": "Comida / Delivery",
    "DOMINOS P": "Comida / Delivery",
    "DONA TOTA SN": "Comida / Delivery",
    "DR HUGO HERNANDEZ": "Salud",
    "DLO*UBER": "Supermercado",
    "DREAMLANDPFSA": "Salidas / Recreación",
    "ELDENTISTADEMISHIJOS": "Salud",
    "ENVIAFLORES": "Regalos",
    "EST STA TER MONT II": "Vacaciones / Entretenimiento",
    "ESTAC PARCO KIOSKO": "Salidas / Recreación",
    "FARM GUADALAJARA": "Salud",
    "GAS": "Gasolina",
    "GINECO OBSTETRICIA": "Salud",
    "GM SUPERCARNES": "Supermercado",
    "H E B SA DE CV": "Supermercado",
    "HEB": "Supermercado",
    "HELADOS SULTANA": "Comida / Delivery",
    "KFC P": "Comida / Delivery",
    "LANONNA": "Vacaciones / Entretenimiento",
    "LIVERPOOL": "Compras Online",
    "MC DONALD": "Comida / Delivery",
    "MERCADO PAGO": "Compras Online",
    "MERCADOLIBRE": "Compras Online",
    "NATURAL FRUIT": "Supermercado",
    "NATURGY": "Servicios",
    "NETFLIX": "Suscripciones",
    "OXXO": "Conveniencia",
    "PAGO MI TELMEX": "Servicios",
    "PAGO POR SPEI": "Pagos y Bonificaciones",
    "PAY PAL*FEVER": "Recreación",
    "PAYPAL *NATURGYMEXI": "Servicios",
    "PAYPAL *SAMSENLINEA": "Supermercado",
    "PAYPAL *UBRPAGOSMEX": "Transporte",
    "PETRO7": "Gasolina",
    "RAPPI": "Comida / Delivery",
    "RENTA DE OFNAS": "Vacaciones / Entretenimiento",
    "REST POLLO FEL": "Comida / Delivery",
    "REST": "Comida / Delivery",
    "SAMSENLINEA": "Supermercado",
    "SORIANA": "Supermercado",
    "SPOTIFY": "Suscripciones",
    "STARBUCKS": "Vacaciones / Entretenimiento",
    "SUP CARNES MURILLO": "Supermercado",
    "SUPERCENTER REF HUINA": "Supermercado",
    "TELCEL": "Servicios",
    "TELMEX CARGO RECURR": "Servicios",
    "TLAYUDAS MANON": "Salidas / Recreación",
    "UBER EATS": "Comida / Delivery",
    "UBER PAGOS MEXICO": "Suscripciones",
    "UBER": "Transporte",
    "VIDEOJUEGOS HAPPYLAND": "Vacaciones / Entretenimiento",
    "WAL MART": "Supermercado",
    "WALMART": "Supermercado",
    "YOUTUBE": "Suscripciones",
}
