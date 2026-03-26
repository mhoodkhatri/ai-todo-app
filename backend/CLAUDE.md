# Backend — FastAPI Todo API

## Stack
- **Language**: Python 3.13+
- **Package Manager**: UV
- **Framework**: FastAPI with async support
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: Neon Serverless PostgreSQL via asyncpg
- **Migrations**: Alembic (async)
- **Auth**: JWT verification via JWKS (EdDSA) with PyJWT + httpx

## Project Structure
```
backend/
├── app/
│   ├── main.py           # FastAPI app, CORS, router includes
│   ├── core/
│   │   ├── config.py     # Pydantic Settings (env vars)
│   │   ├── database.py   # Async engine + session dependency
│   │   └── security.py   # JWT verification dependency
│   ├── models/
│   │   └── task.py       # SQLModel Task table
│   ├── schemas/
│   │   └── common.py     # Shared response schemas
│   └── api/
│       └── health.py     # GET /api/health
├── alembic/              # Database migrations
├── alembic.ini
└── pyproject.toml
```

## Dev Commands
```bash
uv sync                                          # Install dependencies
uv run uvicorn app.main:app --reload --port 8000 # Start dev server
uv run alembic upgrade head                      # Run migrations
uv run alembic revision --autogenerate -m "msg"  # Create migration
```

## Key Conventions
- All routes prefixed with `/api`
- JWT auth via `Depends(get_current_user)` — returns user_id string
- asyncpg + NullPool (Neon handles pooling)
- Environment variables loaded via python-dotenv + Pydantic Settings
