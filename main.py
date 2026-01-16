import tkinter as tk
from src.gui import LoginApp, MainApp

def main():
    root = tk.Tk()

    def logout():
        root.destroy()
        main()

    def on_login(username, role):
        root.destroy()
        new_root = tk.Tk()
        app = MainApp(new_root, username, role, logout)
        new_root.mainloop()

    login_app = LoginApp(root, on_login)
    root.mainloop()

if __name__ == "__main__":
    main()
