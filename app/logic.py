# ==========================================================
# LOGIC
# All backend business logic: validation, book management,
# borrowing/returning, statistics, and user account management.
# This module never imports tkinter - it can be tested or reused
# completely independently of the GUI layer.
# ==========================================================
from datetime import datetime, timedelta

from app.config import LOAN_PERIOD_DAYS, ROLE_OPTIONS
from app.data_store import (
    books_data, transactions_data, activity_log, USER_ACCOUNTS,
    requests_data, next_book_id, next_transaction_id,
    next_request_id, next_student_id, save_data
)


# ==========================================================
# ACTIVITY LOGGER
# ==========================================================
def log_activity(reference_id, subject, action, performed_by="Unknown"):
    activity_log.append({
        "reference_id": reference_id,
        "subject": subject,
        "action": action,
        "performed_by": performed_by,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_data()


# ==========================================================
# ID GENERATORS
# ==========================================================
def generate_book_id():
    book_id = f"BK{next_book_id[0]:04d}"
    next_book_id[0] += 1
    return book_id


def generate_transaction_id():
    transaction_id = f"TX{next_transaction_id[0]:04d}"
    next_transaction_id[0] += 1
    return transaction_id


def generate_student_id():
    student_id = f"STU{next_student_id[0]:04d}"
    next_student_id[0] += 1
    return student_id


def generate_request_id():
    request_id = f"RQ{next_request_id[0]:04d}"
    next_request_id[0] += 1
    return request_id


# ==========================================================
# VALIDATION HELPERS
# ==========================================================
def is_valid_isbn(isbn):
    digits = "".join(ch for ch in isbn if ch.isdigit())
    return len(digits) in (10, 13)


def is_valid_copy_count(value_str):
    try:
        value = int(value_str)
        return value > 0
    except ValueError:
        return False


def is_transaction_overdue(transaction):
    if transaction.get("status") != "Borrowed":
        return False
    try:
        due_date = datetime.strptime(transaction["due_date"], "%Y-%m-%d")
    except (ValueError, KeyError):
        return False
    return datetime.now() > due_date


# ==========================================================
# BOOK MANAGEMENT
# ==========================================================
def add_book(title, author, isbn, category, total_copies, performed_by="Unknown"):
    title = title.strip()
    author = author.strip()
    isbn = isbn.strip()
    total_copies = total_copies.strip()
    if title == "":
        return False, "Book title is required."
    if author == "":
        return False, "Author is required."
    if isbn == "":
        return False, "ISBN is required."
    if not is_valid_isbn(isbn):
        return False, "ISBN must contain either 10 or 13 digits."
    if any(book["isbn"] == isbn for book in books_data):
        return False, f"A book with ISBN '{isbn}' already exists."
    if category == "":
        return False, "Category is required."
    if not is_valid_copy_count(total_copies):
        return False, "Total copies must be a positive whole number."
    book_id = generate_book_id()
    copies = int(total_copies)
    record = {
        "id": book_id,
        "title": title,
        "author": author,
        "isbn": isbn,
        "category": category,
        "total_copies": copies,
        "available_copies": copies,
        "date_added": datetime.now().strftime("%Y-%m-%d")
    }
    books_data.append(record)
    log_activity(book_id, title, "New Book Added to Catalog", performed_by)
    save_data()
    return True, f"{book_id} ('{title}') added successfully."


def update_book(book_id, title, author, isbn, category, total_copies, performed_by="Unknown"):
    book = get_book_by_id(book_id)
    if book is None:
        return False, "Book not found."
    title = title.strip()
    author = author.strip()
    isbn = isbn.strip()
    total_copies = total_copies.strip()
    if title == "":
        return False, "Book title is required."
    if author == "":
        return False, "Author is required."
    if not is_valid_isbn(isbn):
        return False, "ISBN must contain either 10 or 13 digits."
    if any(b["isbn"] == isbn and b["id"] != book_id for b in books_data):
        return False, f"Another book already uses ISBN '{isbn}'."
    if not is_valid_copy_count(total_copies):
        return False, "Total copies must be a positive whole number."
    new_total = int(total_copies)
    currently_borrowed = book["total_copies"] - book["available_copies"]
    if new_total < currently_borrowed:
        return False, (
            f"Cannot set total copies below {currently_borrowed} "
            f"({currently_borrowed} copies are currently on loan)."
        )
    book["title"] = title
    book["author"] = author
    book["isbn"] = isbn
    book["category"] = category
    book["total_copies"] = new_total
    book["available_copies"] = new_total - currently_borrowed
    log_activity(book_id, title, "Book Details Updated", performed_by)
    save_data()
    return True, f"{book_id} updated successfully."


def delete_book(book_id, performed_by="Unknown"):
    book = get_book_by_id(book_id)
    if book is None:
        return False, "Book not found."
    if book["available_copies"] < book["total_copies"]:
        return False, "Cannot delete a book while copies are still on loan."
    books_data.remove(book)
    log_activity(book_id, book["title"], "Book Removed From Catalog", performed_by)
    save_data()
    return True, f"{book_id} ('{book['title']}') removed from catalog."


def get_book_by_id(book_id):
    for book in books_data:
        if book["id"] == book_id:
            return book
    return None


def search_books(keyword):
    keyword = keyword.lower().strip()
    if keyword == "":
        return list(books_data)
    results = []
    for book in books_data:
        if (
            keyword in book["title"].lower()
            or keyword in book["author"].lower()
            or keyword in book["isbn"].lower()
            or keyword in book["category"].lower()
            or keyword in book["id"].lower()
        ):
            results.append(book)
    return results


# ==========================================================
# BORROWING / RETURNING
# ==========================================================
def issue_book(book_id, borrower_name, borrower_id, performed_by="Unknown"):
    borrower_name = borrower_name.strip()
    borrower_id = borrower_id.strip()
    if borrower_name == "":
        return False, "Borrower name is required."
    if borrower_id == "":
        return False, "Borrower ID is required."
    book = get_book_by_id(book_id)
    if book is None:
        return False, "Book not found."
    if book["available_copies"] <= 0:
        return False, f"No available copies of '{book['title']}' to issue."
    issue_date = datetime.now()
    due_date = issue_date + timedelta(days=LOAN_PERIOD_DAYS)
    transaction_id = generate_transaction_id()
    record = {
        "id": transaction_id,
        "book_id": book["id"],
        "book_title": book["title"],
        "borrower_name": borrower_name,
        "borrower_id": borrower_id,
        "issue_date": issue_date.strftime("%Y-%m-%d"),
        "due_date": due_date.strftime("%Y-%m-%d"),
        "return_date": "",
        "status": "Borrowed"
    }
    transactions_data.append(record)
    book["available_copies"] -= 1
    log_activity(
        transaction_id, book["title"],
        f"Book Issued to {borrower_name} (Due {due_date.strftime('%Y-%m-%d')})",
        performed_by
    )
    save_data()
    return True, f"{transaction_id}: '{book['title']}' issued to {borrower_name}, due {due_date.strftime('%Y-%m-%d')}."


def return_book(transaction_id, performed_by="Unknown"):
    transaction = get_transaction_by_id(transaction_id)
    if transaction is None:
        return False, "Transaction not found."
    if transaction["status"] == "Returned":
        return False, "This book has already been returned."
    book = get_book_by_id(transaction["book_id"])
    transaction["status"] = "Returned"
    transaction["return_date"] = datetime.now().strftime("%Y-%m-%d")
    if book is not None:
        book["available_copies"] = min(book["available_copies"] + 1, book["total_copies"])
    log_activity(
        transaction_id, transaction["book_title"],
        f"Book Returned by {transaction['borrower_name']}", performed_by
    )
    save_data()
    return True, f"{transaction_id}: '{transaction['book_title']}' marked as returned."


def get_transaction_by_id(transaction_id):
    for transaction in transactions_data:
        if transaction["id"] == transaction_id:
            return transaction
    return None


def get_transactions_for_borrower(borrower_id):
    return [t for t in transactions_data if t["borrower_id"] == borrower_id]


def refresh_overdue_statuses():
    """Sweep all 'Borrowed' transactions and flip any that are past
    their due date to 'Overdue'. Called whenever data is displayed
    so the status always reflects the current date."""
    changed = False
    for transaction in transactions_data:
        if transaction["status"] == "Borrowed" and is_transaction_overdue(transaction):
            transaction["status"] = "Overdue"
            changed = True
    if changed:
        save_data()


# ==========================================================
# DASHBOARD / LIBRARY STATISTICS
# ==========================================================
def get_library_statistics():
    refresh_overdue_statuses()
    total_titles = len(books_data)
    total_copies = sum(book["total_copies"] for book in books_data)
    available_copies = sum(book["available_copies"] for book in books_data)
    borrowed_copies = total_copies - available_copies
    borrowed = 0
    returned = 0
    overdue = 0
    for transaction in transactions_data:
        status = transaction["status"]
        if status == "Borrowed":
            borrowed += 1
        elif status == "Returned":
            returned += 1
        elif status == "Overdue":
            overdue += 1
    return {
        "total_titles": total_titles,
        "total_copies": total_copies,
        "available_copies": available_copies,
        "borrowed_copies": borrowed_copies,
        "borrowed": borrowed,
        "returned": returned,
        "overdue": overdue,
        "total_transactions": len(transactions_data)
    }


def get_category_breakdown():
    from app.config import BOOK_CATEGORIES
    counts = {category: 0 for category in BOOK_CATEGORIES}
    for book in books_data:
        category = book.get("category", "")
        if category in counts:
            counts[category] += 1
    return counts


# ==========================================================
# DAILY REPORT GENERATOR
# ==========================================================
def generate_daily_report():
    stats = get_library_statistics()
    report = []
    report.append("=" * 60)
    report.append(" LIBRARYSYS DAILY REPORT ")
    report.append("=" * 60)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    report.append(f"Total Book Titles: {stats['total_titles']}")
    report.append(f"Total Copies in Library: {stats['total_copies']}")
    report.append(f"Available Copies: {stats['available_copies']}")
    report.append(f"Copies Currently Borrowed: {stats['borrowed_copies']}")
    report.append("")
    report.append(f"Active Loans (Borrowed): {stats['borrowed']}")
    report.append(f"Overdue Loans: {stats['overdue']}")
    report.append(f"Completed Loans (Returned): {stats['returned']}")
    report.append(f"Total Transactions Recorded: {stats['total_transactions']}")
    report.append("")
    report.append("RECENT ACTIVITY")
    report.append("-" * 60)
    for item in activity_log[-15:]:
        report.append(
            f"{item['timestamp']} | {item['reference_id']} | "
            f"{item['subject']} | by {item.get('performed_by', 'Unknown')} | "
            f"{item['action']}"
        )
    return "\n".join(report)


def export_report(filepath):
    report = generate_daily_report()
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(report)


def export_books_csv(filepath):
    import csv
    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Book ID", "Title", "Author", "ISBN", "Category",
            "Total Copies", "Available Copies", "Date Added"
        ])
        for book in books_data:
            writer.writerow([
                book["id"], book["title"], book["author"], book["isbn"],
                book["category"], book["total_copies"], book["available_copies"],
                book["date_added"]
            ])


