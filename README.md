# Restaurant Ordering System (ROS)

FastAPI + SQLAlchemy backend for a restaurant ordering system: customers, menu, inventory,
orders/payments, promo codes, reviews, and manager reports.

Interactive API docs (Swagger UI): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Setup

1. Clone the repo and create a virtual environment (recommended).
2. Install dependencies from the project root:

```bash
pip install -r requirements.txt
```

### Database

By default the app uses a local SQLite file (`./ros.db`) so you can run without MySQL.

Config lives in `api/dependencies/config.py`:

| Setting | Purpose |
|---|---|
| `use_sqlite = True` | Local SQLite at `sqlite_path` (default `./ros.db`) |
| `use_sqlite = False` | Use the MySQL settings below it (`db_host`, `db_name`, etc.) |

Tables are created automatically on app startup via `api/models/model_loader.py`.

---

## Run the server

From the project root:

```bash
uvicorn api.main:app --reload
```

Then open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to try endpoints.

---

## Seed demo data

Populate every table with realistic sample data for demos (low-stock alerts, guest orders,
promo codes, paid revenue, low-rated dishes, etc.):

```bash
python -m api.seed
```

If the database already has rows, re-run with:

```bash
python -m api.seed --force
```

`--force` clears existing rows, then reseeds.

---

## Tests

Tests run against an isolated in-memory SQLite database (`TESTING=1` is set in
`api/tests/conftest.py`) and do **not** touch `ros.db` / MySQL.

```bash
pytest api/tests
```

Useful variants:

```bash
pytest api/tests -q
pytest api/tests/test_seed.py
pytest api/tests --cov=api
```

---

## Project layout (short)

| Path | Role |
|---|---|
| `api/main.py` | FastAPI app entry |
| `api/routers/` | HTTP routes |
| `api/controllers/` | Business logic |
| `api/models/` | SQLAlchemy models |
| `api/schemas/` | Pydantic request/response models |
| `api/seed.py` | Demo data seeder |
| `api/tests/` | Pytest suite |

---

## Planning documents

| Document | Contents |
|---|---|
| `FEATURES.md` | User stories mapped to the endpoints that implement them |
| `PROJECT_TASKS.md` | Sprint task breakdown and status |
| `TEST_PLAN.md` | Test strategy and coverage notes |

---

## Useful endpoints (after seeding)

| Endpoint | What to try |
|---|---|
| `GET /inventory/alerts` | Ingredients at or below minimum stock |
| `GET /menuitems/?dietary_type=vegan&q=soup` | Menu search / dietary filter |
| `GET /orders/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` | Orders by date range |
| `POST /promocodes/apply` | Apply a promo (e.g. `WELCOME10`) |
| `GET /reports/revenue/daily?date=YYYY-MM-DD` | Daily paid revenue |
| `GET /reports/revenue/trends?start_date=...&end_date=...` | Revenue trends |
| `GET /reports/low-performing` | Low-rated / low-order dishes |
| `POST /menuitems/recompute-availability` | Refresh menu availability from inventory |
