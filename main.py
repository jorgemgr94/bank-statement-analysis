import os
from bank_analysis.parser import extract_data
from bank_analysis.reporter import generate_html_report

if __name__ == "__main__":
    pdf_file = "input/statement.pdf"
    output_target = "output/output.html"

    if not os.path.exists(pdf_file):
        print(f"Error: No se encontró el archivo de entrada '{pdf_file}'")
        exit(1)

    print(f"Analizando {pdf_file}...")
    try:
        items = extract_data(pdf_file)
        if not items:
            print("No se encontraron movimientos.")
        else:
            generate_html_report(items, output_target)
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        import traceback

        traceback.print_exc()
