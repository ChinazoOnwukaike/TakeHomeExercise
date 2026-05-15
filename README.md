# Carbon Footprint — Take-Home Exercise

## How to run

**Backend (Flask, port 5000):**
```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in DATABASE_URL from Supabase
python seed.py                # creates tables and loads seed data
python run.py                 # starts the API on http://localhost:5000
```

**Frontend (Next.js, port 3000):**
```bash
cd frontend
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:5000
npm install
npm run dev                         # opens http://localhost:3000
```

Both must be running at the same time. Open `http://localhost:3000`.

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

The Next.js page renders the component list server-side. Row expansion and block editing are client-side interactions with no full page reloads. After a block edit the Flask API recomputes `total_footprint` on the component row and returns the new value so the UI can update in place.

---

## The 2–3 most interesting trade-offs

### 1. Integer storage for co2e and weight values
All emission factors and material weights are stored as integers scaled by 100 (e.g. `0.80 kg CO₂e` → `80`, `12.5 kg` → `1250`). This avoids floating-point rounding drift that would compound across summations. The backend divides by 100 when computing footprints, and the API returns human-readable floats. The trade-off is that the column type is slightly surprising to a reader who doesn't know the convention, and any import tooling must apply the scaling.

### 2. Rollup-on-write vs. rollup-on-read
`total_footprint` is computed and stored on the `components` row whenever a block is edited (rollup-on-write), rather than being computed at query time (rollup-on-read). With three components and small block counts, either would be fine. I chose rollup-on-write because: (a) reads vastly outnumber writes in a production dashboard; (b) it keeps the GET `/components` response fast and simple; (c) it makes the stored value auditable. The downside is that the stored value can drift if blocks are bulk-edited outside the API, but that's acceptable for this scope.

### 3. Supplier-reported vs. industry-default within a single block row
The CSV ships two rows per (material, block_name): one with a supplier and one without. I merged these into a single `blocks` table row with `co2e_value` (industry default) and `supplier_reported_co2e_value` (nullable). This mirrors the stated domain model — "supplier data overrides the default" — and makes the active value trivial to compute (`COALESCE(supplier_reported_co2e_value, co2e_value)`). The alternative (separate rows with a `source` flag) would require a join or subquery to resolve the active value.

**With more time I would:**
- Add optimistic UI updates on block edit (instead of waiting for the API round-trip)
- Add a `valid_from` column and last-row-wins deduplication logic to the seed
- Add an undo/reset button to revert a block to industry default from the UI (currently requires clearing the supplier field to blank)

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