def export_transactions_csv(filepath):
    import csv
    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Transaction ID", "Book Title", "Borrower Name", "Borrower ID",
            "Issue Date", "Due Date", "Return Date", "Status"
        ])
        for transaction in transactions_data:
            writer.writerow([
                transaction["id"], transaction["book_title"], transaction["borrower_name"],
                transaction["borrower_id"], transaction["issue_date"], transaction["due_date"],
                transaction.get("return_date", ""), transaction["status"]
            ])


# ==========================================================
# USER ACCOUNT MANAGEMENT (Administrator only)
# ==========================================================
def count_administrators():
    return sum(1 for account in USER_ACCOUNTS.values() if account["role"] == "Administrator")


def create_user_account(username, password, role, full_name, performed_by="Unknown"):
    username = username.strip()
    password = password.strip()
    full_name = full_name.strip()
    if username == "":
        return False, "Username is required."
    if password == "":
        return False, "Password is required."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."
    if username in USER_ACCOUNTS:
        return False, f"Username '{username}' already exists."
    if role not in ROLE_OPTIONS:
        return False, "Invalid role selected."
    if full_name == "":
        full_name = username
    USER_ACCOUNTS[username] = {"password": password, "role": role, "full_name": full_name}
    log_activity("-", username, f"User Account Created (Role: {role})", performed_by)
    save_data()
    return True, f"Account '{username}' created successfully."


