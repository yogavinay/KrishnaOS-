"""
ARJUNA - Search & Knowledge Agent (The Researcher)
Searches the internet for real-time information using Tavily.
Returns clean, cited summaries back to KRISHNA.
Powered by local Ollama LLM.
"""

from typing import Dict, Any, Optional
from openai import OpenAI
from config import settings


class ArjunaAgent:
    """
    Search & Knowledge Agent.
    - Searches the web using Tavily API
    - Summarizes results using Ollama LLM
    - Returns cited summaries to KRISHNA
    """

    def __init__(self):
        self.name = "ARJUNA"
        self.status = "initializing"
        self.tavily_client = None
        self.llm_client = None
        print(f"[{self.name}] 🏹 Initializing Search & Knowledge Agent...")

    def initialize(self):
        """Initialize ARJUNA with Tavily and Ollama LLM."""
        try:
            # Initialize Tavily
            if settings.tavily_api_key and settings.tavily_api_key != "your-tavily-key-here":
                from tavily import TavilyClient
                self.tavily_client = TavilyClient(api_key=settings.tavily_api_key)
                print(f"[{self.name}] 🔍 Tavily search connected.")
            else:
                print(f"[{self.name}] ⚠️ No Tavily API key. Search disabled.")

            # Initialize Ollama LLM for summarization
            try:
                self.llm_client = OpenAI(
                    base_url=settings.ollama_base_url,
                    api_key="ollama"
                )
                print(f"[{self.name}] 🧠 Ollama LLM connected for summarization.")
            except Exception as e:
                print(f"[{self.name}] ⚠️ Ollama not available: {e}")

            self.status = "active"
            print(f"[{self.name}] ✅ Search Agent ready.")
        except Exception as e:
            print(f"[{self.name}] ❌ Initialization failed: {e}")
            self.status = "error"

    def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Search the web and return summarized results.
        Called by KRISHNA only.
        """
        self.status = "searching"
        print(f"[{self.name}] 🔍 Searching: '{query}'")

        try:
            if not self.tavily_client:
                return {
                    "success": False,
                    "error": "Tavily not configured. Please set TAVILY_API_KEY in .env file.",
                    "agent": self.name
                }

            # Perform search
            search_results = self.tavily_client.search(
                query=query,
                max_results=max_results,
                search_depth="basic"
            )

            # Extract results
            results = []
            for result in search_results.get("results", []):
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", "")[:500]
                })

            # Summarize with LLM
            summary = self._summarize_results(query, results)

            self.status = "active"
            return {
                "success": True,
                "query": query,
                "summary": summary,
                "sources": [{"title": r["title"], "url": r["url"]} for r in results],
                "agent": self.name
            }

        except Exception as e:
            self.status = "error"
            print(f"[{self.name}] ❌ Search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }

    def _summarize_results(self, query: str, results: list) -> str:
        """Summarize search results using Ollama LLM."""
        if not self.llm_client or not results:
            # Return raw results if no LLM
            return "\n".join([f"• {r['title']}: {r['content'][:200]}" for r in results])

        try:
            results_text = "\n\n".join([
                f"Source: {r['title']} ({r['url']})\n{r['content']}"
                for r in results
            ])

            response = self.llm_client.chat.completions.create(
                model=settings.ollama_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a research assistant. Summarize the following search results into a clear, concise answer. Include source citations. Be brief but thorough. Do NOT use <think> tags."
                    },
                    {
                        "role": "user",
                        "content": f"Question: {query}\n\nSearch Results:\n{results_text}\n\nProvide a clear summary with citations."
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )

            text = response.choices[0].message.content
            # Strip think tags from reasoning models
            if "<think>" in text:
                import re
                text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
            return text
        except Exception as e:
            print(f"[{self.name}] ⚠️ Summarization failed: {e}")
            return "\n".join([f"• {r['title']}: {r['content'][:200]}" for r in results])

    def get_news_summary(self) -> str:
        """Get a quick news summary for startup greeting."""
        result = self.search("latest important news today", max_results=3)
        if result["success"]:
            return result["summary"]
        return "I couldn't fetch the latest news right now."

    def shutdown(self):
        """Shutdown ARJUNA gracefully."""
        self.status = "offline"
        print(f"[{self.name}] 🏹 Search Agent going offline.")
