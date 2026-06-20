import logging
import os
import traceback
from bank_analysis.parser import extract_data
from bank_analysis.reporter import generate_html_report

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

if __name__ == "__main__":
    pdf_file = "input/statement.pdf"
    output_target = "output/output.html"

    if not os.path.exists(pdf_file):
        logging.error("No se encontró el archivo de entrada '%s'", pdf_file)
        exit(1)

    logging.info("Analizando %s...", pdf_file)
    try:
        items = extract_data(pdf_file)
        if not items:
            logging.warning("No se encontraron movimientos.")
        else:
            generate_html_report(items, output_target)
    except Exception as e:
        logging.error("Ocurrió un error inesperado: %s", e)
        traceback.print_exc()
