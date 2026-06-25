# Rolling 10 — Implementation Roadmap (hexagonal, TDD)

## Context

`docs/Requirements.md` defines a sales system that auto-identifies ideal new B2B
customers (BE/NL mid-market), ranks them in a dynamic **Rolling 10**, shows *why*
each was picked (heatmap), and produces personalized **pull-outreach** (FOMO email
+ gated teaser report). Allowed, legal data sources are fixed in
`docs/Allowed-data-sources.md` (KBO dump, NBB API, Apollo/Hunter, VDAB, Wappalyzer).

A scaffold already exists (`backend/` FastAPI + `frontend/` Angular 22) matching the
pipeline **ingest → filter → enrich → score → outreach**, but:

- It is **layered, not hexagonal**: pipeline stages import concrete connectors
  directly (`app/pipeline/enrich.py` → `ApolloConnector()`), scoring is a single
  function (`app/pipeline/score.py:compute_score`), filter is loose predicates
  (`app/pipeline/filter.py`). Nothing can be swapped without editing call sites.
- Connectors (`app/connectors/*.py`) and pipeline `ingest`/`enrich`/filter-apply
  are **stubs** (`raise NotImplementedError`). Only `score.py`, `filter.py`
  predicates, and `outreach/llm.py`/`message.py` have real logic.
- Tests cover scoring + filter only (`backend/tests/test_scoring.py`).

**Goal:** drive the requirements to completion via a roadmap of small, PR-sized,
TDD tasks, while **refactoring in place to a hexagonal (ports & adapters)
architecture** so evaluation algorithms and data sources are swappable.

**Decisions (confirmed with user):**
- Refactor existing tree in place (no rewrite).
- **Live adapters** for all five sources (real KBO/NBB/Apollo/VDAB/Wappalyzer).
- In scope: gated teaser report, warm-connection scoring, heatmap UI polish.
- **PII constraint (from mockup):** decision-maker contacts (Apollo/Hunter) are
  fetched **only at outreach time, in-memory, single call, never persisted** to
  DB/cache/logs. Contact entity stays non-persisted for buyer personas.

---

## Target architecture (hexagonal, inside `backend/app/`)

```
app/
  domain/          # pure, no I/O, no framework
    models.py        value objects: CompanyProfile, Financials, Signals, ScoreResult
    ports.py         Protocol interfaces (the hexagon boundary) — see below
  application/     # use-cases orchestrating ports (still no concrete I/O)
    pipeline.py      RunPipeline service: ingest→filter→enrich→score→rank
    scoring.py       Scorer service (delegates to ScoringStrategy port)
    outreach.py      GenerateOutreach service (email + gated teaser)
  adapters/        # implement ports; the only place I/O / SDKs live
    sources/         kbo.py nbb.py vdab.py wappalyzer.py apollo.py connections.py
    scoring/         weighted.py  (wraps current compute_score logic)
    filtering/       icp_policy.py (wraps current filter predicates)
    outreach/        llm_email.py llm_teaser.py  (wrap existing outreach/*)
    persistence/     sqlmodel repos
  composition.py   # composition root: build_container() wires concrete adapters
                   #   from settings → returns services. The swap point.
  core/            config + constants (unchanged location; thresholds/weights)
  models/          SQLModel entities (persistence schema, unchanged)
  api/routes/      thin controllers calling application services via container
```

**Ports (`domain/ports.py`, `typing.Protocol`)** — each has ≥1 live adapter:

| Port | Method | Live adapter (source) |
|------|--------|-----------------------|
| `CompanySource` | `load_pond() -> Iterable[CompanyProfile]` | KBO weekly dump (CSV/XML in `DATA_DIR`) |
| `FinancialsProvider` | `fetch(enterprise_number) -> Financials` | NBB Open Data API (XBRL/JSON) |
| `VacancyProvider` | `fetch(company) -> list[Vacancy]` | VDAB developer API |
| `TechProvider` | `fetch(domain) -> TechStack` | Wappalyzer API |
| `ContactProvider` | `find_buyer_personas(company) -> list[Contact]` | Apollo/Hunter (outreach-time only) |
| `ConnectionProvider` | `shared(company) -> list[Connection]` | warm-connection CSV (LinkedIn scraping banned) |
| `ScoringStrategy` | `score(Signals) -> ScoreResult` | weighted (default); pluggable |
| `FilterPolicy` | `evaluate(profile, financials) -> Decision` | ICP policy from `constants.py` |
| `OutreachGenerator` | `email(...)`, `teaser(...)` | Claude via `outreach/llm.py` |
| `CompanyRepository` | CRUD for pipeline stages | SQLModel |

