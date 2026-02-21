# Bank Statement Analysis

A Python utility to extract, categorize, and report financial transactions from PDF bank statements.

## Features

- **Categorization**: Automatically categorizes expenses (Supermarket, Services, Subscriptions, etc.).
- **Data Extraction**: Parses charges, payments, and Monthly Installments (MSI) from PDF statements.
- **HTML Reporting**: Generates an interactive HTML report with:
  - Summary of total charges, payments, refunds, and MSI.
  - Collapsible category breakdown.
  - "Copy amount" button for easy transfer to spreadsheets/budget apps.

## Setup

1.  **Install Dependencies**: This project uses `uv` for dependency management.
    ```bash
    uv sync
    ```

## Usage

1.  **Place your PDF**:
    Put your bank statement PDF in the `input/` directory and rename it to `statement.pdf`.
    
    ```
    input/statement.pdf
    ```

2.  **Run the script**:
    ```bash
    make run
    # Or directly with uv:
    uv run main.py
    ```

3.  **View Report**:
    Open the generated report in your browser:
    ```
    output/output.html
    ```

## Project Structure

- `input/`: Directory for input PDF files.
- `output/`: Directory where the HTML report is generated.
- `main.py`: Main entry point for the application.
- `bank_analysis/`: Python package containing the core logic (config, parser, reporter).
- `bank_analysis/config.py`: Configuration file for categorization rules and regex patterns.
