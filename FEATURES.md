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

Reference implementation to copy: the `orders` slice (after §0 fixes).

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
- [x] Smoke tested end-to-end via `TestClient` (create, read-all, read-one, update,
  delete, 404-on-missing) against SQLite — all passing.

## 2. `feature/order-details-crud` — Order Details / Line Items  *(Stories 8, 22)*

- [x] Rewrite **`controllers/order_details.py`** stub to match the new `OrderItem` model
  from §0 (fields like `order_id`, `item_id`, `quantity`). Filter on the real PK.
- [x] Verify **`routers/order_details.py`** (already exists) — 5 endpoints under
  `/orderdetails`.
- [x] Already registered in `index.py`.
- [x] Smoke tested end-to-end via `TestClient` (create, read-all, read-one, update,
  delete, 404-on-missing) against SQLite — all passing.

## 3. `feature/customers-crud` — Customers  *(Stories 16, 17)*

- [x] Create **`controllers/customers.py`** (5 functions; PK `customerID`).
- [x] Create **`routers/customers.py`** under `/customers`; register in `index.py`.
- [x] `hasAccount` flag supports place-order-without-account (16) & optional account (17).
- [x] Schema exists (`schemas/customer.py`) — add a `CustomerUpdate` (currently missing).
- [x] Smoke tested end-to-end via `TestClient` (create, read-all, read-one, update,
  delete, 404-on-missing, create-without-account) against SQLite — all passing.

## 4. `feature/employees-crud` — Restaurant Employees  *(supporting/admin)*

- [x] Create **`controllers/employees.py`** (5 functions; PK `id`).
- [x] Create **`routers/employees.py`** under `/employees`; register in `index.py`.
- [x] Schema exists (`schemas/employee.py`, includes `EmployeeUpdate`).
- [x] Smoke tested end-to-end via `TestClient` (create, read-all, read-one, update,
  delete, 404-on-missing) against SQLite — all passing.

## 5. `feature/inventory-crud` — Inventory  *(Stories 4, 5)*

- [x] Create **`controllers/inventory.py`** (5 functions; PK `ingredient_id`).
- [x] Create **`routers/inventory.py`** under `/inventory`; register in `index.py`.
- [x] Update endpoint enables manual inventory adjustment (Story 5).
- [x] Schema exists (`schemas/inventory.py`, includes `InventoryUpdate`).
- [x] Smoke tested end-to-end via `TestClient` (create, read-all, read-one, update
  (manual adjustment), delete, 404-on-missing) against SQLite — all passing.

## 6. `feature/menu-items-crud` — Menu Items  *(Stories 1, 2, 3, 6)*

- [ ] Create **`controllers/menu_items.py`** (5 functions; PK `item_id`).
- [ ] Create **`routers/menu_items.py`** under `/menuitems`; register in `index.py`.
- [ ] Create (1) / Delete (2) / Update (3) map directly to the CRUD endpoints.
- [ ] Schema exists (`schemas/menu_item.py`, includes `MenuItemUpdate`).

## 7. `feature/menu-item-inventory-crud` — Menu ↔ Ingredient Links  *(Story 4)*

- [ ] Create **`controllers/menu_item_inventory.py`** (5 functions; **composite PK**
  `item_id` + `ingredient_id`). `read_one` / `update` / `delete` take **both** keys.
- [ ] Create **`routers/menu_item_inventory.py`** under `/menuiteminventory` with paths
  like `GET/PUT/DELETE /{item_id}/{ingredient_id}`; register in `index.py`.
- [ ] Schema exists (`schemas/menu_item_inventory.py`).

## 8. `feature/payments-crud` — Payments  *(Stories 18, 19)*

- [ ] Create **`controllers/payments.py`** (5 functions; PK `paymentID`).
- [ ] Create **`routers/payments.py`** under `/payments`; register in `index.py`.
- [ ] `paymentMethod` supports online (18) vs cash-on-delivery/pickup (19).
- [ ] Schema exists (`schemas/payments.py`, includes `PaymentUpdate`).

## 9. `feature/promo-codes-crud` — Promo Codes  *(Stories 12, 13, 28)*

- [ ] Create **`controllers/promo_codes.py`** (5 functions; **string PK** `promoCode`).
- [ ] Create **`routers/promo_codes.py`** under `/promocodes` (`/{promo_code}` string
  path param); register in `index.py`.
- [ ] Schema exists (`schemas/promo_codes.py`, includes `PromoCodeUpdate`).

## 10. `feature/reports-crud` — Reports  *(Stories 10, 14, 15)*

- [ ] Create **`controllers/reports.py`** (5 functions; PK `report_id`).
- [ ] Create **`routers/reports.py`** under `/reports`; register in `index.py`.
- [ ] Schema exists (`schemas/report.py`, includes `ReportUpdate`).

## 11. `feature/restaurant-managers-crud` — Managers  *(supporting/admin)*

- [ ] Create **`controllers/restaurant_managers.py`** (5 functions; PK `manager_id`).
- [ ] Create **`routers/restaurant_managers.py`** under `/managers`; register in `index.py`.
- [ ] Schema exists (`schemas/restaurant_manager.py`, includes `RestaurantManagerUpdate`).

## 12. `feature/reviews-crud` — Reviews  *(Stories 11, 26, 27)*

- [ ] Create **`controllers/reviews.py`** (5 functions; PK `reviewID`).
- [ ] Create **`routers/reviews.py`** under `/reviews`; register in `index.py`.
- [ ] Create (26) / read reviews (11, 27) map to CRUD endpoints.
- [ ] Schema exists (`schemas/review.py`) — add a `ReviewUpdate` (currently missing).

---

## Business-logic endpoints (beyond plain CRUD)

These add custom query/logic routes to an existing router/controller rather than a new
full CRUD slice.

## 13. `feature/inventory-alerts` — Low-stock Alert  *(Story 4)*
- [ ] `GET /inventory/alerts` (or `/low-stock`) returning ingredients where
  `quantity <= minimum_quantity`.

## 14. `feature/menu-auto-disable` — Auto-disable Out-of-stock  *(Story 6)*
- [ ] Logic to set `menu_items.is_available = False` when linked ingredients are depleted
  (endpoint to recompute availability, plus/or hook on inventory update).

## 15. `feature/orders-filter-date` — Filter Orders by Date  *(Story 9)*
- [ ] `GET /orders?start_date=&end_date=` query-param filtering on `orderDate`.

## 16. `feature/menu-search` — Dietary + Keyword Search  *(Stories 24, 25)*
- [ ] `GET /menuitems?dietary_type=` filter (24) and `?q=` keyword search over
  name/description (25).

## 17. `feature/revenue-reports` — Revenue  *(Stories 14, 15)*
- [ ] `GET /reports/revenue/daily` daily total (14) and `/reports/revenue/trends`
  over-time aggregation (15) from `payments`.

## 18. `feature/promo-apply` — Apply Promo at Checkout  *(Story 28)*
- [ ] Endpoint to validate an active/non-expired promo code and apply `discountAmount` to
  an order total.

## 19. `feature/low-performing-dishes` — Analytics  *(Story 10)*
- [ ] `GET /reports/low-performing` aggregating low ratings / low order counts per dish.

---

## Cross-cutting features

## 20. `feature/unit-tests` — Testing
- [ ] Rewrite `tests/test_orders.py` to match the corrected orders controller/model.
- [ ] Add at least one pytest test per new controller (mock DB session via `pytest-mock`).
- [ ] `pytest` passes green.

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
