# Project Tasks — Restaurant Ordering System (ROS)

> Solo project · Restaurant Ordering System (ROS) · Repo: `3155-ROS`
> This document lists **everything that needs to be completed** to satisfy the technical
> requirements and deliverables, with each feature traced to a product-backlog user story
> (§8). Producing the agile deliverables themselves (sprint backlog, sprint reviews, and
> updated product backlog/user stories docs) is intentionally **out of scope** here.

---

## 1. Core Technical Requirements (from project instructions)

- [ ] **CRUD operations for ALL tables** (Create, Read-all, Read-one, Update, Delete).
- [ ] Every endpoint must **work properly** and be traceable to a user story.
- [ ] At least **one pytest unit test** — and all tests must **pass**.
- [ ] Populate the DB with enough sample data to demo every feature.
- [ ] Conventional commit messages, all work on `feature/feature-name` branches.
- [ ] Final product must address the provided evaluation checklist questions.

---

## 2. Current State of the Skeleton

**Stack:** FastAPI + SQLAlchemy + PyMySQL (MySQL), vertical-slice layout
(`models/` → `schemas/` → `controllers/` → `routers/`, registered in `routers/index.py`
and `models/model_loader.py`).

| Table / Model | Model | Schema | Controller | Router | Registered | CRUD status |
|---|---|---|---|---|---|---|
| `orders` | ✅ | ✅ | ✅ | ✅ | ✅ | Full CRUD working (verified) |
| `order_details` (OrderItem) | ❌ missing | ❌ missing | ⚠️ broken | ✅ | ✅ | Model + schema missing → **crashes app** |
| `customers` | ✅ | ✅ | ❌ | ❌ | ❌ | No CRUD |
| `restaurant_employees` | ✅ | ✅ | ❌ | ❌ | ❌ | No CRUD |
| `inventory` | ✅ | ✅ | ❌ | ❌ | ❌ | No CRUD |
| `menu_items` | ✅ | ✅ | ❌ | ❌ | ❌ | No CRUD |
| `menu_item_inventory` | ✅ | ✅ | ❌ | ❌ | ❌ | No CRUD |
| `payments` | ✅ | ✅ | ❌ | ❌ | ❌ | No CRUD |
| `promo_codes` | ✅ | ✅ | ❌ | ❌ | ❌ | No CRUD |
| `reports` | ✅ | ✅ | ❌ | ❌ | ❌ | No CRUD |
| `restaurant_managers` | ✅ | ✅ | ❌ | ❌ | ❌ | No CRUD |
| `reviews` | ✅ | ✅ | ❌ | ❌ | ❌ | No CRUD |

**Reference pattern to copy:** `models/orders.py` → `schemas/orders.py` →
`controllers/orders.py` → `routers/orders.py` (fix the bugs noted below first).

---

## 3. Blocking Bugs to Fix First (app won't run until these are resolved)

These prevent the app from starting or make existing endpoints fail. Fix on a dedicated
branch (e.g. `feature/fix-skeleton-bugs`) before building new features.

- [x] **`order_details` model + schema missing.** `controllers/order_details.py` and
  `routers/order_details.py` import `models.order_details` (`model.OrderDetail`) and
  `schemas.order_details`, but neither file exists → import error crashes the whole app.
  `menu_item.py` also references `relationship("OrderItem")`, and `Order` has no
  `order_items` relationship. Create the `OrderItem`/order_details model + schema (linking
  `orders` ↔ `menu_items` with quantity), add the relationship on `Order`, and register it
  in `model_loader.py`.
- [x] **`controllers/orders.py` is a template stub** — references `customer_name`,
  `description`, and `model.Order.id`, none of which exist on the real `Order` model
  (PK is `orderID`). Rewrite to match the actual `Order` columns. *(Fixed in
  `feature/orders_crud`.)*
- [ ] **`controllers/order_details.py` is a template stub** — references `sandwich_id`,
  `amount`, `.id`. Rewrite to match the real order-details model.
- [x] **Broken foreign keys (column-name mismatches):**
  - `orders.py`: FK `restaurant_employees.employeeID` — actual PK is `id` (there is also a
    string `employee_id`). Pick the correct target and align.
  - `promo_codes.py`: FK `restaurant_managers.managerID` — actual PK is `manager_id`.
  - `review.py`: FK `customers.CustomerID` — actual PK is `customerID` (case mismatch).
- [x] **Relationship back_populates mismatch:** `inventory.py` defines
  `menu_items_links` but `menu_item_inventory.py`'s `ingredient` relationship points to
  `menu_item_links`. Names must match on both sides or the mapper errors out.
- [x] **`review.py` schema/model field mismatch:** schema uses `item_id`, model column is
  `item_ID`. Align them.
- [ ] **`tests/test_orders.py` is broken** — asserts `customer_name`/`description`. Rewrite
  to match the corrected orders controller/model.