The hexagon lets us swap a scoring algorithm (e.g. weighted → ML) or a source
(NBB → mock for tests) by registering a different adapter in `composition.py`.

**TDD discipline (every task):** red → green → refactor. Domain + application
tested with **fakes** implementing the ports (fast, deterministic). Live adapters
tested against the port contract with the **HTTP layer mocked** (`respx`/`httpx`
MockTransport) and one recorded sample payload per source — this keeps adapter
tests deterministic without hitting rate-limited live APIs in CI, while the
adapter code makes real calls at runtime. Add `respx` to `requirements.txt`.

---

## Roadmap deliverable: `roadmap/` folder

Implementation **Task 0** creates `roadmap/` with one Markdown file per task below
(`NN-slug.md`) plus `roadmap/README.md` (index + how-to). Each task file uses:

```
# <NN> — <title>
**Milestone:** Mx   **Depends on:** <task ids>
## Goal           one sentence — the requirement / arch outcome
## TDD steps       1. Red: failing test (path + assertion)  2. Green  3. Refactor
## Files           created / modified
## Acceptance      observable check (test passes / endpoint returns / UI shows)
```

### M0 — Foundations
- `00-roadmap-scaffold` — create `roadmap/` files + index (this list).
- `01-test-infra` — add `respx`, `pytest` markers (`unit`/`adapter`), `conftest.py`
  with fakes for every port; frontend: enable Karma/Jasmine (`skipTests:false`).
- `02-domain-models` — pure value objects in `domain/models.py` (CompanyProfile,
  Financials, Signals, ScoreResult, Decision); tests for invariants.
- `03-ports` — `domain/ports.py` Protocols (table above) + fake adapters in tests.

### M1 — Hexagonal refactor of existing logic (no behavior change)
- `04-scoring-strategy-port` — wrap `compute_score`/`rank_scores` as
  `adapters/scoring/weighted.py` behind `ScoringStrategy`; reuse `SCORE_WEIGHTS`.
  Migrate existing scoring tests to the port. **Reuse** `score.py` logic verbatim.
- `05-filter-policy-port` — wrap `filter.py` predicates as
  `adapters/filtering/icp_policy.py` behind `FilterPolicy`; migrate filter tests.
- `06-repository-port` — `CompanyRepository` over SQLModel (`models/entities.py`).
- `07-application-services` — `application/pipeline.py`, `scoring.py`, `outreach.py`
  use-cases depending only on ports; unit-test with fakes.
- `08-composition-root` — `composition.py:build_container()` wiring concrete
  adapters from `settings`; refactor `pipeline/run.py` + `api/routes/*` to call it.

### M2 — Live source adapters (one task each; HTTP mocked in tests)
- `09-kbo-source` — parse KBO dump in `DATA_DIR` (pandas), filter REGIONS +
  FOCUS_NACE_PREFIXES, exclude EXCLUDED_NACE_PREFIXES → CompanyProfile (the pond).
- `10-nbb-financials` — NBB API by enterprise_number → employees + EBITDA.
- `11-vdab-vacancies` — VDAB API → vacancies, flag IT roles (buyer-intent signal).
- `12-wappalyzer-tech` — Wappalyzer API → tech list + `legacy_score` (impact room).
- `13-connections-warm` — CSV adapter: sales-team 2nd/3rd-degree ties → Connection.

### M3 — Evaluation pipeline end-to-end
- `14-signal-extractors` — pure functions mapping enriched data → `Signals` in
  `[0,1]` per criterion (buyer_intent, impact_potential, financial_fit, sector_fit,
  warm_connection). Tested in isolation.
