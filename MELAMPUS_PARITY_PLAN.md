# Regulatory Compliance Monitor — Melampus Parity Plan

Status: proposed execution plan  
Primary motion: vertical compliance intelligence IP/service  
Required wedge decision: one regulated industry, jurisdiction set, and accountable reviewer

Regulatory Compliance Monitor reaches Melampus parity when a compliance professional can see a complete, source-cited change set for a narrow scope, review a deterministic diff and bounded summary, approve distribution, and audit who received what. Broad source coverage or AI summaries without provenance are not sufficient.

## Project Charter

### Agent execution contract

- Read `README.md`, FastAPI/SQLAlchemy/APScheduler code, scraper/source adapters, React app, database models, and deployment configuration before editing.
- Execute RCM-001 before adding sources, states, topics, or notification channels.
- Treat fetched content as untrusted. Never allow source text to override prompts, tools, recipients, or policy.
- Every displayed claim and summary sentence must link to a source snapshot and location. Generated content is a draft requiring human approval.
- Preserve a deterministic diff and manual summary path when OpenAI, SendGrid, or a source is unavailable.
- Work one task ID per PR; source adapter changes require fixtures and freshness/completeness tests.
- Do not claim legal or regulatory compliance. The product supports monitoring and review.
- PRs must list task IDs, commands, source/evaluation changes, screenshots, security/legal risk, migration, and rollback.

### Product definition

### Problem, user, and buyer

Compliance teams manually monitor fragmented government publications and translate changes into internal action. Missed items, duplicate noise, decontextualized summaries, and untracked email distribution create risk. The primary user is a compliance analyst; the buyer is one regulated organization or consultancy in the vertical selected by RCM-001.

### Product thesis and sellable wedge

The wedge is a cited change-review queue for a bounded source register: fetch and preserve official source snapshots, normalize/deduplicate items, compute deterministic diffs, assign relevance with transparent rules, draft a cited summary, obtain reviewer approval, send to subscribed recipients, and preserve delivery/audit evidence.

### Data rights, ethics, and AI resilience

Official source content retains its source attribution and terms. Customers own watchlists, review notes, recipient data, and derived decisions. Provide export, retention, unsubscribe/consent, and deletion controls. AI is provider-isolated and optional; it may summarize cited diffs but cannot determine legal obligations or send alerts without approval.

### Commercial proof and kill criteria

Sell a service-assisted monitoring pilot for one vertical. Measure source coverage, detection latency, duplicates, analyst acceptance/corrections, false negatives found by parallel manual monitoring, and time saved. Stop or narrow if the bounded source register cannot be monitored reliably or reviewers will not trust cited outputs enough to replace part of their manual process.

## Implementation plan

### Architecture and data

Retain FastAPI, React, SQLAlchemy, Postgres for production, and scheduled ingestion. Use one modular backend with versioned source adapters and a durable job state; do not split services until isolation or scale proves necessary. Core entities are tenant, user/role, source register entry, fetch attempt, immutable snapshot/hash, regulatory item, version/diff, watch rule, relevance decision, summary draft, citation, review decision, subscription/consent, notification, delivery event, audit event, retention policy, and deletion job.

### Ordered task backlog