- [x] **`email-validator` not installed / not in `requirements.txt`** — `schemas/customer.py`
  and `schemas/restaurant_manager.py` use pydantic `EmailStr`, which fails to import without
  it. Add `email-validator` to `requirements.txt` and install.
- [x] **`inventory.py` `onupdate=datetime.now()`** (line 15) is called with parentheses, so
  it's evaluated once at import instead of per-update. Change to `onupdate=datetime.now`.
- [ ] **Missing `*Update` schemas** — add `CustomerUpdate` (`schemas/customer.py`) and
  `ReviewUpdate` (`schemas/review.py`) for their PUT endpoints.
- [x] **DB config** (`dependencies/config.py`) has hardcoded MySQL credentials and leftover
  DB name `sandwich_maker_api`. Confirm a working DB (or switch to SQLite for local
  dev/testing) so the app and tests can run.

---

## 4. CRUD Feature Work (per table)

Each feature = new `controllers/<name>.py` + `routers/<name>.py` (full CRUD), register the
router in `routers/index.py`, and confirm the model is in `model_loader.py`. Follow the
`orders` slice as the template. Each gets its own branch. **Story IDs** reference the
product backlog in §8 for traceability.

- [x] **`feature/orders-crud`** — fix + verify orders CRUD (see bugs above). *(Stories 7, 20, 21, 22, 23)*
- [ ] **`feature/order-details-crud`** — create model + schema + controller + router. *(Stories 8, 22)*
- [ ] **`feature/customers-crud`** — controller + router (schema exists). *(Stories 16, 17)*
- [ ] **`feature/employees-crud`** — controller + router (schema exists). *(supporting/admin CRUD)*
- [ ] **`feature/inventory-crud`** — controller + router (schema exists). *(Stories 4, 5)*
- [ ] **`feature/menu-items-crud`** — controller + router (schema exists). *(Stories 1, 2, 3, 6)*
- [ ] **`feature/menu-item-inventory-crud`** — controller + router (composite PK
  `item_id` + `ingredient_id`; read-one/update/delete need both keys). *(Story 4)*
- [ ] **`feature/payments-crud`** — controller + router (schema exists). *(Stories 18, 19)*
- [ ] **`feature/promo-codes-crud`** — controller + router (string PK `promoCode`). *(Stories 12, 13, 28)*
- [ ] **`feature/reports-crud`** — controller + router (schema exists). *(Stories 10, 14, 15)*
- [ ] **`feature/restaurant-managers-crud`** — controller + router (schema exists). *(supporting/admin CRUD)*
- [ ] **`feature/reviews-crud`** — controller + router (schema exists). *(Stories 11, 26, 27)*

### 4a. Business-logic endpoints (beyond plain CRUD)

Some stories need custom query/logic endpoints in addition to standard CRUD:

- [ ] **`feature/inventory-alerts`** — insufficient-ingredient alert / low-stock endpoint. *(Story 4)*
- [ ] **`feature/menu-auto-disable`** — auto-set `is_available=False` when an item's
  ingredients are out of stock. *(Story 6)*
- [ ] **`feature/orders-filter-date`** — filter orders by date range endpoint. *(Story 9)*
- [ ] **`feature/menu-search`** — search/filter menu by dietary type + keyword search. *(Stories 24, 25)*
- [ ] **`feature/revenue-reports`** — daily revenue total + revenue trends. *(Stories 14, 15)*
- [ ] **`feature/promo-apply`** — apply promo code at checkout (discount calc). *(Story 28)*
- [ ] **`feature/low-performing-dishes`** — identify low-performing dishes from reviews/sales. *(Story 10)*

---

## 5. Testing

- [ ] **`feature/unit-tests`** — at least one passing pytest test (rewrite `test_orders.py`
  and ideally add one test per new controller). Use `pytest-mock` for the DB session as in
  the existing test.
- [ ] Run `pytest` and confirm **all tests pass**.
- [ ] Manually verify every endpoint via `http://127.0.0.1:8000/docs`.

---

## 6. Demo Data & Docs

- [ ] **`feature/seed-data`** — a script/fixture that populates every table with realistic
  sample data for the demo.
- [ ] Update `README.md` with any new setup/run steps if needed.

---

## 7. Definition of Done (technical)

- [ ] All 12 tables have working CRUD endpoints exposed in `/docs`.
- [ ] App starts cleanly with `uvicorn api.main:app --reload` (no import/mapper errors).
- [ ] `pytest` passes.
- [ ] Sample data loads and the full order flow can be demoed end-to-end.
- [ ] Every High/Medium priority story below maps to a working, traceable endpoint.
- [ ] Evaluation-checklist questions are all answerable by the running product.

---

## 8. Product Backlog & User Story Traceability

Source: ROS Product Backlog. This is a **solo build over ~2 weeks — not run as
formal sprints**; the `Sprint` column is kept only for backlog fidelity. Use **Priority**
to drive build order. Map = feature/table that satisfies the story.

