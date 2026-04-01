# Quickstart: AI Todo Chatbot

**Feature**: 003-ai-todo-chatbot
**Date**: 2026-03-29

## Prerequisites

- Existing 002-fullstack-todo-app running (frontend on :3000, backend on :8000)
- Neon PostgreSQL database with `task` table already migrated
- Better Auth configured with JWT (EdDSA) + JWKS
- Python 3.13+, Node.js 22+, uv, npm

## New Environment Variables

Add to both `backend/.env` and `frontend/.env.local`:

```bash
# backend/.env (add to existing)
GEMINI_API_KEY=your-gemini-api-key-here  # Get from https://aistudio.google.com/apikey

# frontend/.env.local (no changes needed — uses existing NEXT_PUBLIC_API_URL)
```

## Backend Setup

```bash
cd backend/

# Add new dependencies
uv add openai-agents "mcp[cli]" openai-chatkit

# Run new migration (creates conversation + message tables)
uv run alembic upgrade head
```

## Frontend Setup

```bash
cd frontend/

# Add ChatKit React SDK
npm install @openai/chatkit-react
```

## New Files to Create

### Backend
```
backend/app/
├── mcp/
│   ├── __init__.py
│   └── server.py          # FastMCP server with 5 task tools
├── chat/
│   ├── __init__.py
│   ├── server.py           # ChatKitServer subclass (respond + agent)
│   ├── store.py            # PostgreSQL Store implementation
│   └── context.py          # RequestContext dataclass
├── models/
│   └── conversation.py     # Conversation + Message SQLModel
├── schemas/
│   └── chat.py             # Chat-related Pydantic schemas
└── api/
    └── chat.py             # POST /chatkit endpoint
```

### Frontend
```
frontend/
├── app/
│   ├── (protected)/
│   │   └── chat/
│   │       └── page.tsx    # Chat page with ChatKit component
│   └── api/
│       └── chatkit/
│           └── route.ts    # Proxy: reads cookie → forwards with Bearer token
├── components/
│   └── chat/
│       └── chat-interface.tsx  # ChatKit wrapper component
└── lib/
    └── chat.ts             # Chat utility functions
```

## Architecture Flow

```
Browser                  Next.js (:3000)              FastAPI (:8000)
┌──────────┐            ┌─────────────────┐          ┌──────────────────┐
│ ChatKit  │──POST───>  │ /api/chatkit    │──POST──> │ /chatkit         │
│ React    │            │ (cookie proxy)  │          │ (ChatKitServer)  │
│ Component│ <──SSE──── │                 │ <──SSE── │                  │
└──────────┘            └─────────────────┘          │   ↓              │
                                                     │ Agent (Gemini)   │
                                                     │   ↓ MCP stdio   │
                                                     │ FastMCP Server   │
                                                     │   ↓              │
                                                     │ PostgreSQL (Neon)│
                                                     └──────────────────┘
```

## Dev Workflow

Terminal 1 (backend):
```bash
cd backend && uv run uvicorn app.main:app --reload --port 8000
```

Terminal 2 (frontend):
```bash
cd frontend && npm run dev
```

Then navigate to `http://localhost:3000/chat` and start chatting with your AI todo assistant.

## Verification Checklist

- [ ] `GEMINI_API_KEY` is set in `backend/.env`
- [ ] `uv run alembic upgrade head` succeeds (conversation + message tables created)
- [ ] Backend starts without errors on :8000
- [ ] Frontend starts without errors on :3000
- [ ] Navigating to `/chat` shows the ChatKit interface
- [ ] Sending "list my tasks" returns the user's tasks
- [ ] Sending "create a task called Test" creates a task visible in /dashboard
- [ ] Responses stream token-by-token (not all at once)
