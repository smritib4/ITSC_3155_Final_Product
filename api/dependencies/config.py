import os


class conf:
    # Use SQLite for local development when MySQL is unavailable.
    # Set use_sqlite = False to use the MySQL settings below.
    use_sqlite = True
    sqlite_path = "./ros.db"

    # Set automatically by api/tests/conftest.py. When true, the app runs
    # against an isolated in-memory SQLite database instead of the dev DB.
    testing = os.getenv("TESTING") == "1"

    db_host = "localhost"
    db_name = "sandwich_maker_api"
    db_port = 3306
    db_user = "root"
    db_password = "Scps85111!"
    app_host = "localhost"
    app_port = 8000
