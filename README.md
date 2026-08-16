# Expense Tracker

A full-stack personal finance tracker built to learn and apply production-style backend patterns: async FastAPI, SQLAlchemy 2.0, PostgreSQL, and a Streamlit frontend — deployed to a live cloud database shared across multiple devices.

This started as a hands-on FastAPI learning project and grew into a daily-use tool, including a real migration from local SQLite to a managed cloud Postgres instance (Neon).

## What it does

- Log expenses with date, amount, description, and category
- Filter transactions by month
- View spending totals and a category breakdown chart
- Compare spending across months (grouped and stacked views)
- Bulk-import historical transactions (e.g. from a spreadsheet) with per-row category assignment
- Edit or delete existing transactions
- Runs against a shared cloud database, so multiple devices see the same live data

## Tech stack

**Backend**
- FastAPI (async)
- SQLAlchemy 2.0 (`Mapped` / `mapped_column`, async ORM)
- PostgreSQL, hosted on [Neon](https://neon.tech) (serverless, scale-to-zero)
- Pydantic v2 (request/response schemas)
- Pytest + pytest-asyncio + httpx (isolated async test suite with dependency-injected test database)

**Frontend**
- Streamlit
- Pandas (data shaping and aggregation)
- Plotly (comparison charts)

## Architecture notes

- **Async throughout** — `AsyncSession`, `create_async_engine`, and `asyncpg` as the Postgres driver, with `selectinload` used to safely eager-load relationships (required in async SQLAlchemy, since implicit lazy-loading isn't safe in this context).
- **Layered structure** — `models/` (database shape) → `schemas/` (API input/output shape) → `crud/` (data access) → `routers/` (HTTP layer), keeping each concern isolated and independently testable.
- **Connection pooling tuned for a serverless database** — `pool_pre_ping=True` and `pool_recycle=300` handle Neon's scale-to-zero behavior, so idle-then-resumed connections don't silently fail.
- **Fully isolated test suite** — a separate test database, created and torn down per test via a pytest fixture, with `app.dependency_overrides` swapping the database dependency during tests. No test run touches real data.

## Running locally

```bash
git clone <repo-url>
cd expense_tracker
python -m venv venv
venv\Scripts\activate      # or source venv/bin/activate on macOS/Linux
pip install -r requirements.txt
```

Create a `.env` file in the project root:
```
DATABASE_URL=postgresql+asyncpg://user:password@host/dbname
```

Run the API:
```bash
python -m uvicorn app.main:app --reload
```

Run the frontend (in a separate terminal):
```bash
streamlit run st_app.py
```

Run the tests:
```bash
pytest -v
```

## What this project demonstrates

Built with a deliberate focus on understanding every architectural decision rather than copying working code — including debugging real async/ORM issues (missing `await`, eager-loading errors, dependency-injection scoping) and a genuine SQLite-to-Postgres data migration with foreign-key ID remapping.