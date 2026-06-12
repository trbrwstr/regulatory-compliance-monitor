# Regulatory Compliance Monitor

A production-minded MVP for teams that need to stay ahead of regulatory change without manually checking government sites every day.

The app monitors regulatory sources, stores relevant updates, summarizes likely business impact in plain English, and gives operators a dashboard for regulations, alerts, subscribers, and source management.

> **Positioning for freelance clients:** this is a strong starting point for a compliance intelligence portal, client-facing alert product, internal risk dashboard, or proof-of-concept that can be adapted to a specific industry, jurisdiction, and workflow.

## Client Value

Regulatory teams, founders, consultants, and operators often lose time translating dense agency updates into practical next steps. This project reduces that friction by turning raw regulatory feeds into searchable records and actionable notifications.

**What a client gets:**

- A working FastAPI backend with scheduled monitoring and REST APIs.
- A React dashboard for reviewing regulations, alerts, and subscribers.
- Federal Register integration plus extensible RSS and state-site scraper modules.
- AI-generated summaries designed for non-legal stakeholders.
- Email alert plumbing for subscriber-based delivery.
- A clear path from local MVP to production deployment.

## Best-Fit Use Cases

- **Compliance consultants** who want to deliver custom alerts to clients.
- **Startups and SMBs** that need lightweight monitoring before buying enterprise GRC software.
- **Industry associations** that need member-facing regulatory bulletins.
- **Legal, fintech, healthcare, or food-service teams** that need category-specific tracking.
- **Agencies/freelancers** building a paid compliance-monitoring product for a niche market.

## Current Feature Set

- **Multi-source monitoring**: Federal Register API, RSS feeds, and state regulatory site modules.
- **AI summarization**: plain-English summaries and impact framing for regulatory updates.
- **Industry filtering**: default support for Fintech, Healthcare, Food Service, and General updates.
- **Email alerts**: subscriber alert workflow with SendGrid integration points.
- **Dashboard**: overview stats, regulation review, alert tracking, and subscriber management.
- **Source management**: add, list, and remove monitored regulatory sources.
- **Manual trigger**: run a monitoring cycle on demand for demos and testing.

## Architecture

| Layer | Technology | Purpose |
|-------|------------|---------|
| Backend API | Python, FastAPI | REST endpoints, orchestration, dashboard data |
| Data layer | SQLAlchemy, SQLite/PostgreSQL | Local development storage and production-ready database path |
| Scheduler | APScheduler | Periodic source checks and alert processing |
| Scrapers | Federal Register API, RSS, state modules | Source-specific ingestion |
| Summaries | OpenAI API | Plain-English impact summaries |
| Email | SendGrid | Alert delivery |
| Frontend | React, Vite, TailwindCSS | Operator dashboard |

## Repository Structure

```text
backend/
  main.py                 # FastAPI app, startup tasks, dashboard stats, monitor trigger
  models.py               # SQLAlchemy models
  database.py             # Database setup/session helpers
  routers/                # API routes for regulations, alerts, sources, subscriptions
  scrapers/               # Federal Register, RSS, and state regulatory ingestion modules
  services/               # Scheduler, summarizer, and alert delivery services
frontend/
  src/                    # React dashboard pages and components
  package.json            # Frontend scripts and dependencies
README.md
```

## Local Setup

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```

The API will run at `http://localhost:8000`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

The dashboard will run at `http://localhost:5173` by default.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes for AI summaries | OpenAI API key used by the summarization service. |
| `SENDGRID_API_KEY` | Yes for email alerts | SendGrid API key used for outbound alert delivery. |
| `SENDGRID_FROM_EMAIL` | Yes for email alerts | Verified sender email address in SendGrid. |
| `DATABASE_URL` | Optional | Database connection string. Defaults to local SQLite when unset. |

## Key API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/health` | Basic service health check. |
| `GET` | `/api/dashboard/stats` | Dashboard totals for regulations, high-impact items, alerts, and subscribers. |
| `POST` | `/api/monitor/trigger` | Manually trigger a Federal Register monitoring cycle. |
| `GET` | `/api/regulations` | List regulations with optional industry and impact filters. |
| `GET` | `/api/alerts` | List alerts with optional status/subscriber filters. |
| `GET` | `/api/subscriptions` | List subscribers. |
| `POST` | `/api/subscriptions` | Add a subscriber and selected industries. |
| `GET` | `/api/sources` | List configured regulatory sources. |
| `POST` | `/api/sources` | Add a regulatory source. |
| `GET` | `/api/sources/industries` | List supported industry categories. |

## Demo Workflow for Clients

1. Start the backend and frontend locally.
2. Open the dashboard and review seeded industry categories.
3. Trigger monitoring with `POST /api/monitor/trigger`.
4. Review captured regulations and generated summaries.
5. Add a test subscriber for a target industry.
6. Confirm alert records and email delivery behavior.
7. Discuss production requirements: source coverage, approval flows, authentication, deployment, and reporting.

## Production Hardening Checklist

Before using this with real client data or paid subscribers, prioritize:

- Add authentication and role-based access for the dashboard and API.
- Restrict CORS to the production frontend domain.
- Move from SQLite to managed PostgreSQL.
- Add retries, rate limits, and structured logs around scrapers and email delivery.
- Add unsubscribe, consent, and audit trails for email compliance.
- Validate and normalize all third-party source inputs.
- Add human review for high-impact alerts before sending them externally.
- Add automated backend and frontend test coverage.
- Add deployment configuration for the chosen host.

## Suggested Freelance Delivery Packages

### MVP Customization

- Brand the dashboard.
- Configure industries, keywords, and monitored sources.
- Connect production API keys.
- Deploy backend, frontend, and database.

### Compliance Alert Product

- Add authentication, teams, and client workspaces.
- Build subscriber self-service preferences.
- Add approval workflows before alerts are sent.
- Add analytics for delivered, opened, and failed alerts.

### Enterprise/Internal Tooling

- Add SSO, audit logs, and stricter access controls.
- Integrate Slack, Teams, or ticketing systems.
- Add custom risk scoring and review queues.
- Add exports for compliance reports and board updates.

## Important Disclaimer

This software is a monitoring and summarization tool, not legal advice. AI-generated summaries should be reviewed by qualified professionals before clients make legal, compliance, or operational decisions.

## Roadmap Ideas

- Keyword and geography-based source configuration.
- Alert approval queue with reviewer notes.
- Diffing between proposed and final rules.
- Client-facing portal for alert preferences.
- Slack/Teams notifications.
- Source reliability scoring and failed-scrape reporting.
- Compliance calendar with effective-date reminders.