def delete_user_account(username, performed_by="Unknown"):
    if username not in USER_ACCOUNTS:
        return False, "Account not found."
    if username == performed_by:
        return False, "You cannot delete your own account while logged in."
    if USER_ACCOUNTS[username]["role"] == "Administrator" and count_administrators() <= 1:
        return False, "Cannot delete the last remaining Administrator account."
    del USER_ACCOUNTS[username]
    log_activity("-", username, "User Account Deleted", performed_by)
    save_data()
    return True, f"Account '{username}' deleted successfully."


def change_user_role(username, new_role, performed_by="Unknown"):
    if username not in USER_ACCOUNTS:
        return False, "Account not found."
    if new_role not in ROLE_OPTIONS:
        return False, "Invalid role selected."
    old_role = USER_ACCOUNTS[username]["role"]
    if old_role == "Administrator" and new_role != "Administrator" and count_administrators() <= 1:
        return False, "Cannot change the role of the last remaining Administrator."
    USER_ACCOUNTS[username]["role"] = new_role
    log_activity("-", username, f"Role Changed: {old_role} -> {new_role}", performed_by)
    save_data()
    return True, f"'{username}' role changed to {new_role}."


# ==========================================================
# STUDENT REGISTRATION (Administrator / Librarian)
# A student account's username IS its auto-generated Student ID,
# so a student's login username always doubles as their borrower ID.
# ==========================================================
def register_student(full_name, performed_by="Unknown"):
    full_name = full_name.strip()
    if full_name == "":
        return False, "Student full name is required.", None
    student_id = generate_student_id()
    while student_id in USER_ACCOUNTS:
        student_id = generate_student_id()
    password = student_id  # simple default password = their ID; they can be told to change it
    USER_ACCOUNTS[student_id] = {
        "password": password,
        "role": "Student",
        "full_name": full_name
    }
    log_activity(student_id, full_name, "Student Registered", performed_by)
    save_data()
    return True, f"Student registered. ID: {student_id}  Password: {password}", student_id


