# ==========================================================
# LOGIN WINDOW
# ==========================================================
import tkinter as tk
from tkinter import messagebox

from app.config import PRIMARY_COLOR, ACCENT_COLOR
from app.data_store import USER_ACCOUNTS


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("LibrarySys Login")
        self.root.geometry("1000x600")
        self.root.configure(bg=PRIMARY_COLOR)
        self.root.resizable(False, False)

        # LEFT PANEL
        left_panel = tk.Frame(root, bg=PRIMARY_COLOR, width=500)
        left_panel.pack(side="left", fill="both")
        left_panel.pack_propagate(False)
        tk.Label(
            left_panel, text="\U0001F4DA", font=("Segoe UI", 80),
            bg=PRIMARY_COLOR, fg="white"
        ).pack(pady=(70, 10))
        tk.Label(
            left_panel, text="LIBRARYSYS", font=("Segoe UI", 28, "bold"),
            bg=PRIMARY_COLOR, fg="white"
        ).pack()
        tk.Label(
            left_panel, text="LIMKOKWING LIBRARY\nMANAGEMENT SYSTEM",
            font=("Segoe UI", 15), bg=PRIMARY_COLOR, fg=ACCENT_COLOR, justify="center"
        ).pack(pady=20)
        tk.Label(
            left_panel, text="PROG103 FINAL PROJECT", font=("Segoe UI", 12, "bold"),
            bg=PRIMARY_COLOR, fg="white"
        ).pack(pady=5)
        tk.Label(
            left_panel, text="Faculty of ICT\nLimkokwing University",
            font=("Segoe UI", 11), bg=PRIMARY_COLOR, fg="white", justify="center"
        ).pack()
        tk.Label(
            left_panel, text="Supporting SDG 4:\nQuality Education",
            font=("Segoe UI", 11), bg=PRIMARY_COLOR, fg="#AED6F1", justify="center"
        ).pack(pady=40)

        # RIGHT PANEL
        right_panel = tk.Frame(root, bg="white")
        right_panel.pack(side="right", fill="both", expand=True)
        login_frame = tk.Frame(right_panel, bg="white")
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            login_frame, text="LOGIN", font=("Segoe UI", 26, "bold"),
            bg="white", fg=PRIMARY_COLOR
        ).grid(row=0, column=0, columnspan=2, pady=20)

        tk.Label(
            login_frame, text="Username", font=("Segoe UI", 11), bg="white"
        ).grid(row=1, column=0, sticky="w", pady=10)
        self.username_entry = tk.Entry(login_frame, width=30, font=("Segoe UI", 12))
        self.username_entry.grid(row=2, column=0, pady=5)

        tk.Label(
            login_frame, text="Password", font=("Segoe UI", 11), bg="white"
        ).grid(row=3, column=0, sticky="w", pady=10)
        self.password_entry = tk.Entry(
            login_frame, width=30, show="*", font=("Segoe UI", 12)
        )
        self.password_entry.grid(row=4, column=0, pady=5)
        self.password_entry.bind("<Return>", lambda event: self.login())

        self.login_button = tk.Button(
            login_frame, text="LOGIN", width=25, bg=PRIMARY_COLOR, fg="white",
            font=("Segoe UI", 11, "bold"), cursor="hand2", command=self.login
        )
        self.login_button.grid(row=5, column=0, pady=25)

        # Demo Account Info
        info_frame = tk.LabelFrame(
            right_panel, text="Demo Accounts", bg="white", fg=PRIMARY_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        info_frame.place(relx=0.5, rely=0.85, anchor="center")
        tk.Label(
            info_frame, text="Admin : admin / admin123  (full access)",
            bg="white", font=("Segoe UI", 9)
        ).pack(anchor="w", padx=10)
        tk.Label(
            info_frame, text="Librarian : librarian / lib2026  (catalog & loans)",
            bg="white", font=("Segoe UI", 9)
        ).pack(anchor="w", padx=10)
        tk.Label(
            info_frame, text="Student : student / student123  (catalog + own history)",
            bg="white", font=("Segoe UI", 9)
        ).pack(anchor="w", padx=10)

    # ==========================================================
    # LOGIN FUNCTION
    # ==========================================================
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if username == "" or password == "":
            messagebox.showerror(
                "Login Failed", "Please enter both a username and a password."
            )
            return

        if username not in USER_ACCOUNTS:
            messagebox.showerror(
                "Login Failed", "Wrong username or password. Please try again."
            )
            return

        if USER_ACCOUNTS[username]["password"] != password:
            messagebox.showerror(
                "Login Failed", "Wrong username or password. Please try again."
            )
            return

        role = USER_ACCOUNTS[username]["role"]
        full_name = USER_ACCOUNTS[username].get("full_name", username)
        messagebox.showinfo("Login Successful", f"Welcome {full_name}\nRole: {role}")
        self.root.destroy()

        # Imported here (not at module top) to avoid a circular import
        # between login_window.py and main_app.py.
        from app.gui.main_app import LibrarySysApp
        dashboard_root = tk.Tk()
        LibrarySysApp(dashboard_root, username, role, full_name)
        dashboard_root.mainloop()
