"""
DHARMA - Memory & Personality Agent (The Soul)
Stores conversations, learns user habits, extracts knowledge,
provides context to KRISHNA. Enhanced with fact extraction
and memory search.
"""

import datetime
import re
from typing import Dict, List, Optional, Any
from openai import OpenAI
from core.memory.database import db, Conversation, Session, UserProfile, UserFact
from config import settings


class DharmaAgent:
    """
    Memory & Personality Agent.
    - Stores all conversations to database
    - Extracts structured facts from conversations
    - Loads last session context on startup
    - Tracks user habits and preferences
    - Provides KRISHNA with relevant past context
    - Searches past conversations by keyword
    """

    def __init__(self):
        self.name = "DHARMA"
        self.status = "initializing"
        self.llm_client = None
        self._current_session: Optional[Session] = None
        print(f"[{self.name}] 🕉️ Initializing Memory & Personality Agent...")

    def initialize(self):
        """Initialize DHARMA - connect to database and LLM."""
        try:
            db.initialize()
            self._start_new_session()

            # Connect to Ollama for fact extraction and summaries
            try:
                self.llm_client = OpenAI(
                    base_url=settings.ollama_base_url,
                    api_key="ollama"
                )
            except:
                pass

            self.status = "active"
            print(f"[{self.name}] ✅ Memory Agent active. Soul is awake.")
        except Exception as e:
            print(f"[{self.name}] ❌ Initialization failed: {e}")
            self.status = "error"

    def _start_new_session(self):
        """Start a new user session."""
        try:
            session = db.get_session()
            new_session = Session(
                start_time=datetime.datetime.utcnow(),
                is_active=True
            )
            session.add(new_session)
            session.commit()
            self._current_session = new_session
            session.close()
            print(f"[{self.name}] 📝 New session started (ID: {new_session.id})")
        except Exception as e:
            print(f"[{self.name}] ⚠️ Could not start session: {e}")

    def save_conversation(self, user_input: str, agent_response: str,
                          agent_used: str = "krishna", intent: str = None,
                          sentiment: str = None, metadata: dict = None):
        """Save a conversation exchange and extract facts."""
        try:
            session = db.get_session()
            conv = Conversation(
                session_id=self._current_session.id if self._current_session else None,
                user_input=user_input,
                agent_response=agent_response,
                agent_used=agent_used,
                intent=intent,
                sentiment=sentiment,
                metadata_=metadata
            )
            session.add(conv)

            # Update session interaction count
            if self._current_session:
                db_session = session.query(Session).filter_by(id=self._current_session.id).first()
                if db_session:
                    db_session.total_interactions = (db_session.total_interactions or 0) + 1

            session.commit()
            conv_id = conv.id
            session.close()

            # Extract facts asynchronously (don't block the main flow)
            try:
                self._extract_and_store_facts(user_input, agent_response, conv_id)
            except:
                pass

        except Exception as e:
            print(f"[{self.name}] ⚠️ Failed to save conversation: {e}")

    def _extract_and_store_facts(self, user_input: str, agent_response: str, conv_id: int):
        """Extract structured facts from a conversation using LLM."""
        if not self.llm_client:
            return

        # Only extract from substantive conversations
        if len(user_input) < 15:
            return

        try:
            response = self.llm_client.chat.completions.create(
                model=settings.ollama_model,
                messages=[
                    {"role": "system", "content": """Extract key facts about the user from this conversation.
Return ONLY a JSON array of facts. Each fact has: type, key, value.
Types: preference, project, schedule, person, interest, skill, dislike
If no meaningful facts, return empty array: []
Do NOT use <think> tags. Return ONLY the JSON array.

Examples:
[{"type": "preference", "key": "favorite_language", "value": "Python"}]
[{"type": "project", "key": "current_project", "value": "Mahabharata AI System"}]
[{"type": "interest", "key": "topic", "value": "machine learning"}]
[]"""},
                    {"role": "user", "content": f"User said: {user_input}\nAssistant replied: {agent_response[:300]}"}
                ],
                temperature=0.1,
                max_tokens=300
            )

            text = response.choices[0].message.content.strip()
            # Strip think tags
            if "<think>" in text:
                text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

            # Parse JSON
            import json
            # Find JSON array in text
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                facts = json.loads(match.group())
                if facts and isinstance(facts, list):
                    session = db.get_session()
                    for fact in facts[:3]:  # Max 3 facts per conversation
                        if all(k in fact for k in ["type", "key", "value"]):
                            # Check if fact already exists
                            existing = session.query(UserFact).filter_by(
                                fact_type=fact["type"],
                                fact_key=fact["key"]
                            ).first()

                            if existing:
                                existing.fact_value = fact["value"]
                                existing.updated_at = datetime.datetime.utcnow()
                                existing.source_conversation_id = conv_id
                            else:
                                new_fact = UserFact(
                                    fact_type=fact["type"],
                                    fact_key=fact["key"],
                                    fact_value=fact["value"],
                                    source_conversation_id=conv_id
                                )
                                session.add(new_fact)

                    session.commit()
                    session.close()

        except Exception as e:
            # Silent failure — fact extraction is non-critical
            pass

    def get_last_session_info(self) -> Dict[str, Any]:
        """Get information about the last session for startup greeting."""
        try:
            session = db.get_session()
            last_session = session.query(Session).filter(
                Session.is_active == False
            ).order_by(Session.end_time.desc()).first()

            if last_session and last_session.end_time:
                time_away = datetime.datetime.utcnow() - last_session.end_time
                hours_away = time_away.total_seconds() / 3600

                result = {
                    "has_previous_session": True,
                    "hours_away": round(hours_away, 1),
                    "last_session_summary": last_session.summary or "No summary available.",
                    "last_session_interactions": last_session.total_interactions or 0,
                    "was_away_long": hours_away > 8
                }
            else:
                result = {
                    "has_previous_session": False,
                    "hours_away": 0,
                    "last_session_summary": None,
                    "last_session_interactions": 0,
                    "was_away_long": False
                }

            session.close()
            return result
        except Exception as e:
            print(f"[{self.name}] ⚠️ Could not get last session: {e}")
            return {
                "has_previous_session": False,
                "hours_away": 0,
                "last_session_summary": None,
                "last_session_interactions": 0,
                "was_away_long": False
            }

    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Get recent conversations for context injection."""
        try:
            session = db.get_session()
            conversations = session.query(Conversation).order_by(
                Conversation.timestamp.desc()
            ).limit(limit).all()

            result = []
            for conv in reversed(conversations):
                result.append({
                    "user": conv.user_input,
                    "assistant": conv.agent_response,
                    "agent": conv.agent_used,
                    "timestamp": conv.timestamp.isoformat() if conv.timestamp else None
                })

            session.close()
            return result
        except Exception as e:
            print(f"[{self.name}] ⚠️ Could not get conversations: {e}")
            return []

    def search_memory(self, query: str, limit: int = 10) -> List[Dict]:
        """Search past conversations by keyword."""
        try:
            session = db.get_session()
            # Simple keyword search
            conversations = session.query(Conversation).filter(
                Conversation.user_input.ilike(f"%{query}%") |
                Conversation.agent_response.ilike(f"%{query}%")
            ).order_by(
                Conversation.timestamp.desc()
            ).limit(limit).all()

            result = []
            for conv in conversations:
                result.append({
                    "user": conv.user_input,
                    "assistant": conv.agent_response[:200],
                    "agent": conv.agent_used,
                    "timestamp": conv.timestamp.isoformat() if conv.timestamp else None
                })

            session.close()
            return result
        except Exception as e:
            print(f"[{self.name}] ⚠️ Memory search failed: {e}")
            return []

    def get_user_facts(self, fact_type: str = None) -> List[Dict]:
        """Get stored user facts, optionally filtered by type."""
        try:
            session = db.get_session()
            query = session.query(UserFact)
            if fact_type:
                query = query.filter_by(fact_type=fact_type)
            facts = query.order_by(UserFact.updated_at.desc()).all()

            result = [
                {
                    "type": f.fact_type,
                    "key": f.fact_key,
                    "value": f.fact_value,
                    "confidence": f.confidence,
                    "updated": f.updated_at.isoformat() if f.updated_at else None
                }
                for f in facts
            ]
            session.close()
            return result
        except Exception as e:
            print(f"[{self.name}] ⚠️ Could not get facts: {e}")
            return []

    def get_user_profile(self) -> Dict[str, Any]:
        """Get or create the user profile."""
        try:
            session = db.get_session()
            profile = session.query(UserProfile).first()

            if not profile:
                profile = UserProfile(name=settings.user_name)
                session.add(profile)
                session.commit()

            result = {
                "name": profile.name,
                "preferences": profile.preferences or {},
                "habits": profile.habits or {},
                "last_seen": profile.last_seen.isoformat() if profile.last_seen else None,
                "total_sessions": profile.total_sessions or 0
            }

            # Update last seen
            profile.last_seen = datetime.datetime.utcnow()
            profile.total_sessions = (profile.total_sessions or 0) + 1
            session.commit()
            session.close()
            return result
        except Exception as e:
            print(f"[{self.name}] ⚠️ Could not get user profile: {e}")
            return {"name": settings.user_name, "preferences": {}, "habits": {}}

    def build_context_for_krishna(self) -> str:
        """Build a rich context string for KRISHNA before each task."""
        recent = self.get_recent_conversations(limit=5)
        profile = self.get_user_profile()
        facts = self.get_user_facts()

        context_parts = [
            f"User Name: {profile.get('name', settings.user_name)}",
            f"Total Sessions: {profile.get('total_sessions', 0)}",
        ]

        if profile.get("preferences"):
            context_parts.append(f"User Preferences: {profile['preferences']}")

        # Add extracted facts
        if facts:
            context_parts.append("\nKnown facts about user:")
            for f in facts[:10]:
                context_parts.append(f"  - {f['type']}: {f['key']} = {f['value']}")

        if recent:
            context_parts.append("\nRecent conversation history:")
            for conv in recent[-3:]:
                context_parts.append(f"  User: {conv['user'][:100]}")
                context_parts.append(f"  Assistant: {conv['assistant'][:100]}")

        return "\n".join(context_parts)

    def end_session(self, summary: str = None):
        """End the current session with an LLM-generated summary."""
        try:
            if self._current_session:
                # Try to generate summary with LLM
                if not summary and self.llm_client:
                    summary = self._generate_session_summary()

                session = db.get_session()
                db_session = session.query(Session).filter_by(id=self._current_session.id).first()
                if db_session:
                    db_session.end_time = datetime.datetime.utcnow()
                    db_session.is_active = False
                    db_session.summary = summary or "Session ended normally."
                    session.commit()
                session.close()
                print(f"[{self.name}] 📝 Session ended.")
        except Exception as e:
            print(f"[{self.name}] ⚠️ Could not end session: {e}")

    def _generate_session_summary(self) -> str:
        """Generate a session summary using LLM."""
        try:
            recent = self.get_recent_conversations(limit=20)
            if not recent or not self.llm_client:
                return "Session ended normally."

            conv_text = "\n".join([
                f"User: {c['user'][:100]}\nAssistant: {c['assistant'][:100]}"
                for c in recent[-10:]
            ])

            response = self.llm_client.chat.completions.create(
                model=settings.ollama_model,
                messages=[
                    {"role": "system", "content": "Summarize this conversation session in 2-3 sentences. Focus on what the user did, what topics were discussed, and any outcomes. Be concise. Do NOT use <think> tags."},
                    {"role": "user", "content": f"Session conversations:\n{conv_text}"}
                ],
                temperature=0.3,
                max_tokens=200
            )

            text = response.choices[0].message.content.strip()
            if "<think>" in text:
                text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
            return text
        except:
            return "Session ended normally."

    def shutdown(self):
        """Shutdown DHARMA gracefully."""
        self.end_session()
        self.status = "offline"
        print(f"[{self.name}] 💤 Memory Agent going to sleep.")
