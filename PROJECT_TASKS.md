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
| `order_details` (OrderItem) | ✅ | ✅ | ✅ | ✅ | ✅ | Full CRUD working (verified) |
| `customers` | ✅ | ✅ | ✅ | ✅ | ✅ | Full CRUD working (verified) |
| `restaurant_employees` | ✅ | ✅ | ✅ | ✅ | ✅ | Full CRUD working (verified) |
| `inventory` | ✅ | ✅ | ✅ | ✅ | ✅ | Full CRUD working (verified) |
| `menu_items` | ✅ | ✅ | ✅ | ✅ | ✅ | Full CRUD working (verified) |
| `menu_item_inventory` | ✅ | ✅ | ✅ | ✅ | ✅ | Full CRUD working (verified, composite PK) |
| `payments` | ✅ | ✅ | ✅ | ✅ | ✅ | Full CRUD working (verified) |
| `promo_codes` | ✅ | ✅ | ✅ | ✅ | ✅ | Full CRUD working (verified, string PK) |
| `reports` | ✅ | ✅ | ✅ | ✅ | ✅ | Full CRUD working (verified) |
| `restaurant_managers` | ✅ | ✅ | ✅ | ✅ | ✅ | Full CRUD working (verified) |
| `reviews` | ✅ | ✅ | ✅ | ✅ | ✅ | Full CRUD working (verified) |

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
- [x] **`controllers/order_details.py` is a template stub** — references `sandwich_id`,
  `amount`, `.id`. Rewrite to match the real order-details model. *(Fixed in
  `feature/order_details_crud`.)*
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
- [x] **`tests/test_orders.py` is broken** — asserts `customer_name`/`description`. Rewrote
  to match the corrected orders controller/model *(done in `testing_features_1to6`)*.
- [x] **`email-validator` not installed / not in `requirements.txt`** — `schemas/customer.py`
  and `schemas/restaurant_manager.py` use pydantic `EmailStr`, which fails to import without
  it. Add `email-validator` to `requirements.txt` and install.
- [x] **`inventory.py` `onupdate=datetime.now()`** (line 15) is called with parentheses, so
  it's evaluated once at import instead of per-update. Change to `onupdate=datetime.now`.
- [x] **Missing `*Update` schemas** — add `CustomerUpdate` (`schemas/customer.py`) *(done in
  `feature/customers_crud`)* and `ReviewUpdate` (`schemas/review.py`) *(done in
  `feature/reviews_crud`)* for their PUT endpoints.
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
- [x] **`feature/order-details-crud`** — create model + schema + controller + router. *(Stories 8, 22)*
- [x] **`feature/customers-crud`** — controller + router (schema exists). *(Stories 16, 17)*
- [x] **`feature/employees-crud`** — controller + router (schema exists). *(supporting/admin CRUD)*
- [x] **`feature/inventory-crud`** — controller + router (schema exists). *(Stories 4, 5)*
- [x] **`feature/menu-items-crud`** — controller + router (schema exists). *(Stories 1, 2, 3, 6)*
- [x] **`feature/menu-item-inventory-crud`** — controller + router (composite PK
  `item_id` + `ingredient_id`; read-one/update/delete need both keys). *(Story 4)*
- [x] **`feature/payments-crud`** — controller + router (schema exists). *(Stories 18, 19)*
- [x] **`feature/promo-codes-crud`** — controller + router (string PK `promoCode`). *(Stories 12, 13, 28)*
- [x] **`feature/reports-crud`** — controller + router (schema exists). *(Stories 10, 14, 15)*
- [x] **`feature/restaurant-managers-crud`** — controller + router (schema exists). *(supporting/admin CRUD)*
- [x] **`feature/reviews-crud`** — controller + router (schema exists; added `ReviewUpdate`). *(Stories 11, 26, 27)*

### 4a. Business-logic endpoints (beyond plain CRUD)

Some stories need custom query/logic endpoints in addition to standard CRUD:

- [x] **`feature/inventory-alerts`** — insufficient-ingredient alert / low-stock endpoint. *(Story 4)*
- [x] **`feature/menu-auto-disable`** — auto-set `is_available=False` when an item's
  ingredients are out of stock. *(Story 6)*
- [x] **`feature/orders-filter-date`** — filter orders by date range endpoint. *(Story 9)*
- [x] **`feature/menu-search`** — search/filter menu by dietary type + keyword search. *(Stories 24, 25)*
- [x] **`feature/revenue-reports`** — daily revenue total + revenue trends. *(Stories 14, 15)*
- [x] **`feature/promo-apply`** — apply promo code at checkout (discount calc). *(Story 28)*
- [ ] **`feature/low-performing-dishes`** — identify low-performing dishes from reviews/sales. *(Story 10)*

---

## 5. Testing

