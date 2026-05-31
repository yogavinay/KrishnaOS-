"""
GitHub Integration
Clone repos, commit, push, pull, create repos via GitHub API.
"""

import os
import subprocess
from typing import Dict, Any, Optional
from pathlib import Path
from config import settings


class GitHubIntegration:
    """GitHub integration using git CLI and GitHub REST API."""

    def __init__(self):
        self.token = settings.github_token
        self.workspace = str(Path.home() / "Desktop")

    def clone_repo(self, url: str, path: str = None) -> Dict[str, Any]:
        """Clone a GitHub repository."""
        if not path:
            repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
            path = os.path.join(self.workspace, repo_name)

        try:
            result = subprocess.run(
                f'git clone "{url}" "{path}"',
                shell=True, capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0:
                return {"success": True, "summary": f"Cloned: {url} → {path}", "path": path}
            return {"success": False, "error": result.stderr.strip()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def commit_and_push(self, path: str, message: str = "Update from MAHABHARATA") -> Dict[str, Any]:
        """Stage all, commit, and push."""
        try:
            cmds = [
                f'cd /d "{path}" && git add -A',
                f'cd /d "{path}" && git commit -m "{message}"',
                f'cd /d "{path}" && git push',
            ]
            outputs = []
            for cmd in cmds:
                r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
                outputs.append(r.stdout.strip() or r.stderr.strip())
                if r.returncode != 0 and "nothing to commit" not in (r.stdout + r.stderr):
                    return {"success": False, "error": "\n".join(outputs)}

            return {"success": True, "summary": f"Committed and pushed: {message}", "output": "\n".join(outputs)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_repo(self, name: str, private: bool = False, description: str = "") -> Dict[str, Any]:
        """Create a new GitHub repository using the API."""
        if not self.token:
            return {"success": False, "error": "GitHub token not configured. Set GITHUB_TOKEN in .env"}

        try:
            import httpx
            response = httpx.post(
                "https://api.github.com/user/repos",
                headers={
                    "Authorization": f"token {self.token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json={
                    "name": name,
                    "private": private,
                    "description": description or f"Created by MAHABHARATA System"
                },
                timeout=30
            )

            if response.status_code == 201:
                data = response.json()
                return {
                    "success": True,
                    "summary": f"Created repo: {data['html_url']}",
                    "url": data["html_url"],
                    "clone_url": data["clone_url"]
                }
            return {"success": False, "error": f"GitHub API error {response.status_code}: {response.text[:500]}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_repo_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository info from GitHub API."""
        try:
            import httpx
            headers = {"Accept": "application/vnd.github.v3+json"}
            if self.token:
                headers["Authorization"] = f"token {self.token}"

            response = httpx.get(
                f"https://api.github.com/repos/{owner}/{repo}",
                headers=headers, timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "summary": (
                        f"📦 {data['full_name']}\n"
                        f"⭐ {data['stargazers_count']} stars | 🍴 {data['forks_count']} forks\n"
                        f"📝 {data.get('description', 'No description')}\n"
                        f"🔗 {data['html_url']}"
                    ),
                    "data": data
                }
            return {"success": False, "error": f"Not found: {owner}/{repo}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
