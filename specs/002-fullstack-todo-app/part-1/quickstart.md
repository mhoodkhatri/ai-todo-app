# Quickstart: Full-Stack Todo App — Part 1

**Date**: 2026-03-25 | **Prerequisites**: Node.js 20+, Python 3.13+, UV, Neon account

## 1. Neon Database Setup

1. Create a Neon project at [console.neon.tech](https://console.neon.tech)
2. Copy the connection string: `postgresql://user:password@ep-xxx.region.neon.tech/neondb?sslmode=require`
3. Note both the direct and pooled connection strings (pooled uses port 5432 with `-pooler` suffix)

## 2. Generate Secrets

```bash
# Generate BETTER_AUTH_SECRET (32+ character random string)
openssl rand -base64 32
```

## 3. Backend Setup

```bash
cd backend/

# Initialize Python environment
uv sync

# Create .env from template
cp .env.example .env
# Edit .env with your DATABASE_URL, BETTER_AUTH_JWKS_URL, FRONTEND_URL

# Run database migrations
uv run alembic upgrade head

# Start development server
uv run uvicorn app.main:app --reload --port 8000
```

### Backend .env.example

```env
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx.region.neon.tech/neondb?sslmode=require
BETTER_AUTH_SECRET=<same value as frontend — shared secret for JWT verification>
FRONTEND_URL=http://localhost:3000
```

## 4. Frontend Setup

```bash
cd frontend/

# Install dependencies
npm install

# Create .env.local from template
cp .env.example .env.local
# Edit .env.local with your DATABASE_URL, BETTER_AUTH_SECRET, NEXT_PUBLIC_API_URL

# Run Better Auth database migration (creates auth tables in Neon)
npx @better-auth/cli migrate

# Start development server
npm run dev
```

### Frontend .env.example

```env
DATABASE_URL=postgresql://user:password@ep-xxx.region.neon.tech/neondb?sslmode=require
BETTER_AUTH_SECRET=<your-generated-secret>
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

## 5. Verify Setup

1. **Backend health**: `curl http://localhost:8000/api/health` → `{"status": "ok"}`
2. **Frontend**: Open `http://localhost:3000` → should redirect to sign-in page
3. **Sign up**: Create account with display name, email, password
4. **Dashboard**: After signup, should redirect to `/dashboard`
5. **Sign out**: Click sign out → redirected to sign-in page
6. **Protected route**: Visit `/dashboard` while signed out → redirected to sign-in
7. **JWT verification**: Frontend should be able to call FastAPI with JWT token

## 6. Development Workflow

```bash
# Terminal 1: Backend
cd backend && uv run uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

## Environment Variable Reference

| Variable | Service | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | Both | Neon PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | Frontend | Better Auth signing secret |
| `BETTER_AUTH_URL` | Frontend | Better Auth base URL |
| `NEXT_PUBLIC_API_URL` | Frontend | FastAPI backend URL (client-side) |
| `NEXT_PUBLIC_BETTER_AUTH_URL` | Frontend | Better Auth URL (client-side) |
| `BETTER_AUTH_SECRET` | Backend | Shared secret for HS256 JWT verification (same as frontend) |
| `FRONTEND_URL` | Backend | Frontend URL for CORS |