| ID | Feature Name | Priority | Pts | Sprint | Maps to (feature → table) |
|---|---|---|---|---|---|
| 1 | Create menu items | High | 5 | 1 | `feature/menu-items-crud` → menu_items |
| 2 | Delete menu items | High | 3 | 1 | `feature/menu-items-crud` → menu_items |
| 3 | Update menu items | High | 3 | 1 | `feature/menu-items-crud` → menu_items |
| 4 | Insufficient ingredient alert | High | 8 | 1 | `feature/inventory-alerts` → inventory, menu_item_inventory |
| 5 | Manually adjust inventory | Medium | 3 | 2 | `feature/inventory-crud` → inventory |
| 6 | Auto-disable out-of-stock items | Medium | 5 | 2 | `feature/menu-auto-disable` → menu_items, inventory |
| 7 | View all orders | High | 3 | 1 | `feature/orders-crud` → orders |
| 8 | View order details | High | 3 | 1 | `feature/order-details-crud` → order_details |
| 9 | Filter orders by date range | Medium | 3 | 2 | `feature/orders-filter-date` → orders |
| 10 | Identify low-performing dishes | Medium | 5 | 2 | `feature/low-performing-dishes` → reports, reviews |
| 11 | View complaint/review reasons | Medium | 5 | 2 | `feature/reviews-crud` → reviews |
| 12 | Create/manage promo codes | Medium | 5 | 2 | `feature/promo-codes-crud` → promo_codes |
| 13 | View promo code performance | Low | 3 | — | `feature/promo-codes-crud` / reports |
| 14 | Daily revenue total | High | 3 | 1 | `feature/revenue-reports` → payments, reports |
| 15 | Revenue trends over time | Low | 5 | — | `feature/revenue-reports` → reports |
| 16 | Place an order without an account | High | 5 | 1 | `feature/customers-crud`, `feature/orders-crud` |
| 17 | Optional account creation | Low | 3 | — | `feature/customers-crud` → customers |
| 18 | Pay for an order online | High | 8 | 1 | `feature/payments-crud` → payments |
| 19 | Pay cash on delivery/pickup | Medium | 3 | 2 | `feature/payments-crud` → payments |
| 20 | Choose takeout or delivery | High | 3 | 2 | `feature/orders-crud` → orders (orderType) |
| 21 | Estimated ready/delivery time | Medium | 3 | 2 | `feature/orders-crud` → orders (estimatedTime) |
| 22 | Track orders / view order details | High | 5 | 1 | `feature/orders-crud`, `feature/order-details-crud` |
| 23 | Real-time status updates | Medium | 5 | 2 | `feature/orders-crud` → orders (orderStatus) |
| 24 | Search/filter by dietary type | Medium | 5 | 2 | `feature/menu-search` → menu_items |
| 25 | Keyword search | Medium | 3 | 2 | `feature/menu-search` → menu_items |
| 26 | Rate and review a dish | Medium | 5 | 2 | `feature/reviews-crud` → reviews |
| 27 | View other customers' reviews | Low | 3 | — | `feature/reviews-crud` → reviews |
| 28 | Apply a promo code at checkout | Medium | 3 | 2 | `feature/promo-apply` → orders, promo_codes |

### Suggested solo build order (~2 weeks)

Work by priority; get the app running, then breadth (CRUD for all tables), then depth
(business-logic endpoints), then polish.

1. **Week 1 — foundation + High priority**
   - `feature/fix-skeleton-bugs` (must come first — app won't run otherwise)
   - `feature/order-details-crud`, `feature/orders-crud` (Stories 7, 8, 22, 20, 21, 23)
   - `feature/menu-items-crud` (Stories 1, 2, 3)
   - `feature/customers-crud` + `feature/payments-crud` (Stories 16, 18, 19)
   - `feature/inventory-crud` + `feature/inventory-alerts` (Stories 4, 5)
2. **Week 2 — remaining CRUD + Medium/Low logic + polish**
   - `feature/promo-codes-crud`, `feature/reviews-crud`, `feature/reports-crud`
   - Supporting CRUD: `feature/employees-crud`, `feature/restaurant-managers-crud`,
     `feature/menu-item-inventory-crud`
   - Business logic: `feature/menu-search`, `feature/orders-filter-date`,
     `feature/revenue-reports`, `feature/promo-apply`, `feature/menu-auto-disable`,
     `feature/low-performing-dishes`
   - `feature/unit-tests`, `feature/seed-data`, README, final endpoint verification

**Low-priority / optional if time runs short:** Stories 13, 15, 17, 27 (still covered by
the CRUD endpoints for their tables).

> **Tables required for "CRUD for ALL tables" that have no direct story:**
> `restaurant_employees`, `restaurant_managers`, `menu_item_inventory`, `reports` — build
> standard CRUD for these as supporting/admin features so the evaluation requirement is met.