| ID | Priority | Work | Acceptance evidence |
|---|---|---|---|
| RCM-001 | P0 | Select the first vertical, jurisdictions, official source register, buyer, review owner, excluded advice, and freshness objective. | ADR and demo contain only the bounded supported scope and truthfully label gaps. |
| RCM-002 | P0 | Define versioned source-adapter contract with allowlisted endpoints, SSRF controls, rate limits, retries/backoff, conditional requests, size/type limits, and terms/attribution metadata. | Adapter contract tests cover success, changed/unchanged, malformed, timeout, rate-limit, and hostile redirects. |
| RCM-003 | P0 | Store immutable source snapshots/hashes and normalized item versions; compute deterministic semantic/text diffs. | Any displayed change can be reconstructed from preserved source versions and citations. |
| RCM-004 | P0 | Add source health, freshness, gap, duplicate, and parse-drift monitoring with operator-visible status. | A disabled/broken/stale source creates an alert and prevents a false “all clear” state. |
| RCM-005 | P0 | Implement authentication, tenant isolation, analyst/admin roles, secure sessions/tokens, and sensitive-action auditing. | Matrix tests deny cross-tenant watchlists, notes, recipients, source state, and exports. |
| RCM-006 | P0 | Build transparent relevance rules and reviewer override before adding AI ranking. | Fixtures explain why items match/skip; overrides are versioned and reversible. |
| RCM-007 | P0 | Add provider-isolated, schema-validated, citation-constrained summaries with prompt-injection defenses and deterministic/manual fallback. | Every sentence maps to cited diff content; malformed/unavailable provider leaves a reviewable diff, not a lost item. |
| RCM-008 | P0 | Require reviewer approval for publish/send and make notification delivery idempotent with consent, unsubscribe, retry, suppression, and audit. | Replay sends once; unsubscribed/suppressed recipients receive nothing; approval identity is recorded. |
| RCM-009 | P0 | Add end-to-end coverage for fetch → snapshot → normalize → diff → match → summarize/fallback → approve → deliver → audit. | CI passes provider/source/mail failure and retry scenarios against Postgres. |
| RCM-010 | P0 | Add transactional migrations, encrypted backup/restore, health/readiness, structured logs, scheduler leadership/idempotency, metrics, and rollback. | Restore recovers source history, reviewer decisions, consents, and delivery state without duplicate alerts. |
| RCM-011 | P1 | Add machine-readable export, retention, and verified deletion for customer data while preserving required public-source provenance. | Export/deletion tests document exactly what is retained and why. |
| RCM-012 | P1 | Build evaluation harness for bounded-source recall, latency, duplicates, citation validity, relevance acceptance, and summary corrections. | Results separate seeded fixtures from live pilot evidence and expose missing-source periods. |
| RCM-013 | P1 | Produce architecture/data flow, threat model, source register, terms/data-rights record, model/provider card, licenses, claims ledger, demo/runbooks, and diligence index. | Reviewer can trace every source, output, control, and claim. |
| RCM-014 | P1 | Run a parallel manual-versus-product pilot with a qualified compliance reviewer. | Pilot reports missed items, correction burden, latency, and time saved without claiming legal compliance. |
| RCM-015 | P2 | Add a source/jurisdiction only when a buyer need and adapter-quality owner are named. | Expansion passes the same recall/freshness/citation gates. |

### Security and operations

Threat-model SSRF and hostile redirects, prompt injection, malicious source payloads, source drift, missed publications, cross-tenant access, recipient abuse, duplicate sends, forged approvals, secrets leakage, and misleading “all clear” status. Use endpoint allowlists, safe parsers, strict schemas, least privilege, content isolation, explicit incomplete states, verified email controls, and non-content logs.

### Verification commands

Use current backend/frontend manifests. Minimum evidence includes backend unit/integration tests, adapter fixtures, migration/restore, authorization, scheduler/replay, source-health evaluation, frontend type/lint/test/build, browser e2e, and production health. Confirm exact commands before adding CI rather than creating a parallel toolchain.

## MVP milestones

### M0 — Scope and source contract

- **Outcome:** one vertical and bounded official source register are authoritative.
- **Deliverables:** RCM-001 and RCM-002.
- **Dependencies:** qualified reviewer input.
- **Exit gate:** support, freshness, and incomplete-state behavior are explicit and testable.
- **Deferred:** more jurisdictions and alert channels.

### M1 — Cited review workflow

- **Outcome:** source changes become approved, auditable notifications.
- **Deliverables:** RCM-003 through RCM-009.
- **Dependencies:** M0.
- **Exit gate:** citation, stale-source, authorization, injection, consent, and replay tests pass.
- **Deferred:** autonomous advice or sending.

### M2 — Production and diligence

- **Outcome:** monitoring is recoverable, measurable, and buyer-reviewable.
- **Deliverables:** RCM-010 through RCM-013.
- **Dependencies:** M1.
- **Exit gate:** restore/rollback plus evaluation and diligence review pass.
- **Deferred:** broad source expansion.

### M3 — Qualified pilot

- **Outcome:** a professional validates completeness and workflow value.
- **Deliverables:** RCM-014.
- **Dependencies:** M2 and parallel manual monitoring.
- **Exit gate:** results justify continued vertical investment and identify any RCM-015 need.
- **Deferred:** RCM-015 until the gate passes.

### Next three actions

1. Execute RCM-001 with a written vertical/source-register ADR before changing scrapers.
2. Execute RCM-002 by wrapping one existing source in the versioned adapter contract and adversarial fixtures.
3. Establish a parallel manual-monitoring method so later recall and latency claims have a credible reference.
