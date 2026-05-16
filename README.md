# Carbon Footprint — Take-Home Exercise

## How to run

```bash
echo "DATABASE_URL=postgresql://postgres:2IgN3Vi4p1YpBAZC@db.xxzzewusiglujvqlpzpi.supabase.co:5432/postgres" > backend/.env
echo "FLASK_APP=run.py" >> backend/.env
echo "NEXT_PUBLIC_API_URL=http://localhost:5000" > frontend/.env.local
make install
make migrate
make seed
make dev
```

Both servers start in one terminal with color-coded output. Ctrl+C stops both. Open `http://localhost:3000`.

<details>
<summary>Manual commands (without Make)</summary>

**Backend:**
```bash
cd backend
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
FLASK_APP=run.py ./venv/bin/flask db upgrade
./venv/bin/python seed.py
./venv/bin/python run.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
</details>

> **Port conflicts:** `make dev` will fail if ports 3000 or 5000 are already in use. Run `lsof -ti:3000 | xargs kill -9` or `lsof -ti:5000 | xargs kill -9` to free them before retrying.

---

## Tests

```bash
make test
```

Runs the backend pytest suite (27 tests) against an in-memory SQLite database — no Supabase connection required. Coverage:
- **Serializers** — `serialize_block` and `serialize_material`: source field, active co2e selection, value scaling, sort order, supplier name
- **Recompute logic** — `_recompute_component`: supplier-reported values, fallback to industry default, partial supplier data
- **Routes** — all three endpoints: response shapes, 404/400 error cases, block update and footprint recompute

**Why SQLite in-memory for tests:** A separate test database would require a second Supabase project or a local Postgres instance, adding setup burden for anyone running the tests. SQLite in-memory requires no infrastructure, runs fast, and is fully isolated — nothing written during tests persists or touches the real database. The tradeoff is that SQLite is not identical to Postgres (looser typing, some constraint differences), so Postgres-specific bugs could slip through. For this app the risk is low: there are no Postgres-specific queries or types in use, and the logic being tested is Python arithmetic rather than database behavior.

`DATABASE_URL` is set to the SQLite URL at the top of `conftest.py` before any app imports, ensuring `load_dotenv` cannot override it with the real Supabase URL.

---

## Architecture overview

```
Browser (Next.js, :3000)
    │  server-side fetch on page load → GET /api/components
    │  client-side fetch on row expand → GET /api/components/:id
    │  client-side PATCH on block edit → PATCH /api/blocks/:id
    ▼
Flask API (:5000)
    │  SQLAlchemy ORM
    ▼
PostgreSQL (Supabase)
    tables: suppliers, components, materials, blocks
