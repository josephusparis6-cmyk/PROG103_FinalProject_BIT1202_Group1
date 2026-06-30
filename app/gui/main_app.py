# ==========================================================
# MAIN APPLICATION SHELL
# Builds the header, sidebar, and routes between pages. The actual
# page content (build_*_page methods) lives in pages.py and is
# mixed into this class so the file doesn't become one giant blob.
# ==========================================================
import tkinter as tk
from tkinter import messagebox

from app.config import (
    APP_TITLE, WINDOW_BG, PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR,
    ROLE_PERMISSIONS, ROLE_BADGE_COLOR, NAV_PAGES
)
from app.gui.pages import PagesMixin


class LibrarySysApp(PagesMixin):
    def __init__(self, root, username, role, full_name):
        self.root = root
        self.username = username
        self.role = role
        self.full_name = full_name
        self.root.title(APP_TITLE)
        try:
            self.root.state("zoomed")
        except tk.TclError:
            self.root.geometry("1300x800")
        self.root.configure(bg=WINDOW_BG)
        self.build_header()
        self.body_frame = tk.Frame(self.root, bg=WINDOW_BG)
        self.body_frame.pack(fill="both", expand=True)
        self.build_sidebar()
        self.build_main_area()
        self.update_clock()

    # ==========================================================
    # ACCESS CONTROL HELPERS
    # ==========================================================
    def has_access(self, page_key):
        return page_key in ROLE_PERMISSIONS.get(self.role, set())

    def access_denied(self):
        messagebox.showerror(
            "Access Denied",
            "Your account role does not have permission to view this page."
        )

    # ==========================================================
    # HEADER
    # ==========================================================
    def build_header(self):
        from datetime import datetime
        self.header = tk.Frame(self.root, bg=PRIMARY_COLOR, height=80)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)
        tk.Label(
            self.header, text="\U0001F4DA LIBRARYSYS", font=("Segoe UI", 22, "bold"),
            bg=PRIMARY_COLOR, fg="white"
        ).pack(side="left", padx=20)
        self.clock_label = tk.Label(
            self.header, text="", font=("Segoe UI", 11), bg=PRIMARY_COLOR, fg="white"
        )
        self.clock_label.pack(side="right", padx=20)
        self.user_label = tk.Label(
            self.header, text=f"{self.full_name} ({self.role})",
            font=("Segoe UI", 11, "bold"), bg=PRIMARY_COLOR,
            fg=ROLE_BADGE_COLOR.get(self.role, ACCENT_COLOR)
        )
        self.user_label.pack(side="right", padx=20)

    # ==========================================================
    # SIDEBAR (only shows the pages this role is allowed to open)
    # ==========================================================
    def build_sidebar(self):
        self.sidebar = tk.Frame(self.body_frame, bg=SECONDARY_COLOR, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        page_commands = {
            "dashboard": self.show_dashboard,
            "catalog": self.show_catalog_page,
            "manage_books": self.show_manage_books_page,
            "register_student": self.show_register_student_page,
            "requests": self.show_requests_page,
            "issue": self.show_issue_page,
            "return": self.show_return_page,
            "history": self.show_history_page,
            "my_history": self.show_my_history_page,
            "reports": self.show_reports_page,
            "activity": self.show_activity_page,
            "users": self.show_users_page
        }
        allowed = ROLE_PERMISSIONS.get(self.role, set())
        for key, label in NAV_PAGES:
            if key not in allowed:
                continue
            tk.Button(
                self.sidebar,
                text=label,
                command=page_commands[key],
                font=("Segoe UI", 11, "bold"),
                bg=SECONDARY_COLOR,
                fg="white",
                relief="flat",
                activebackground="#3D6BB5",
                activeforeground="white",
                width=22,
                pady=12
            ).pack(pady=5)
        tk.Frame(self.sidebar, bg=SECONDARY_COLOR, height=2).pack(fill="x", pady=10)
        tk.Button(
            self.sidebar,
            text="Logout",
            command=self.logout,
            font=("Segoe UI", 11, "bold"),
            bg="#7B241C",
            fg="white",
            relief="flat",
            activebackground="#C0392B",
            activeforeground="white",
            width=22,
            pady=12
        ).pack(pady=5)

    # ==========================================================
    # MAIN AREA
    # ==========================================================
    def build_main_area(self):
        self.main_frame = tk.Frame(self.body_frame, bg=WINDOW_BG)
        self.main_frame.pack(side="left", fill="both", expand=True)
        self.show_dashboard()

    # ==========================================================
    # LIVE CLOCK
    # ==========================================================
    def update_clock(self):
        from datetime import datetime
        self.clock_label.config(text=datetime.now().strftime("%d %B %Y | %H:%M:%S"))
        self.root.after(1000, self.update_clock)

    # ==========================================================
    # CLEAR MAIN FRAME
    # ==========================================================
    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ==========================================================
    # GENERIC SORTABLE TREEVIEW HELPER
    # ==========================================================
    def make_sortable(self, tree, columns):
        for col in columns:
            tree.heading(col, command=lambda c=col, t=tree: self.sort_tree_column(t, c, False))

    def sort_tree_column(self, tree, col, reverse):
        items = [(tree.set(item, col), item) for item in tree.get_children("")]

        def sort_key(pair):
            value = pair[0]
            try:
                return (0, float(value))
            except (ValueError, TypeError):
                return (1, str(value).lower())

        items.sort(key=sort_key, reverse=reverse)
        for index, (_, item) in enumerate(items):
            tree.move(item, "", index)
        tree.heading(col, command=lambda: self.sort_tree_column(tree, col, not reverse))

    # ==========================================================
    # LOGOUT
    # ==========================================================
    def logout(self):
        answer = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if answer:
            self.root.destroy()
            from app.gui.login_window import LoginWindow
            login_root = tk.Tk()
            LoginWindow(login_root)
            login_root.mainloop()
