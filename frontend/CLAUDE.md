# Frontend — Next.js Todo App

## Stack
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS 4
- **Auth**: Better Auth with JWT plugin (HS256)
- **Validation**: Zod
- **Database**: Neon PostgreSQL via pg adapter (Better Auth only)

## Project Structure
```
frontend/
├── app/
│   ├── (auth)/            # Public auth pages (signin, signup)
│   ├── (protected)/       # Authenticated pages (dashboard)
│   ├── api/auth/[...all]/ # Better Auth API handler
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Landing → redirect to /dashboard
├── components/
│   └── auth/              # Auth form components
├── lib/
│   ├── auth.ts            # Better Auth server config
│   ├── auth-client.ts     # Better Auth client instance
│   └── validations.ts     # Zod schemas
└── proxy.ts               # Route protection (Next.js 16)
```

## Dev Commands
```bash
npm install                        # Install dependencies
npm run dev                        # Start dev server (port 3000)
npx @better-auth/cli migrate      # Run Better Auth migrations
npm run build                      # Production build
```

## Key Conventions
- `proxy.ts` replaces `middleware.ts` (Next.js 16 pattern)
- Server components use `auth.api.getSession()` for session checks
- Client components use `authClient` from `lib/auth-client.ts`
- Route params and searchParams are async (must `await`)
- BETTER_AUTH_SECRET shared for session management; JWT uses EdDSA via JWKS
- Backend verifies JWTs by fetching `/api/auth/jwks` public key
