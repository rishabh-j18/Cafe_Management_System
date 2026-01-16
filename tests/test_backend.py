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
    users = {"user": "pass"}
    config = {"tax_rate": 0.1, "service_charge": 5.0, "currency": "$"}

    menu_file = data_dir.join("menu.json")
    users_file = data_dir.join("users.json")
    config_file = data_dir.join("config.json")

    with open(menu_file, 'w') as f:
        json.dump(menu, f)
    with open(users_file, 'w') as f:
        json.dump(users, f)
    with open(config_file, 'w') as f:
        json.dump(config, f)

    # Monkeypatch the data_dir in CafeBackend class or instance
    # Since CafeBackend hardcodes "data", we need to override it.
    # We will subclass for testing or mock os.path.join, but simplest is to change the instance var

    backend = CafeBackend()
    backend.data_dir = str(data_dir)
    backend.menu_file = str(menu_file)
    backend.users_file = str(users_file)
    backend.config_file = str(config_file)
    backend.history_file = str(data_dir.join("sales_history.csv"))
    backend._load_data() # Reload with new files

    return backend

def test_login(backend_setup):
    backend = backend_setup
    assert backend.verify_login("user", "pass") == True
    assert backend.verify_login("user", "wrong") == False
    assert backend.verify_login("unknown", "pass") == False

def test_calculate_bill_simple(backend_setup):
    backend = backend_setup
    quantities = {"TestItem": 2}
    bill = backend.calculate_bill(quantities)

    assert bill["items_cost"] == 20 # 2 * 10
    assert bill["service_charge"] == 5.0
    assert bill["sub_total"] == 25.0
    assert bill["tax"] == 2.5 # 10% of 25
    assert bill["total_bill"] == 27.5

def test_stock_check(backend_setup):
    backend = backend_setup
    # Request more than stock
    quantities = {"TestItem": 10}
    with pytest.raises(StockError) as excinfo:
        backend.calculate_bill(quantities)
    assert "Insufficient stock" in str(excinfo.value)

    # Request item with 0 stock
    quantities = {"TestItem2": 1}
    with pytest.raises(StockError):
        backend.calculate_bill(quantities)

def test_process_transaction(backend_setup):
    backend = backend_setup
    quantities = {"TestItem": 2}
    receipt = backend.process_transaction(quantities, "user")

    # Check if stock reduced
    with open(backend.menu_file, 'r') as f:
        menu = json.load(f)
    assert menu["TestItem"]["stock"] == 3 # 5 - 2

    # Check if logged
    assert os.path.exists(backend.history_file)
    with open(backend.history_file, 'r') as f:
        content = f.read()
        assert "user" in content
        assert "TestItemx2" in content
        assert "27.50" in content
