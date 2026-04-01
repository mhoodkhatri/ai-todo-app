"""TodoChatKitServer — ChatKit server with OpenAI Agents SDK + Groq."""

import logging
import uuid
from datetime import datetime, timezone

from agents import Runner
from chatkit.server import ChatKitServer
from chatkit.agents import simple_to_agent_input, ThreadItemDoneEvent
from chatkit.types import UserMessageItem, AssistantMessageItem

from app.chat.agent import create_agent
from app.chat.context import RequestContext
from app.chat.store import PostgresStore

logger = logging.getLogger(__name__)


def _filter_text_items(items):
    """Keep only user and assistant messages to avoid tool-call format issues."""
    return [
        item for item in items
        if isinstance(item, (UserMessageItem, AssistantMessageItem))
    ]


class TodoChatKitServer(ChatKitServer[RequestContext]):
    """ChatKit server that delegates to an OpenAI Agents SDK agent with function tools."""

    async def respond(self, thread, input_user_message, context):
        try:
            items_page = await self.store.load_thread_items(
                thread.id, after=None, limit=20, order="desc", context=context
            )
            items = list(reversed(items_page.data))
            items = _filter_text_items(items)
            input_items = await simple_to_agent_input(items)
        except Exception:
            logger.exception("Failed to load conversation history")
            input_items = []

        try:
            agent = create_agent(context.user_id)
            logger.warning("Running agent for user=%s with %d input items", context.user_id, len(input_items))
            result = await Runner.run(agent, input_items)
            logger.warning("Agent result: %s", result.final_output[:500] if result.final_output else "EMPTY")

            assistant_item = AssistantMessageItem(
                id=str(uuid.uuid4()),
                thread_id=thread.id,
                created_at=datetime.now(timezone.utc),
                content=[{"type": "output_text", "text": result.final_output, "annotations": []}],
            )
            await self.store.add_thread_item(
                thread.id, assistant_item, context=context
            )
            logger.warning("Yielding ThreadItemDoneEvent, item_id=%s", assistant_item.id)
            yield ThreadItemDoneEvent(item=assistant_item)
        except Exception as exc:
            logger.exception("Agent execution failed")
            # Extract failed_generation from Groq errors as a fallback response
            error_msg = str(exc)
            fallback_text = None
            if "failed_generation" in error_msg:
                try:
                    import json as _json
                    # Parse the error body to get the failed_generation text
                    start = error_msg.index("{")
                    err_body = _json.loads(error_msg[start:])
                    fallback_text = err_body.get("error", {}).get("failed_generation", "")
                except Exception:
                    pass

            if fallback_text:
                logger.warning("Using failed_generation as fallback response")
                assistant_item = AssistantMessageItem(
                    id=str(uuid.uuid4()),
                    thread_id=thread.id,
                    created_at=datetime.now(timezone.utc),
                    content=[{"type": "output_text", "text": fallback_text, "annotations": []}],
                )
                await self.store.add_thread_item(
                    thread.id, assistant_item, context=context
                )
                yield ThreadItemDoneEvent(item=assistant_item)
            else:
                raise


def create_chatkit_server() -> TodoChatKitServer:
    store = PostgresStore()
    return TodoChatKitServer(store=store)
