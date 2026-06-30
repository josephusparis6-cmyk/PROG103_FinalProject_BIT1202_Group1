# ==========================================================
# PAGES
# All page-building and page-refreshing methods for LibrarySys,
# bundled as a mixin so main_app.py's LibrarySysApp class stays
# focused on the shell (header/sidebar/routing) while this file
# focuses purely on page content.
# ==========================================================
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from app.config import (
    WINDOW_BG, PRIMARY_COLOR, BOOK_CATEGORIES, CATEGORY_FILTER_OPTIONS,
    TRANSACTION_STATUS_OPTIONS, TRANSACTION_STATUS_FILTER_OPTIONS,
    ROLE_OPTIONS, LOAN_PERIOD_DAYS
)
from app.data_store import books_data, transactions_data, activity_log, USER_ACCOUNTS, requests_data
from app.logic import (
    add_book, update_book, delete_book, get_book_by_id, search_books,
    issue_book, return_book, get_transaction_by_id, get_transactions_for_borrower,
    refresh_overdue_statuses, get_library_statistics, get_category_breakdown,
    generate_daily_report, export_report, export_books_csv, export_transactions_csv,
    create_user_account, delete_user_account, change_user_role,
    register_student, get_all_students, request_book, get_pending_requests,
    get_requests_for_student, approve_request, reject_request
)


