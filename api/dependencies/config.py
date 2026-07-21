class conf:
    # Use SQLite for local development when MySQL is unavailable.
    # Set use_sqlite = False to use the MySQL settings below.
    use_sqlite = True
    sqlite_path = "./ros.db"

    db_host = "localhost"
    db_name = "sandwich_maker_api"
    db_port = 3306
    db_user = "root"
    db_password = "Scps85111!"
    app_host = "localhost"
    app_port = 8000
