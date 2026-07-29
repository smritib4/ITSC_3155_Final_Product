import os

# Must be set before anything under `api` (in particular api.dependencies.database)
# is imported, since that module reads this flag once at import time to decide
# which database engine to build.
os.environ["TESTING"] = "1"

import pytest
from fastapi.testclient import TestClient

from ..dependencies.database import Base, engine
from ..main import app


@pytest.fixture(autouse=True)
def reset_database():
    """Give every test function a clean set of empty tables.

    Uses the shared in-memory SQLite engine configured in
    api/dependencies/database.py (active because TESTING=1 above), so tests
    never touch the real dev database (ros.db / MySQL).
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """FastAPI test client wired to the isolated in-memory test database."""
    return TestClient(app)
