# inStream — Enterprise Intake Intelligence

inStream turns unstructured email and documents into structured, auditable
business workflows. It is built as a reusable **Enterprise Work Intake
Platform** — not a one-off automation for any single customer. Discovery is
customer #1, not the product; the platform is designed to later serve banks,
insurers, law firms, hospitals, universities, municipalities, and any
enterprise that receives work through email.

No platform code contains customer-specific logic. Every customer's rules,
prompts, field mappings, email templates, and workflow routing live in a
**customer pack** under `customer_packs/<name>/` — see
`customer_packs/_template/` for the fully-documented shape a real pack
follows. `discovery/` (Phase 2) will be the first one.

## Product line

| Product | What it covers | Where it lives today |
|---|---|---|
| **inStream Core** | Intake, ingestion, OCR/AI abstraction, orchestration | `packages/*`, `apps/worker` |
| **inStream Verify** | Human review, exception handling | `WorkflowState.ROUTED_REVIEW` / `ROUTED_INVALID`, dashboard review queue |
| **inStream Flow** | Workflow automation & routing | `packages/workflow`, `packages/rules` |
| **inStream Insights** | Analytics & SLA dashboards | `packages/analytics`, `/analytics` API, dashboard |
| **inStream Studio** | Visual rule builder for non-technical users | `apps/dashboard` rule builder (placeholder today) |

These are naming/positioning only in Phase 1 — the modules above are one
platform, not separate deployables yet.

## Architecture

```
instream/
  apps/
    api/            FastAPI — HTTP surface, tenant/RBAC-scoped
    worker/         Celery — ingestion -> OCR -> AI -> validation -> workflow pipeline
    dashboard/      Next.js — review queue, rule builder, analytics (placeholders in Phase 1)
  packages/
    shared/         Common types, tenant context, errors, blob storage interface
    db/             SQLAlchemy models + Alembic migrations (the full schema)
    connectors/     EmailConnector interface — IMAPConnector (real) + Outlook/Gmail/Exchange (stubs)
    ingestion/      AttachmentExtractor — PDF/DOCX/image/ZIP
    ocr/             OCRProvider interface — MockOCRProvider + cloud-provider stubs
    ai/              AIProvider interface — MockAIProvider + Anthropic/OpenAI stubs (reasoning only, never PASS/FAIL)
    rules/           Deterministic Rules Engine + YAML condition-tree DSL
    workflow/        WorkflowEngine — the RECEIVED -> ... -> COMPLETED state machine
    confidence/      ConfidenceEngine — aggregates field confidence, classifies AUTO/REVIEW/FAIL
    destinations/    DestinationConnector interface — CSV + Postgres (real) + Excel/SharePoint/Salesforce/SAP/Dynamics/Sheets (stubs)
    audit/           Append-only AuditLogger
    analytics/       Daily rollups + summary queries (automation rate, SLA, exceptions)
    notifications/   NotificationProvider interface — console/Jinja2 templating
    auth/            JWT issuance/verification, password hashing, RBAC dependency
  customer_packs/
    _template/       Documented reference pack — rules/, prompts/, mappings/, templates/, workflows/
```

Every module is an interface (`base.py`, usually a `typing.Protocol`) plus
one or more implementations behind a factory — swapping a provider means
changing config, not code. See `packages/rules/instream_rules/dsl.py` for the
rule condition-tree schema and `customer_packs/_template/workflows/example_workflow.yaml`
for how confidence thresholds and destination routing are configured per pack.

**A deterministic rule failure always wins over AI confidence** —
`packages/workflow/instream_workflow/engine.py`'s `route()` sends any
`FAIL` straight to the exception queue regardless of how confident the
OCR/AI extraction was. AI only decides between straight-through processing
and human review.

## Phase 1 scope (this pass)

Built: the full schema, every package interface, reference implementations
that need no external credentials (`IMAPConnector`, PDF/DOCX/image/ZIP
extraction, `MockOCRProvider`, `MockAIProvider`, CSV + Postgres
destinations), the Rules/Workflow/Confidence engines (unit-tested), the
FastAPI app, the Celery pipeline, and a dashboard scaffold.

Not yet built (later phases, per the roadmap below): the Discovery customer
pack, real Outlook/Gmail/Exchange connectors, real cloud OCR/AI providers,
SharePoint/Salesforce/SAP/Dynamics destinations, production deployment.

## Roadmap

1. **Core Platform** (this pass) — infrastructure only, no Discovery.
2. **Discovery Customer Pack** — retirement/withdrawal claim validation
   rules, forms, email templates, Excel mapping.
3. **Dashboard** — review queue, analytics, audit trail, rule builder wired
   to real data.
4. **Outlook Integration** — real inbox connectors.
5. **Production** — security hardening, monitoring, deployment.

## Getting started

Requires: Python 3.11+, [uv](https://docs.astral.sh/uv/), Node 20+, pnpm,
Docker.

```bash
bash scripts/dev_up.sh      # docker compose up, uv sync, alembic upgrade, seed a dev tenant
bash scripts/run_api.sh     # FastAPI on :8000
bash scripts/run_worker.sh  # Celery worker (uses --pool=solo, required on Windows)
pnpm dashboard:dev          # Next.js on :3000
```

Log in with the seeded user: `admin@example.com` / `changeme123`
(`POST /auth/login`). New tenant onboarding isn't exposed over the API in
Phase 1 — see the docstring in `scripts/seed.py` for why, and
`apps/api/instream_api/routers/tenants.py`.

This machine's Docker Postgres is mapped to **5433**, not 5432 — a native
Postgres service was already bound to 5432. See `.env.example`.

### Tests

```bash
uv run pytest tests/unit -v
```

29 unit tests cover the Rules Engine (condition tree, composite and/or/not,
applies_to scoping), the Workflow Engine (state transitions, rule-failure-
overrides-confidence routing), the Confidence Engine (both aggregation
strategies), connectors, ingestion extractors, OCR/AI mocks, and both
destinations (CSV + a real Postgres round-trip).
