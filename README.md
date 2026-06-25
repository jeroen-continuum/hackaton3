# Rolling 10 — Customer Discovery & Outreach

Finds ideal new B2B customers (BE/NL mid-market), ranks them in a dynamic
**Rolling 10**, shows *why* each was picked (heatmap), and generates personalized
pull-outreach (FOMO email + gated teaser report).

Pipeline: **KBO** dump (pond) → **NBB** financials filter → enrich (**Apollo/VDAB/Wappalyzer**)
→ weighted **score** → top 10. Results are precomputed into a DB; the web app only reads.

## Architecture

```
backend/   FastAPI API + batch pipeline (Python)   — port 8000
frontend/  Angular dashboard                        — port 4200
docs/       requirements & data-source research
```

See `docs/` for the full requirements and the allowed/legal data sources.

## Run locally (dev)

**Backend** (SQLite default — zero setup):
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # add API keys when wiring real connectors
python -m app.db.seed           # seed reference cases + one demo company
uvicorn app.main:app --reload   # http://localhost:8000/docs
```

> **Financials filters:** the size + financial filters need NBB-style data per
> company. We have no real feed, so generate synthetic figures (deterministic,
> weighted) for the whole company table:
> ```bash
> python -m app.db.seed_financials          # no-op if financials already exist
> python -m app.db.seed_financials --force  # wipe + regenerate
> ```
> Run this after `load-kbo`. Without it, the Employees / Financial filters have
> no effect (companies with no financial row pass straight through).

> **AI "Why this company" brief:** `POST /companies/{id}/brief/generate` crawls
> the company's website, caches the page in the DB (`websitecrawl` table, crawled
> once), and uses it + the financials to generate reasons / financial summary /
> signals (`companybrief` table), surfaced on the company detail view. The same
> cached page also personalises the outreach email/teaser.
> Crawling is OFF by default (`ENABLE_WEB_CRAWL=false`) — the brief then runs from
> the cache + financials only, no browser needed. To crawl live sites:
> ```bash
> pip install crawl4ai && crawl4ai-setup   # one-time: installs headless Chromium
> ENABLE_WEB_CRAWL=true uvicorn app.main:app --reload
> ```

**Frontend:**
```bash
cd frontend
npm install
npx ng serve                    # http://localhost:4200
```

## Run with Docker (Postgres + API + UI)

```bash
cp backend/.env.example backend/.env
docker compose up --build
# UI: http://localhost:4200   API: http://localhost:8000/docs
docker compose exec backend python -m app.db.seed   # seed demo data
```

## Run the pipeline (batch)

```bash
cd backend && python -m app.pipeline.run
```
While the source connectors are stubs (`app/connectors/`), use `python -m app.db.seed`
to demo the full stack end-to-end. Wire connectors one at a time — each pipeline
stage (`app/pipeline/ingest|filter|enrich|score.py`) is independent.

## Tune the model

ICP thresholds, exclusions, and scoring weights live in **`backend/app/core/constants.py`** —
edit there and re-run the pipeline to change *which* 10 companies surface.

## Tests

```bash
cd backend && pytest          # scoring + filter rules
```

## Project layout

```
backend/app/
  core/        config + constants (ICP thresholds, scoring weights)
  connectors/  one cached client per source: kbo, nbb, apollo, vdab, wappalyzer
  pipeline/    ingest → filter → enrich → score → run (orchestrator)
  outreach/    FOMO email + gated teaser report (Claude API)
  models/      Company, FinancialData, Contact, Vacancy, TechStack, Score, OutreachAsset
  api/routes/  companies, scoring, outreach
  db/          session + seed
frontend/src/app/
  core/        ApiService + typed models
  features/    dashboard (Rolling 10) · company-detail (heatmap) · outreach
  shared/      heatmap component
```
