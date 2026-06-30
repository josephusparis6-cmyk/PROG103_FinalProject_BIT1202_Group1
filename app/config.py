# ==========================================================
# CONFIG
# Application-wide constants: settings, lists, roles, navigation.
# Pure configuration - no filesystem or GUI code lives here.
# ==========================================================

# ----------------------------------------------------------
# APPLICATION SETTINGS
# ----------------------------------------------------------
APP_TITLE = "LibrarySys - Limkokwing Library Management System"
DATA_FILE = "data.json"
WINDOW_BG = "#043744"
PRIMARY_COLOR = "#FFB507"      # deep academic blue
SECONDARY_COLOR = "#021D43"
ACCENT_COLOR = "#000000"       # gold/brass accent (library plaque feel)
LOAN_PERIOD_DAYS = 14          # how many days a book may be borrowed before it is overdue

# ----------------------------------------------------------
# SYSTEM LISTS
# ----------------------------------------------------------
BOOK_CATEGORIES = [
    "Fiction",
    "Non-Fiction",
    "Science & Technology",
    "Mathematics",
    "History",
    "Reference",
    "Periodicals"
]
TRANSACTION_STATUS_OPTIONS = [
    "Borrowed",
    "Returned",
    "Overdue"
]
TRANSACTION_STATUS_FILTER_OPTIONS = ["All"] + TRANSACTION_STATUS_OPTIONS
CATEGORY_FILTER_OPTIONS = ["All"] + BOOK_CATEGORIES
REQUEST_STATUS_OPTIONS = ["Pending", "Approved", "Rejected"]

# ----------------------------------------------------------
# DEFAULT USER ACCOUNTS
# ----------------------------------------------------------
# Starting point only - once the app has run once, the live set of
# accounts lives in data_store.USER_ACCOUNTS and is persisted to disk.
# ----------------------------------------------------------
DEFAULT_USER_ACCOUNTS = {
    "admin": {
        "password": "admin123",
        "role": "Administrator",
        "full_name": "System Administrator"
    },
    "librarian": {
        "password": "lib2026",
        "role": "Librarian",
        "full_name": "Head Librarian"
    },
    "student": {
        "password": "student123",
        "role": "Student",
        "full_name": "Demo Student"
    }
}

# ----------------------------------------------------------
# ROLE-BASED ACCESS CONTROL
# ----------------------------------------------------------
ROLE_PERMISSIONS = {
    "Administrator": {"dashboard", "catalog", "manage_books", "register_student", "requests", "issue", "return", "history", "reports", "activity", "users"},
    "Librarian":      {"dashboard", "catalog", "manage_books", "register_student", "requests", "issue", "return", "history", "reports"},
    "Student":        {"dashboard", "catalog", "my_history"}
}
ROLE_OPTIONS = ["Administrator", "Librarian", "Student"]
ROLE_BADGE_COLOR = {
    "Administrator": "#D4AF37",
    "Librarian": "#85C1E9",
    "Student": "#D5DBDB"
}
# NAV_PAGES is intentionally split: Students see "my_history" (their own
# loans/requests only) while staff see "history" (every transaction in the system).
NAV_PAGES = [
    ("dashboard", "Dashboard"),
    ("catalog", "Book Catalog"),
    ("manage_books", "Manage Books"),
    ("register_student", "Register Student"),
    ("requests", "Book Requests"),
    ("issue", "Issue Book"),
    ("return", "Return Book"),
    ("history", "Borrow History"),
    ("my_history", "My Books"),
    ("reports", "Reports"),
    ("activity", "Activity Log"),
    ("users", "User Management")
]
