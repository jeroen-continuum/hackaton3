# Rolling 10 Roadmap

A 27-task implementation plan for the Rolling 10 B2B customer discovery system (FastAPI + Angular).

## M0 — Foundations

- [00-roadmap-scaffold](00-roadmap-scaffold.md) — Create roadmap/ folder with 27 task files + README index.
- [01-test-infra](01-test-infra.md) — Add respx to requirements.txt; set up pytest markers and fake adapters.
- [02-domain-models](02-domain-models.md) — Create domain dataclasses (CompanyProfile, Financials, Signals, ScoreResult, Decision).
- [03-ports](03-ports.md) — Create Protocol interfaces for all ports (CompanySource, FinancialsProvider, etc.).

## M1 — Hexagonal refactor

- [04-scoring-strategy-port](04-scoring-strategy-port.md) — Wrap scoring logic behind ScoringStrategy protocol.
- [05-filter-policy-port](05-filter-policy-port.md) — Wrap filtering logic behind FilterPolicy protocol.
- [06-repository-port](06-repository-port.md) — Implement CompanyRepository port over SQLModel.
- [07-application-services](07-application-services.md) — Create RunPipeline, Scorer, and GenerateOutreach services.
- [08-composition-root](08-composition-root.md) — Create composition root wiring adapters into container.

## M2 — Live source adapters

- [09-kbo-source](09-kbo-source.md) — Implement KboSource (CompanySource).
- [10-nbb-financials](10-nbb-financials.md) — Implement NbbFinancialsProvider.
- [11-vdab-vacancies](11-vdab-vacancies.md) — Implement VdabVacancyProvider.
- [12-wappalyzer-tech](12-wappalyzer-tech.md) — Implement WappalyzerTechProvider.
- [13-connections-warm](13-connections-warm.md) — Implement CsvConnectionProvider.

## M3 — Evaluation pipeline

- [14-signal-extractors](14-signal-extractors.md) — Create pure signal extraction functions.
- [15-pipeline-wiring](15-pipeline-wiring.md) — Implement the full RunPipeline.run() orchestration.
- [16-rolling-10-rules](16-rolling-10-rules.md) — Implement get_rolling10() and mark_contacted() logic.

## M4 — Pull-outreach

- [17-solution-cases](17-solution-cases.md) — Populate solution cases and create SolutionCaseRepository.
- [18-fomo-email](18-fomo-email.md) — Implement LLM email generator with FOMO framing.
- [19-gated-teaser](19-gated-teaser.md) — Implement LLM teaser generator (preview + gated full).

## M5 — API

- [20-companies-api](20-companies-api.md) — Refactor companies API routes to use application services.
- [21-outreach-api](21-outreach-api.md) — Add outreach endpoints (email, contact-lookup, mark contacted).

## M6 — Frontend

- [22-dashboard-rolling10](22-dashboard-rolling10.md) — Display Rolling 10 list in dashboard.
- [23-heatmap-polish](23-heatmap-polish.md) — Add signal heatmap with per-criterion bars.
- [24-outreach-ui](24-outreach-ui.md) — Build outreach UI with draft editor and send-gate.

## M7 — Demo & verification

- [25-seed-and-docker](25-seed-and-docker.md) — Refresh seed and verify docker compose workflow.
- [26-e2e-smoke](26-e2e-smoke.md) — Run full E2E pipeline and smoke tests.
