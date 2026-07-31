# Features Breakdown — Restaurant Ordering System (ROS)

> Solo project. Companion to `PROJECT_TASKS.md`. This file breaks every feature down into
> the concrete work items inside it: **model / schema / controller / router / registration
> / tests**. Each feature is built on its own `feature/feature-name` branch.

**Standard CRUD contract** (unless noted, every `*-crud` feature implements all of these):

| Layer | Work items |
|---|---|
| Controller (`api/controllers/<name>.py`) | `create`, `read_all`, `read_one`, `update`, `delete` |
| Router (`api/routers/<name>.py`) | `POST /` · `GET /` · `GET /{id}` · `PUT /{id}` · `DELETE /{id}` |
| Registration | add `app.include_router(...)` in `api/routers/index.py` |
| Model | confirm registered in `api/models/model_loader.py` |
| Schema | `Base` / `Create` / `Update` / response (most already exist) |
| Tests | `api/tests/test_<name>.py` — pytest integration test hitting the real endpoints (via the `client` fixture in `api/tests/conftest.py`) against the isolated in-memory test DB; cover create, read-all, read-one (+ 404), update (+ 404), delete (+ 404) |

Reference implementation to copy: the `orders` slice (after §0 fixes).

**Standing convention:** every feature branch from here on out includes its test file as part
of the work item — when a work item's boxes get checked off, `api/tests/test_<name>.py` is
created/updated and passing in the same pass. No separate "testing" branch needed per feature.

---

## 0. `feature/fix-skeleton-bugs` — Foundation (do first)

**Goal:** App must start cleanly (`uvicorn api.main:app --reload`) with no import/mapper
errors before any feature is built. Not CRUD — these are prerequisite fixes.

- [x] Create missing **`api/models/order_details.py`** (`OrderItem`) linking `orders` ↔
  `menu_items` with a quantity column; add the matching `order_items` relationship on
  `Order` and register the model in `model_loader.py`.
- [x] Create missing **`api/schemas/order_details.py`** (`OrderDetailBase/Create/Update` +
  response) matching the new model.
- [x] Fix broken FKs: `orders.py` → `restaurant_employees` (PK is `id`),
  `promo_codes.py` → `restaurant_managers.manager_id`, `review.py` → `customers.customerID`.
- [x] Fix relationship name mismatch between `inventory.py` (`menu_items_links`) and
  `menu_item_inventory.py` (`menu_item_links`).
- [x] Fix `review.py` schema/model field mismatch (`item_id` vs `item_ID`).
- [x] Confirm DB connectivity in `dependencies/config.py` (MySQL running, or switch to
  SQLite for local dev/testing).
- [x] Smoke test: server boots and `/docs` renders.

---

## 1. `feature/orders-crud` — Orders  *(Stories 7, 20, 21, 22, 23)*

- [x] Rewrite **`controllers/orders.py`** stub to match the real `Order` model
  (PK `orderID`; fields `orderStatus`, `orderType`, `totalPrice`, `estimatedTime`,
  `orderDate`, `promoCode`, `customerID`, `employeeID`). Filter on `Order.orderID`.
- [x] Verify **`routers/orders.py`** (already exists) — 5 endpoints under `/orders`.
- [x] `orderStatus` update supports real-time status updates (Story 23); `orderType`
  supports takeout/delivery (Story 20); `estimatedTime` supports Story 21.
- [x] Already registered in `index.py`.
- [x] `api/tests/test_orders.py` — 8 tests (create, read-all, read-one + 404, update + 404,
  delete + 404) — all passing.

## 2. `feature/order-details-crud` — Order Details / Line Items  *(Stories 8, 22)*

- [x] Rewrite **`controllers/order_details.py`** stub to match the new `OrderItem` model
  from §0 (fields like `order_id`, `item_id`, `quantity`). Filter on the real PK.
- [x] Verify **`routers/order_details.py`** (already exists) — 5 endpoints under
  `/orderdetails`.
- [x] Already registered in `index.py`.
- [x] `api/tests/test_order_details.py` — 8 tests (create, read-all, read-one + 404,
  update + 404, delete + 404), creating real orders/menu items first — all passing.

## 3. `feature/customers-crud` — Customers  *(Stories 16, 17)*

- [x] Create **`controllers/customers.py`** (5 functions; PK `customerID`).
- [x] Create **`routers/customers.py`** under `/customers`; register in `index.py`.
- [x] `hasAccount` flag supports place-order-without-account (16) & optional account (17).
- [x] Schema exists (`schemas/customer.py`) — add a `CustomerUpdate` (currently missing).
- [x] `api/tests/test_customers.py` — 9 tests (create, invalid-email-422, read-all,
  read-one + 404, update + 404, delete + 404) — all passing.

## 4. `feature/employees-crud` — Restaurant Employees  *(supporting/admin)*