class PagesMixin:
    # ==========================================================
    # DASHBOARD PAGE
    # ==========================================================
    def show_dashboard(self):
        if not self.has_access("dashboard"):
            self.access_denied()
            return
        self.clear_main_frame()
        self.build_dashboard()

    def build_dashboard(self):
        title = tk.Label(
            self.main_frame, text="LibrarySys Management Dashboard",
            font=("Segoe UI", 24, "bold"), bg=WINDOW_BG, fg=PRIMARY_COLOR
        )
        title.pack(pady=(20, 10))

        cards_frame = tk.Frame(self.main_frame, bg=WINDOW_BG)
        cards_frame.pack(fill="x", padx=20, pady=5)
        self.titles_card = self.create_card(cards_frame, "BOOK TITLES", "#2471A3")
        self.copies_card = self.create_card(cards_frame, "TOTAL COPIES", "#1A3E6F")
        self.available_card = self.create_card(cards_frame, "AVAILABLE NOW", "#1E8449")
        self.borrowed_card = self.create_card(cards_frame, "ON LOAN", "#B7950B")

        cards_frame2 = tk.Frame(self.main_frame, bg=WINDOW_BG)
        cards_frame2.pack(fill="x", padx=20, pady=(5, 10))
        self.overdue_card = self.create_card(cards_frame2, "OVERDUE LOANS", "#922B21")
        self.returned_card = self.create_card(cards_frame2, "RETURNED (ALL TIME)", "#7D3C98")

        middle_frame = tk.Frame(self.main_frame, bg=WINDOW_BG)
        middle_frame.pack(fill="both", expand=True, padx=20, pady=5)
        activity_frame = tk.LabelFrame(
            middle_frame, text="Recent Activity", font=("Segoe UI", 11, "bold"), bg="white"
        )
        activity_frame.pack(side="left", fill="both", expand=True, padx=10)
        self.activity_text = tk.Text(activity_frame, height=14, font=("Consolas", 10))
        self.activity_text.pack(fill="both", expand=True)

        category_frame = tk.LabelFrame(
            middle_frame, text="Books by Category", font=("Segoe UI", 11, "bold"), bg="white"
        )
        category_frame.pack(side="left", fill="both", expand=True, padx=10)
        columns = ("Category", "Titles")
        self.category_tree = ttk.Treeview(category_frame, columns=columns, show="headings", height=11)
        for col in columns:
            self.category_tree.heading(col, text=col)
            self.category_tree.column(col, width=180, anchor="center")
        self.category_tree.pack(fill="both", expand=True)

        charts_row = tk.Frame(self.main_frame, bg=WINDOW_BG)
        charts_row.pack(fill="x", padx=20, pady=(5, 10))
        chart_frame = tk.LabelFrame(
            charts_row, text="Category Breakdown", font=("Segoe UI", 11, "bold"), bg="white"
        )
        chart_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.category_chart_canvas = tk.Canvas(chart_frame, height=170, bg="white", highlightthickness=0)
        self.category_chart_canvas.pack(fill="x", expand=True, padx=10, pady=10)
        self.category_chart_canvas.bind("<Configure>", lambda event: self.draw_category_chart())

        status_chart_frame = tk.LabelFrame(
            charts_row, text="Loan Status Breakdown", font=("Segoe UI", 11, "bold"), bg="white"
        )
        status_chart_frame.pack(side="left", fill="both", expand=True, padx=(10, 0))
        self.loan_status_chart_canvas = tk.Canvas(status_chart_frame, height=170, bg="white", highlightthickness=0)
        self.loan_status_chart_canvas.pack(fill="x", expand=True, padx=10, pady=10)
        self.loan_status_chart_canvas.bind("<Configure>", lambda event: self.draw_loan_status_chart())

        tk.Button(
            self.main_frame, text="Refresh Dashboard", font=("Segoe UI", 11, "bold"),
            bg=PRIMARY_COLOR, fg="white", command=self.refresh_dashboard
        ).pack(pady=10)
        self.refresh_dashboard()

    def create_card(self, parent, title, color):
        frame = tk.Frame(parent, bg=color, width=250, height=120)
        frame.pack(side="left", expand=True, fill="both", padx=10)
        frame.pack_propagate(False)
        tk.Label(
            frame, text=title, font=("Segoe UI", 11, "bold"), bg=color, fg="white",
            wraplength=230, justify="center"
        ).pack(pady=10)
        value_label = tk.Label(frame, text="0", font=("Segoe UI", 28, "bold"), bg=color, fg="white")
        value_label.pack()
        return value_label

    def draw_category_chart(self):
        if not hasattr(self, "category_chart_canvas"):
            return
        canvas = self.category_chart_canvas
        canvas.delete("all")
        counts = get_category_breakdown()
        max_count = max(counts.values()) if counts else 0
        width = canvas.winfo_width()
        if width <= 1:
            width = 800
        bar_colors = ["#1A3E6F", "#2471A3", "#1E8449", "#B7950B", "#7D3C98", "#922B21", "#566573"]
        row_height = 23
        label_width = 150
        top_margin = 6
        for index, (category, count) in enumerate(counts.items()):
            y = top_margin + index * row_height
            bar_max_width = max(width - label_width - 70, 10)
            bar_width = 0 if max_count == 0 else int((count / max_count) * bar_max_width)
            color = bar_colors[index % len(bar_colors)]
            canvas.create_text(10, y + 10, anchor="w", text=category, font=("Segoe UI", 9))
            canvas.create_rectangle(
                label_width, y, label_width + max(bar_width, 2), y + 16, fill=color, outline=color
            )
            canvas.create_text(
                label_width + bar_width + 10, y + 8, anchor="w", text=str(count), font=("Segoe UI", 9, "bold")
            )

    def draw_loan_status_chart(self):
        if not hasattr(self, "loan_status_chart_canvas"):
            return
        canvas = self.loan_status_chart_canvas
        canvas.delete("all")
        counts = {status: 0 for status in TRANSACTION_STATUS_OPTIONS}
        for transaction in transactions_data:
            status = transaction.get("status", "")
            if status in counts:
                counts[status] += 1
        max_count = max(counts.values()) if counts else 0
        width = canvas.winfo_width()
        if width <= 1:
            width = 800
        status_colors = {"Borrowed": "#B7950B", "Returned": "#1E8449", "Overdue": "#922B21"}
        row_height = 40
        label_width = 100
        top_margin = 12
        for index, status in enumerate(TRANSACTION_STATUS_OPTIONS):
            y = top_margin + index * row_height
            count = counts[status]
            bar_max_width = max(width - label_width - 70, 10)
            bar_width = 0 if max_count == 0 else int((count / max_count) * bar_max_width)
            color = status_colors.get(status, "#7F8C8D")
            canvas.create_text(10, y + 12, anchor="w", text=status, font=("Segoe UI", 10))
            canvas.create_rectangle(
                label_width, y, label_width + max(bar_width, 2), y + 20, fill=color, outline=color
            )
            canvas.create_text(
                label_width + bar_width + 10, y + 10, anchor="w", text=str(count), font=("Segoe UI", 10, "bold")
            )

    def refresh_dashboard(self):
        if not hasattr(self, "titles_card"):
            return
        stats = get_library_statistics()
        self.titles_card.config(text=str(stats["total_titles"]))
        self.copies_card.config(text=str(stats["total_copies"]))
        self.available_card.config(text=str(stats["available_copies"]))
        self.borrowed_card.config(text=str(stats["borrowed_copies"]))
        self.overdue_card.config(text=str(stats["overdue"]))
        self.returned_card.config(text=str(stats["returned"]))

        self.activity_text.delete("1.0", tk.END)
        for log in reversed(activity_log[-20:]):
            line = (
                f"{log['timestamp']} | {log['reference_id']} | "
                f"{log.get('performed_by', 'Unknown')} | {log['action']}\n"
            )
            self.activity_text.insert(tk.END, line)

        for item in self.category_tree.get_children():
            self.category_tree.delete(item)
        category_counts = {}
        for book in books_data:
            category = book["category"]
            category_counts[category] = category_counts.get(category, 0) + 1
        for category, count in category_counts.items():
            self.category_tree.insert("", "end", values=(category, count))

        self.draw_category_chart()
        self.draw_loan_status_chart()

    # ==========================================================
    # BOOK CATALOG PAGE (Search/browse - available to all roles)
    # ==========================================================
    def show_catalog_page(self):
        if not self.has_access("catalog"):
            self.access_denied()
            return
        self.clear_main_frame()
        self.build_catalog_page()

    def build_catalog_page(self):
        title = tk.Label(
            self.main_frame, text="Book Catalog",
            font=("Segoe UI", 22, "bold"), bg=WINDOW_BG, fg=PRIMARY_COLOR
        )
        title.pack(pady=15)

        search_panel = tk.Frame(self.main_frame, bg="white", padx=20, pady=15)
        search_panel.pack(fill="x", padx=20)
        tk.Label(
            search_panel, text="Search by title, author, ISBN, or category",
            font=("Segoe UI", 11), bg="white"
        ).grid(row=0, column=0, padx=(0, 10))
        self.catalog_search_entry = tk.Entry(search_panel, width=35, font=("Segoe UI", 12))
        self.catalog_search_entry.grid(row=0, column=1, padx=10)
        self.catalog_search_entry.bind("<Return>", lambda event: self.search_catalog())
        tk.Button(
            search_panel, text="Search", bg=PRIMARY_COLOR, fg="white",
            font=("Segoe UI", 11, "bold"), command=self.search_catalog
        ).grid(row=0, column=2, padx=5)
        tk.Button(
            search_panel, text="Clear", bg="#7F8C8D", fg="white",
            font=("Segoe UI", 11, "bold"), command=self.clear_catalog_search
        ).grid(row=0, column=3, padx=5)
        tk.Label(
            search_panel, text="Category:", font=("Segoe UI", 10), bg="white"
        ).grid(row=0, column=4, padx=(20, 5))
        self.catalog_category_filter = ttk.Combobox(
            search_panel, values=CATEGORY_FILTER_OPTIONS, width=16, state="readonly"
        )
        self.catalog_category_filter.set("All")
        self.catalog_category_filter.grid(row=0, column=5)
        self.catalog_category_filter.bind("<<ComboboxSelected>>", lambda event: self.search_catalog())

        table_frame = tk.Frame(self.main_frame, bg=WINDOW_BG)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        columns = ("Book ID", "Title", "Author", "ISBN", "Category", "Total Copies", "Available")
        self.catalog_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=18)
        widths = [90, 240, 170, 110, 150, 100, 90]
        for col, width in zip(columns, widths):
            self.catalog_tree.heading(col, text=col)
            self.catalog_tree.column(col, width=width, anchor="center")
        self.catalog_tree.column("Title", anchor="w")
        self.catalog_tree.column("Author", anchor="w")
        self.make_sortable(self.catalog_tree, columns)
        self.catalog_tree.tag_configure("none_available", background="#FADBD8")
        self.catalog_tree.tag_configure("low_stock", background="#FCF3CF")
        self.catalog_tree.pack(fill="both", expand=True)

        self.catalog_empty_label = tk.Label(
            self.main_frame, text="No books match your search.",
            font=("Segoe UI", 11, "italic"), bg=WINDOW_BG, fg="#7F8C8D"
        )

        if self.role == "Student":
            request_frame = tk.Frame(self.main_frame, bg=WINDOW_BG)
            request_frame.pack(pady=10)
            tk.Button(
                request_frame, text="Request Selected Book", bg=PRIMARY_COLOR, fg="white",
                font=("Segoe UI", 11, "bold"), width=24, command=self.request_selected_book_action
            ).pack()
            tk.Label(
                request_frame, text="Books with 0 available copies cannot be requested.",
                font=("Segoe UI", 9, "italic"), bg=WINDOW_BG, fg="#7F8C8D"
            ).pack(pady=(4, 0))

        self.refresh_catalog()

    def request_selected_book_action(self):
        selection = self.catalog_tree.selection()
        if not selection:
            messagebox.showerror("Selection Error", "Please select a book to request.")
            return
        book_id = self.catalog_tree.item(selection[0], "values")[0]
        success, message = request_book(self.username, book_id, performed_by=self.username)
        if success:
            messagebox.showinfo("Request Submitted", message)
        else:
            messagebox.showerror("Cannot Request Book", message)

    def search_catalog(self):
        keyword = self.catalog_search_entry.get().strip()
        category_filter = self.catalog_category_filter.get() if hasattr(self, "catalog_category_filter") else "All"
        results = search_books(keyword)
        if category_filter != "All":
            results = [book for book in results if book["category"] == category_filter]
        self.render_catalog_rows(results)

    def clear_catalog_search(self):
        self.catalog_search_entry.delete(0, tk.END)
        self.catalog_category_filter.set("All")
        self.refresh_catalog()

    def refresh_catalog(self):
        if not hasattr(self, "catalog_tree"):
            return
        self.render_catalog_rows(list(books_data))

    def render_catalog_rows(self, book_list):
        for item in self.catalog_tree.get_children():
            self.catalog_tree.delete(item)
        for book in book_list:
            if book["available_copies"] == 0:
                tag = "none_available"
            elif book["available_copies"] <= max(1, book["total_copies"] // 4):
                tag = "low_stock"
            else:
                tag = ""
            self.catalog_tree.insert(
                "", "end",
                values=(
                    book["id"], book["title"], book["author"], book["isbn"],
                    book["category"], book["total_copies"], book["available_copies"]
                ),
                tags=(tag,) if tag else ()
            )
        if hasattr(self, "catalog_empty_label"):
            if len(book_list) == 0:
                self.catalog_empty_label.pack(pady=5)
            else:
                self.catalog_empty_label.pack_forget()

    # ==========================================================
    # MANAGE BOOKS PAGE (Librarian / Administrator)
    # ==========================================================
    def show_manage_books_page(self):
        if not self.has_access("manage_books"):
            self.access_denied()
            return
        self.clear_main_frame()
        self.build_manage_books_page()

    def build_manage_books_page(self):
        title = tk.Label(
            self.main_frame, text="Manage Books",
            font=("Segoe UI", 22, "bold"), bg=WINDOW_BG, fg=PRIMARY_COLOR
        )
        title.pack(pady=15)

        body = tk.Frame(self.main_frame, bg=WINDOW_BG)
        body.pack(fill="both", expand=True, padx=20, pady=5)

        # Left: existing books table
        list_frame = tk.LabelFrame(
            body, text="Catalog", font=("Segoe UI", 11, "bold"), bg="white"
        )
        list_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        columns = ("Book ID", "Title", "Author", "Category", "Total", "Available")
        self.manage_books_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=16)
        widths = [80, 220, 150, 140, 60, 80]
        for col, width in zip(columns, widths):
            self.manage_books_tree.heading(col, text=col)
            self.manage_books_tree.column(col, width=width, anchor="center")
        self.manage_books_tree.column("Title", anchor="w")
        self.manage_books_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.manage_books_tree.bind("<<TreeviewSelect>>", lambda event: self.on_manage_book_selected())

        list_btn_frame = tk.Frame(list_frame, bg="white")
        list_btn_frame.pack(pady=(0, 10))
        tk.Button(
            list_btn_frame, text="Load Selected for Editing", bg="#2471A3", fg="white",
            font=("Segoe UI", 10, "bold"), command=self.load_selected_book_for_edit
        ).pack(side="left", padx=5)
        tk.Button(
            list_btn_frame, text="Delete Selected Book", bg="#7B241C", fg="white",
            font=("Segoe UI", 10, "bold"), command=self.delete_selected_book
        ).pack(side="left", padx=5)

        # Right: add/edit form
        form_frame = tk.LabelFrame(
            body, text="Add / Edit Book", font=("Segoe UI", 11, "bold"), bg="white"
        )
        form_frame.pack(side="left", fill="y", padx=(10, 0))
        inner = tk.Frame(form_frame, bg="white", padx=20, pady=15)
        inner.pack()

        self.editing_book_id = None

        tk.Label(inner, text="Title", font=("Segoe UI", 10), bg="white").grid(row=0, column=0, sticky="w", pady=6)
        self.book_title_entry = tk.Entry(inner, width=32, font=("Segoe UI", 11))
        self.book_title_entry.grid(row=1, column=0, pady=(0, 8))

        tk.Label(inner, text="Author", font=("Segoe UI", 10), bg="white").grid(row=2, column=0, sticky="w", pady=6)
        self.book_author_entry = tk.Entry(inner, width=32, font=("Segoe UI", 11))
        self.book_author_entry.grid(row=3, column=0, pady=(0, 8))

        tk.Label(inner, text="ISBN (10 or 13 digits)", font=("Segoe UI", 10), bg="white").grid(row=4, column=0, sticky="w", pady=6)
        self.book_isbn_entry = tk.Entry(inner, width=32, font=("Segoe UI", 11))
        self.book_isbn_entry.grid(row=5, column=0, pady=(0, 8))

        tk.Label(inner, text="Category", font=("Segoe UI", 10), bg="white").grid(row=6, column=0, sticky="w", pady=6)
        self.book_category_combo = ttk.Combobox(inner, values=BOOK_CATEGORIES, width=29, state="readonly")
        self.book_category_combo.set(BOOK_CATEGORIES[0])
        self.book_category_combo.grid(row=7, column=0, pady=(0, 8))

        tk.Label(inner, text="Total Copies", font=("Segoe UI", 10), bg="white").grid(row=8, column=0, sticky="w", pady=6)
        self.book_copies_entry = tk.Entry(inner, width=32, font=("Segoe UI", 11))
        self.book_copies_entry.grid(row=9, column=0, pady=(0, 12))

        button_row = tk.Frame(inner, bg="white")
        button_row.grid(row=10, column=0, pady=5)
        tk.Button(
            button_row, text="Save Book", bg=PRIMARY_COLOR, fg="white", width=14,
            font=("Segoe UI", 10, "bold"), command=self.save_book_action
        ).pack(side="left", padx=5)
        tk.Button(
            button_row, text="Clear Form", bg="#7F8C8D", fg="white", width=14,
            font=("Segoe UI", 10, "bold"), command=self.clear_book_form
        ).pack(side="left", padx=5)

        self.book_form_status_label = tk.Label(
            inner, text="Adding a new book.", font=("Segoe UI", 9, "italic"), bg="white", fg="#7F8C8D"
        )
        self.book_form_status_label.grid(row=11, column=0, pady=(10, 0), sticky="w")

        self.refresh_manage_books_table()

    def refresh_manage_books_table(self):
        if not hasattr(self, "manage_books_tree"):
            return
        for item in self.manage_books_tree.get_children():
            self.manage_books_tree.delete(item)
        for book in books_data:
            self.manage_books_tree.insert(
                "", "end",
                values=(
                    book["id"], book["title"], book["author"], book["category"],
                    book["total_copies"], book["available_copies"]
                )
            )

    def on_manage_book_selected(self):
        pass  # selection alone does nothing; explicit "Load" button avoids accidental form overwrites

    def load_selected_book_for_edit(self):
        selection = self.manage_books_tree.selection()
        if not selection:
            messagebox.showerror("Selection Error", "Please select a book to edit.")
            return
        book_id = self.manage_books_tree.item(selection[0], "values")[0]
        book = get_book_by_id(book_id)
        if book is None:
            messagebox.showerror("Error", "Book not found.")
            return
        self.editing_book_id = book_id
        self.book_title_entry.delete(0, tk.END)
        self.book_title_entry.insert(0, book["title"])
        self.book_author_entry.delete(0, tk.END)
        self.book_author_entry.insert(0, book["author"])
        self.book_isbn_entry.delete(0, tk.END)
        self.book_isbn_entry.insert(0, book["isbn"])
        self.book_category_combo.set(book["category"])
        self.book_copies_entry.delete(0, tk.END)
        self.book_copies_entry.insert(0, str(book["total_copies"]))
        self.book_form_status_label.config(text=f"Editing {book_id} - '{book['title']}'.")

    def clear_book_form(self):
        self.editing_book_id = None
        self.book_title_entry.delete(0, tk.END)
        self.book_author_entry.delete(0, tk.END)
        self.book_isbn_entry.delete(0, tk.END)
        self.book_category_combo.set(BOOK_CATEGORIES[0])
        self.book_copies_entry.delete(0, tk.END)
        self.book_form_status_label.config(text="Adding a new book.")

    def save_book_action(self):
        title = self.book_title_entry.get()
        author = self.book_author_entry.get()
        isbn = self.book_isbn_entry.get()
        category = self.book_category_combo.get()
        copies = self.book_copies_entry.get()

        if self.editing_book_id is None:
            success, message = add_book(title, author, isbn, category, copies, performed_by=self.username)
        else:
            success, message = update_book(
                self.editing_book_id, title, author, isbn, category, copies, performed_by=self.username
            )
        if success:
            messagebox.showinfo("Success", message)
            self.clear_book_form()
            self.refresh_manage_books_table()
            self.refresh_dashboard()
        else:
            messagebox.showerror("Validation Error", message)

    def delete_selected_book(self):
        selection = self.manage_books_tree.selection()
        if not selection:
            messagebox.showerror("Selection Error", "Please select a book to delete.")
            return
        values = self.manage_books_tree.item(selection[0], "values")
        book_id, book_title = values[0], values[1]
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Permanently remove '{book_title}' ({book_id}) from the catalog?\nThis cannot be undone."
        )
        if not confirm:
            return
        success, message = delete_book(book_id, performed_by=self.username)
        if success:
            messagebox.showinfo("Success", message)
            self.refresh_manage_books_table()
            self.refresh_dashboard()
        else:
            messagebox.showerror("Cannot Delete", message)

    # ==========================================================
    # ISSUE BOOK PAGE (Librarian / Administrator)
    # ==========================================================
    def show_issue_page(self):
        if not self.has_access("issue"):
            self.access_denied()
            return
        self.clear_main_frame()
        self.build_issue_page()

    def build_issue_page(self):
        title = tk.Label(
            self.main_frame, text="Issue Book to Borrower",
            font=("Segoe UI", 22, "bold"), bg=WINDOW_BG, fg=PRIMARY_COLOR
        )
        title.pack(pady=20)
        form_frame = tk.Frame(self.main_frame, bg="white", padx=30, pady=30)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Select Book", font=("Segoe UI", 11), bg="white").grid(
            row=0, column=0, sticky="w", pady=10, padx=10
        )
        self.issue_book_combo = ttk.Combobox(form_frame, width=50, state="readonly")
        self.issue_book_combo.grid(row=0, column=1, pady=10)

        tk.Label(form_frame, text="Borrower Name", font=("Segoe UI", 11), bg="white").grid(
            row=1, column=0, sticky="w", pady=10, padx=10
        )
        self.borrower_name_entry = tk.Entry(form_frame, width=40, font=("Segoe UI", 11))
        self.borrower_name_entry.grid(row=1, column=1, pady=10)

        tk.Label(form_frame, text="Borrower ID\n(Student/Staff ID)", font=("Segoe UI", 11), bg="white", justify="left").grid(
            row=2, column=0, sticky="w", pady=10, padx=10
        )
        self.borrower_id_entry = tk.Entry(form_frame, width=40, font=("Segoe UI", 11))
        self.borrower_id_entry.grid(row=2, column=1, pady=10)

        tk.Label(
            form_frame, text=f"Loan period: {LOAN_PERIOD_DAYS} days from today",
            font=("Segoe UI", 9, "italic"), bg="white", fg="#7F8C8D"
        ).grid(row=3, column=0, columnspan=2, sticky="w", padx=10)

        button_frame = tk.Frame(self.main_frame, bg=WINDOW_BG)
        button_frame.pack(pady=20)
        tk.Button(
            button_frame, text="Issue Book", bg=PRIMARY_COLOR, fg="white", width=20,
            font=("Segoe UI", 11, "bold"), command=self.issue_book_action
        ).pack(side="left", padx=10)
        tk.Button(
            button_frame, text="Refresh Book List", bg="#2471A3", fg="white", width=20,
            font=("Segoe UI", 11, "bold"), command=self.load_issue_book_dropdown
        ).pack(side="left", padx=10)
        self.load_issue_book_dropdown()

    def load_issue_book_dropdown(self):
        if not hasattr(self, "issue_book_combo"):
            return
        available_books = [b for b in books_data if b["available_copies"] > 0]
        values = [f"{b['id']} - {b['title']} ({b['available_copies']} available)" for b in available_books]
        self.issue_book_combo["values"] = values

    def issue_book_action(self):
        selected = self.issue_book_combo.get()
        if selected == "":
            messagebox.showerror("Selection Error", "Please select a book to issue.")
            return
        book_id = selected.split(" - ")[0]
        success, message = issue_book(
            book_id, self.borrower_name_entry.get(), self.borrower_id_entry.get(),
            performed_by=self.username
        )
        if success:
            messagebox.showinfo("Success", message)
            self.borrower_name_entry.delete(0, tk.END)
            self.borrower_id_entry.delete(0, tk.END)
            self.load_issue_book_dropdown()
            self.refresh_dashboard()
        else:
            messagebox.showerror("Cannot Issue Book", message)

    # ==========================================================
    # RETURN BOOK PAGE (Librarian / Administrator)
    # ==========================================================
    def show_return_page(self):
        if not self.has_access("return"):
            self.access_denied()
            return
        self.clear_main_frame()
        self.build_return_page()

    def build_return_page(self):
        title = tk.Label(
            self.main_frame, text="Return Book",
            font=("Segoe UI", 22, "bold"), bg=WINDOW_BG, fg=PRIMARY_COLOR
        )
        title.pack(pady=20)
        form_frame = tk.Frame(self.main_frame, bg="white", padx=30, pady=30)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Select Active Loan", font=("Segoe UI", 11), bg="white").grid(
            row=0, column=0, sticky="w", pady=10, padx=10
        )
        self.return_transaction_combo = ttk.Combobox(form_frame, width=60, state="readonly")
        self.return_transaction_combo.grid(row=0, column=1, pady=10)

        button_frame = tk.Frame(self.main_frame, bg=WINDOW_BG)
        button_frame.pack(pady=20)
        tk.Button(
            button_frame, text="Mark as Returned", bg=PRIMARY_COLOR, fg="white", width=20,
            font=("Segoe UI", 11, "bold"), command=self.return_book_action
        ).pack(side="left", padx=10)
        tk.Button(
            button_frame, text="Refresh List", bg="#2471A3", fg="white", width=20,
            font=("Segoe UI", 11, "bold"), command=self.load_return_dropdown
        ).pack(side="left", padx=10)
        self.load_return_dropdown()

    def load_return_dropdown(self):
        if not hasattr(self, "return_transaction_combo"):
            return
        refresh_overdue_statuses()
        active_loans = [t for t in transactions_data if t["status"] in ("Borrowed", "Overdue")]
        values = [
            f"{t['id']} - {t['book_title']} ({t['borrower_name']}, due {t['due_date']})"
            for t in active_loans
        ]
        self.return_transaction_combo["values"] = values

    def return_book_action(self):
        selected = self.return_transaction_combo.get()
        if selected == "":
            messagebox.showerror("Selection Error", "Please select a loan to mark as returned.")
            return
        transaction_id = selected.split(" - ")[0]
        success, message = return_book(transaction_id, performed_by=self.username)
        if success:
            messagebox.showinfo("Success", message)
            self.load_return_dropdown()
            self.refresh_dashboard()
        else:
            messagebox.showerror("Cannot Return Book", message)

    # ==========================================================
    # BORROW HISTORY PAGE (Librarian / Administrator - all transactions)
    # ==========================================================
    def show_history_page(self):
        if not self.has_access("history"):
            self.access_denied()
            return
        self.clear_main_frame()
        self.build_history_page()

    def build_history_page(self):
        refresh_overdue_statuses()
        title = tk.Label(
            self.main_frame, text="Borrow History (All Transactions)",
            font=("Segoe UI", 22, "bold"), bg=WINDOW_BG, fg=PRIMARY_COLOR
        )
        title.pack(pady=15)

        filter_frame = tk.Frame(self.main_frame, bg=WINDOW_BG)
        filter_frame.pack(fill="x", padx=15, pady=(0, 5))
        tk.Label(filter_frame, text="Filter by Status:", bg=WINDOW_BG, font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        self.history_status_filter = ttk.Combobox(
            filter_frame, values=TRANSACTION_STATUS_FILTER_OPTIONS, width=15, state="readonly"
        )
        self.history_status_filter.set("All")
        self.history_status_filter.pack(side="left")
        self.history_status_filter.bind("<<ComboboxSelected>>", lambda event: self.refresh_history_table())

        table_frame = tk.Frame(self.main_frame, bg=WINDOW_BG)
        table_frame.pack(fill="both", expand=True, padx=15, pady=10)
        columns = ("Transaction ID", "Book Title", "Borrower", "Borrower ID", "Issue Date", "Due Date", "Return Date", "Status")
        self.history_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=18)
        widths = [110, 220, 150, 110, 100, 100, 100, 90]
        for col, width in zip(columns, widths):
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=width, anchor="center")
        self.history_tree.column("Book Title", anchor="w")
        self.make_sortable(self.history_tree, columns)
        self.history_tree.tag_configure("overdue", background="#F1948A")
        self.history_tree.tag_configure("returned", background="#D5F5E3")
        self.history_tree.tag_configure("borrowed", background="#FCF3CF")
        self.history_tree.pack(fill="both", expand=True)

        self.history_empty_label = tk.Label(
            self.main_frame, text="No transactions match the current filter.",
            font=("Segoe UI", 11, "italic"), bg=WINDOW_BG, fg="#7F8C8D"
        )

        button_frame = tk.Frame(self.main_frame, bg=WINDOW_BG)
        button_frame.pack(pady=10)
        tk.Button(
            button_frame, text="Refresh", bg=PRIMARY_COLOR, fg="white", width=18,
            font=("Segoe UI", 11, "bold"), command=self.refresh_history_table
        ).pack(side="left", padx=10)
        tk.Button(
            button_frame, text="Export CSV", bg="#2471A3", fg="white", width=18,
            font=("Segoe UI", 11, "bold"), command=self.export_transactions_action
        ).pack(side="left", padx=10)
        self.refresh_history_table()

    def refresh_history_table(self):
        if not hasattr(self, "history_tree"):
            return
        refresh_overdue_statuses()
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        status_filter = self.history_status_filter.get() if hasattr(self, "history_status_filter") else "All"
        filtered = transactions_data if status_filter == "All" else [
            t for t in transactions_data if t["status"] == status_filter
        ]
        for transaction in filtered:
            tag = transaction["status"].lower()
            self.history_tree.insert(
                "", "end",
                values=(
                    transaction["id"], transaction["book_title"], transaction["borrower_name"],
                    transaction["borrower_id"], transaction["issue_date"], transaction["due_date"],
                    transaction.get("return_date", ""), transaction["status"]
                ),
                tags=(tag,)
            )
        if hasattr(self, "history_empty_label"):
            if len(filtered) == 0:
                self.history_empty_label.pack(pady=5)
            else:
                self.history_empty_label.pack_forget()

    def export_transactions_action(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not filepath:
            return
        try:
            export_transactions_csv(filepath)
            messagebox.showinfo("Export Successful", "Transactions exported successfully.")
        except Exception as error:
            messagebox.showerror("Export Error", str(error))

    # ==========================================================
    # MY BOOKS PAGE (Student - own loans, requests, and history)
    # ==========================================================
    def show_my_history_page(self):
        if not self.has_access("my_history"):
            self.access_denied()
            return
        self.clear_main_frame()
        self.build_my_history_page()

    def build_my_history_page(self):
        refresh_overdue_statuses()
        title = tk.Label(
            self.main_frame, text=f"My Books ({self.username})",
            font=("Segoe UI", 22, "bold"), bg=WINDOW_BG, fg=PRIMARY_COLOR
        )
        title.pack(pady=15)

        # ----- Currently borrowed books -----
        current_frame = tk.LabelFrame(
            self.main_frame, text="Books Currently Assigned to Me", font=("Segoe UI", 11, "bold"), bg="white"
        )
        current_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        columns = ("Transaction ID", "Book Title", "Issue Date", "Due Date", "Status")
        self.my_current_tree = ttk.Treeview(current_frame, columns=columns, show="headings", height=6)
        widths = [110, 280, 110, 110, 100]
        for col, width in zip(columns, widths):
            self.my_current_tree.heading(col, text=col)
            self.my_current_tree.column(col, width=width, anchor="center")
        self.my_current_tree.column("Book Title", anchor="w")
        self.my_current_tree.tag_configure("overdue", background="#F1948A")
        self.my_current_tree.tag_configure("borrowed", background="#FCF3CF")
        self.my_current_tree.pack(fill="both", expand=True, padx=10, pady=10)
        tk.Button(
            current_frame, text="Return Selected Book", bg=PRIMARY_COLOR, fg="white",
            font=("Segoe UI", 10, "bold"), command=self.return_my_book_action
        ).pack(pady=(0, 10))

        # ----- Pending / past requests -----
        requests_frame = tk.LabelFrame(
            self.main_frame, text="My Book Requests", font=("Segoe UI", 11, "bold"), bg="white"
        )
        requests_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        req_columns = ("Request ID", "Book Title", "Status", "Requested On")
        self.my_requests_tree = ttk.Treeview(requests_frame, columns=req_columns, show="headings", height=6)
        req_widths = [110, 300, 110, 160]
        for col, width in zip(req_columns, req_widths):
            self.my_requests_tree.heading(col, text=col)
            self.my_requests_tree.column(col, width=width, anchor="center")
        self.my_requests_tree.column("Book Title", anchor="w")
        self.my_requests_tree.tag_configure("Pending", background="#FCF3CF")
        self.my_requests_tree.tag_configure("Approved", background="#D5F5E3")
        self.my_requests_tree.tag_configure("Rejected", background="#FADBD8")
        self.my_requests_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # ----- Full personal history -----
        history_frame = tk.LabelFrame(
            self.main_frame, text="My Full Borrow History", font=("Segoe UI", 11, "bold"), bg="white"
        )
        history_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        hist_columns = ("Transaction ID", "Book Title", "Issue Date", "Due Date", "Return Date", "Status")
        self.my_history_tree = ttk.Treeview(history_frame, columns=hist_columns, show="headings", height=6)
        hist_widths = [110, 260, 100, 100, 100, 90]
        for col, width in zip(hist_columns, hist_widths):
            self.my_history_tree.heading(col, text=col)
            self.my_history_tree.column(col, width=width, anchor="center")
        self.my_history_tree.column("Book Title", anchor="w")
        self.my_history_tree.tag_configure("overdue", background="#F1948A")
        self.my_history_tree.tag_configure("returned", background="#D5F5E3")
        self.my_history_tree.tag_configure("borrowed", background="#FCF3CF")
        self.my_history_tree.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Button(
            self.main_frame, text="Refresh", bg="#2471A3", fg="white",
            font=("Segoe UI", 10, "bold"), command=self.load_my_history
        ).pack(pady=(0, 15))

        self.load_my_history()

    def load_my_history(self):
        borrower_id = self.username
        refresh_overdue_statuses()

        for item in self.my_current_tree.get_children():
            self.my_current_tree.delete(item)
        for item in self.my_requests_tree.get_children():
            self.my_requests_tree.delete(item)
        for item in self.my_history_tree.get_children():
            self.my_history_tree.delete(item)

        history = get_transactions_for_borrower(borrower_id)
        for transaction in history:
            tag = transaction["status"].lower()
            if transaction["status"] in ("Borrowed", "Overdue"):
                self.my_current_tree.insert(
                    "", "end",
                    values=(
                        transaction["id"], transaction["book_title"],
                        transaction["issue_date"], transaction["due_date"], transaction["status"]
                    ),
                    tags=(tag,)
                )
            self.my_history_tree.insert(
                "", "end",
                values=(
                    transaction["id"], transaction["book_title"], transaction["issue_date"],
                    transaction["due_date"], transaction.get("return_date", ""), transaction["status"]
                ),
                tags=(tag,)
            )

        for request in get_requests_for_student(borrower_id):
            self.my_requests_tree.insert(
                "", "end",
                values=(request["id"], request["book_title"], request["status"], request["request_date"]),
                tags=(request["status"],)
            )

    def return_my_book_action(self):
        selection = self.my_current_tree.selection()
        if not selection:
            messagebox.showerror("Selection Error", "Please select a book to return.")
            return
        transaction_id = self.my_current_tree.item(selection[0], "values")[0]
        success, message = return_book(transaction_id, performed_by=self.username)
        if success:
            messagebox.showinfo("Success", message)
            self.load_my_history()
        else:
            messagebox.showerror("Cannot Return Book", message)

    # ==========================================================
    # REGISTER STUDENT PAGE (Administrator / Librarian)
    # ==========================================================
    def show_register_student_page(self):
        if not self.has_access("register_student"):
            self.access_denied()
            return
        self.clear_main_frame()
        self.build_register_student_page()

    def build_register_student_page(self):
        title = tk.Label(
            self.main_frame, text="Register Student",
            font=("Segoe UI", 22, "bold"), bg=WINDOW_BG, fg=PRIMARY_COLOR
        )
        title.pack(pady=20)

        body = tk.Frame(self.main_frame, bg=WINDOW_BG)
        body.pack(fill="both", expand=True, padx=20, pady=5)

        form_frame = tk.LabelFrame(body, text="New Student", font=("Segoe UI", 11, "bold"), bg="white")
        form_frame.pack(side="left", fill="y", padx=(0, 10))
        inner = tk.Frame(form_frame, bg="white", padx=20, pady=20)
        inner.pack()
        tk.Label(inner, text="Full Name", font=("Segoe UI", 10), bg="white").grid(row=0, column=0, sticky="w", pady=6)
        self.student_fullname_entry = tk.Entry(inner, width=30, font=("Segoe UI", 11))
        self.student_fullname_entry.grid(row=1, column=0, pady=(0, 10))
        self.student_fullname_entry.bind("<Return>", lambda event: self.register_student_action())
        tk.Button(
            inner, text="Register Student", bg=PRIMARY_COLOR, fg="white", width=24,
            font=("Segoe UI", 10, "bold"), command=self.register_student_action
        ).grid(row=2, column=0, pady=5)
        tk.Label(
            inner, text="A Student ID and login password are\ngenerated automatically.",
            font=("Segoe UI", 8, "italic"), bg="white", fg="#7F8C8D", justify="left"
        ).grid(row=3, column=0, pady=(15, 0), sticky="w")

        list_frame = tk.LabelFrame(body, text="Registered Students", font=("Segoe UI", 11, "bold"), bg="white")
        list_frame.pack(side="left", fill="both", expand=True)
        columns = ("Student ID", "Full Name")
        self.students_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=16)
        for col, width in zip(columns, [120, 260]):
            self.students_tree.heading(col, text=col)
            self.students_tree.column(col, width=width, anchor="center")
        self.students_tree.column("Full Name", anchor="w")
        self.students_tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.refresh_students_table()

    def refresh_students_table(self):
        if not hasattr(self, "students_tree"):
            return
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
        for student in get_all_students():
            self.students_tree.insert("", "end", values=(student["student_id"], student["full_name"]))

    def register_student_action(self):
        success, message, student_id = register_student(
            self.student_fullname_entry.get(), performed_by=self.username
        )
        if success:
            messagebox.showinfo("Student Registered", message)
            self.student_fullname_entry.delete(0, tk.END)
            self.refresh_students_table()
        else:
            messagebox.showerror("Validation Error", message)

    # ==========================================================
    # BOOK REQUESTS PAGE (Administrator / Librarian)
    # ==========================================================
    def show_requests_page(self):
        if not self.has_access("requests"):
            self.access_denied()
            return
        self.clear_main_frame()
        self.build_requests_page()

    def build_requests_page(self):
        title = tk.Label(
            self.main_frame, text="Pending Book Requests",
            font=("Segoe UI", 22, "bold"), bg=WINDOW_BG, fg=PRIMARY_COLOR
        )
        title.pack(pady=20)

        table_frame = tk.Frame(self.main_frame, bg=WINDOW_BG)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        columns = ("Request ID", "Book Title", "Student ID", "Student Name", "Requested On")
        self.requests_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=16)
        widths = [100, 260, 100, 200, 160]
        for col, width in zip(columns, widths):
            self.requests_tree.heading(col, text=col)
            self.requests_tree.column(col, width=width, anchor="center")
        self.requests_tree.column("Book Title", anchor="w")
        self.requests_tree.pack(fill="both", expand=True)

        self.requests_empty_label = tk.Label(
            self.main_frame, text="No pending requests.",
            font=("Segoe UI", 11, "italic"), bg=WINDOW_BG, fg="#7F8C8D"
        )

        button_frame = tk.Frame(self.main_frame, bg=WINDOW_BG)
        button_frame.pack(pady=15)
        tk.Button(
            button_frame, text="Approve Selected", bg="#1E8449", fg="white", width=18,
            font=("Segoe UI", 11, "bold"), command=self.approve_request_action
        ).pack(side="left", padx=10)
        tk.Button(
            button_frame, text="Reject Selected", bg="#922B21", fg="white", width=18,
            font=("Segoe UI", 11, "bold"), command=self.reject_request_action
        ).pack(side="left", padx=10)
        tk.Button(
            button_frame, text="Refresh", bg="#2471A3", fg="white", width=18,
            font=("Segoe UI", 11, "bold"), command=self.refresh_requests_table
        ).pack(side="left", padx=10)

        self.refresh_requests_table()

    def refresh_requests_table(self):
        if not hasattr(self, "requests_tree"):
            return
        for item in self.requests_tree.get_children():
            self.requests_tree.delete(item)
        pending = get_pending_requests()
        for request in pending:
            self.requests_tree.insert(
                "", "end",
                values=(
                    request["id"], request["book_title"], request["student_id"],
                    request["student_name"], request["request_date"]
                )
            )
        if len(pending) == 0:
            self.requests_empty_label.pack(pady=5)
        else:
            self.requests_empty_label.pack_forget()

    def approve_request_action(self):
        selection = self.requests_tree.selection()
        if not selection:
            messagebox.showerror("Selection Error", "Please select a request to approve.")
            return
        request_id = self.requests_tree.item(selection[0], "values")[0]
        success, message = approve_request(request_id, performed_by=self.username)
        if success:
            messagebox.showinfo("Approved", message)
            self.refresh_requests_table()
            self.refresh_dashboard()
        else:
            messagebox.showerror("Cannot Approve", message)

    def reject_request_action(self):
        selection = self.requests_tree.selection()
        if not selection:
            messagebox.showerror("Selection Error", "Please select a request to reject.")
            return
        request_id = self.requests_tree.item(selection[0], "values")[0]
        confirm = messagebox.askyesno("Confirm Rejection", f"Reject request {request_id}?")
        if not confirm:
            return
        success, message = reject_request(request_id, performed_by=self.username)
        if success:
            messagebox.showinfo("Rejected", message)
            self.refresh_requests_table()
        else:
            messagebox.showerror("Cannot Reject", message)

    # ==========================================================
    # REPORTS PAGE (Librarian / Administrator)
    # ==========================================================
    def show_reports_page(self):
        if not self.has_access("reports"):
            self.access_denied()
            return
        self.clear_main_frame()
        self.build_reports_page()

    def build_reports_page(self):
        title = tk.Label(

            self.main_frame, text="Reports & Data Export",
            font=("Segoe UI", 22, "bold"), bg=WINDOW_BG, fg=PRIMARY_COLOR
        )
        title.pack(pady=20)
        report_frame = tk.Frame(self.main_frame, bg="white", padx=20, pady=20)
        report_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.report_text = tk.Text(report_frame, font=("Consolas", 10), wrap="word")
        self.report_text.pack(fill="both", expand=True)

        button_frame = tk.Frame(self.main_frame, bg=WINDOW_BG)
        button_frame.pack(pady=15)
        tk.Button(
            button_frame, text="Generate Report", bg=PRIMARY_COLOR, fg="white",
            font=("Segoe UI", 11, "bold"), width=18, command=self.show_report
        ).pack(side="left", padx=5)
        tk.Button(
            button_frame, text="Export Report (.txt)", bg="#2471A3", fg="white",
            font=("Segoe UI", 11, "bold"), width=20, command=self.export_report_file
        ).pack(side="left", padx=5)
        tk.Button(
            button_frame, text="Export Books CSV", bg="#7D3C98", fg="white",
            font=("Segoe UI", 11, "bold"), width=18, command=self.export_books_action
        ).pack(side="left", padx=5)
        tk.Button(
            button_frame, text="Export Loans CSV", bg="#117864", fg="white",
            font=("Segoe UI", 11, "bold"), width=18, command=self.export_transactions_action
        ).pack(side="left", padx=5)
        self.show_report()

    def show_report(self):
        report = generate_daily_report()
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, report)

    def export_report_file(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if not filepath:
            return
        try:
            export_report(filepath)
            messagebox.showinfo("Success", "Report exported successfully.")
        except Exception as error:
            messagebox.showerror("Export Error", str(error))

    def export_books_action(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not filepath:
            return
        try:
            export_books_csv(filepath)
            messagebox.showinfo("Success", "Book catalog exported successfully.")
        except Exception as error:
            messagebox.showerror("Export Error", str(error))

    # ==========================================================
    # ACTIVITY LOG PAGE (Administrator only)
    # ==========================================================
    def show_activity_page(self):
        if not self.has_access("activity"):
            self.access_denied()
            return
        self.clear_main_frame()
        self.build_activity_page()

    def build_activity_page(self):
        title = tk.Label(
            self.main_frame, text="System Activity Log (Administrator Only)",
            font=("Segoe UI", 22, "bold"), bg=WINDOW_BG, fg=PRIMARY_COLOR
        )
        title.pack(pady=20)
        log_frame = tk.Frame(self.main_frame, bg="white")
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        columns = ("Reference", "Subject", "Action", "Performed By", "Timestamp")
        self.activity_tree = ttk.Treeview(log_frame, columns=columns, show="headings")
        widths = [100, 180, 320, 130, 200]
        for col, width in zip(columns, widths):
            self.activity_tree.heading(col, text=col)
            self.activity_tree.column(col, width=width, anchor="center")
        self.activity_tree.column("Action", anchor="w")
        self.make_sortable(self.activity_tree, columns)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.activity_tree.yview)
        self.activity_tree.configure(yscrollcommand=scrollbar.set)
        self.activity_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        btn_frame = tk.Frame(self.main_frame, bg=WINDOW_BG)
        btn_frame.pack(pady=10)
        tk.Button(
            btn_frame, text="Refresh Activity Log", bg=PRIMARY_COLOR, fg="white",
            font=("Segoe UI", 11, "bold"), width=20, command=self.refresh_activity_log
        ).pack()
        self.refresh_activity_log()

    def refresh_activity_log(self):
        if not hasattr(self, "activity_tree"):
            return
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        for log in reversed(activity_log):
            self.activity_tree.insert(
                "", "end",
                values=(
                    log["reference_id"], log["subject"], log["action"],
                    log.get("performed_by", "Unknown"), log["timestamp"]
                )
            )

    # ==========================================================
    # USER MANAGEMENT PAGE (Administrator only)
    # ==========================================================
    def show_users_page(self):
        if not self.has_access("users"):
            self.access_denied()
            return
        self.clear_main_frame()
        self.build_users_page()

    def build_users_page(self):
        title = tk.Label(
            self.main_frame, text="User Account Management (Administrator Only)",
            font=("Segoe UI", 22, "bold"), bg=WINDOW_BG, fg=PRIMARY_COLOR
        )
        title.pack(pady=20)
        body = tk.Frame(self.main_frame, bg=WINDOW_BG)
        body.pack(fill="both", expand=True, padx=20, pady=5)

        list_frame = tk.LabelFrame(body, text="Existing Accounts", font=("Segoe UI", 11, "bold"), bg="white")
        list_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        columns = ("Username", "Full Name", "Role")
        self.users_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=14)
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=160, anchor="center")
        self.users_tree.pack(fill="both", expand=True, padx=10, pady=10)

        list_btn_frame = tk.Frame(list_frame, bg="white")
        list_btn_frame.pack(pady=(0, 10))
        tk.Button(
            list_btn_frame, text="Delete Selected Account", bg="#7B241C", fg="white",
            font=("Segoe UI", 10, "bold"), command=self.delete_selected_user
        ).pack(side="left", padx=5)
        tk.Button(
            list_btn_frame, text="Change Role of Selected", bg="#2471A3", fg="white",
            font=("Segoe UI", 10, "bold"), command=self.change_role_of_selected
        ).pack(side="left", padx=5)

        form_frame = tk.LabelFrame(body, text="Create New Account", font=("Segoe UI", 11, "bold"), bg="white")
        form_frame.pack(side="left", fill="y", padx=(10, 0))
        inner = tk.Frame(form_frame, bg="white", padx=20, pady=20)
        inner.pack()

        tk.Label(inner, text="Full Name", font=("Segoe UI", 10), bg="white").grid(row=0, column=0, sticky="w", pady=6)
        self.new_fullname_entry = tk.Entry(inner, width=28, font=("Segoe UI", 11))
        self.new_fullname_entry.grid(row=1, column=0, pady=(0, 8))

        tk.Label(inner, text="Username", font=("Segoe UI", 10), bg="white").grid(row=2, column=0, sticky="w", pady=6)
        self.new_username_entry = tk.Entry(inner, width=28, font=("Segoe UI", 11))
        self.new_username_entry.grid(row=3, column=0, pady=(0, 8))

        tk.Label(inner, text="Password", font=("Segoe UI", 10), bg="white").grid(row=4, column=0, sticky="w", pady=6)
        self.new_password_entry = tk.Entry(inner, width=28, font=("Segoe UI", 11), show="*")
        self.new_password_entry.grid(row=5, column=0, pady=(0, 8))

        tk.Label(inner, text="Role", font=("Segoe UI", 10), bg="white").grid(row=6, column=0, sticky="w", pady=6)
        self.new_role_combo = ttk.Combobox(inner, values=ROLE_OPTIONS, width=25, state="readonly")
        self.new_role_combo.set(ROLE_OPTIONS[-1])
        self.new_role_combo.grid(row=7, column=0, pady=(0, 15))

        tk.Button(
            inner, text="Create Account", bg=PRIMARY_COLOR, fg="white", width=24,
            font=("Segoe UI", 10, "bold"), command=self.create_account_action
        ).grid(row=8, column=0, pady=5)
        tk.Label(
            inner, text="Note: you cannot delete your own\naccount or the last Administrator.",
            font=("Segoe UI", 8, "italic"), bg="white", fg="#7F8C8D", justify="left"
        ).grid(row=9, column=0, pady=(15, 0), sticky="w")

        self.refresh_users_table()

    def refresh_users_table(self):
        if not hasattr(self, "users_tree"):
            return
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        for username, info in sorted(USER_ACCOUNTS.items()):
            self.users_tree.insert("", "end", values=(username, info.get("full_name", username), info["role"]))

    def create_account_action(self):
        success, message = create_user_account(
            self.new_username_entry.get(), self.new_password_entry.get(),
            self.new_role_combo.get(), self.new_fullname_entry.get(),
            performed_by=self.username
        )
        if success:
            messagebox.showinfo("Success", message)
            self.new_fullname_entry.delete(0, tk.END)
            self.new_username_entry.delete(0, tk.END)
            self.new_password_entry.delete(0, tk.END)
            self.new_role_combo.set(ROLE_OPTIONS[-1])
            self.refresh_users_table()
        else:
            messagebox.showerror("Validation Error", message)

    def delete_selected_user(self):
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showerror("Selection Error", "Please select an account to delete.")
            return
        target_username = self.users_tree.item(selection[0], "values")[0]
        confirm = messagebox.askyesno(
            "Confirm Deletion", f"Permanently delete the account '{target_username}'?\nThis cannot be undone."
        )
        if not confirm:
            return
        success, message = delete_user_account(target_username, performed_by=self.username)
        if success:
            messagebox.showinfo("Success", message)
            self.refresh_users_table()
        else:
            messagebox.showerror("Cannot Delete", message)

    def change_role_of_selected(self):
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showerror("Selection Error", "Please select an account to change.")
            return
        target_username = self.users_tree.item(selection[0], "values")[0]
        current_role = USER_ACCOUNTS.get(target_username, {}).get("role", ROLE_OPTIONS[-1])
        new_role = self._prompt_role_choice(target_username, current_role)
        if new_role is None:
            return
        success, message = change_user_role(target_username, new_role, performed_by=self.username)
        if success:
            messagebox.showinfo("Success", message)
            self.refresh_users_table()
        else:
            messagebox.showerror("Cannot Change Role", message)

    def _prompt_role_choice(self, target_username, current_role):
        chooser = tk.Toplevel(self.root)
        chooser.title("Change Role")
        chooser.geometry("320x180")
        chooser.configure(bg="white")
        chooser.resizable(False, False)
        tk.Label(
            chooser, text=f"New role for '{target_username}'", font=("Segoe UI", 11, "bold"), bg="white"
        ).pack(pady=(20, 10))
        role_combo = ttk.Combobox(chooser, values=ROLE_OPTIONS, width=25, state="readonly")
        role_combo.set(current_role)
        role_combo.pack(pady=5)
        result = {"role": None}

        def confirm_choice():
            result["role"] = role_combo.get()
            chooser.destroy()

        tk.Button(
            chooser, text="Confirm", bg=PRIMARY_COLOR, fg="white", font=("Segoe UI", 10, "bold"),
            command=confirm_choice
        ).pack(pady=15)
        chooser.transient(self.root)
        chooser.grab_set()
        self.root.wait_window(chooser)
        return result["role"]





