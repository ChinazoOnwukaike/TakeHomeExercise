# Terralytiq Take-Home Exercise

Thanks for the live design session. This take-home is the implementation phase of the same exercise — we'd like you to build a minimal end-to-end version of what you sketched.

## What to build

A small web app that:

1. Models **components** (the things a manufacturer produces or buys), where each component is composed of one or more **materials**, and each material is broken into one or more production **blocks** that carry the underlying emission factors
2. Computes a per-unit carbon footprint for a component by rolling up emissions through that hierarchy
3. Lets a user edit at least one input that triggers a meaningful recompute through the hierarchy — what you choose to make editable is up to you, and we want to hear your reasoning in the README

You're free to pivot from your live design — just note in the README what changed and why.

How much of the hierarchy you choose to model in your schema is your call — flatter is fine if you justify it (e.g., collapsing blocks into a single per-material factor); richer is fine if you can pull it off without sprawling. We'd rather see a deliberate scope decision than an exhaustive but half-built model.

## Time expectations

We expect this to take **3–6 focused hours over 24–48 hours**. Please don't go beyond that. We're looking for clear thinking and a working slice, not feature completeness or polish. Descoping with good rationale is a positive signal; sprawling submissions are not.

## Tech stack

Three requirements:

- **Backend**: Python (Flask, FastAPI, or similar)
- **Persistence**: a relational database — PostgreSQL preferred, SQLite is fine if you want to avoid Docker / Supabase setup
- **Frontend**: React. We use **Next.js + TypeScript + React** day-to-day and prefer it, but any React-based setup (Vite, Create React App, etc.) is acceptable — note your choice in the README.

## Seed data

In `seed-data/` you'll find three CSVs:

- **`components.csv`** — the components themselves
- **`component_materials.csv`** — the materials each component is made of, with supplier and weight
- **`blocks.csv`** — production blocks per material, each carrying a `kg_co2e_per_unit` emission factor; some have a supplier-reported variant that overrides the industry default

Use them as your starting dataset. The supplier-specific vs. industry-default pattern is intentional — it's a real dynamic in our domain (suppliers report their own data, which overrides industry defaults) and we're interested in how you choose to model and surface it. Treat the CSV layout as input format, not a schema prescription — how you normalize this into your database is up to you.

**Out of scope: temporal versioning.** Blocks include a `valid_from` column for realism, but you don't need to model versioning. Use the most recent row for each (material, supplier, block_name) tuple. Mentioning how you'd approach versioning in the README is welcome but not required.

You can extend the dataset if you want to demonstrate something specific. Don't replace it wholesale.

## On using AI

Use AI tools freely — we use Claude Code daily and want to see how you collaborate with one. The bar isn't "did you write every line yourself"; it's "do you understand what you shipped, can you justify the decisions, and would you catch issues in AI output."

In the README, please note:

- Which parts you reached for AI on
- What you accepted vs. overrode
- Any moment where AI pushed you in a direction you ended up rejecting

## Deliverables

Submit a Git repo (link or zip) containing:

1. **Working code** — runnable locally with clear setup instructions
2. **README** covering:
   - How to run it (one paragraph)
   - Architecture overview — what runs where, how data flows
   - The 2–3 most interesting trade-offs you made, why, and what you'd do differently with more time
   - AI usage notes (per the section above)
3. **(Optional)** A short Loom or screen recording (≤2 min) demoing the app

## What this exercise is — and isn't

This exercise is solely for evaluating how you think and build. It is intentionally not tied to anything we plan to ship, and we won't reuse your code. We're aware you have a job, a life, and limited evening hours — the time cap is real, please respect it for your own sake.

If you have questions while working, email matthias.wagner@terralytiq.com — asking is encouraged, not penalized.
