# Testing Approach — ROS API

## Why this approach

The grading rubric only requires "at least one pytest unit test" that passes, plus
evidence endpoints "work properly." For a solo, ~2-week project, a single layer of
**integration/API tests** covers that bar more efficiently than a full 3-layer pyramid:

- Hitting real HTTP endpoints via `TestClient` already exercises the router, schema,
  and controller code together against a real (in-memory) database — a separate layer
  of pure mocked-controller unit tests would just re-test the same logic in isolation,
  without adding much confidence for the time spent.
- An in-memory SQLite database (isolated from the dev `ros.db` file / MySQL) keeps
  tests fast, repeatable, and side-effect-free, while still validating real SQL
  behavior (constraints, defaults, relationships) instead of mocks.
- One flat test file per feature (`api/tests/test_<name>.py`), with small focused test
  functions per operation (create / read-all / read-one + 404 / update + 404 /
  delete + 404) rather than one giant lifecycle test, so a single broken endpoint
  fails one test instead of masking others.

## How test isolation works

- `api/dependencies/config.py` exposes `conf.testing`, set from the `TESTING` env var.
- `api/dependencies/database.py` checks `conf.testing`: when true, it builds the engine
  from `sqlite:///:memory:` with `StaticPool` (needed so the single in-memory DB is
  shared across the app and test code — a plain `NullPool` would give each connection
  its own throwaway database) instead of pointing at `ros.db`/MySQL.
- `api/tests/conftest.py` sets `TESTING=1` **before** importing `api.main`, since
  `main.py` builds the engine once at import time. It also provides an autouse fixture
  that runs `create_all`/`drop_all` around every test function (full isolation between
  tests) and a `client` (`TestClient`) fixture used by all test files.

This means the test suite never touches your real dev database, and every test starts
from empty tables.

## Status

Done — integration tests exist for all 6 CRUD features built so far (`orders`,
`order_details`, `customers`, `employees`, `inventory`, `menu_items`): 49 tests, all
passing (`pytest api/tests`).

**Standing convention** (also documented in `FEATURES.md`): every future feature work
item adds/updates its own `api/tests/test_<name>.py` in the same branch, so a dedicated
testing catch-up branch shouldn't be needed again.

Still pending / optional, not required for grading:
- An end-to-end smoke test chaining multiple routers in one flow (e.g. create customer
  → create menu item → place order → add order-details → update status), to mirror a
  real user journey rather than one feature at a time.
- `pyproject.toml` with `pytest` markers (`integration`, `e2e`) — only worth adding if
  a second test layer (like the e2e test above) actually gets introduced.
- A small set of mocked-controller unit tests (`pytest-mock`, already installed) for
  tricky error-handling paths (e.g. duplicate-email `SQLAlchemyError` handling) — pure
  stretch goal.