- `15-pipeline-wiring` — implement `application/pipeline.py` ingest→filter→enrich
  →extract signals→score→rank; persist stages; `run.py` prints Rolling 10.
- `16-rolling-10-rules` — top-10 non-contacted by rank; marking contacted rolls the
  next in (move logic into a use-case, tested).

### M4 — Pull-outreach
- `17-solution-cases` — seed WiiPlus reference cases (`SolutionCase`) per sector;
  repository to fetch by sector for grounding.
- `18-fomo-email` — `adapters/outreach/llm_email.py`: subject "De nieuwe lead voor
  [naam]", FOMO body grounded in sector cases + missed %; structured output parse.
- `19-gated-teaser` — `llm_teaser.py`: "Three things to know about AI in [Sector]";
  split preview (~1.5 pages) vs gated `teaser_full`; persist on OutreachAsset.

### M5 — API
- `20-companies-api` — `/companies/top10` + `/companies/{id}` via services (replace
  inline queries in `api/routes/companies.py`); match `frontend/core/models.ts`.
- `21-outreach-api` — `/companies/{id}/outreach` (email+teaser) and a
  **contact-lookup** endpoint that calls `ContactProvider` in-memory, returns
  buyer personas, and **does not persist** (mockup PII rule). Mark-contacted route.

### M6 — Frontend (Angular, matches mockup)
- `22-dashboard-rolling10` — Rolling 10 list: rank, score, sector, contact status;
  bind to `ApiService.top10()`. Component tests.
- `23-heatmap-polish` — per-criterion heatmap in `shared/heatmap` + company-detail
  "why this company" panel (intent / budget fit / IT maturity / solution match).
- `24-outreach-ui` — outreach editor: AI draft + reset, gated teaser preview, human
  send-gate ("mark as sent · human verifies & sends"), contact lookup trigger.

### M7 — Demo & verification
- `25-seed-and-docker` — refresh `db/seed.py` for the new model; verify
  `docker compose up` + seed renders a populated Rolling 10 with heatmap.
- `26-e2e-smoke` — backend `pytest` green; one end-to-end test pond→top10; manual
  run-through per Verification below.

---

## Key reuse (do not rewrite)
- `backend/app/pipeline/score.py` — scoring math → wrap, don't replace (Task 04).
- `backend/app/pipeline/filter.py` — ICP predicates → wrap (Task 05).
- `backend/app/core/constants.py` — thresholds + `SCORE_WEIGHTS`, single source of
  truth; adapters read from here.
- `backend/app/outreach/llm.py`, `message.py`, `prompts.py`, `teaser.py` — wrap
  behind `OutreachGenerator` (Tasks 18–19).
- `backend/app/connectors/base.py:CachedConnector` — reuse on-disk cache for
  KBO/NBB/VDAB/Wappalyzer adapters (NOT for Apollo contacts — PII no-persist).
- `frontend/src/app/core/{api,models}.ts` — existing typed contract; keep API shape.

---

## Verification

- **Per task:** `cd backend && pytest -q` green; new test fails first (red proven).
  Frontend: `npx ng test --watch=false` for touched components.
- **Adapter contract:** each live adapter has a test asserting it satisfies its port
  with a mocked HTTP payload; a manual smoke against the real API once keys are set.
- **End-to-end (M7):**
  1. `cd backend && python -m app.db.seed` then `python -m app.pipeline.run` →
     prints a ranked Rolling 10.
  2. `uvicorn app.main:app` → `GET /companies/top10` returns 10 ranked companies
     with breakdown; `GET /companies/{id}/outreach` returns email + gated teaser;
     contact-lookup endpoint returns personas and writes nothing to DB.
  3. `docker compose up --build` + seed → frontend at :4200 shows Rolling 10,
     heatmap, "why", and the outreach editor with send-gate.
- **Swap proof (architecture acceptance):** register a second `ScoringStrategy`
  (or a fake `FinancialsProvider`) in `composition.py` and show the pipeline runs
  unchanged — demonstrates the hexagon.
