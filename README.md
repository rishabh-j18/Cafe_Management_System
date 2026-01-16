# Cafe Management System

A production-ready, Python-based Cafe Management System with a GUI built using Tkinter. This application allows for managing menu items, processing orders, tracking stock, and logging sales history.

## Features

*   **Dynamic Menu**: Menu items and prices are loaded from a JSON configuration file (`data/menu.json`).
*   **Inventory Management**: Automatically tracks stock levels. Prevents sales if items are out of stock.
*   **Authentication**: Secure login system for cashiers/admins.
*   **Sales Logging**: detailed transaction history is saved to a CSV file (`data/sales_history.csv`) for analysis.
*   **Receipt Generation**: Generates and saves text-based receipts.
*   **Responsive UI**: Built with Tkinter using a grid layout for better usability.

## Prerequisites

*   Python 3.x
*   Required Python packages (listed in `requirements.txt`):
    *   `Pillow`
    *   `pandas` (for future data analysis capabilities)
    *   `pytest` (for running tests)

## Installation

1.  Clone the repository.
2.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Run the application:
    ```bash
    python main.py
    ```
2.  **Login**:
    *   **Admin**: Username: `admin`, Password: `admin123`
    *   **Cashier**: Username: `cashier`, Password: `cafe2024`
    *(Credentials can be managed in `data/users.json`)*

3.  **Main Interface**:
    *   **Menu**: Select quantities for items on the left.
    *   **Calculate**: Click to see the bill breakdown (Cost, Service Charge, Tax, Total).
    *   **Print/Pay**: Finalizes the transaction, deducts stock, saves the receipt to `receipts/` folder, and logs the sale.
    *   **History**: Click the "History" button in the header to view past transactions.

## Configuration

*   **Menu & Stock**: Edit `data/menu.json` to change items, prices, and initial stock.
*   **Settings**: Edit `data/config.json` to adjust Tax Rate, Service Charge, and Currency symbol.
*   **Users**: Edit `data/users.json` to add or remove users.

## Data Analysis

Sales data is stored in `data/sales_history.csv`. You can open this file in Excel, Google Sheets, or load it into Python using `pandas` for advanced analysis (revenue trends, popular items, etc.).

## Testing

To run the automated unit tests:
```bash
export PYTHONPATH=$PYTHONPATH:.
pytest tests/
```
