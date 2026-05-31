"""
KRISHNA - Master Orchestrator (The Commander)
Central brain that receives commands, delegates to agents, and responds.
Powered by local Ollama LLM.
"""

import datetime
from typing import Dict, Any, Optional
from openai import OpenAI
from config import settings
from core.memory.shared_memory import shared_memory
from core.planner.router import TaskRouter
from agents.dharma.memory_agent import DharmaAgent
from agents.arjuna.search_agent import ArjunaAgent
from agents.bhima.system_agent import BhimaAgent
from agents.karna.code_agent import KarnaAgent
from voice.stt.whisper_stt import WhisperSTT
from voice.tts.tts_engine import EdgeTTSEngine


class KrishnaOrchestrator:
    """
    Master Orchestrator - The Commander.
    All agents communicate through KRISHNA only.
    """

    SYSTEM_PROMPT = f"""You are KRISHNA, the master AI assistant of the MAHABHARATA system.
You are speaking to {settings.user_name}. You are wise, helpful, warm, and conversational.
You speak like a trusted advisor — confident but caring.
Keep responses concise unless asked for detail.
If given search results or system output from other agents, incorporate them naturally.
Never mention internal agent names to the user — just answer naturally.
Do NOT wrap your response in <think> tags or show internal reasoning. Just respond directly."""

    def __init__(self):
        self.name = "KRISHNA"
        self.status = "initializing"
        self.llm_client = None

        # Sub-components
        self.router = TaskRouter()
        self.dharma = DharmaAgent()
        self.arjuna = ArjunaAgent()
        self.bhima = BhimaAgent()
        self.karna = KarnaAgent()
        self.stt = WhisperSTT()
        self.tts = EdgeTTSEngine()

        print(f"\n{'='*50}")
        print(f"  🕉️  MAHABHARATA SYSTEM - Initializing...")
        print(f"{'='*50}\n")

    def initialize(self):
        """Initialize KRISHNA and all sub-agents."""
        # Initialize Ollama LLM (OpenAI-compatible API)
        try:
            self.llm_client = OpenAI(
                base_url=settings.ollama_base_url,
                api_key="ollama"  # Ollama doesn't need a real key
            )
            print(f"[{self.name}] 🧠 Ollama LLM connected: {settings.ollama_model}")
        except Exception as e:
            print(f"[{self.name}] ⚠️ Ollama connection failed: {e}")

        # Initialize all agents (DHARMA first per design rules)
        self.dharma.initialize()
        shared_memory.set_agent_state("dharma", "active")

        self.arjuna.initialize()
        shared_memory.set_agent_state("arjuna", "active")

        self.bhima.initialize()
        shared_memory.set_agent_state("bhima", "active")

        self.karna.initialize()
        shared_memory.set_agent_state("karna", "active")

        self.router.initialize()

        # Initialize voice
        self.stt.initialize()
        self.tts.initialize()

        self.status = "active"
        shared_memory.set_agent_state("krishna", "active")
        print(f"\n[{self.name}] ✅ All systems online. KRISHNA is ready.\n")

    def startup_greeting(self):
        """Generate and speak the startup greeting."""
        # Get context from DHARMA
        session_info = self.dharma.get_last_session_info()
        hour = datetime.datetime.now().hour

        # Time-based greeting
        if 6 <= hour < 12:
            greeting = f"Good morning, {settings.user_name}."
        elif 12 <= hour < 17:
            greeting = f"Welcome back, {settings.user_name}. Good afternoon."
        else:
            greeting = f"Good evening, {settings.user_name}. Ready when you are."

        # Add system ready message
        greeting += " I am Krishna, your system is ready. How can I serve you today?"

        # If away for a long time
        if session_info.get("was_away_long"):
            hours = session_info.get("hours_away", 0)
            greeting += f" You were away for {hours:.0f} hours."
            # Get news summary from ARJUNA
            try:
                news = self.arjuna.get_news_summary()
                if news:
                    greeting += f" Here's what you might have missed: {news}"
            except:
                pass

        # Speak the greeting
        self.tts.speak(greeting)
        return greeting

    def process_input(self, user_input: str) -> str:
        """Process user input end-to-end."""
        if not user_input or not user_input.strip():
            return ""

        print(f"\n[{self.name}] 📥 User: {user_input}")
        shared_memory.set_agent_state("krishna", "processing")

        # Step 1: DHARMA injects context (always first)
        context = self.dharma.build_context_for_krishna()
        shared_memory.add_to_conversation_buffer("user", user_input)

        # Step 2: Route to the right agent
        route = self.router.route(user_input)
        agent_name = route.get("agent", "KRISHNA")
        intent = route.get("intent", "unknown")
        subtask = route.get("subtask", user_input)
        print(f"[{self.name}] 🔀 Routed to: {agent_name} (intent: {intent})")

        # Step 3: Execute with the chosen agent
        agent_result = None
        if agent_name == "ARJUNA":
            agent_result = self.arjuna.search(subtask)
        elif agent_name == "BHIMA":
            agent_result = self._handle_bhima(subtask, user_input)
        elif agent_name == "KARNA":
            agent_result = self._handle_karna(subtask, user_input)

        # Step 4: Generate final response with LLM
        response = self._generate_response(user_input, agent_result, context)

        # Step 5: Save to DHARMA
        self.dharma.save_conversation(
            user_input=user_input,
            agent_response=response,
            agent_used=agent_name.lower(),
            intent=intent
        )
        shared_memory.add_to_conversation_buffer("assistant", response, agent_name.lower())
        shared_memory.set_agent_state("krishna", "active")

        print(f"[{self.name}] 📤 Response: {response[:100]}...")
        return response

    def _handle_bhima(self, subtask: str, user_input: str) -> Dict[str, Any]:
        """Handle BHIMA routing — system operations."""
        lower = subtask.lower()

        # Detect intent for Bhima
        if any(kw in lower for kw in ["open", "launch", "start"]):
            # Extract app name
            for prefix in ["open ", "launch ", "start "]:
                if lower.startswith(prefix):
                    app = lower[len(prefix):].strip()
                    return self.bhima.open_application(app)
            return self.bhima.open_application(lower.replace("open", "").strip())

        elif any(kw in lower for kw in ["kill", "close", "stop", "end process"]):
            for prefix in ["kill ", "close ", "stop "]:
                if lower.startswith(prefix):
                    proc = lower[len(prefix):].strip()
                    return self.bhima.kill_process(proc)
            return self.bhima.execute_command(subtask)

        elif any(kw in lower for kw in ["system info", "cpu", "ram", "memory", "disk", "battery"]):
            return self.bhima.get_system_info()

        elif any(kw in lower for kw in ["screenshot", "screen capture"]):
            return self.bhima.take_screenshot()

        elif any(kw in lower for kw in ["list files", "show files", "dir ", "ls "]):
            # Extract path or use default
            path = lower.replace("list files", "").replace("show files", "").strip()
            if not path:
                path = "~"
            return self.bhima.list_directory(path)

        elif any(kw in lower for kw in ["install ", "winget"]):
            app = lower.replace("install ", "").strip()
            return self.bhima.install_app(app)

        else:
            # Generic command execution
            return self.bhima.execute_command(subtask)

    def _handle_karna(self, subtask: str, user_input: str) -> Dict[str, Any]:
        """Handle KARNA routing — code & engineering tasks."""
        lower = subtask.lower()

        if any(kw in lower for kw in ["write", "create", "generate", "make"]) and \
           any(kw in lower for kw in ["code", "script", "program", "function", "file", "class"]):
            return self.karna.generate_code(user_input)

        elif any(kw in lower for kw in ["read", "show", "display", "cat"]) and \
             any(kw in lower for kw in ["file", "code", "script"]):
            # Try to extract filepath
            return self.karna.read_code(subtask)

        elif any(kw in lower for kw in ["run", "execute"]) and \
             any(kw in lower for kw in ["script", "code", "python", "file"]):
            return self.karna.run_code(subtask)

        elif any(kw in lower for kw in ["git ", "clone", "commit", "push", "pull"]):
            return self.karna.git_operation(subtask)

        elif any(kw in lower for kw in ["debug", "fix", "analyze", "explain"]):
            return self.karna.analyze_code(subtask)

        elif any(kw in lower for kw in ["project", "scaffold", "init"]):
            return self.karna.create_project(subtask)

        else:
            # Default: treat as code generation request
            return self.karna.generate_code(user_input)

    def _generate_response(self, user_input: str, agent_result: Optional[Dict],
                           context: str) -> str:
        """Generate the final response using Ollama LLM."""
        if not self.llm_client:
            if agent_result and agent_result.get("success"):
                return agent_result.get("summary") or agent_result.get("output") or "Done."
            return "I'm sorry, my LLM is not connected. Make sure Ollama is running."

        # Build messages
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        # Add context from DHARMA
        if context:
            messages.append({
                "role": "system",
                "content": f"User context from memory:\n{context}"
            })

        # Add conversation history
        history = shared_memory.get_conversation_for_llm(last_n=6)
        messages.extend(history)

        # Add agent results if any
        if agent_result:
            if agent_result.get("success"):
                extra = agent_result.get("summary") or agent_result.get("output") or ""
                sources = agent_result.get("sources", [])
                src_text = ""
                if sources:
                    src_text = "\nSources: " + ", ".join(
                        [s.get("title", "") for s in sources[:3]]
                    )
                messages.append({
                    "role": "system",
                    "content": f"Agent result:\n{extra}{src_text}"
                })
            else:
                messages.append({
                    "role": "system",
                    "content": f"Agent error: {agent_result.get('error', 'Unknown error')}"
                })

        messages.append({"role": "user", "content": user_input})

        try:
            response = self.llm_client.chat.completions.create(
                model=settings.ollama_model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024
            )
            text = response.choices[0].message.content.strip()
            # Strip any <think>...</think> blocks from reasoning models
            if "<think>" in text:
                import re
                text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
            return text
        except Exception as e:
            print(f"[{self.name}] ❌ LLM error: {e}")
            if agent_result and agent_result.get("success"):
                return agent_result.get("summary") or agent_result.get("output") or "Done."
            return f"I encountered an error: {e}. Is Ollama running?"

    def voice_loop(self):
        """Main voice interaction loop."""
        print(f"\n[{self.name}] 🎤 Voice mode active. Say '{settings.wake_word}' or just speak.")
        print(f"[{self.name}] ⌨️  Or type your message. Type 'quit' to exit.\n")

        while self.status == "active":
            try:
                # Text input mode (for testing without mic)
                user_input = input(f"\n🕉️  {settings.user_name} > ").strip()

                if user_input.lower() in ["quit", "exit", "bye", "goodbye"]:
                    self.tts.speak(f"Goodbye, {settings.user_name}. Until next time.")
                    break

                if user_input.lower() == "voice":
                    # Switch to voice mode
                    text = self.stt.listen_until_silence()
                    if text:
                        user_input = text
                    else:
                        print("[STT] No speech detected. Try again.")
                        continue

                if not user_input:
                    continue

                response = self.process_input(user_input)
                self.tts.speak(response)

            except KeyboardInterrupt:
                print("\n[KRISHNA] Interrupted.")
                break
            except Exception as e:
                print(f"[{self.name}] ❌ Error: {e}")

    def shutdown(self):
        """Graceful shutdown of all agents."""
        print(f"\n[{self.name}] 🔄 Shutting down MAHABHARATA SYSTEM...")
        self.dharma.shutdown()
        self.arjuna.shutdown()
        self.bhima.shutdown()
        self.karna.shutdown()
        self.status = "offline"
        print(f"[{self.name}] 💤 All agents offline. System shutdown complete.")