```

The Next.js page renders the component list server-side. Row expansion and block editing are client-side interactions with no full page reloads. After a block edit the Flask API recomputes `total_footprint` on the component row and returns the new value so the UI can update in place. A client-side search bar filters components by name or SKU (hyphen-tolerant, so `c001` matches `c-001`).

**Backend structure:**
- `app/models/` — one file per model (`supplier.py`, `component.py`, `material.py`, `block.py`); `__init__.py` re-exports all four so import paths are stable.
- `app/routes/` — one Flask Blueprint per resource (`components.py`, `blocks.py`); serialization logic lives in `serializers.py`; `__init__.py` exposes `register_routes(app)`. `app/__init__.py` only handles Flask initialization.

**Frontend structure:**
- `lib/api/` — one file per resource (`components.ts`, `blocks.ts`); shared base URL in `client.ts`; `index.ts` re-exports everything so component imports are unchanged.
- `lib/types/` — one file per type (`block.ts`, `material.ts`, `component.ts`); `index.ts` re-exports all interfaces.

---

## Trade-offs

### 1. Integer storage for co2e and weight values
All emission factors and material weights are stored as integers scaled by 100 (e.g. `0.80 kg CO₂e` → `80`, `12.5 kg` → `1250`). This avoids floating-point rounding drift that would compound across summations. The backend divides by 100 when computing footprints, and the API returns human-readable floats. The trade-off is that the column type is slightly surprising to a reader who doesn't know the convention, and any import tooling must apply the scaling.

### 2. Rollup-on-write vs. rollup-on-read
`total_footprint` is computed and stored on the `components` row whenever a block is edited (rollup-on-write), rather than being computed at query time (rollup-on-read). With three components and small block counts, either would be fine. I chose rollup-on-write because: (a) reads vastly outnumber writes in a production dashboard; (b) it keeps the GET `/components` response fast and simple; (c) it makes the stored value auditable. The downside is that the stored value can drift if blocks are bulk-edited outside the API, but that's acceptable for this scope.

### 3. Supplier-reported vs. industry-default within a single block row
The CSV ships two rows per (material, block_name): one with a supplier and one without. I merged these into a single `blocks` table row with `co2e_value` (industry default) and `supplier_reported_co2e_value` (nullable). This mirrors the stated domain model — "supplier data overrides the default" — and makes the active value trivial to compute (`COALESCE(supplier_reported_co2e_value, co2e_value)`). The alternative (separate rows with a `source` flag) would require a join or subquery to resolve the active value.

### 4. Two-column split for Weight and CO₂e
Weight and CO₂e are separate columns in the table rather than sharing one. Weight only ever appears on material rows; CO₂e only on component and block rows. A single shared column with an ambiguous header ("Weight / CO₂e value") forces the reader to infer which is which from context. Splitting makes each column unambiguous — empty cells in the non-applicable rows are clearer than overloading one column with two different meanings.

### 5. SQLAlchemy lazy loading on the `materials` relationship
`Component` has a `materials` relationship which SQLAlchemy only queries when accessed in code. In the `GET /api/components` list endpoint, `c.materials` is never accessed so no materials are loaded. In `GET /api/components/<id>`, materials are always accessed to build the nested response. In the current codebase this gives no practical efficiency advantage over an explicit filter query — it is a convenience rather than a performance optimization, since there is no conditional logic that would skip materials.

### 6. Flask-Migrate for schema management
Schema changes are managed through Alembic migrations via Flask-Migrate rather than `db.create_all()`. `db.create_all()` works for a fresh database but can't evolve an existing schema — adding a column to a model won't add it to a live table. Flask-Migrate generates versioned migration files that live in git alongside the code. Any schema change produces a new migration file; `make migrate` applies all pending migrations safely against a live database without dropping data.

### 7. `create_app(test_config)` for test isolation
The Flask app factory accepts an optional `test_config` dict that overrides config before `db.init_app()` is called. This lets tests swap in `sqlite:///:memory:` without touching environment variables or the production config path. Without this pattern, the Postgres `DATABASE_URL` from `.env` would be loaded before the test could override it, causing tests to hit the real database.

**With more time I would:**
- Add optimistic UI updates on block edit (instead of waiting for the API round-trip)
- Add an undo/reset button to revert a block to industry default from the UI (currently requires clearing the supplier field to blank)
- Make `seed.py` idempotent — currently it re-inserts all data on every run, which would fail with unique constraint violations against a non-empty database. A guard checking `Component.query.count() > 0` before inserting would prevent accidental re-seeding of a live database
- Add frontend tests (Jest + React Testing Library) covering the search filter, block edit dialog, and table expansion

---

## AI usage notes

This project was built collaboratively with Claude Code.

- **Schema design**: I specified the schema; Claude confirmed the seed-data mapping and caught that blocks.csv ships separate rows for supplier-reported and industry-default values that need to be merged into one DB row.
- **What Claude suggested that I overrode**:
  1. Using `component_id` (e.g. `c-001`) as the primary key — I changed this to UUID PKs with `c-001` as `sku`.
  2. Storing co2e and weight as floats — I changed to integer × 100 storage with backend scaling.
  3. Omitting `description` from the components table — I added it back.
  4. Handling `valid_from` — I explicitly excluded it; Claude had planned to at least parse it.
- **What Claude suggested that I accepted**: the rollup-on-write strategy, the merged block row schema, the overall project layout, and the Next.js App Router server component → client component split.

---

## Running log of overrides / rejections

| # | Suggested | Changed to | Reason |
|---|---|---|---|
| 1 | `component_id` (c-001) as PK | UUID PKs; c-001 is `sku` | Consistent UUID convention |
| 2 | Store co2e as float | Integer × 100 | Precision / no floating-point drift |
| 3 | Store weight as float | Integer × 100 | Same 2-decimal convention as co2e |
| 4 | Drop `description` from components | Keep `description` | Wanted it in the schema |
| 5 | Minimal `valid_from` handling | Ignore completely | Out of scope |
| 6 | Shared "Weight / CO₂e" column | Two separate columns | Each column should have one meaning |
| 7 | SKU after component name | SKU before component name | Easier to scan |
| 8 | No component description in UI | Description shown below component name | More context at a glance |
| 9 | Search on exact SKU only | Strip hyphens so `c001` matches `c-001` | More forgiving UX |
