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

# Pattern to strip trailing suffixes from descriptions (RFC, REF, etc.)
# Examples: "; RFC: OPM150323DI1", "; REF: 123456789", ";REF:FOO"
DESCRIPTION_CLEANUP_PATTERN = re.compile(r"\s*;\s*(?:RFC|REF)\s*:\s*\S+")

# Pattern to strip trailing reference annotations like " *1234" or " *REF123"
TRAILING_REF_PATTERN = re.compile(r"\s+\*\S+$")

# Note: Payments and refunds in the new layout just appear as regular transactions with a `-` sign (e.g., PAGO POR SPEI -$35,000.00)
# We use the TRANSACTION_PATTERN to capture them and classify them based on the sign and description.
PAYMENT_PATTERN = None  # No longer needed, handled by TRANSACTION_PATTERN

# Categories mapping (keywords -> category)
CATEGORY_KEYWORDS = {
    "29505F1 GAL V ORIENTE": "Vacaciones / Entretenimiento",
    "7 ELEVEN": "Supermercado",
    "7ELEVEN": "Supermercado",
    "ABACUS.AI": "Trabajo",
    "ABARROTES MISION": "Supermercado",
    "BOSTON PIZZA CUMBRES": "Comida / Delivery",
    "CINEPOLIS DULCERIA": "Vacaciones / Entretenimiento",
    "TACOS AL CARBON SANTIA": "Comida / Delivery",
    "AGUA": "Servicios",
    "AIRBNB *": "Vacaciones / Entretenimiento",
    "ARENA MONTERREY": "Vacaciones / Entretenimiento",
    "AMAZON": "Compras Online",
    "AMAZONPRIMESUBS": "Suscripciones",
    "ANGEL COLOR": "Escuela",
    "APODACA EVENTOS": "Vacaciones / Entretenimiento",
    "BENA330575": "Salud",
    "BENAVI 330603 CITADEL": "Salud",
    "BENAVIDES SUC": "Salud",
    "BODEGA SAN MIGUEL": "Supermercado",
    "BONIFICACIÓN CON CASHBACK": "Pagos y Bonificaciones",
    "BOUT YALIN CHEN": "Comida / Delivery",
    "CAFET GABY S HIDAL": "Comida / Delivery",
    "CAFEBRERIA EL PENDULO": "Comida / Delivery",
    "CANELI SA DE CV": "Comida / Delivery",
    "CARNES JA CARLOS": "Supermercado",
    "CFE": "Servicios",
    "CINEPOLIS ": "Vacaciones / Entretenimiento",
    "COM RAP P LOCO SUC PLA": "Comida / Delivery",
    "COM RAPCHINA KING": "Comida / Delivery",
    "COMERC ALIMENTOS GOOL": "Comida / Delivery",
    "CONEKTA*URBANI": "Transporte",
    "COPPEL ": "Compras Online",
    "COSTCO MTY SENDERO": "Supermercado",
    "COSTCO": "Supermercado",
    "CREM YOGUFRUT 14": "Comida / Delivery",
    "DEL KING ENTERTAINMENT": "Vacaciones / Entretenimiento",
    "DIDI FOODS": "Comida / Delivery",
    "DEL SOL 1112 MP": "Escuela",
    "DEL SOL 1188 MP": "Escuela",
    "DOMINOS P": "Comida / Delivery",
    "DONA TOTA SN": "Comida / Delivery",
    "DR HUGO HERNANDEZ": "Salud",
    "DLO*UBER": "Supermercado",
    "DREAMLANDPFSA": "Vacaciones / Entretenimiento",
    "ELDENTISTADEMISHIJOS": "Salud",
    "ENVIAFLORES": "Regalos",
    "EST STA TER MONT II": "Vacaciones / Entretenimiento",
    "ESTAC PARCO KIOSKO": "Vacaciones / Entretenimiento",
    "FARM GUADALAJARA": "Salud",
    "FENGFA COMIDA CANTONES": "Comida / Delivery",
    "FRUTERIA EL MAGA": "Supermercado",
    "GALERIAS VALLE ORIENTE": "Vacaciones / Entretenimiento",
    "GAS": "Gasolina",
    "GINECO OBSTETRICIA": "Salud",
    "GM SUPERCARNES": "Supermercado",
    "H E B SA DE CV": "Supermercado",
    "HEB": "Supermercado",
    "HELADOS SULTANA": "Comida / Delivery",
    "HM MX": "Ropa / Moda",
    "HOME DEPOT M ALEMAN": "Hogar / Mantenimiento",
    "HOTEL NOVOTEL": "Vacaciones / Entretenimiento",
    "HOTEL R NOVOTEL": "Vacaciones / Entretenimiento",
    "IVA INTERES": "Comisiones / Intereses",
    "KFC P": "Comida / Delivery",
    "KK PASEO DE LA FE": "Comida / Delivery",
    "LANONNA": "Vacaciones / Entretenimiento",
    "LEFTIES": "Ropa / Moda",
    "LIVERPOOL": "Compras Online",
    "MC DONALD": "Comida / Delivery",
    "MERCADO PAGO": "Compras Online",
    "MERCADOLIBRE": "Compras Online",
    "MERPAGO*AWARENAMOVIL": "Compras Online",
    "MERPAGO*ELBDT": "Compras Online",
    "MERPAGO*RENTAMOVISTAR": "Servicios",
    "MINISO GALERIAS VALLE": "Ropa / Moda",
    "NATURAL FRUIT": "Supermercado",
    "NATURGY": "Servicios",
    "NETFLIX": "Suscripciones",
    "OPENPAY*KIGO PARKIMOVI": "Transporte",
    "OPLINEA*BENDITOCAFELUZ": "Comida / Delivery",
    "OXXO": "Supermercado",
    "PAGO MI TELMEX": "Servicios",
    "PAGO POR SPEI": "Pagos y Bonificaciones",
    "PANADERIA LEO 1": "Comida / Delivery",
    "PAY PAL*FEVER": "Recreación",
    "PAY PAL*KIGO": "Transporte",
    "PAYPAL *EPIC GAMES": "Vacaciones / Entretenimiento",
    "PAYPAL*BODAURRERA": "Supermercado",
    "PAYPAL*KIGO": "Transporte",
    "PAYPAL*MICROSOFT": "Compras Online",
    "PAYPAL *NATURGYMEXI": "Servicios",
    "PAYPAL *SAMSENLINEA": "Supermercado",
    "PAYPAL *UBRPAGOSMEX": "Transporte",
    "PAYPAL": "Otros",
    "PEKITAS ESTET INFANTIL": "Escuela",
    "PETRO7": "Gasolina",
    "RAPPI": "Comida / Delivery",
    "RENTA DE OFNAS": "Vacaciones / Entretenimiento",
    "REST POLLO FEL": "Comida / Delivery",
    "REST": "Comida / Delivery",
    "ROCK&BILLY CITADEL": "Comida / Delivery",
    "SAMSENLINEA": "Supermercado",
    "SORIANA": "Supermercado",
    "SPOTIFY": "Suscripciones",
    "STARBUCKS": "Vacaciones / Entretenimiento",
    "SUP CARNES MURILLO": "Supermercado",
    "SUPERCENTER REF HUINA": "Supermercado",
    "SULTANES BEBIDAS MU": "Vacaciones / Entretenimiento",
    "TELCEL": "Servicios",
    "TELEFONICAPFACTAPPMU": "Servicios",
    "TELMEX CARGO RECURR": "Servicios",
    "TH FUNDIDORA": "Comida / Delivery",
    "TIEND INT SUC MATRIZ": "Escuela",
    "TLAYUDAS MANON": "Vacaciones / Entretenimiento",
    "TODOMODA": "Ropa / Moda",
    "UBR FLEX MEXICO": "Transporte",
    "UBER EATS": "Comida / Delivery",
    "UBER PAGOS MEXICO": "Suscripciones",
    "UBER": "Transporte",
    "VIDEOJUEGOS HAPPYLAND": "Vacaciones / Entretenimiento",
    "WAL MART": "Supermercado",
    "WALMART": "Supermercado",
    "YOUTUBE": "Suscripciones",
    "ZUMA ABTS MERCO LIN VI": "Supermercado",
    "ZUMA*EPIK LINDA VISTA": "Vacaciones / Entretenimiento",
    "PINPEO*RAA FESTIVALES": "Vacaciones / Entretenimiento",
}
