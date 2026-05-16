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

> **OS:** These commands assume macOS or Linux.

<details>
<summary>Windows instructions (WSL)</summary>

The Makefile and shell commands use Unix paths and tools. On Windows, the easiest path is WSL (Windows Subsystem for Linux):

1. Install WSL: `wsl --install` in PowerShell, then restart
2. Open a WSL terminal and clone the repo there
3. Follow the standard setup instructions above — they work as-is inside WSL

Alternatively, run the manual commands with Windows paths:

```bat
cd backend
python -m venv venv
venv\Scripts\pip install -r requirements.txt
set FLASK_APP=run.py
venv\Scripts\flask db upgrade
venv\Scripts\python seed.py
venv\Scripts\python run.py
```

```bat
cd frontend
npm install
npm run dev
```
</details>

---

## Tests

```bash
make test           # backend
make test-frontend  # frontend
```

Runs the backend pytest suite (27 tests) against an in-memory SQLite database — no Supabase connection required. Coverage:
- **Serializers** — `serialize_block` and `serialize_material`: source field, active co2e selection, value scaling, sort order, supplier name
- **Recompute logic** — `_recompute_component`: supplier-reported values, fallback to industry default, partial supplier data
- **Routes** — all three endpoints: response shapes, 404/400 error cases, block update and footprint recompute

**Why SQLite in-memory for tests:** A separate test database would require a second Supabase project or a local Postgres instance, adding setup burden for anyone running the tests. SQLite in-memory requires no infrastructure, runs fast, and is fully isolated — nothing written during tests persists or touches the real database. The tradeoff is that SQLite is not identical to Postgres (looser typing, some constraint differences), so Postgres-specific bugs could slip through. For this app the risk is low: there are no Postgres-specific queries or types in use, and the logic being tested is Python arithmetic rather than database behavior.

`DATABASE_URL` is set to the SQLite URL at the top of `conftest.py` before any app imports, ensuring `load_dotenv` cannot override it with the real Supabase URL.

The frontend suite (Jest + React Testing Library) covers `EditBlockDialog` — the core interactive component: rendering the industry default as read-only, pre-filling the supplier value, saving with a value or null, error state on API failure, disabled state while saving, cancel, and backdrop click.

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

**What is editable and why:** The editable field is the supplier-reported CO₂e value on each block. This is the value suppliers submit based on their actual production processes, which overrides the industry default — editing it is the most meaningful lever because it reflects how footprints change in practice: as suppliers report more accurate data, the rollup updates automatically through the hierarchy.

**Backend structure:**
- `app/models/` — one file per model (`supplier.py`, `component.py`, `material.py`, `block.py`); `__init__.py` re-exports all four so import paths are stable.
- `app/routes/` — one Flask Blueprint per resource (`components.py`, `blocks.py`); serialization logic lives in `serializers.py`; `__init__.py` exposes `register_routes(app)`. `app/__init__.py` only handles Flask initialization.

**Frontend structure:**
- `lib/api/` — one file per resource (`components.ts`, `blocks.ts`); shared base URL in `client.ts`; `index.ts` re-exports everything so component imports are unchanged.
- `lib/types/` — one file per type (`block.ts`, `material.ts`, `component.ts`); `index.ts` re-exports all interfaces.

---

## Trade-offs

### 1. Rollup-on-write vs. rollup-on-read
`total_footprint` is computed and stored on the `components` row whenever a block is edited (rollup-on-write), rather than being computed at query time (rollup-on-read). With three components and small block counts, either would be fine. I chose rollup-on-write because: (a) reads vastly outnumber writes in a production dashboard; (b) it keeps the GET `/components` response fast and simple; (c) it makes the stored value auditable. The downside is that the stored value can drift if blocks are bulk-edited outside the API, but that's acceptable for this scope.

### 2. SQLAlchemy lazy loading on the `materials` relationship
`Component` has a `materials` relationship which SQLAlchemy only queries when accessed in code. In the `GET /api/components` list endpoint, `c.materials` is never accessed so no materials are loaded. In `GET /api/components/<id>`, materials are always accessed to build the nested response. In the current codebase this gives no practical efficiency advantage over an explicit filter query — it is a convenience rather than a performance optimization, since there is no conditional logic that would skip materials.

### 3. Flask-Migrate for schema management
Schema changes are managed through Alembic migrations via Flask-Migrate rather than `db.create_all()`. `db.create_all()` works for a fresh database but can't evolve an existing schema — adding a column to a model won't add it to a live table. Flask-Migrate generates versioned migration files that live in git alongside the code. Any schema change produces a new migration file; `make migrate` applies all pending migrations safely against a live database without dropping data.


**With more time I would:**
- Add a Postgres trigger (deployed via a Flask-Migrate migration) that recomputes `total_footprint` on any `INSERT`, `UPDATE`, or `DELETE` to `blocks` — eliminating drift regardless of how the write originated, rather than relying on the API call path to always fire the recompute
- Switch the `materials` and `blocks` SQLAlchemy relationships to `selectinload` (eager loading) to prevent N+1 queries as the dataset grows — currently `GET /api/components/<id>` fires one query per material to fetch its blocks
- Add optimistic UI updates on block edit (instead of waiting for the API round-trip)
- Add an undo/reset button to revert a block to industry default from the UI (currently requires clearing the supplier field to blank)
- Add frontend tests (Jest + React Testing Library) covering the search filter, block row rendering, and table expansion

---

## AI usage notes

This project (and README) was built collaboratively with Claude Code. Claude wrote the implementation throughout — routes, serializers, frontend components, and tests — working from my directions on structure and decisions. My role was specifying requirements, overriding suggestions I disagreed with, and steering the architecture.

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
