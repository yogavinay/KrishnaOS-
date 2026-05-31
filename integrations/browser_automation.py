"""
Browser Automation Integration
Open URLs, search Google/YouTube, manage browser tabs.
"""

import webbrowser
import subprocess
import urllib.parse
from typing import Dict, Any, List


class BrowserAutomation:
    """Browser automation using webbrowser module and subprocess."""

    def open_url(self, url: str) -> Dict[str, Any]:
        """Open a URL in the default browser."""
        try:
            # Ensure URL has scheme
            if not url.startswith(("http://", "https://")):
                url = "https://" + url

            webbrowser.open(url)
            return {"success": True, "summary": f"Opened: {url}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_multiple_urls(self, urls: List[str]) -> Dict[str, Any]:
        """Open multiple URLs in browser tabs."""
        try:
            opened = []
            for url in urls:
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url
                webbrowser.open_new_tab(url)
                opened.append(url)

            return {"success": True, "summary": f"Opened {len(opened)} tabs:\n" + "\n".join(f"  🔗 {u}" for u in opened)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_google(self, query: str) -> Dict[str, Any]:
        """Open a Google search."""
        encoded = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/search?q={encoded}"
        webbrowser.open(url)
        return {"success": True, "summary": f"Searching Google: {query}"}

    def search_youtube(self, query: str) -> Dict[str, Any]:
        """Open a YouTube search."""
        encoded = urllib.parse.quote_plus(query)
        url = f"https://www.youtube.com/results?search_query={encoded}"
        webbrowser.open(url)
        return {"success": True, "summary": f"Searching YouTube: {query}"}

    def search_github(self, query: str) -> Dict[str, Any]:
        """Search on GitHub."""
        encoded = urllib.parse.quote_plus(query)
        url = f"https://github.com/search?q={encoded}"
        webbrowser.open(url)
        return {"success": True, "summary": f"Searching GitHub: {query}"}

    def search_stackoverflow(self, query: str) -> Dict[str, Any]:
        """Search on Stack Overflow."""
        encoded = urllib.parse.quote_plus(query)
        url = f"https://stackoverflow.com/search?q={encoded}"
        webbrowser.open(url)
        return {"success": True, "summary": f"Searching Stack Overflow: {query}"}

    def open_gmail(self) -> Dict[str, Any]:
        """Open Gmail."""
        webbrowser.open("https://mail.google.com")
        return {"success": True, "summary": "Opened Gmail."}

    def open_calendar(self) -> Dict[str, Any]:
        """Open Google Calendar."""
        webbrowser.open("https://calendar.google.com")
        return {"success": True, "summary": "Opened Google Calendar."}

    def open_drive(self) -> Dict[str, Any]:
        """Open Google Drive."""
        webbrowser.open("https://drive.google.com")
        return {"success": True, "summary": "Opened Google Drive."}

    def open_chatgpt(self) -> Dict[str, Any]:
        """Open ChatGPT."""
        webbrowser.open("https://chat.openai.com")
        return {"success": True, "summary": "Opened ChatGPT."}
