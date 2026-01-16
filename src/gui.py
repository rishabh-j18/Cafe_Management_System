import tkinter as tk
from tkinter import messagebox, ttk, Toplevel, Text, Scrollbar, END, simpledialog
from PIL import ImageTk, Image
from datetime import datetime
import os
import csv
from src.backend import CafeBackend, StockError

class LoginApp:
    def __init__(self, root, on_login_success):
        self.root = root
        self.root.title("Cafe Login")
        self.root.geometry("300x200")
        self.root.resizable(False, False)
        self.on_login_success = on_login_success
        self.backend = CafeBackend()

        tk.Label(root, text="Username").pack(pady=5)
        self.user_entry = tk.Entry(root)
        self.user_entry.pack(pady=5)

        tk.Label(root, text="Password").pack(pady=5)
        self.pass_entry = tk.Entry(root, show="*")
        self.pass_entry.pack(pady=5)

        tk.Button(root, text="Login", command=self.login).pack(pady=20)
        self.root.bind('<Return>', lambda event: self.login())

    def login(self):
        user = self.user_entry.get()
        password = self.pass_entry.get()
        success, role = self.backend.verify_login(user, password)
        if success:
            self.on_login_success(user, role)
        else:
            messagebox.showerror("Error", "Invalid Credentials")

