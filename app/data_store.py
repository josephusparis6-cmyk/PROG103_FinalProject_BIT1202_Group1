# ==========================================================
# DATA STORE
# Holds the application's in-memory data and handles saving it to,
# and loading it from, a local JSON file. Nothing in this module
# knows about tkinter - it is pure data plumbing.
# ==========================================================
import json
import os
import copy
from app.config import DATA_FILE, DEFAULT_USER_ACCOUNTS

# ----------------------------------------------------------
# GLOBAL DATA
# ----------------------------------------------------------
books_data = []          # one record per book title
transactions_data = []   # one record per borrow/return event
requests_data = []       # one record per student book request (Pending/Approved/Rejected)
activity_log = []        # full audit trail of staff/admin actions
USER_ACCOUNTS = copy.deepcopy(DEFAULT_USER_ACCOUNTS)
next_book_id = [1]
next_transaction_id = [1]
next_request_id = [1]
next_student_id = [1]


def save_data():
    """Atomic write: write to a temp file then replace, so a crash
    mid-save can never leave data.json half-written/corrupted."""
    try:
        data = {
            "books": books_data,
            "transactions": transactions_data,
            "requests": requests_data,
            "activity_log": activity_log,
            "next_book_id": next_book_id[0],
            "next_transaction_id": next_transaction_id[0],
            "next_request_id": next_request_id[0],
            "next_student_id": next_student_id[0],
            "user_accounts": USER_ACCOUNTS
        }
        temp_path = DATA_FILE + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        os.replace(temp_path, DATA_FILE)
    except Exception as error:
        print("Save Error:", error)


def load_data():
    global books_data, transactions_data, requests_data, activity_log
    if not os.path.exists(DATA_FILE):
        return
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        books_data[:] = data.get("books", [])
        transactions_data[:] = data.get("transactions", [])
        requests_data[:] = data.get("requests", [])
        activity_log[:] = data.get("activity_log", [])
        next_book_id[0] = data.get("next_book_id", 1)
        next_transaction_id[0] = data.get("next_transaction_id", 1)
        next_request_id[0] = data.get("next_request_id", 1)
        next_student_id[0] = data.get("next_student_id", 1)
        saved_accounts = data.get("user_accounts")
        if saved_accounts:
            USER_ACCOUNTS.clear()
            USER_ACCOUNTS.update(saved_accounts)
    except Exception as error:
        print("Load Error:", error)
