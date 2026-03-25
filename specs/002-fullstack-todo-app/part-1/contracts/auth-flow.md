# Auth Flow Contract: Full-Stack Todo App

**Date**: 2026-03-25 | **Scope**: Part 1 — Authentication

## Architecture

```text
┌─────────────────────────────────────────────────┐
│                   BROWSER                        │
│                                                  │
│  ┌──────────────┐     ┌──────────────────────┐  │
│  │ Auth Forms    │     │ Dashboard (Part 2+)   │  │
│  │ (signin/up)   │     │ API calls with JWT    │  │
│  └──────┬───────┘     └──────────┬───────────┘  │
│         │                        │               │
└─────────┼────────────────────────┼───────────────┘
          │                        │
          ▼                        ▼
┌─────────────────────┐   ┌────────────────────────┐
│   NEXT.JS 16+       │   │   FASTAPI BACKEND      │
│   (port 3000)       │   │   (port 8000)           │
│                     │   │                          │
│  Better Auth Server │   │  JWT Middleware          │
│  ├─ /api/auth/*     │   │  ├─ Verify HS256 sig    │
│  ├─ JWT Plugin      │   │  │   with shared         │
│  │   (HS256)        │   │  │   BETTER_AUTH_SECRET   │
│  ├─ Session Mgmt    │   │  ├─ Extract user_id      │
│  └─ pg Adapter      │   │  └─ Return 401 if invalid│
│                     │   │                          │
│       ┌─────────────┘   │                          │
│       │                 │                          │
│       ▼                 │          │               │
│  ┌─────────────────────────────────┼──────────┐   │
│  │      NEON SERVERLESS POSTGRESQL │          │   │
│  │                                 ▼          │   │
│  │  ┌───────────┐   ┌─────────────────────┐  │   │
│  │  │ Auth      │   │ Application Tables   │  │   │
│  │  │ Tables    │   │ (task)               │  │   │
│  │  │ (user,    │   │                      │  │   │
│  │  │  session, │   │ Queries filtered by  │  │   │
│  │  │  account) │   │ user_id from JWT     │  │   │
│  │  └───────────┘   └─────────────────────┘  │   │
│  └───────────────────────────────────────────┘   │
└──────────────────────────────────────────────────┘
```

## Auth Endpoints (Better Auth — Next.js side)

All endpoints are handled by Better Auth at `/api/auth/*`.

### POST /api/auth/sign-up/email

**Purpose**: Create a new user account (FR-001)

**Request**:
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "securepass123"
}
```

**Success Response** (200):
```json
{
  "user": {
    "id": "abc123",
    "name": "Jane Doe",
    "email": "jane@example.com",
    "createdAt": "2026-03-25T10:00:00.000Z"
  },
  "session": {
    "id": "sess_xyz",
    "token": "...",
    "expiresAt": "2026-04-24T10:00:00.000Z"
  }
}
```

**Error Responses**:
- `422`: Validation error (name empty/too long, invalid email, password too short)
- `409`: Email already registered (FR-001 scenario 6)

**Validation** (FR-022):
- `name`: 1–100 characters, not whitespace-only
- `email`: Valid email format
- `password`: Minimum 8 characters

### POST /api/auth/sign-in/email

**Purpose**: Authenticate existing user (FR-002)

**Request**:
```json
{
  "email": "jane@example.com",
  "password": "securepass123"
}
```

**Success Response** (200):
```json
{
  "user": { "id": "abc123", "name": "Jane Doe", "email": "jane@example.com" },
  "session": { "id": "sess_xyz", "token": "...", "expiresAt": "..." }
}
```

**Error Responses**:
- `401`: Invalid credentials (wrong email or password)

### POST /api/auth/sign-out

**Purpose**: End user session (FR-017)

**Headers**: Requires session cookie

**Success Response** (200):
```json
{ "success": true }
```

### GET /api/auth/get-session

**Purpose**: Check current session validity (FR-016)

**Headers**: Requires session cookie

**Success Response** (200):
```json
{
  "user": { "id": "abc123", "name": "Jane Doe", "email": "jane@example.com" },
  "session": { "id": "sess_xyz", "expiresAt": "..." }
}
```

**No session** (200): `null`

### GET /api/auth/token

**Purpose**: Get JWT for FastAPI requests (FR-003)

**Headers**: Requires session cookie

**Success Response** (200):
```json
{
  "token": "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9..."
}
```

## FastAPI Endpoints (Part 1)

### GET /api/health

**Purpose**: Backend health check

**Response** (200):
```json
{ "status": "ok" }
```

**No authentication required.**

### JWT Verification Contract (all future endpoints)

**Header**: `Authorization: Bearer <jwt-token>`

**Verification steps** (Constitution §V — shared secret):
1. Extract token from `Authorization` header
2. Decode and verify JWT using `BETTER_AUTH_SECRET` with HS256 algorithm
3. Validate claims: `exp` not expired, `sub` present
4. Return `sub` claim as `user_id`

**No network calls required** — verification uses only the shared secret, identical in both services.

**Error responses**:
- `401 Unauthorized`: Missing header, invalid token, expired token, invalid signature
- Response body: `{ "detail": "Unauthorized" }` (no information leakage)

## Frontend Route Protection

### proxy.ts Contract

| Route Pattern | Auth Required | Behavior |
|---------------|---------------|----------|
| `/signin`, `/signup` | No | If authenticated, redirect to `/dashboard` |
| `/dashboard`, `/dashboard/*` | Yes | If not authenticated, redirect to `/signin` |
| `/api/*` | Skip | Handled by API route handlers |
| `/` | No | Redirect to `/dashboard` (then proxy handles auth) |

### Session Expiry Handling

When a session expires during active use:
1. Better Auth client detects expired session on next API call
2. Frontend redirects to `/signin`
3. Sign-in page shows "Session expired, please sign in again" message
