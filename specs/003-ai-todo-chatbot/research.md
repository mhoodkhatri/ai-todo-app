# Research: AI Todo Chatbot

**Feature**: 003-ai-todo-chatbot
**Date**: 2026-03-29
**Status**: Complete

## R1: OpenAI Agents SDK — Custom Model Provider (Gemini)

**Decision**: Use `OpenAIChatCompletionsModel` with `AsyncOpenAI` client pointing to Gemini's OpenAI-compatible endpoint.

**Rationale**: The OpenAI Agents SDK natively supports custom model providers via the `OpenAIChatCompletionsModel` class. Gemini 2.5 Flash exposes an OpenAI-compatible `/v1beta/openai/` endpoint, making it a drop-in replacement. This satisfies the constitution's requirement for OpenAI Agents SDK while using the free-tier Gemini model.

**Implementation Pattern**:
```python
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled

# Disable OpenAI tracing when using non-OpenAI provider
set_tracing_disabled(True)

gemini_client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=gemini_client,
)

agent = Agent(
    name="Todo Assistant",
    instructions="...",
    model=model,
    mcp_servers=[mcp_server],
)
```

**Alternatives Considered**:
- Direct Gemini SDK (`google-generativeai`): Rejected — not compatible with OpenAI Agents SDK
- OpenAI models (GPT-4o-mini): Rejected — requires paid API key, spec requires free-tier

**Key Notes**:
- Must call `set_tracing_disabled(True)` since no OpenAI API key is present
- Gemini base URL: `https://generativelanguage.googleapis.com/v1beta/openai/`
- Environment variable: `GEMINI_API_KEY`

---

## R2: MCP Server Architecture — Transport & Integration

**Decision**: Use `MCPServerStdio` with a standalone Python FastMCP server script, spawned as a subprocess by the Agents SDK.

**Rationale**: The OpenAI Agents SDK has built-in MCP client support via `mcp_servers` parameter on `Agent`. Using stdio transport is the simplest approach for same-machine communication. The MCP server runs as a separate Python script using FastMCP, keeping the MCP protocol boundary clean as required by FR-018 and FR-019.

**Implementation Pattern**:
```python
# backend/app/mcp/server.py — Standalone MCP server
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("todo_mcp")

@mcp.tool(name="todo_create_task", annotations={"destructiveHint": False})
async def todo_create_task(user_id: str, title: str, description: str | None = None) -> str:
    """Create a new task for the specified user."""
    # Direct DB access via asyncpg
    ...

if __name__ == "__main__":
    mcp.run()  # stdio transport (default)
```

```python
# In ChatKitServer.respond() — MCP client via Agents SDK
from agents.mcp import MCPServerStdio

async with MCPServerStdio(
    name="Todo MCP Server",
    params={
        "command": "uv",
        "args": ["run", "python", "-m", "app.mcp.server"],
    },
    cache_tools_list=True,
) as mcp_server:
    agent = Agent(
        name="Todo Assistant",
        mcp_servers=[mcp_server],
        ...
    )
```

**Alternatives Considered**:
- `MCPServerStreamableHttp`: More complex, requires separate HTTP endpoint — overkill for same-process communication
- Direct `function_tool` (no MCP): Simplest but violates FR-018/FR-019 MCP requirements
- Mount FastMCP ASGI app on FastAPI: Possible but tightly couples the MCP server to the web framework

**Key Notes**:
- User isolation: `user_id` passed as a required parameter to every MCP tool
- Agent system prompt instructs the model to always pass the authenticated user_id
- MCP server script has its own database connection (reads `DATABASE_URL` from env)
- `cache_tools_list=True` avoids re-listing tools on every run
- Subprocess lifecycle managed by `async with` context manager

---

## R3: OpenAI ChatKit — Backend (Python SDK)

**Decision**: Use `openai-chatkit` Python package (`ChatKitServer` + custom `Store`) for the backend chat infrastructure.

**Rationale**: ChatKit provides a batteries-included framework for chat: request routing, SSE streaming, conversation persistence, and agent integration. The `ChatKitServer` base class handles protocol concerns while we implement `respond()` for agent logic and `Store` for PostgreSQL persistence.

**Implementation Pattern**:
```python
# pip install openai-chatkit
from chatkit.server import ChatKitServer
from chatkit.agents import simple_to_agent_input, stream_agent_response
from agents import Agent, Runner

class TodoChatKitServer(ChatKitServer[RequestContext]):
    async def respond(self, thread, input_user_message, context):
        # 1. Load conversation history
        items_page = await self.store.load_thread_items(
            thread.id, after=None, limit=20, order="desc", context=context
        )
        items = list(reversed(items_page.data))
        input_items = await simple_to_agent_input(items)

        # 2. Create agent with MCP server + Gemini model
        async with MCPServerStdio(...) as mcp_server:
            agent = Agent(
                name="Todo Assistant",
                model=gemini_model,
                mcp_servers=[mcp_server],
                instructions=f"...User ID: {context.user_id}...",
            )
            # 3. Stream response
            result = Runner.run_streamed(agent, input_items)
            async for event in stream_agent_response(context, result):
                yield event
```

