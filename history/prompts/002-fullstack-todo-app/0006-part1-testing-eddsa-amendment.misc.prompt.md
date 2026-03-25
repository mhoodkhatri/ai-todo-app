---
id: 6
title: Part 1 Testing and EdDSA Amendment
stage: misc
date: 2026-03-25
surface: agent
model: claude-opus-4-6
feature: 002-fullstack-todo-app
branch: 002-fullstack-todo-app
user: human
command: resume part 1 testing
labels: ["testing", "jwt", "eddsa", "jwks", "amendment", "acceptance-criteria"]
links:
  spec: specs/002-fullstack-todo-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - frontend/lib/auth.ts
  - backend/app/core/security.py
  - backend/CLAUDE.md
  - frontend/CLAUDE.md
  - specs/002-fullstack-todo-app/part-1/plan.md
  - CLAUDE.md
tests:
  - AC-1 signup creates account and redirects to dashboard
  - AC-2 signin with valid credentials returns 200
  - AC-3 wrong password returns 401
  - AC-4 signout clears session and redirects to signin
  - AC-5 unauthenticated dashboard access redirects to signin
  - AC-6 duplicate email returns 422
  - JWT EdDSA verification via JWKS on backend
---

## Prompt

resume part 1 testing

## Response snapshot

Ran full acceptance test suite (AC-1 through AC-6) — all passed. Discovered two issues during testing:

1. **emailAndPassword not enabled**: Better Auth requires explicit `emailAndPassword: { enabled: true }` in config. Added to `frontend/lib/auth.ts`.

2. **HS256 not supported by Better Auth JWT plugin**: The plugin only supports asymmetric algorithms (EdDSA, RS256, ES256). The `algorithm: "HS256"` config was silently ignored, and tokens were signed with EdDSA. User chose Option 1 (amend to EdDSA + JWKS). Updated:
   - `backend/app/core/security.py` — JWKS-based EdDSA verification (caches public key)
   - `frontend/lib/auth.ts` — Removed invalid HS256 config
   - Plan, CLAUDE.md files — Documented the amendment

All 6 acceptance criteria + JWT end-to-end verification passed.