class MainApp:
    def __init__(self, root, username, role, logout_callback):
        self.root = root
        self.username = username
        self.role = role
        self.logout_callback = logout_callback
        self.backend = CafeBackend()
        self.menu_data = self.backend.get_menu()
        self.menu_vars = {} # Stores IntVars for quantities

        self.root.title(f"Cafe Management System - {self.username} ({self.role})")

        # Maximize window based on platform
        try:
            self.root.state('zoomed')
        except:
            self.root.attributes('-zoomed', True)

        self.root['bg'] = "white"

        self.setup_ui()

    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#0C9608")
        header_frame.pack(fill=tk.X)

        # Try loading logo
        try:
            if os.path.exists("cafe.png"):
                img = Image.open("cafe.png").resize((50, 50), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)
                tk.Label(header_frame, image=self.logo_img, bg="#0C9608").pack(side=tk.LEFT, padx=10, pady=5)
        except Exception as e:
            print(f"Error loading image: {e}")

        tk.Label(header_frame, text="Cafe Management System", font=('verdana', 20, 'bold'), fg="white", bg="#0C9608").pack(side=tk.LEFT, padx=10)

        # Right Header Buttons
        tk.Button(header_frame, text="Logout", command=self.logout_callback, bg="red", fg="white").pack(side=tk.RIGHT, padx=10)
        tk.Button(header_frame, text="History", command=self.view_history, bg="white", fg="#0C9608").pack(side=tk.RIGHT, padx=10)

        if self.role == "admin":
             tk.Button(header_frame, text="Edit Menu", command=self.edit_menu_popup, bg="blue", fg="white").pack(side=tk.RIGHT, padx=10)

        tk.Label(header_frame, text=f"{self.username} ({self.role})", font=('verdana', 10), fg="white", bg="#0C9608").pack(side=tk.RIGHT, padx=10)

        # Main Content Area
        content_frame = tk.Frame(self.root, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Menu Section (Left)
        menu_frame = tk.LabelFrame(content_frame, text="Menu", font=('verdana', 12, 'bold'), bg="white", fg="#0C9608")
        menu_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Scrollable Menu
        canvas = tk.Canvas(menu_frame, bg="white")
        scrollbar = tk.Scrollbar(menu_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="white")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.create_menu_items()

        # Bill Section (Right)
        bill_frame = tk.Frame(content_frame, bg="white")
        bill_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # Costs Display
        cost_frame = tk.LabelFrame(bill_frame, text="Bill Summary", font=('verdana', 12, 'bold'), bg="white", fg="#0C9608")
        cost_frame.pack(fill=tk.X, pady=5)

        self.vars = {
            "Items Cost": tk.StringVar(),
            "Service Charge": tk.StringVar(),
            "Tax": tk.StringVar(),
            "Total": tk.StringVar()
        }

        r = 0
        for label, var in self.vars.items():
            tk.Label(cost_frame, text=label, font=('verdana', 10, 'bold'), bg="white").grid(row=r, column=0, sticky="w", padx=10, pady=5)
            tk.Entry(cost_frame, textvariable=var, state="readonly", font=('verdana', 10)).grid(row=r, column=1, padx=10, pady=5)
            r += 1

        # Buttons
        btn_frame = tk.Frame(bill_frame, bg="white")
        btn_frame.pack(fill=tk.X, pady=20)

        tk.Button(btn_frame, text="Calculate", command=self.calculate, bg="#c9a511", fg="white", font=('verdana', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Print/Pay", command=self.print_receipt, bg="#0C9608", fg="white", font=('verdana', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Email Receipt", command=self.email_receipt, bg="orange", fg="white", font=('verdana', 10, 'bold'), width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Clear", command=self.clear, bg="red", fg="white", font=('verdana', 10, 'bold'), width=10).pack(side=tk.LEFT, padx=5)

        # Receipt Preview
        tk.Label(bill_frame, text="Receipt Preview", font=('verdana', 10, 'bold'), bg="white").pack(anchor="w")
        self.receipt_area = Text(bill_frame, height=15, width=40)
        self.receipt_area.pack(fill=tk.BOTH, expand=True)

    def create_menu_items(self):
        row = 0
        tk.Label(self.scrollable_frame, text="Item", font=('verdana', 10, 'bold'), bg="white").grid(row=row, column=0, padx=5, pady=5, sticky="w")
        tk.Label(self.scrollable_frame, text="Price", font=('verdana', 10, 'bold'), bg="white").grid(row=row, column=1, padx=5, pady=5)
        tk.Label(self.scrollable_frame, text="Stock", font=('verdana', 10, 'bold'), bg="white").grid(row=row, column=2, padx=5, pady=5)
        tk.Label(self.scrollable_frame, text="Qty", font=('verdana', 10, 'bold'), bg="white").grid(row=row, column=3, padx=5, pady=5)
        row += 1

        currency = self.backend.config["currency"]

        for item, details in self.menu_data.items():
            tk.Label(self.scrollable_frame, text=item, font=('verdana', 10), bg="white").grid(row=row, column=0, padx=5, pady=2, sticky="w")
            tk.Label(self.scrollable_frame, text=f"{currency}{details['price']}", font=('verdana', 10), bg="white").grid(row=row, column=1, padx=5, pady=2)

            stock_lbl = tk.Label(self.scrollable_frame, text=str(details['stock']), font=('verdana', 10), bg="white")
            if details['stock'] == 0:
                stock_lbl.config(fg="red", text="Out")
            stock_lbl.grid(row=row, column=2, padx=5, pady=2)

            var = tk.StringVar(value="0")
            entry = tk.Entry(self.scrollable_frame, textvariable=var, width=5)
            entry.grid(row=row, column=3, padx=5, pady=2)

            self.menu_vars[item] = var
            row += 1

    def get_quantities(self):
        quantities = {}
        for item, var in self.menu_vars.items():
            try:
                val = var.get().strip()
                if not val:
                    qty = 0
                else:
                    qty = int(val)
                if qty < 0:
                    raise ValueError
                quantities[item] = qty
            except ValueError:
                messagebox.showerror("Error", f"Invalid quantity for {item}")
                return None
        return quantities

    def calculate(self):
        quantities = self.get_quantities()
        if quantities is None:
            return None

        try:
            bill_data = self.backend.calculate_bill(quantities)
            currency = self.backend.config["currency"]

            self.vars["Items Cost"].set(f"{currency}{bill_data['items_cost']:.2f}")
            self.vars["Service Charge"].set(f"{currency}{bill_data['service_charge']:.2f}")
            self.vars["Tax"].set(f"{currency}{bill_data['tax']:.2f}")
            self.vars["Total"].set(f"{currency}{bill_data['total_bill']:.2f}")

            # Preview receipt text without saving
            receipt_text = self.backend._generate_receipt(self.username, bill_data)
            self.receipt_area.delete(1.0, END)
            self.receipt_area.insert(END, receipt_text)

            return quantities

        except StockError as e:
            messagebox.showerror("Stock Error", str(e))
            return None

    def print_receipt(self):
        quantities = self.calculate() # Re-validate and re-calculate
        if quantities is None:
            return

        # Check if total is 0
        total = float(self.vars["Total"].get().replace(self.backend.config["currency"], ""))
        if total <= 0:
            messagebox.showwarning("Warning", "No items selected.")
            return

        if messagebox.askyesno("Confirm", "Process transaction and print receipt?"):
            try:
                receipt = self.backend.process_transaction(quantities, self.username)

                # Save to file
                if not os.path.exists("receipts"):
                    os.makedirs("receipts")
                filename = f"receipts/receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(filename, "w") as f:
                    f.write(receipt)

                messagebox.showinfo("Success", f"Transaction saved.\nReceipt saved to {filename}")
                self.clear()
                self.refresh_menu_stock() # Refresh stock display

            except Exception as e:
                messagebox.showerror("Error", f"Failed to process transaction: {e}")

    def email_receipt(self):
        # We need the receipt text first.
        # This implies we must calculate first.
        receipt_text = self.receipt_area.get(1.0, END).strip()
        if not receipt_text:
             messagebox.showwarning("Warning", "Calculate bill first to generate receipt.")
             return

        recipient = simpledialog.askstring("Email Receipt", "Enter Recipient Email:")
        if recipient:
            try:
                self.backend.send_receipt_email(recipient, receipt_text)
                messagebox.showinfo("Success", "Email sent successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def edit_menu_popup(self):
        popup = Toplevel(self.root)
        popup.title("Edit Menu (Admin)")
        popup.geometry("400x500")

        canvas = tk.Canvas(popup)
        scrollbar = tk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(scroll_frame, text="Item Name").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(scroll_frame, text="Price").grid(row=0, column=1, padx=5, pady=5)
        tk.Label(scroll_frame, text="Stock").grid(row=0, column=2, padx=5, pady=5)

        row = 1
        entries = {}
        for item, details in self.menu_data.items():
            tk.Label(scroll_frame, text=item).grid(row=row, column=0, padx=5, pady=2)

            p_var = tk.StringVar(value=str(details['price']))
            p_entry = tk.Entry(scroll_frame, textvariable=p_var, width=8)
            p_entry.grid(row=row, column=1, padx=5, pady=2)

            s_var = tk.StringVar(value=str(details['stock']))
            s_entry = tk.Entry(scroll_frame, textvariable=s_var, width=8)
            s_entry.grid(row=row, column=2, padx=5, pady=2)

            entries[item] = (p_var, s_var)
            row += 1

        # Add New Item Section
        tk.Label(scroll_frame, text="Add New:", font=('bold')).grid(row=row, column=0, pady=10)
        row += 1
        new_name = tk.Entry(scroll_frame, width=15)
        new_name.grid(row=row, column=0, padx=5)
        new_price = tk.Entry(scroll_frame, width=8)
        new_price.grid(row=row, column=1, padx=5)
        new_stock = tk.Entry(scroll_frame, width=8)
        new_stock.grid(row=row, column=2, padx=5)

        def save_changes():
            # Update existing
            for item, (p_var, s_var) in entries.items():
                try:
                    p = int(p_var.get())
                    s = int(s_var.get())
                    self.backend.update_menu_item(item, p, s)
                except ValueError:
                    pass # Ignore invalid inputs

            # Add new
            name = new_name.get().strip()
            if name:
                try:
                    p = int(new_price.get())
                    s = int(new_stock.get())
                    self.backend.add_menu_item(name, p, s)
                except ValueError:
                    messagebox.showwarning("Error", "Invalid data for new item")

            messagebox.showinfo("Success", "Menu updated!")
            self.refresh_menu_stock()
            popup.destroy()

        tk.Button(popup, text="Save Changes", command=save_changes, bg="green", fg="white").pack(pady=10)


    def clear(self):
        for var in self.menu_vars.values():
            var.set("0")
        for var in self.vars.values():
            var.set("")
        self.receipt_area.delete(1.0, END)

    def refresh_menu_stock(self):
        # Reload menu from backend and refresh the frame
        self.menu_data = self.backend.get_menu()
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.create_menu_items()

    def view_history(self):
        history_win = Toplevel(self.root)
        history_win.title("Sales History")
        history_win.geometry("600x400")

        text_area = Text(history_win)
        text_area.pack(fill=tk.BOTH, expand=True)

        try:
            if os.path.exists(self.backend.history_file):
                with open(self.backend.history_file, "r") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        text_area.insert(END, " | ".join(row) + "\n")
            else:
                text_area.insert(END, "No history available.")
        except Exception as e:
             text_area.insert(END, f"Error reading history: {e}")