**Key Helpers**:
- `simple_to_agent_input()`: Converts ChatKit thread items → Agent SDK input format
- `stream_agent_response()`: Converts Agent SDK streamed run → ChatKit SSE events
- `Store`: Abstract interface for thread/item persistence (we implement with PostgreSQL)

---

## R4: OpenAI ChatKit — Frontend (React SDK)

**Decision**: Use `@openai/chatkit-react` npm package with `useChatKit` hook pointing to our FastAPI backend.

**Rationale**: ChatKit provides a pre-built, production-quality chat UI component with streaming support, thread management, and full customizability. Using the `useChatKit` hook with a custom `fetch` interceptor allows us to inject JWT auth headers and connect to our FastAPI backend instead of OpenAI directly.

**Implementation Pattern**:
```tsx
// npm install @openai/chatkit-react
import { useChatKit, ChatKit } from "@openai/chatkit-react";

function ChatPage() {
  const chatkit = useChatKit({
    api: {
      url: `${process.env.NEXT_PUBLIC_API_URL}/chatkit`,
      // Custom fetch to inject JWT auth
      fetch: async (url, options) => {
        const token = await getJwtToken();
        return fetch(url, {
          ...options,
          headers: {
            ...options.headers,
            Authorization: `Bearer ${token}`,
          },
        });
      },
    },
    onResponseStart: () => setIsResponding(true),
    onResponseEnd: () => setIsResponding(false),
    onError: ({ error }) => { console.error(error); },
  });

  return <ChatKit control={chatkit.control} />;
}
```

**Script Loading** (required for web component):
```tsx
// app/layout.tsx
import Script from "next/script";
<Script
  src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
  strategy="beforeInteractive"
/>
```

**Key Notes**:
- ChatKit renders as a web component (`<openai-chatkit>`)
- Script must load `beforeInteractive` in Next.js
- Custom `fetch` injects `Authorization: Bearer <jwt>` on every request
- Thread management (new conversation, resume) handled by ChatKit automatically
- No domain key needed when connecting to custom backend

---

## R5: ChatKit Store — PostgreSQL Persistence

**Decision**: Implement a custom `Store` class backed by PostgreSQL (Neon) using asyncpg, storing conversations and messages in dedicated tables.

**Rationale**: ChatKit requires a `Store` implementation for thread/item persistence. Our existing Neon PostgreSQL database is the natural choice. We add two new tables (`conversation` and `message`) alongside the existing `task` table.

**Store Interface Methods** (must implement):
- `load_thread(thread_id, context)` → Thread
- `save_thread(thread, context)` → None
- `delete_thread(thread_id, context)` → None
- `load_threads(context)` → list[Thread]
- `load_thread_items(thread_id, ...)` → Page[ThreadItem]
- `add_thread_item(thread_id, item, context)` → None
- `save_item(thread_id, item, context)` → None
- `delete_thread_item(thread_id, item_id, context)` → None
- `generate_thread_id()` → str
- `generate_item_id()` → str

**Key Notes**:
- All Store operations scoped by `user_id` from RequestContext for user isolation
- Uses existing asyncpg engine from `core/database.py`
- Tables managed via Alembic migration

---

## R6: Conversation History & Streaming

**Decision**: Load last 20 messages from the Store per request, convert to agent input via `simple_to_agent_input()`, and stream responses via `stream_agent_response()`.

**Rationale**: ChatKit manages full conversation persistence. The Agent SDK receives conversation history as input items. Streaming is handled end-to-end: Agent SDK → `stream_agent_response()` → SSE → ChatKit React component.

**Flow**:
1. ChatKit React sends user message to `/chatkit` endpoint
2. FastAPI extracts JWT → user_id → creates RequestContext
3. `ChatKitServer.process()` routes to `respond()`
4. `respond()` loads last 20 items from Store
5. `simple_to_agent_input()` converts to Agent SDK format
6. `Runner.run_streamed()` executes agent with Gemini + MCP tools
7. Agent calls MCP tools → tools execute task CRUD → return results
8. `stream_agent_response()` converts to SSE events
9. SSE streamed back to ChatKit React component
10. ChatKit auto-persists items via Store

---

## R7: MCP Tool Authentication & User Isolation

**Decision**: Pass `user_id` as a required parameter on every MCP tool. The agent is instructed via system prompt to always include the authenticated user's ID.

**Rationale**: MCP protocol doesn't forward HTTP auth headers. The standard pattern (per ChatKit integration skill) is to inject credentials into the agent's system prompt. Each MCP tool receives `user_id` and uses it to scope all database queries, enforcing user isolation at the data layer.

**System Prompt Pattern**:
```
You are a helpful todo assistant. You manage tasks for the user.

## Authentication Context
- User ID: {user_id}

CRITICAL: When calling ANY tool, you MUST include user_id="{user_id}" as the first parameter.
Never use a different user_id. This ensures you only access this user's tasks.
```

**Alternatives Considered**:
- Environment variable per subprocess: Complex, subprocess-per-request is expensive
- MCP server-side auth middleware: Not supported in stdio transport
- Shared state via lifespan context: Doesn't cross process boundaries
