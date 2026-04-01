from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Incoming ChatKit request — the ChatKit SDK handles routing internally."""
    pass


class ChatErrorResponse(BaseModel):
    detail: str
