# ==========================================================
# LIBRARYSYS
# Limkokwing Library Management System
# PROG103 Final Project
#
# Entry point: run this file to start the application.
#   python3 main.py
#
# This file deliberately contains no business logic or page code -
# it only loads saved data and opens the login window. See the
# app/ package for everything else:
#   app/config.py       - constants, lists, roles
#   app/data_store.py   - in-memory data + save/load to data.json
#   app/logic.py        - all backend business logic
#   app/gui/login_window.py - login screen
#   app/gui/main_app.py     - application shell (header/sidebar/routing)
#   app/gui/pages.py        - all page content
# ==========================================================
import tkinter as tk

from app.data_store import load_data
from app.gui.login_window import LoginWindow


def main():
    load_data()
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
