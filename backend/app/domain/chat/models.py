from typing import Literal

from pydantic import BaseModel


# Chat models define the message shapes used across conversation flows.
class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
