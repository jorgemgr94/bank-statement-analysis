from bank_analysis.parser import extract_data
from bank_analysis.reporter import generate_html_report

if __name__ == "__main__":
    pdf_file = "input/statement.pdf"
    output_target = "output/output.html"
    
    print(f"Analizando {pdf_file}...")
    try:
        items = extract_data(pdf_file)
        if not items:
            print("No se encontraron movimientos.")
        else:
            generate_html_report(items, output_target)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{pdf_file}'")
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        import traceback
        traceback.print_exc()
