"""
MAHABHARATA SYSTEM - FastAPI Routes
REST API + WebSocket for the frontend dashboard.
"""

import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from api.models import ChatRequest, ChatResponse, StatusResponse, HistoryResponse, HistoryItem
from core.memory.shared_memory import shared_memory

router = APIRouter()

# Will be set by main.py after KRISHNA initializes
krishna_instance = None


def set_krishna(krishna):
    global krishna_instance
    krishna_instance = krishna


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Get system status and agent states."""
    return StatusResponse(
        system="MAHABHARATA",
        status="active" if krishna_instance else "offline",
        agents=shared_memory.get_all_agent_states()
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message and get a response."""
    if not krishna_instance:
        return ChatResponse(
            response="System not initialized.",
            agent_used="none",
            timestamp=datetime.datetime.utcnow().isoformat()
        )

    response = krishna_instance.process_input(request.message)

    return ChatResponse(
        response=response,
        agent_used="krishna",
        timestamp=datetime.datetime.utcnow().isoformat()
    )


@router.get("/history", response_model=HistoryResponse)
async def get_history():
    """Get conversation history."""
    if not krishna_instance:
        return HistoryResponse()

    convos = krishna_instance.dharma.get_recent_conversations(limit=50)
    items = [
        HistoryItem(
            user_input=c["user"],
            agent_response=c["assistant"],
            agent_used=c.get("agent", "krishna"),
            timestamp=c.get("timestamp")
        ) for c in convos
    ]
    return HistoryResponse(conversations=items, total=len(items))


@router.get("/agents")
async def get_agents():
    """Get all agent details."""
    return {
        "agents": [
            {"name": "KRISHNA", "role": "Master Orchestrator", "emoji": "🧠", "status": shared_memory.get_agent_state("krishna")},
            {"name": "ARJUNA", "role": "Search & Knowledge", "emoji": "🏹", "status": shared_memory.get_agent_state("arjuna")},
            {"name": "BHIMA", "role": "System Operator", "emoji": "⚡", "status": shared_memory.get_agent_state("bhima")},
            {"name": "DHARMA", "role": "Memory & Personality", "emoji": "💜", "status": shared_memory.get_agent_state("dharma")},
            {"name": "KARNA", "role": "Coder & Engineer", "emoji": "⚙️", "status": shared_memory.get_agent_state("karna")},
        ]
    }


@router.get("/system-info")
async def get_system_info():
    """Get system information from BHIMA."""
    if not krishna_instance:
        return {"success": False, "error": "System not initialized."}
    return krishna_instance.bhima.get_system_info()


@router.get("/facts")
async def get_user_facts():
    """Get stored user facts from DHARMA."""
    if not krishna_instance:
        return {"facts": []}
    facts = krishna_instance.dharma.get_user_facts()
    return {"facts": facts}


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time communication."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if krishna_instance:
                response = krishna_instance.process_input(data)
            else:
                response = "System not initialized."
            await websocket.send_json({
                "response": response,
                "timestamp": datetime.datetime.utcnow().isoformat()
            })
    except WebSocketDisconnect:
        print("[API] WebSocket client disconnected.")
