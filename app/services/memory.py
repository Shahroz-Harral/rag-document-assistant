"""
RAG Document Assistant — Session Memory Store

Provides in-memory session conversation history tracking per session_id.
"""

import uuid
from typing import List, Dict, Tuple, Optional


class SessionMemoryManager:
    """Stores recent conversation turns for active sessions."""

    def __init__(self, max_history_turns: int = 6):
        self.max_history_turns = max_history_turns
        self._sessions: Dict[str, List[Tuple[str, str]]] = {}

    def generate_session_id(self) -> str:
        """Generates a unique session ID string."""
        return str(uuid.uuid4())

    def get_history(self, session_id: str) -> List[Tuple[str, str]]:
        """Returns the list of (user_question, assistant_answer) pairs for session_id."""
        return self._sessions.get(session_id, [])

    def format_history_for_prompt(self, session_id: str) -> str:
        """Formats session history into a readable string snippet for LLM prompts."""
        history = self.get_history(session_id)
        if not history:
            return "None"

        formatted = []
        for user_msg, assistant_msg in history:
            formatted.append(f"User: {user_msg}\nAssistant: {assistant_msg}")

        return "\n\n".join(formatted)

    def add_turn(self, session_id: str, user_question: str, assistant_answer: str) -> None:
        """Appends a user-assistant turn to the session history."""
        if session_id not in self._sessions:
            self._sessions[session_id] = []

        self._sessions[session_id].append((user_question, assistant_answer))

        # Enforce max history length
        if len(self._sessions[session_id]) > self.max_history_turns:
            self._sessions[session_id] = self._sessions[session_id][-self.max_history_turns:]

    def clear_session(self, session_id: str) -> bool:
        """Clears history for a given session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False


# Global singleton memory manager
memory_manager = SessionMemoryManager()
