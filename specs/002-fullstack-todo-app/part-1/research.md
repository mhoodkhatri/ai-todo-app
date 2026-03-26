# Research: Full-Stack Todo App — Part 1

**Date**: 2026-03-25 | **Scope**: Foundation, Database & Authentication

## 1. Better Auth with Next.js 16+ App Router

### Decision: Better Auth with JWT Plugin + pg adapter

**Rationale**: Better Auth is the prescribed auth framework (Constitution). Its JWT plugin issues JWTs that a separate FastAPI backend can verify independently. The `pg` adapter connects directly to Neon PostgreSQL.

**Alternatives considered**:
- Auth.js (NextAuth v5): More popular, but constitution mandates Better Auth
- Clerk/Auth0: Managed services, not prescribed by constitution

### Setup Details

- **Installation**: `npm install better-auth`
- **CLI**: `npx @better-auth/cli generate` (schema), `npx @better-auth/cli migrate` (apply)
- **Server config**: `lib/auth.ts` — `betterAuth()` with `database: new Pool({ connectionString })`, `secret: BETTER_AUTH_SECRET`, JWT plugin
- **Client config**: `lib/auth-client.ts` — `createAuthClient({ baseURL })`
- **API handler**: `app/api/auth/[...all]/route.ts` — `toNextJsHandler(auth)`
- **JWT plugin**: Adds `/api/auth/token` endpoint and `/api/auth/jwks` endpoint. Signs tokens with EdDSA by default. Token claims include `sub` (user ID), `iss`, `aud`, `exp`.

### Better Auth Database Tables (auto-managed)

| Table | Key Fields | Purpose |
|-------|------------|---------|
| `user` | id, name, email, emailVerified, image, createdAt, updatedAt | User accounts |
| `session` | id, userId, token, expiresAt, ipAddress, userAgent | Active sessions |
| `account` | id, userId, accountId, provider, accessToken | Auth providers |
| `verification` | id, identifier, value, expiresAt | Email/token verification |

### Auth Flows

- **Sign up**: `authClient.signUp.email({ email, password, name })` → creates user + session
- **Sign in**: `authClient.signIn.email({ email, password })` → creates session, issues JWT
- **Sign out**: `authClient.signOut()` → invalidates session
- **Get token**: `authClient.token()` → returns current JWT for API calls
- **Session check**: `auth.api.getSession({ headers: await headers() })` → server-side

## 2. JWT Verification in FastAPI

### Decision: Shared secret (HS256) with PyJWT — per Constitution §V

**Rationale**: Constitution §V explicitly mandates: "The FastAPI backend MUST verify every request using JWT middleware with a shared secret (`BETTER_AUTH_SECRET` env var, identical in both services)." HS256 (HMAC-SHA256) uses the same secret to sign (Better Auth) and verify (FastAPI). No network calls needed — verification is purely local.

**Alternatives considered**:
- EdDSA/RS256 with JWKS endpoint: More secure (asymmetric), but violates constitution's "shared secret" requirement.
- Forward token to Better Auth for validation: Adds latency, tight coupling, single point of failure.

### Implementation

- **Python packages**: `pyjwt>=2.8.0` (no `cryptography` needed for HS256)
- **Token decode**: `jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])` → extract `sub` as user_id
- **FastAPI dependency**: `Depends(get_current_user)` returns user_id string
- **401 response**: Missing/invalid/expired token → `HTTPException(401, "Unauthorized")`
- **No network calls**: Verification uses only the shared secret — no JWKS fetch needed

### Better Auth JWT Plugin Configuration

```typescript
// lib/auth.ts
import { jwt } from "better-auth/plugins";

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET,
  plugins: [
    jwt({
      jwt: {
        algorithm: "HS256",  // Symmetric — uses BETTER_AUTH_SECRET
        expirationTime: "15m",
      },
    }),
  ],
});
```

### FastAPI Verification

```python
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"],
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return user_id
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Unauthorized")
```

### JWT Claims Structure

```json
{
  "sub": "user-id-string",
  "iss": "http://localhost:3000",
  "aud": "http://localhost:3000",
  "iat": 1711324800,
  "exp": 1711325700
}
```

## 3. Neon Serverless PostgreSQL + SQLModel

### Decision: asyncpg driver + NullPool + SQLModel

**Rationale**: `asyncpg` is the fastest async PostgreSQL driver for Python (5x faster than psycopg3). `NullPool` avoids double-pooling since Neon provides built-in pgbouncer. SQLModel is the prescribed ORM (Constitution).

**Alternatives considered**:
- psycopg3 (async): Slower but more familiar API. Not needed since SQLModel abstracts the driver.
- psycopg2 (sync): No async support, poor fit for FastAPI.

### Connection Configuration

```python
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@ep-xxx.neon.tech/db?sslmode=require",
    pool_class=NullPool,
    pool_pre_ping=True,
    connect_args={"statement_cache_size": 0}  # Required for pgbouncer
)
```

### Key Settings
- `NullPool`: Let Neon's pgbouncer handle pooling
- `pool_pre_ping=True`: Detect stale connections after Neon scale-down
- `statement_cache_size=0`: Required for pgbouncer transaction mode
- `sslmode=require`: Required for Neon connections

## 4. Next.js 16 Breaking Changes

### Decision: Use proxy.ts (not middleware.ts), async params

**Rationale**: Next.js 16 deprecates `middleware.ts` in favor of `proxy.ts` which runs in Node.js runtime. All route params and searchParams are now async (must `await`). Turbopack is the default bundler.

**Key migrations**:
- `middleware.ts` → `proxy.ts`, `middleware()` → `proxy()` function
- `{ params }` → `{ params }` with `const { slug } = await params`
- Turbopack is default, no configuration needed

### Route Protection Pattern

```typescript
// proxy.ts
export async function proxy(request: NextRequest) {
  const session = await auth.api.getSession({ headers: await headers() });
  if (!session && isProtectedRoute(request.nextUrl.pathname)) {
    return NextResponse.redirect(new URL("/signin", request.url));
  }
  return NextResponse.next();
}
```

## 5. FastAPI Project Setup with UV

### Decision: UV package manager + layered project structure

**Rationale**: UV is 10-100x faster than pip, creates reproducible lockfiles (`uv.lock`), and is officially recommended by the FastAPI team. Constitution mandates UV.

### Commands
```bash
uv init --name todo-backend --python 3.13
uv add fastapi uvicorn[standard] sqlmodel asyncpg pyjwt cryptography httpx alembic python-dotenv
uv add --dev pytest pytest-asyncio
```

## 6. Frontend Token Management

### Decision: Better Auth client manages tokens automatically

**Rationale**: Better Auth's client SDK handles session persistence via cookies and token retrieval via `authClient.token()`. No manual localStorage/sessionStorage management needed. The client automatically refreshes sessions.

**Flow for FastAPI requests**:
1. Frontend calls `authClient.token()` to get current JWT
2. Includes JWT in `Authorization: Bearer <token>` header
3. FastAPI `security.py` dependency verifies using shared `BETTER_AUTH_SECRET` (HS256)
4. Returns user_id to endpoint handler
