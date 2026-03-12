import tkinter as tk
from src.gui import LoginApp, MainApp

def main():
    while True:
        # Phase 1: Login
        root = tk.Tk()
        session = {"username": None, "role": None}

        def on_login(username, role):
            session["username"] = username
            session["role"] = role
            root.destroy() # Ends the login mainloop

        login_app = LoginApp(root, on_login)
        root.mainloop()

        # If no user logged in (window closed), exit the loop
        if not session["username"]:
            break

        # Phase 2: Main Application
        new_root = tk.Tk()
        logout_flag = [False]

        def logout():
            logout_flag[0] = True
            new_root.destroy() # Ends the app mainloop

        app = MainApp(new_root, session["username"], session["role"], logout)
        new_root.mainloop()

        # If user closed the app without clicking logout, exit the loop
        if not logout_flag[0]:
            break

if __name__ == "__main__":
    main()
