import pytest
import json
import os
import csv
from src.backend import CafeBackend, StockError

@pytest.fixture
def backend_setup(tmpdir):
    # Setup temporary data directory
    data_dir = tmpdir.mkdir("data")

    menu = {
        "TestItem": {"price": 10, "stock": 5},
        "TestItem2": {"price": 20, "stock": 0}
    }
    users = {
        "admin": {"password": "pass", "role": "admin"},
        "user": {"password": "pass", "role": "cashier"}
    }
    config = {
        "tax_rate": 0.1,
        "service_charge": 5.0,
        "currency": "$",
        "smtp": {
            "server": "smtp.example.com",
            "port": 587,
            "sender_email": "test@example.com",
            "password": "pass"
        }
    }

    menu_file = data_dir.join("menu.json")
    users_file = data_dir.join("users.json")
    config_file = data_dir.join("config.json")

    with open(menu_file, 'w') as f:
        json.dump(menu, f)
    with open(users_file, 'w') as f:
        json.dump(users, f)
    with open(config_file, 'w') as f:
        json.dump(config, f)

    backend = CafeBackend()
    backend.data_dir = str(data_dir)
    backend.menu_file = str(menu_file)
    backend.users_file = str(users_file)
    backend.config_file = str(config_file)
    backend.history_file = str(data_dir.join("sales_history.csv"))
    backend._load_data()

    return backend

def test_login(backend_setup):
    backend = backend_setup
    assert backend.verify_login("admin", "pass") == (True, "admin")
    assert backend.verify_login("user", "pass") == (True, "cashier")
    assert backend.verify_login("user", "wrong") == (False, None)
    assert backend.verify_login("unknown", "pass") == (False, None)

def test_calculate_bill_simple(backend_setup):
    backend = backend_setup
    quantities = {"TestItem": 2}
    bill = backend.calculate_bill(quantities)

    assert bill["items_cost"] == 20
    assert bill["service_charge"] == 5.0
    assert bill["sub_total"] == 25.0
    assert bill["tax"] == 2.5
    assert bill["total_bill"] == 27.5

def test_stock_check(backend_setup):
    backend = backend_setup
    quantities = {"TestItem": 10}
    with pytest.raises(StockError) as excinfo:
        backend.calculate_bill(quantities)
    assert "Insufficient stock" in str(excinfo.value)

    quantities = {"TestItem2": 1}
    with pytest.raises(StockError):
        backend.calculate_bill(quantities)

def test_process_transaction(backend_setup):
    backend = backend_setup
    quantities = {"TestItem": 2}
    receipt = backend.process_transaction(quantities, "user")

    with open(backend.menu_file, 'r') as f:
        menu = json.load(f)
    assert menu["TestItem"]["stock"] == 3

    assert os.path.exists(backend.history_file)
    with open(backend.history_file, 'r') as f:
        content = f.read()
        assert "user" in content
        assert "TestItemx2" in content
        assert "27.50" in content

def test_admin_functions(backend_setup):
    backend = backend_setup
    # Update existing
    backend.update_menu_item("TestItem", 15, 50)
    assert backend.menu["TestItem"]["price"] == 15
    assert backend.menu["TestItem"]["stock"] == 50

    # Add new
    backend.add_menu_item("NewItem", 100, 10)
    assert backend.menu["NewItem"]["price"] == 100
    assert backend.menu["NewItem"]["stock"] == 10
