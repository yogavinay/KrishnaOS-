"""
MAHABHARATA SYSTEM - API Request/Response Models
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    message: str
    mode: str = "text"  # "text" or "voice"


class ChatResponse(BaseModel):
    response: str
    agent_used: str = "krishna"
    intent: str = ""
    timestamp: str = ""


class StatusResponse(BaseModel):
    system: str = "MAHABHARATA"
    status: str = "active"
    agents: Dict[str, str] = {}
    uptime: str = ""


class HistoryItem(BaseModel):
    user_input: str
    agent_response: str
    agent_used: str
    timestamp: Optional[str] = None


class HistoryResponse(BaseModel):
    conversations: List[HistoryItem] = []
    total: int = 0
