# Restaurant Ordering System (ROS)

FastAPI + SQLAlchemy backend for a restaurant ordering system: customers, menu, inventory,
orders/payments, promo codes, reviews, and manager reports.

Interactive API docs (Swagger UI): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Setup

1. Clone the repo and create a virtual environment (recommended).
2. Install dependencies from the project root:

`ash
pip install -r requirements.txt
`

### Database

By default the app uses a local SQLite file (./ros.db) so you can run without MySQL.

Config lives in pi/dependencies/config.py:

| Setting | Purpose |
|---|---|
| use_sqlite = True | Local SQLite at sqlite_path (default ./ros.db) |
| use_sqlite = False | Use the MySQL settings below it (db_host, db_name, etc.) |

Tables are created automatically on app startup via pi/models/model_loader.py.

---

## Run the server

From the project root:

`ash
uvicorn api.main:app --reload
`

Then open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to try endpoints.

---

## Seed demo data

Populate every table with realistic sample data for demos (low-stock alerts, guest orders,
promo codes, paid revenue, low-rated dishes, etc.):

`ash
python -m api.seed
`

If the database already has rows, re-run with:

`ash
python -m api.seed --force
`

--force clears existing rows, then reseeds.

---

## Tests

Tests run against an isolated in-memory SQLite database (TESTING=1 is set in
pi/tests/conftest.py) and do **not** touch 
os.db / MySQL.

`ash
pytest api/tests
`

Useful variants:

`ash
pytest api/tests -q
pytest api/tests/test_seed.py
pytest api/tests --cov=api
`

---

## Project layout (short)

| Path | Role |
|---|---|
| pi/main.py | FastAPI app entry |
| pi/routers/ | HTTP routes |
| pi/controllers/ | Business logic |
| pi/models/ | SQLAlchemy models |
| pi/schemas/ | Pydantic request/response models |
| pi/seed.py | Demo data seeder |
| pi/tests/ | Pytest suite |

---

## Useful endpoints (after seeding)

| Endpoint | What to try |
|---|---|
| GET /inventory/alerts | Ingredients at or below minimum stock |
| GET /menuitems/?dietary_type=vegan&q=soup | Menu search / dietary filter |
| GET /orders/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD | Orders by date range |
| POST /promocodes/apply | Apply a promo (e.g. WELCOME10) |
| GET /reports/revenue/daily?date=YYYY-MM-DD | Daily paid revenue |
| GET /reports/revenue/trends?start_date=...&end_date=... | Revenue trends |
| GET /reports/low-performing | Low-rated / low-order dishes |
| POST /menuitems/recompute-availability | Refresh menu availability from inventory |
