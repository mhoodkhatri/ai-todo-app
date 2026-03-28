# Research: Task Filtering, Responsive UI & Polish (Part 3)

**Branch**: `002-fullstack-todo-app-part-3` | **Date**: 2026-03-28

## Research Tasks

### R1: Session Expiry Detection with Better Auth + JWT (EdDSA)

**Context**: Part 3 requires detecting expired tokens during active use and redirecting users to sign-in with an informative message.

**Findings**:
- Better Auth issues JWTs via its JWT plugin with configurable expiry (default varies by config)
- The backend's `security.py` already decodes JWTs via JWKS and returns 401 on expired/invalid tokens
- The frontend's `lib/api.ts` fetches tokens from `/api/auth/token` before each API request
- The signin page already supports a `session-expired` query parameter (from Part 1 implementation)

**Decision**: Centralized 401 interception in `lib/api.ts`
- When any API response returns 401, redirect to `/signin?expired=true`
- Use `window.location.href` for hard redirect (clears React state)
- No token refresh logic needed — Better Auth manages session lifecycle

**Rationale**: Single interception point covers all API calls. The existing signin page already shows an expiry banner. No new dependencies or complex refresh flows.

**Alternatives considered**:
1. *Polling session status* — Rejected: adds unnecessary network overhead; reactive detection on API failure is sufficient
2. *JWT expiry pre-check* — Rejected: requires parsing JWT on client, duplicates server-side logic, still needs 401 handling as fallback
3. *Better Auth session middleware* — Rejected: only works for SSR pages, not client-side API calls

---

### R2: Responsive Design Best Practices — Tailwind CSS 4

**Context**: Part 3 requires responsive UI working on mobile (320px+) through desktop (1024px+).

**Findings**:
- Tailwind CSS 4 uses mobile-first breakpoints: `sm` (640px), `md` (768px), `lg` (1024px), `xl` (1280px)
- Current codebase uses `max-w-4xl` (896px) containers and `px-4` padding — good baseline
- Touch targets should be minimum 44x44px per WCAG 2.5.5 (Apple HIG: 44pt)
- Tailwind's `min-h-[44px]` and `min-w-[44px]` enforce minimum touch sizes

**Decision**: Mobile-first with three effective breakpoints:
- **Base** (320px+): Stacked layouts, full-width inputs, larger touch targets
- **md** (768px+): Wider containers, horizontal metadata in task items
- **lg** (1024px+): `max-w-4xl` container, comfortable spacing, side-by-side elements

**Key patterns to apply**:
- Filter buttons: `flex flex-col sm:flex-row` — stack on smallest screens, row on sm+
- Task items: Stack title/metadata vertically on mobile, horizontal on md+
- Dashboard header: Stack user info below title on mobile, flex-row on md+
- Form inputs: Full-width always, but max-width constraints on lg+
- Delete modal: `mx-4 sm:mx-auto sm:max-w-sm` — proper mobile margins

**Alternatives considered**:
1. *CSS container queries* — Rejected: good tech but Tailwind 4's breakpoint utilities are sufficient and more consistent with the existing codebase
2. *Separate mobile components* — Rejected: duplication; responsive Tailwind classes handle this cleanly

---

### R3: Performance Optimization for Next.js 16 Task List

**Context**: SC-008 requires task list loads and renders within 3 seconds on standard broadband.

**Findings**:
- Current flow: Dashboard (server component) renders → TaskList (client) mounts → fetches token → fetches tasks → renders
- The token fetch + task fetch are sequential (token needed for auth header)
- On standard broadband (~10Mbps), two sequential API calls (token + tasks) should complete in <500ms
- React 19 concurrent features can help but aren't needed for this scale
- The main potential bottleneck: cold start on Neon serverless (first connection can take 1-3s)

**Decision**: Measure first, optimize only if needed. Expected optimizations if needed:
1. **Neon cold start**: Already mitigated by asyncpg + NullPool; Neon's auto-suspend timeout can be configured
2. **Sequential fetches**: Could parallelize token fetch and session check, but token is needed first — leave as-is
3. **Component rendering**: Client-side filter changes don't re-fetch — already optimal
4. **Bundle size**: Next.js 16 tree-shaking handles this; no large dependencies added

**Rationale**: The architecture is already lean. Two small API calls over broadband should render well under 3 seconds. Measure with Chrome DevTools Network tab before adding complexity.

---

### R4: Error Handling — Network vs API Errors

**Context**: Part 3 requires graceful error display when backend/DB is unreachable.

**Findings**:
- Current `lib/api.ts` catches errors but doesn't distinguish network failures from API errors
- Network errors (fetch throws `TypeError: Failed to fetch`) indicate backend is unreachable
- API errors (4xx/5xx responses) indicate backend is running but something went wrong
- The task-list component already shows a red error banner

**Decision**: Differentiate error types in `lib/api.ts`:
- **Network error** (fetch throws): Display "Unable to connect to the server. Please check your connection and try again."
- **401 Unauthorized**: Redirect to signin (session expiry flow)
- **4xx errors**: Display the API error message (validation, not found, etc.)
- **5xx errors**: Display "Something went wrong. Please try again later."

**Rationale**: Users need different messaging for "server is down" vs "your input was wrong" vs "your session expired". One error banner with context-appropriate text.

---

## Summary of Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| R1 | Centralized 401 interception in API client | Single point of change; signin page already supports expiry banner |
| R2 | Mobile-first Tailwind with base/md/lg breakpoints | Matches spec requirements; consistent with existing codebase patterns |
| R3 | Measure performance first, optimize only if needed | Architecture is already lean; premature optimization adds complexity |
| R4 | Differentiated error messaging by error type | Users need context-appropriate error messages |

All NEEDS CLARIFICATION items are resolved. No external dependencies or integrations require further research.
