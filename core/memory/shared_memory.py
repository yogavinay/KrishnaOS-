"""
MAHABHARATA SYSTEM - Shared Memory
Global shared context store accessible by all agents through KRISHNA.
"""

import datetime
from typing import Any, Dict, List, Optional


class SharedMemory:
    """
    In-memory shared context store.
    All agents read/write through KRISHNA only.
    """

    def __init__(self):
        self._context: Dict[str, Any] = {}
        self._conversation_buffer: List[Dict] = []
        self._max_buffer_size = 50
        self._current_session_id: Optional[int] = None
        self._user_context: Dict[str, Any] = {}
        self._agent_states: Dict[str, str] = {
            "krishna": "idle",
            "arjuna": "idle",
            "bhima": "idle",
            "dharma": "idle",
            "karna": "idle",
        }

    def set(self, key: str, value: Any):
        """Store a value in shared memory."""
        self._context[key] = {
            "value": value,
            "updated_at": datetime.datetime.utcnow().isoformat()
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from shared memory."""
        entry = self._context.get(key)
        if entry:
            return entry["value"]
        return default

    def add_to_conversation_buffer(self, role: str, content: str, agent: str = "krishna"):
        """Add a message to the conversation buffer."""
        self._conversation_buffer.append({
            "role": role,
            "content": content,
            "agent": agent,
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        # Keep buffer size manageable
        if len(self._conversation_buffer) > self._max_buffer_size:
            self._conversation_buffer = self._conversation_buffer[-self._max_buffer_size:]

    def get_conversation_buffer(self, last_n: int = 10) -> List[Dict]:
        """Get the last N messages from the conversation buffer."""
        return self._conversation_buffer[-last_n:]

    def get_conversation_for_llm(self, last_n: int = 10) -> List[Dict]:
        """Get conversation history formatted for LLM API calls."""
        messages = []
        for msg in self._conversation_buffer[-last_n:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        return messages

    def set_agent_state(self, agent: str, state: str):
        """Update an agent's state."""
        self._agent_states[agent.lower()] = state

    def get_agent_state(self, agent: str) -> str:
        """Get an agent's current state."""
        return self._agent_states.get(agent.lower(), "unknown")

    def get_all_agent_states(self) -> Dict[str, str]:
        """Get all agent states."""
        return self._agent_states.copy()

    def set_user_context(self, context: Dict[str, Any]):
        """Set user context from DHARMA."""
        self._user_context.update(context)

    def get_user_context(self) -> Dict[str, Any]:
        """Get current user context."""
        return self._user_context.copy()

    def clear_buffer(self):
        """Clear the conversation buffer."""
        self._conversation_buffer.clear()

    def reset(self):
        """Full reset of shared memory."""
        self._context.clear()
        self._conversation_buffer.clear()
        self._user_context.clear()


# Singleton
shared_memory = SharedMemory()