See `TEST_PLAN.md` for the full strategy/rationale (integration tests against an isolated
in-memory SQLite DB, via `api/tests/conftest.py`'s `client` fixture).

- [x] **`testing_features_1to6`** — one `api/tests/test_<name>.py` integration-test file per
  completed feature (orders, order_details, customers, employees, inventory, menu_items);
  rewrote the broken `test_orders.py`. 49 tests total.
- [x] Run `pytest` and confirm **all tests pass** (49 passed).
- [ ] Manually verify every endpoint via `http://127.0.0.1:8000/docs`.
- [ ] **Standing convention:** every feature work item from #7 onward adds/updates its own
  `api/tests/test_<name>.py` in the same branch — no separate testing branch going forward.

---

## 6. Demo Data & Docs

- [ ] **`feature/seed-data`** — a script/fixture that populates every table with realistic
  sample data for the demo.
- [ ] Update `README.md` with any new setup/run steps if needed.

---

## 7. Definition of Done (technical)

- [x] All 12 tables have working CRUD endpoints exposed in `/docs`.
- [ ] App starts cleanly with `uvicorn api.main:app --reload` (no import/mapper errors).
- [ ] `pytest` passes.
- [ ] Sample data loads and the full order flow can be demoed end-to-end.
- [ ] Every High/Medium priority story below maps to a working, traceable endpoint.
- [ ] Evaluation-checklist questions are all answerable by the running product (see §9).

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

---

## 9. Evaluation Checklist Traceability

The project instructions require the final product to "address" a provided list of
questions (from the staff's and customer's perspective). Each maps to a feature in
`FEATURES.md` (section numbers below refer to `FEATURES.md`, not this document); ✅ =
already answerable by a working endpoint, ⏳ = needs a feature still pending there
(§9–12 CRUD, §13–19 business logic).

### Staff perspective

| Question | Answered by | Status |
|---|---|---|
| Can I easily create, update, or delete menu items? | `POST/PUT/DELETE /menuitems/{id}` — §6 | ✅ |
| How does the system alert me if there are insufficient ingredients to fulfill an order? | `GET /inventory/alerts` comparing `inventory.quantity` vs `minimum_quantity` — §13 `inventory-alerts` | ✅ |
| How can I view the list of all orders? Is there an option to view details of a specific order? | `GET /orders/` + `GET /orders/{id}` (§1); line items via `GET /orderdetails/` (§2) | ✅ |
| How can I identify dishes that are less popular or have received complaints? Understand reasons behind dissatisfaction? | `reviews` CRUD (§12) surfaces comments/ratings per dish; `GET /reports/low-performing` aggregates low ratings/low order counts (§19 `low-performing-dishes`) | ⏳ (partial: §12 done; still needs §19) |
| Can I create and manage promotional codes, including setting expiration dates? | `promo_codes` CRUD (§9) — model has `expirationDate` + `active` columns | ✅ |
| How can I determine total revenue generated from food sales on any given day? | `GET /reports/revenue/daily` aggregating paid `payments.amount` by `orders.orderDate` — §17 `revenue-reports` | ✅ |
| Is there a way to view the list of orders within a specific date range? | `GET /orders?start_date=&end_date=` — §15 `orders-filter-date` | ✅ |

### Customer perspective

| Question | Answered by | Status |
|---|---|---|
| How to place an order without signing up for an account? | Create a guest `Customer` with `hasAccount=false` (name/phone/email only, no login) via `POST /customers/`, then `POST /orders/` with that `customerID` — §3 + §1 | ✅ |
| How to pay for an order? | `POST /payments/` linked to the order — §8 | ✅ |
| Does the system support takeout/delivery? How do I specify my preference? | `orders.orderType` field, set on `POST/PUT /orders/` — §1 | ✅ |
| How can I track the status of my order by my tracking number? | `GET /orders/{orderID}` returns `orderStatus`; `orderID` doubles as the tracking number — §1 | ✅ |
| Is there a feature to search for specific types of food (e.g. vegetarian)? | `GET /menuitems?dietary_type=` filter + `?q=` keyword search — §16 `menu-search` | ✅ |
| How can I rate/review dishes and share experiences with other customers? | `reviews` CRUD (§12): `POST /reviews/` to create, `GET /reviews/` to browse others' | ✅ |
| How do I apply a promo code to my order? | `POST /promocodes/apply` validates active/non-expired code and discounts `orders.totalPrice` — §18 `promo-apply` | ✅ |

### Net remaining work to fully cover the checklist

All ✅ items are already live. **All 12 tables now have CRUD.** The remaining ⏳ checklist
item is `low-performing-dishes` (§19) — reviews CRUD (§12) is done, but the aggregate
endpoint is still pending. No new tables/models are needed — just that endpoint.