- [x] Create **`controllers/employees.py`** (5 functions; PK `id`).
- [x] Create **`routers/employees.py`** under `/employees`; register in `index.py`.
- [x] Schema exists (`schemas/employee.py`, includes `EmployeeUpdate`).
- [x] `api/tests/test_employees.py` — 8 tests (create, read-all, read-one + 404,
  update + 404, delete + 404) — all passing.

## 5. `feature/inventory-crud` — Inventory  *(Stories 4, 5)*

- [x] Create **`controllers/inventory.py`** (5 functions; PK `ingredient_id`).
- [x] Create **`routers/inventory.py`** under `/inventory`; register in `index.py`.
- [x] Update endpoint enables manual inventory adjustment (Story 5).
- [x] Schema exists (`schemas/inventory.py`, includes `InventoryUpdate`).
- [x] `api/tests/test_inventory.py` — 8 tests (create, read-all, read-one + 404,
  update (manual adjustment) + 404, delete + 404) — all passing.

## 6. `feature/menu-items-crud` — Menu Items  *(Stories 1, 2, 3, 6)*

- [x] Create **`controllers/menu_items.py`** (5 functions; PK `item_id`).
- [x] Create **`routers/menu_items.py`** under `/menuitems`; register in `index.py`.
- [x] Create (1) / Delete (2) / Update (3) map directly to the CRUD endpoints.
- [x] Schema exists (`schemas/menu_item.py`, includes `MenuItemUpdate`).
- [x] `api/tests/test_menu_items.py` — 8 tests (create, read-all, read-one + 404,
  update (`is_available` toggle for Story 6) + 404, delete + 404) — all passing.

## 7. `feature/menu-item-inventory-crud` — Menu ↔ Ingredient Links  *(Story 4)*

- [x] Create **`controllers/menu_item_inventory.py`** (5 functions; **composite PK**
  `item_id` + `ingredient_id`). `read_one` / `update` / `delete` take **both** keys.
- [x] Create **`routers/menu_item_inventory.py`** under `/menuiteminventory` with paths
  like `GET/PUT/DELETE /{item_id}/{ingredient_id}`; registered in `index.py`.
- [x] Schema exists (`schemas/menu_item_inventory.py`).
- [x] `api/tests/test_menu_item_inventory.py` — 8 tests (create, read-all, read-one + 404,
  update + 404, delete + 404), creating a real menu item + ingredient first — all passing.

## 8. `feature/payments-crud` — Payments  *(Stories 18, 19)*

- [x] Create **`controllers/payments.py`** (5 functions; PK `paymentID`).
- [x] Create **`routers/payments.py`** under `/payments`; registered in `index.py`.
- [x] `paymentMethod` supports online (18) vs cash-on-delivery/pickup (19).
- [x] Schema exists (`schemas/payments.py`, includes `PaymentUpdate`).
- [x] `api/tests/test_payments.py` — 8 tests (create, read-all, read-one + 404, update
  (status change e.g. refund) + 404, delete + 404), creating a real order first — all
  passing.

## 9. `feature/promo-codes-crud` — Promo Codes  *(Stories 12, 13, 28)*

- [x] Create **`controllers/promo_codes.py`** (5 functions; **string PK** `promoCode`).
- [x] Create **`routers/promo_codes.py`** under `/promocodes` (`/{promo_code}` string
  path param); registered in `index.py`.
- [x] Schema exists (`schemas/promo_codes.py`, includes `PromoCodeUpdate`).
- [x] `api/tests/test_promo_codes.py` — 8 tests (create, read-all, read-one + 404, update
  (e.g. deactivate / change discount) + 404, delete + 404), seeding a manager first for
  the required `managerID` FK — all passing.

## 10. `feature/reports-crud` — Reports  *(Stories 10, 14, 15)*

- [x] Create **`controllers/reports.py`** (5 functions; PK `report_id`).
- [x] Create **`routers/reports.py`** under `/reports`; registered in `index.py`.
- [x] Schema exists (`schemas/report.py`, includes `ReportUpdate`).
- [x] `api/tests/test_reports.py` — 8 tests (create, read-all, read-one + 404, update + 404,
  delete + 404) — all passing.

## 11. `feature/restaurant-managers-crud` — Managers  *(supporting/admin)*

- [x] Create **`controllers/restaurant_managers.py`** (5 functions; PK `manager_id`).
- [x] Create **`routers/restaurant_managers.py`** under `/managers`; registered in `index.py`.
- [x] Schema exists (`schemas/restaurant_manager.py`, includes `RestaurantManagerUpdate`).
- [x] `api/tests/test_restaurant_managers.py` — 9 tests (create, invalid-email-422, read-all,
  read-one + 404, update + 404, delete + 404) — all passing.

## 12. `feature/reviews-crud` — Reviews  *(Stories 11, 26, 27)*