def get_all_students():
    return [
        {"student_id": username, "full_name": info.get("full_name", username)}
        for username, info in USER_ACCOUNTS.items() if info.get("role") == "Student"
    ]


# ==========================================================
# BOOK REQUEST WORKFLOW (Student requests -> Admin/Librarian approves)
# ==========================================================
def request_book(student_id, book_id, performed_by="Unknown"):
    student_id = student_id.strip()
    account = USER_ACCOUNTS.get(student_id)
    if account is None or account.get("role") != "Student":
        return False, "Only registered students may request books."
    book = get_book_by_id(book_id)
    if book is None:
        return False, "Book not found."
    if book["available_copies"] <= 0:
        return False, f"'{book['title']}' has no available copies right now. Please try again later."
    already_borrowed = any(
        t["borrower_id"] == student_id and t["book_id"] == book_id and t["status"] in ("Borrowed", "Overdue")
        for t in transactions_data
    )
    if already_borrowed:
        return False, f"You already have '{book['title']}' on loan."
    duplicate_pending = any(
        r["student_id"] == student_id and r["book_id"] == book_id and r["status"] == "Pending"
        for r in requests_data
    )
    if duplicate_pending:
        return False, f"You already have a pending request for '{book['title']}'."
    request_id = generate_request_id()
    record = {
        "id": request_id,
        "book_id": book["id"],
        "book_title": book["title"],
        "student_id": student_id,
        "student_name": account.get("full_name", student_id),
        "status": "Pending",
        "request_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "transaction_id": ""
    }
    requests_data.append(record)
    log_activity(request_id, book["title"], f"Book Requested by {record['student_name']}", performed_by)
    save_data()
    return True, f"{request_id}: request for '{book['title']}' submitted. Awaiting approval."


def get_request_by_id(request_id):
    for request in requests_data:
        if request["id"] == request_id:
            return request
    return None


def get_pending_requests():
    return [r for r in requests_data if r["status"] == "Pending"]


def get_requests_for_student(student_id):
    return [r for r in requests_data if r["student_id"] == student_id]


def approve_request(request_id, performed_by="Unknown"):
    request = get_request_by_id(request_id)
    if request is None:
        return False, "Request not found."
    if request["status"] != "Pending":
        return False, f"This request has already been {request['status'].lower()}."
    success, message = issue_book(
        request["book_id"], request["student_name"], request["student_id"],
        performed_by=performed_by
    )
    if not success:
        return False, message
    request["status"] = "Approved"
    request["transaction_id"] = transactions_data[-1]["id"]
    log_activity(
        request_id, request["book_title"],
        f"Book Request Approved for {request['student_name']}", performed_by
    )
    save_data()
    return True, f"{request_id} approved. {message}"


def reject_request(request_id, performed_by="Unknown"):
    request = get_request_by_id(request_id)
    if request is None:
        return False, "Request not found."
    if request["status"] != "Pending":
        return False, f"This request has already been {request['status'].lower()}."
    request["status"] = "Rejected"
    log_activity(
        request_id, request["book_title"],
        f"Book Request Rejected for {request['student_name']}", performed_by
    )
    save_data()
    return True, f"{request_id} rejected."
