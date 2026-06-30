# LibrarySys — Limkokwing Library Management System

A desktop GUI application built in Python (tkinter) for managing a university library's book catalog and borrowing process. Built as a Final Project for **PROG103: Principles of Structured Programming** at Limkokwing University of Creative Technology, Sierra Leone.

> Aligned with **UN Sustainable Development Goal 4: Quality Education** — reliable access to learning materials is foundational to quality education, and a structured borrowing system reduces lost books, untracked loans, and wasted staff time that would otherwise come out of a library's ability to serve students.

---

## 📌 Problem It Solves

Without a digital system, a small library's book records, borrower records, and due dates live in scattered notebooks or nowhere at all. Nobody can answer "how many copies of this book are available right now?", "who currently has it?", or "is it overdue?" without manually flipping through paper logs. LibrarySys gives a Librarian or Administrator a single source of truth for the catalog and every active or past loan, and gives Students a way to check what's available and what they personally currently have out.

## ✨ Features

- **Role-based access control** — Administrator, Librarian, and Student accounts each see a different sidebar and a different set of pages.
- **Book Catalog** — searchable/filterable by title, author, ISBN, or category, with colour-coded stock levels (none available / low stock).
- **Manage Books** *(Librarian/Admin)* — add, edit, or remove book titles, with safeguards (can't delete a book while copies are on loan, can't reduce total copies below the number currently borrowed).
- **Issue Book** *(Librarian/Admin)* — issue any available copy to a named borrower with a 14-day loan period, automatically calculating the due date.
- **Return Book** *(Librarian/Admin)* — mark an active loan as returned; the book's available count updates automatically.
- **Borrow History** *(Librarian/Admin)* — every transaction ever recorded, filterable by status (Borrowed/Returned/Overdue), with CSV export.
- **My Borrow History** *(Student)* — students can look up their own loan history by Borrower ID; they cannot see anyone else's.
- **Dashboard** — live KPI cards (titles, total copies, available, on loan, overdue, returned all-time), a recent activity feed, a books-by-category breakdown chart, and a loan-status breakdown chart.
- **Reports** *(Librarian/Admin)* — generate and export a daily summary report (.txt), plus full CSV exports of the book catalog and the transaction history.
- **Activity Log** *(Administrator only)* — a full audit trail of every action taken in the system and who performed it.
- **User Management** *(Administrator only)* — create new staff/student accounts, change a user's role, or delete an account, with built-in safeguards (can't delete your own account or the last remaining Administrator).
- **Automatic overdue detection** — any active loan past its due date is automatically reclassified as "Overdue" wherever loan status is displayed.
- **Persistent storage** — all data (catalog, transactions, accounts, activity log) is saved locally to `data.json` using an atomic write (write-then-replace) so the file can't be left corrupted by an interrupted save.

## 🖥️ Tech Stack

- **Language:** Python 3
- **GUI:** tkinter / ttk (standard library — no external GUI dependencies)
- **Data storage:** JSON (local file, `data.json`)
- **Export formats:** CSV, plain text

## 📂 Project Structure

This project is organised as a proper Python package rather than a single file, separating configuration, data persistence, business logic, and GUI layers:

```
librarysys/
├── main.py                    # entry point — python3 main.py
├── app/
│   ├── __init__.py
│   ├── config.py                # constants, lists, roles, navigation
│   ├── data_store.py            # in-memory data + save/load to data.json
│   ├── logic.py                 # all backend business logic (no tkinter here)
│   └── gui/
│       ├── __init__.py
│       ├── login_window.py        # login screen
│       ├── main_app.py            # app shell: header, sidebar, routing
│       └── pages.py               # every page's content (mixed into main_app)
├── data.json                  # auto-generated on first save (not tracked in git)
├── README.md
├── LICENSE
└── .gitignore
```

Splitting the code this way means `app/logic.py` has zero dependency on tkinter and could be tested or reused completely independently of the GUI — a deliberate demonstration of separating program logic from the interface.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or later (tkinter ships with most standard Python installations)

### Installation & Run

```bash
# Clone the repository
git clone https://github.com/<your-username>/librarysys.git
cd librarysys

# Run the application
python3 main.py
```

No external packages are required — the project uses only Python's standard library (`tkinter`, `json`, `csv`, `os`, `datetime`).

### Demo Accounts

| Role          | Username     | Password      | Access                                            |
|---------------|--------------|---------------|----------------------------------------------------|
| Administrator | `admin`      | `admin123`    | Full access, including Activity Log and User Management |
| Librarian     | `librarian`  | `lib2026`     | Catalog, Manage Books, Issue/Return, History, Reports |
| Student       | `student`    | `student123`  | Catalog (browse only) and My Borrow History         |

> Note: user accounts are stored in `data.json` once the app has been run, so any accounts created via **User Management** (Administrator only) will persist across restarts.

## 🧱 Structured Programming Principles Applied

- **Variables & constants** for configuration (`LOAN_PERIOD_DAYS`, `BOOK_CATEGORIES`, `ROLE_PERMISSIONS`, etc.)
- **Multiple data types** — strings, integers, booleans, lists, and dictionaries
- **Decision structures** (`if` / `elif` / `else`) for validation, access control, and loan status logic
- **Iteration** (`for` loops) for searching, filtering, totalling, and populating every table in the interface
- **94 user-defined functions/methods** across 7 files, with backend logic (`app/logic.py`) fully separated from the GUI layer (`app/gui/`)

## 🔐 Data, Privacy & Compliance

- Only the minimum personal data needed (borrower name, borrower ID) is collected for a loan record.
- Data is stored locally in a human-readable, exportable format (JSON → CSV/TXT), avoiding lock-in to any proprietary format.
- The Activity Log tracks staff/admin actions for accountability; Students can only ever view their own borrow history, never anyone else's.

## 📄 License

This project is licensed under the [MIT License](LICENSE) — see the LICENSE file for details.

## 🎓 Academic Context

- **Module:** PROG103 — Principles of Structured Programming
- **Institution:** Limkokwing University of Creative Technology, Sierra Leone
- **Semester:** 02, March 2026 – July 2026
