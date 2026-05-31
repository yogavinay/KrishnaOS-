"""
Task Router - Intent Classification & Routing
Routes user commands to the appropriate agent.
Now includes KARNA routing and uses Ollama LLM.
"""

from typing import Dict, Any
from openai import OpenAI
from config import settings


class TaskRouter:
    """Classifies user intent and routes to the correct agent."""

    SYSTEM_PROMPT = """You are a task router for an AI system called MAHABHARATA.
You must classify the user's intent and decide which agent should handle it.

Available agents:
- ARJUNA: For search, research, news, knowledge questions, "what is", "who is", "tell me about", weather, current events, Wikipedia lookups
- BHIMA: For system commands, opening/closing apps, file operations, terminal commands, "open", "run", "execute", "list files", system info, screenshots, installing software, killing processes
- KARNA: For coding tasks, writing scripts, creating files, reading code, debugging, git operations, creating projects, programming questions, "write code", "create a script", "make a program"
- KRISHNA: For general conversation, greetings, opinions, creative tasks, casual chat, personal advice

Respond with ONLY a JSON object (no markdown, no extra text, no thinking):
{"agent": "ARJUNA|BHIMA|KARNA|KRISHNA", "intent": "brief description", "subtask": "specific task for the agent"}

Examples:
User: "Search for latest AI news" -> {"agent": "ARJUNA", "intent": "search", "subtask": "search for latest AI news"}
User: "Open Chrome" -> {"agent": "BHIMA", "intent": "open_app", "subtask": "open chrome"}
User: "Write a Python script to sort a list" -> {"agent": "KARNA", "intent": "code_generation", "subtask": "write a Python script to sort a list"}
User: "How are you?" -> {"agent": "KRISHNA", "intent": "greeting", "subtask": "respond to greeting"}
User: "Clone this repo github.com/user/repo" -> {"agent": "KARNA", "intent": "git_operation", "subtask": "clone github.com/user/repo"}
User: "Take a screenshot" -> {"agent": "BHIMA", "intent": "screenshot", "subtask": "take a screenshot"}
User: "Create a new web project" -> {"agent": "KARNA", "intent": "create_project", "subtask": "create a new web project"}"""

    def __init__(self):
        self.llm_client = None
        print("[ROUTER] 🔀 Initializing Task Router...")

    def initialize(self):
        try:
            self.llm_client = OpenAI(
                base_url=settings.ollama_base_url,
                api_key="ollama"
            )
            print("[ROUTER] ✅ Router ready with Ollama LLM.")
        except Exception as e:
            print(f"[ROUTER] ⚠️ Ollama not available: {e}. Using keyword routing.")

    def route(self, user_input: str) -> Dict[str, Any]:
        """Classify intent and determine which agent handles it."""
        # Try LLM-based routing first
        if self.llm_client:
            try:
                return self._llm_route(user_input)
            except Exception as e:
                print(f"[ROUTER] ⚠️ LLM routing failed: {e}")

        # Fallback: keyword-based routing
        return self._keyword_route(user_input)

    def _llm_route(self, user_input: str) -> Dict[str, Any]:
        """Route using Ollama LLM."""
        import json
        response = self.llm_client.chat.completions.create(
            model=settings.ollama_model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            temperature=0.1,
            max_tokens=150
        )
        text = response.choices[0].message.content.strip()
        # Strip <think>...</think> from reasoning models
        if "<think>" in text:
            import re
            text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
        # Clean markdown wrapping if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(text)

    def _keyword_route(self, user_input: str) -> Dict[str, Any]:
        """Simple keyword-based routing fallback."""
        lower = user_input.lower()

        code_keywords = ["code", "script", "program", "function", "class", "debug",
                         "git ", "clone", "commit", "push", "pull", "write a",
                         "create a script", "make a program", "python", "javascript",
                         "html", "create project", "scaffold", "fix the code",
                         "read file", "edit file", "run script"]
        system_keywords = ["open", "launch", "close", "kill", "execute", "terminal",
                          "command", "system info", "screenshot", "install",
                          "list files", "folder", "process", "battery", "disk",
                          "cpu", "ram", "memory"]
        search_keywords = ["search", "find", "what is", "who is", "tell me about",
                          "news", "weather", "latest", "how to", "explain", "why",
                          "look up", "define", "meaning of"]

        for kw in code_keywords:
            if kw in lower:
                return {"agent": "KARNA", "intent": "code_task", "subtask": user_input}

        for kw in system_keywords:
            if kw in lower:
                return {"agent": "BHIMA", "intent": "system_command", "subtask": user_input}

        for kw in search_keywords:
            if kw in lower:
                return {"agent": "ARJUNA", "intent": "search", "subtask": user_input}

        return {"agent": "KRISHNA", "intent": "conversation", "subtask": user_input}
