# Regulatory Compliance Monitor

AI-powered system that monitors Federal Register updates, state regulatory sites, and industry bodies, then pushes relevant alerts to subscribers with plain-English impact summaries.

## Architecture

- **Backend**: Python / FastAPI
- **Scrapers**: Federal Register API, RSS feeds, state regulatory sites
- **Summarization**: OpenAI GPT-4 for plain-English impact summaries
- **Alerts**: SendGrid email delivery
- **Scheduler**: APScheduler for periodic monitoring
- **Database**: SQLite (dev) / PostgreSQL (prod) via SQLAlchemy
- **Frontend**: React + Vite + TailwindCSS

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Fill in your API keys
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 summarization |
| `SENDGRID_API_KEY` | SendGrid API key for email delivery |
| `SENDGRID_FROM_EMAIL` | Verified sender email for SendGrid |
| `DATABASE_URL` | Database connection string (default: SQLite) |

## Features

- **Multi-source monitoring**: Federal Register, RSS feeds, state regulatory sites
- **AI summarization**: GPT-4 generates plain-English impact summaries
- **Industry filtering**: Fintech, Healthcare, Food Service categories
- **Email alerts**: Automated delivery to subscribers via SendGrid
- **Dashboard**: Real-time view of regulatory updates and alert management
- **Subscription management**: Users subscribe to specific industries/topics
