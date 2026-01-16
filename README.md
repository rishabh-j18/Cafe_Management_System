# Cafe Management System

A production-ready, Python-based Cafe Management System with a GUI built using Tkinter. This application allows for managing menu items, processing orders, tracking stock, and logging sales history.

## Features

*   **Role-Based Access Control**:
    *   **Admin**: Can manage menu items (add/edit prices & stock), view history, and process sales.
    *   **Cashier**: Restricted to processing sales and viewing history.
*   **Dynamic Menu**: Menu items and prices are loaded from a JSON configuration file (`data/menu.json`).
*   **Inventory Management**: Automatically tracks stock levels. Prevents sales if items are out of stock. Admin can replenish stock via the UI.
*   **Sales Logging**: Detailed transaction history is saved to a CSV file (`data/sales_history.csv`) for analysis.
*   **Receipt Generation**:
    *   Generates and saves text-based receipts to `receipts/` folder.
    *   **Email Receipt**: Option to email the receipt to the customer (requires SMTP config).
*   **Responsive UI**: Built with Tkinter using a grid layout, maximized window support, and intuitive design.

## Prerequisites

*   Python 3.x
*   Required Python packages (listed in `requirements.txt`):
    *   `Pillow`
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
    *(Users and roles can be managed in `data/users.json`)*

3.  **Main Interface**:
    *   **Menu**: Select quantities for items on the left.
    *   **Calculate**: Click to see the bill breakdown.
    *   **Print/Pay**: Finalizes the transaction, deducts stock, saves the receipt, and logs the sale.
    *   **Email Receipt**: Click to send the receipt via email (configure SMTP in `data/config.json`).
    *   **History**: View past transactions.
    *   **Edit Menu (Admin Only)**: Update prices, add stock, or create new items.
    *   **Logout**: Return to the login screen.

## Configuration

*   **Menu**: Edit `data/menu.json` or use the Admin UI.
*   **Users**: Edit `data/users.json` to add users. Format:
    ```json
    "username": { "password": "password", "role": "admin" }
    ```
*   **Settings**: Edit `data/config.json` to adjust Tax Rate, Service Charge, Currency, and SMTP settings.
    *   **SMTP Example**:
        ```json
        "smtp": {
            "server": "smtp.gmail.com",
            "port": 587,
            "sender_email": "your-email@gmail.com",
            "password": "your-app-password"
        }
        ```

## Testing

To run the automated unit tests:
```bash
export PYTHONPATH=$PYTHONPATH:.
pytest tests/
```
