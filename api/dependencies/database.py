from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from .config import conf
from urllib.parse import quote_plus

if conf.testing:
    # Isolated in-memory database used only by the pytest suite. StaticPool
    # keeps a single shared connection alive so every session (app + test
    # code) sees the same in-memory tables for the life of the process.
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
elif conf.use_sqlite:
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{conf.sqlite_path}"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    SQLALCHEMY_DATABASE_URL = (
        f"mysql+pymysql://{conf.db_user}:{quote_plus(conf.db_password)}"
        f"@{conf.db_host}:{conf.db_port}/{conf.db_name}?charset=utf8mb4"
    )
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
