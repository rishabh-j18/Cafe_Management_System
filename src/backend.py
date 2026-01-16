import json
import csv
import os
from datetime import datetime

class StockError(Exception):
    pass

class CafeBackend:
    def __init__(self):
        self.data_dir = "data"
        self.menu_file = os.path.join(self.data_dir, "menu.json")
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.config_file = os.path.join(self.data_dir, "config.json")
        self.history_file = os.path.join(self.data_dir, "sales_history.csv")

        self._load_data()

    def _load_data(self):
        with open(self.menu_file, 'r') as f:
            self.menu = json.load(f)
        with open(self.users_file, 'r') as f:
            self.users = json.load(f)
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)

    def verify_login(self, username, password):
        if username in self.users and self.users[username] == password:
            return True
        return False

    def get_menu(self):
        return self.menu

    def calculate_bill(self, quantities):
        """
        quantities: dict {item_name: quantity}
        Returns: dict with cost breakdown and bill details
        """
        items_cost = 0
        bill_details = []

        # Check for stock availability first
        missing_stock = []
        for item, qty in quantities.items():
            if qty > 0:
                if item not in self.menu:
                    continue # Should not happen if UI is consistent
                if self.menu[item]["stock"] < qty:
                    missing_stock.append(f"{item} (Available: {self.menu[item]['stock']})")

        if missing_stock:
            raise StockError(f"Insufficient stock for: {', '.join(missing_stock)}")

        # Calculate costs
        for item, qty in quantities.items():
            if qty > 0:
                price = self.menu[item]["price"]
                cost = price * qty
                items_cost += cost
                bill_details.append({
                    "item": item,
                    "qty": qty,
                    "price": price,
                    "cost": cost
                })

        service_charge = self.config["service_charge"]
        sub_total = items_cost + service_charge
        tax = sub_total * self.config["tax_rate"]
        total_bill = sub_total + tax

        return {
            "items_cost": items_cost,
            "service_charge": service_charge,
            "sub_total": sub_total,
            "tax": tax,
            "total_bill": total_bill,
            "details": bill_details
        }

    def process_transaction(self, quantities, cashier_name):
        """
        Finalizes the transaction: deducts stock, updates menu.json, logs sale.
        Returns: formatted receipt string.
        """
        # Recalculate to be safe (or pass the result from calculate_bill)
        bill_data = self.calculate_bill(quantities)

        # Deduct stock
        for item_data in bill_data["details"]:
            item_name = item_data["item"]
            qty = item_data["qty"]
            self.menu[item_name]["stock"] -= qty

        # Save updated menu (stock)
        with open(self.menu_file, 'w') as f:
            json.dump(self.menu, f, indent=4)

        # Log transaction
        self._log_transaction(cashier_name, bill_data)

        return self._generate_receipt(cashier_name, bill_data)

    def _log_transaction(self, cashier_name, bill_data):
        file_exists = os.path.isfile(self.history_file)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        items_summary = "; ".join([f"{d['item']}x{d['qty']}" for d in bill_data["details"]])

        with open(self.history_file, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Cashier", "Items", "Items Cost", "Tax", "Total Bill"])

            writer.writerow([
                timestamp,
                cashier_name,
                items_summary,
                bill_data["items_cost"],
                f"{bill_data['tax']:.2f}",
                f"{bill_data['total_bill']:.2f}"
            ])

    def _generate_receipt(self, cashier_name, bill_data):
        currency = self.config["currency"]
        lines = []
        lines.append("="*40)
        lines.append(f"{'Cafe Management System':^40}")
        lines.append("="*40)
        lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Cashier: {cashier_name}")
        lines.append("-" * 40)
        lines.append(f"{'Item':<20} {'Qty':<5} {'Price':<7} {'Total':<6}")
        lines.append("-" * 40)

        for item in bill_data["details"]:
            lines.append(f"{item['item']:<20} {item['qty']:<5} {currency}{item['price']:<6} {currency}{item['cost']:<6}")

        lines.append("-" * 40)
        lines.append(f"{'Items Cost':<30} {currency}{bill_data['items_cost']:.2f}")
        lines.append(f"{'Service Charge':<30} {currency}{bill_data['service_charge']:.2f}")
        lines.append(f"{'Tax (' + str(int(self.config['tax_rate']*100)) + '%)':<30} {currency}{bill_data['tax']:.2f}")
        lines.append("-" * 40)
        lines.append(f"{'TOTAL BILL':<30} {currency}{bill_data['total_bill']:.2f}")
        lines.append("="*40)
        lines.append(f"{'Thank You':^40}")
        lines.append("="*40)

        return "\n".join(lines)