- [x] Create **`controllers/reviews.py`** (5 functions; PK `reviewID`).
- [x] Create **`routers/reviews.py`** under `/reviews`; registered in `index.py`.
- [x] Create (26) / read reviews (11, 27) map to CRUD endpoints.
- [x] Schema exists (`schemas/review.py`) — added `ReviewUpdate`.
- [x] `api/tests/test_reviews.py` — 9 tests (create, invalid-rating-422, read-all,
  read-one + 404, update + 404, delete + 404), creating a real customer + menu item
  first — all passing.

---

## Business-logic endpoints (beyond plain CRUD)

These add custom query/logic routes to an existing router/controller rather than a new
full CRUD slice.

## 13. `feature/inventory-alerts` — Low-stock Alert  *(Story 4)*
- [x] `GET /inventory/alerts` returning ingredients where `quantity <= minimum_quantity`
  (declared before `/{item_id}` so the path is not captured as an int id).
- [x] `api/tests/test_inventory_alerts.py` — 4 tests (low-stock only, equal-to-minimum,
  empty when all stocked, multiple alerts) — all passing.

## 14. `feature/menu-auto-disable` — Auto-disable Out-of-stock  *(Story 6)*
- [x] `POST /menuitems/recompute-availability` sets `is_available=False` when any linked
  ingredient has `quantity < quantity_required` (declared before `/{item_id}`).
- [x] Hook on inventory `PUT` to recompute availability after stock changes.
- [x] `api/tests/test_menu_auto_disable.py` — 4 tests (recompute disables depleted,
  keeps available when stocked, skips unlinked items, inventory-update hook) — all passing.

## 15. `feature/orders-filter-date` — Filter Orders by Date  *(Story 9)*
- [x] `GET /orders?start_date=&end_date=` query-param filtering on `orderDate`
  (optional params; inclusive day bounds).
- [x] `api/tests/test_orders_filter_date.py` — 5 tests (both bounds, start-only,
  end-only, empty range, no-params returns all) — all passing.

## 16. `feature/menu-search` — Dietary + Keyword Search  *(Stories 24, 25)*
- [x] `GET /menuitems?dietary_type=` filter (24) and `?q=` keyword search over
  name/description (25); both optional and combinable.
- [x] `api/tests/test_menu_search.py` — 6 tests (dietary filter, name keyword,
  description keyword, combined filters, empty results, no-params returns all) —
  all passing.

## 17. `feature/revenue-reports` — Revenue  *(Stories 14, 15)*
- [x] `GET /reports/revenue/daily?date=` daily paid-payment total (14) and
  `GET /reports/revenue/trends?start_date=&end_date=` over-time aggregation (15),
  joining `payments` → `orders.orderDate` (payments have no date column).
- [x] `api/tests/test_revenue_reports.py` — 5 tests (daily total, excludes non-paid,
  zero day, trends range, inverted range 400) — all passing.

## 18. `feature/promo-apply` — Apply Promo at Checkout  *(Story 28)*
- [ ] Endpoint to validate an active/non-expired promo code and apply `discountAmount` to
  an order total.

## 19. `feature/low-performing-dishes` — Analytics  *(Story 10)*
- [ ] `GET /reports/low-performing` aggregating low ratings / low order counts per dish.

---

## Cross-cutting features

## 20. `testing_features_1to6` — Testing Catch-up (Features 1–6)
- [x] Add `TESTING` env-var switch (`dependencies/config.py`) + isolated in-memory
  SQLite engine with `StaticPool` (`dependencies/database.py`), so the test suite never
  touches the dev DB (`ros.db` / MySQL).
- [x] Add `api/tests/conftest.py` — sets `TESTING=1`, provides an autouse fixture that
  creates/drops all tables per test function, and a `client` (`TestClient`) fixture.
- [x] Rewrite `api/tests/test_orders.py` (was a broken stub using a nonexistent
  `customer_name`/`description` schema) to match the corrected `Order` model.
- [x] `api/tests/test_order_details.py`, `test_customers.py`, `test_employees.py`,
  `test_inventory.py`, `test_menu_items.py` — one file per feature (49 tests total).
- [x] Add `pytest-cov` to `requirements.txt`.
- [x] `pytest api/tests` passes green (49 passed).

See the **Standing convention** note above §1: every feature branch from work item 7 onward
adds/updates its own `api/tests/test_<name>.py` as part of that work item — a dedicated
catch-up branch like this one shouldn't be needed again.

## 21. `feature/seed-data` — Demo Data
- [ ] Script/fixture populating every table with realistic sample data for the demo.

## 22. `feature/docs` — Documentation
- [ ] Update `README.md` with any new setup/run/test steps.

---

## Coverage check — CRUD for all 12 tables

| Table | Feature |
|---|---|
| orders | §1 |
| order_details (OrderItem) | §0 + §2 |
| customers | §3 |
| restaurant_employees | §4 |
| inventory | §5 |
| menu_items | §6 |
| menu_item_inventory | §7 |
| payments | §8 |
| promo_codes | §9 |
| reports | §10 |
| restaurant_managers | §11 |
| reviews | §12 |
