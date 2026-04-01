"""ChatKit endpoint — single POST /chatkit route.

The ChatKit SDK handles all request routing internally (send_message,
list_threads, load_thread, etc.). We extract user_id from JWT and
create a RequestContext for user isolation.
"""

import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response, StreamingResponse

from app.chat.context import RequestContext
from app.chat.server import create_chatkit_server
from app.core.security import get_current_user
from chatkit.server import StreamingResult

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

_chatkit_server = create_chatkit_server()


@router.post("/chatkit")
async def chatkit_endpoint(
    request: Request,
    user_id: str = Depends(get_current_user),
) -> Response:
    context = RequestContext(user_id=user_id)
    body = await request.body()
    try:
        result = await _chatkit_server.process(body, context)
    except Exception:
        logger.exception("ChatKit process failed")
        raise

    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    return Response(content=result.json, media_type="application/json")
