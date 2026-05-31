"""
KARNA - Coder & Engineer Agent (The Builder)
Writes, reads, edits, runs code. Manages git operations.
Generates code using local Ollama LLM.
"""

import os
import subprocess
import re
from typing import Dict, Any, Optional
from pathlib import Path
from openai import OpenAI
from config import settings


class KarnaAgent:
    """
    Coder & Engineer Agent.
    - Generates code using Ollama LLM
    - Reads, writes, edits files
    - Runs scripts (Python, JS, batch, PowerShell)
    - Git operations (clone, commit, push, pull)
    - Project scaffolding
    """

    CODE_SYSTEM_PROMPT = """You are KARNA, an expert software engineer and coder.
You write clean, well-commented, production-quality code.
When asked to write code, respond ONLY with the code wrapped in a code block.
Use the format:
```language
code here
```
If a filename is implied, include it as a comment at the top.
Do NOT add explanations outside the code block unless specifically asked.
Do NOT use <think> tags."""

    def __init__(self):
        self.name = "KARNA"
        self.status = "initializing"
        self.llm_client = None
        self.workspace = str(Path.home() / "Desktop")
        print(f"[{self.name}] ⚙️ Initializing Coder & Engineer Agent...")

    def initialize(self):
        """Initialize KARNA with Ollama LLM."""
        try:
            self.llm_client = OpenAI(
                base_url=settings.ollama_base_url,
                api_key="ollama"
            )
            self.status = "active"
            print(f"[{self.name}] ✅ Coder Agent ready. LLM: {settings.ollama_model}")
        except Exception as e:
            print(f"[{self.name}] ❌ Initialization failed: {e}")
            self.status = "error"

    # ─────────────────────────────────────────────
    # CODE GENERATION
    # ─────────────────────────────────────────────

    def generate_code(self, request: str) -> Dict[str, Any]:
        """Generate code based on user's natural language request."""
        print(f"[{self.name}] 💻 Generating code for: {request}")

        if not self.llm_client:
            return {"success": False, "error": "LLM not connected.", "agent": self.name}

        try:
            response = self.llm_client.chat.completions.create(
                model=settings.ollama_model,
                messages=[
                    {"role": "system", "content": self.CODE_SYSTEM_PROMPT},
                    {"role": "user", "content": request}
                ],
                temperature=0.3,
                max_tokens=2048
            )

            text = response.choices[0].message.content.strip()
            # Strip think tags from reasoning models
            if "<think>" in text:
                text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

            # Extract code blocks
            code_blocks = re.findall(r'```(\w*)\n(.*?)```', text, re.DOTALL)

            if code_blocks:
                language, code = code_blocks[0]
                # Try to auto-detect filename from request or code
                filename = self._extract_filename(request, code, language)

                if filename:
                    filepath = os.path.join(self.workspace, filename)
                    self._write_file(filepath, code)
                    return {
                        "success": True,
                        "summary": f"Generated and saved: {filepath}\n\n```{language}\n{code}\n```",
                        "output": code,
                        "filepath": filepath,
                        "language": language,
                        "agent": self.name
                    }
                else:
                    return {
                        "success": True,
                        "summary": f"Generated code:\n\n```{language}\n{code}\n```",
                        "output": code,
                        "language": language,
                        "agent": self.name
                    }
            else:
                return {
                    "success": True,
                    "summary": text,
                    "output": text,
                    "agent": self.name
                }

        except Exception as e:
            print(f"[{self.name}] ❌ Code generation failed: {e}")
            return {"success": False, "error": str(e), "agent": self.name}

    def _extract_filename(self, request: str, code: str, language: str) -> Optional[str]:
        """Try to extract a filename from the request or code."""
        # Check for explicit filename in request
        patterns = [
            r'(?:called?|named?|as|save\s+(?:as|to)?|file\s*(?:name)?)\s+["\']?(\S+\.\w+)["\']?',
            r'(\w+\.\w{1,5})\s',
        ]
        for pattern in patterns:
            match = re.search(pattern, request, re.IGNORECASE)
            if match:
                return match.group(1)

        # Check for filename comment in code
        for line in code.split('\n')[:3]:
            match = re.search(r'#\s*(?:file(?:name)?:?\s*)?(\S+\.\w+)', line, re.IGNORECASE)
            if match:
                return match.group(1)

        # Default extensions by language
        ext_map = {
            "python": ".py", "py": ".py",
            "javascript": ".js", "js": ".js",
            "typescript": ".ts", "ts": ".ts",
            "html": ".html", "css": ".css",
            "java": ".java", "cpp": ".cpp", "c": ".c",
            "rust": ".rs", "go": ".go",
            "bash": ".sh", "shell": ".sh", "sh": ".sh",
            "batch": ".bat", "bat": ".bat",
            "powershell": ".ps1", "ps1": ".ps1",
            "sql": ".sql", "json": ".json", "yaml": ".yml",
        }

        if language.lower() in ext_map:
            # Generate a sensible name from the request
            words = re.findall(r'\w+', request.lower())
            # Filter out common words
            skip = {"write", "create", "make", "generate", "a", "an", "the", "that",
                    "which", "code", "script", "program", "function", "for", "to",
                    "me", "please", "can", "you", "in", "python", "javascript"}
            meaningful = [w for w in words if w not in skip][:3]
            if meaningful:
                name = "_".join(meaningful) + ext_map[language.lower()]
                return name

        return None

    # ─────────────────────────────────────────────
    # FILE OPERATIONS
    # ─────────────────────────────────────────────

    def _write_file(self, filepath: str, content: str):
        """Write content to a file, creating dirs as needed."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"[{self.name}] 📝 Written: {filepath}")

    def read_code(self, request: str) -> Dict[str, Any]:
        """Read a code file. Extract filepath from request."""
        filepath = self._extract_path(request)
        if not filepath:
            return {"success": False, "error": "Could not determine which file to read. Please specify a file path.", "agent": self.name}

        try:
            path = Path(os.path.expanduser(filepath))
            if not path.exists():
                return {"success": False, "error": f"File not found: {path}", "agent": self.name}

            content = path.read_text(encoding="utf-8", errors="replace")

            # Detect language from extension
            ext_lang = {
                ".py": "python", ".js": "javascript", ".ts": "typescript",
                ".html": "html", ".css": "css", ".java": "java",
                ".cpp": "cpp", ".c": "c", ".rs": "rust", ".go": "go",
                ".sh": "bash", ".bat": "batch", ".ps1": "powershell",
                ".sql": "sql", ".json": "json", ".yaml": "yaml", ".yml": "yaml",
                ".md": "markdown", ".xml": "xml", ".toml": "toml",
            }
            lang = ext_lang.get(path.suffix.lower(), "")

            return {
                "success": True,
                "summary": f"📄 {path.name} ({len(content)} chars):\n\n```{lang}\n{content[:5000]}\n```",
                "output": content[:10000],
                "agent": self.name
            }
        except Exception as e:
            return {"success": False, "error": str(e), "agent": self.name}

    def _extract_path(self, request: str) -> Optional[str]:
        """Extract a file path from a request string."""
        # Look for quoted paths
        match = re.search(r'["\']([^"\']+\.\w+)["\']', request)
        if match:
            return match.group(1)

        # Look for paths with common extensions
        match = re.search(r'(\S+\.\w{1,5})', request)
        if match:
            candidate = match.group(1)
            # Filter out URLs
            if not candidate.startswith(('http://', 'https://')):
                return candidate

        # Look for absolute/relative paths
        match = re.search(r'([A-Za-z]:\\[^\s]+|/[^\s]+|~[^\s]+)', request)
        if match:
            return match.group(1)

        return None

    # ─────────────────────────────────────────────
    # CODE EXECUTION
    # ─────────────────────────────────────────────

    def run_code(self, request: str) -> Dict[str, Any]:
        """Run a script file."""
        filepath = self._extract_path(request)
        if not filepath:
            return {"success": False, "error": "Could not determine which file to run. Please specify a file path.", "agent": self.name}

        path = Path(os.path.expanduser(filepath))
        if not path.exists():
            return {"success": False, "error": f"File not found: {path}", "agent": self.name}

        ext = path.suffix.lower()
        runner_map = {
            ".py": f'python "{path}"',
            ".js": f'node "{path}"',
            ".ts": f'npx ts-node "{path}"',
            ".bat": f'"{path}"',
            ".ps1": f'powershell -ExecutionPolicy Bypass -File "{path}"',
            ".sh": f'bash "{path}"',
        }

        cmd = runner_map.get(ext)
        if not cmd:
            return {"success": False, "error": f"Don't know how to run {ext} files.", "agent": self.name}

        print(f"[{self.name}] ▶️ Running: {path.name}")
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                timeout=120, cwd=str(path.parent)
            )
            output = (result.stdout or "").strip()
            error = (result.stderr or "").strip()

            if result.returncode == 0:
                return {
                    "success": True,
                    "summary": f"✅ {path.name} ran successfully:\n\n```\n{output[:3000]}\n```",
                    "output": output[:5000],
                    "agent": self.name
                }
            else:
                return {
                    "success": False,
                    "error": f"Script failed (exit code {result.returncode}):\n{error[:2000]}",
                    "output": output[:2000],
                    "agent": self.name
                }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Script timed out (120s).", "agent": self.name}
        except Exception as e:
            return {"success": False, "error": str(e), "agent": self.name}

    # ─────────────────────────────────────────────
    # GIT OPERATIONS
    # ─────────────────────────────────────────────

    def git_operation(self, request: str) -> Dict[str, Any]:
        """Handle git operations based on natural language."""
        lower = request.lower()

        if "clone" in lower:
            # Extract URL
            url_match = re.search(r'(https?://\S+|git@\S+)', request)
            if url_match:
                url = url_match.group(1)
                dest = os.path.join(self.workspace, url.split("/")[-1].replace(".git", ""))
                return self._run_git(f'git clone "{url}" "{dest}"', cwd=self.workspace)
            return {"success": False, "error": "No repository URL found.", "agent": self.name}

        elif "commit" in lower:
            msg_match = re.search(r'(?:message|msg|")(.*?)(?:"|$)', request)
            msg = msg_match.group(1) if msg_match else "Update from KARNA"
            result = self._run_git("git add -A", cwd=self.workspace)
            if result["success"]:
                return self._run_git(f'git commit -m "{msg}"', cwd=self.workspace)
            return result

        elif "push" in lower:
            return self._run_git("git push", cwd=self.workspace)

        elif "pull" in lower:
            return self._run_git("git pull", cwd=self.workspace)

        elif "status" in lower:
            return self._run_git("git status", cwd=self.workspace)

        elif "log" in lower:
            return self._run_git("git log --oneline -20", cwd=self.workspace)

        elif "branch" in lower:
            return self._run_git("git branch -a", cwd=self.workspace)

        elif "diff" in lower:
            return self._run_git("git diff", cwd=self.workspace)

        else:
            return self._run_git(f"git {request}", cwd=self.workspace)

    def _run_git(self, cmd: str, cwd: str = None) -> Dict[str, Any]:
        """Run a git command."""
        try:
            print(f"[{self.name}] 🔧 Git: {cmd}")
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                timeout=120, cwd=cwd or self.workspace
            )
            output = (result.stdout or "").strip()
            error = (result.stderr or "").strip()
            combined = output or error

            return {
                "success": result.returncode == 0,
                "summary": f"```\n{combined[:3000]}\n```" if combined else "Done.",
                "output": combined[:5000],
                "agent": self.name
            }
        except Exception as e:
            return {"success": False, "error": str(e), "agent": self.name}

    # ─────────────────────────────────────────────
    # CODE ANALYSIS
    # ─────────────────────────────────────────────

    def analyze_code(self, request: str) -> Dict[str, Any]:
        """Read a file and analyze/explain it using LLM."""
        filepath = self._extract_path(request)
        if filepath:
            read_result = self.read_code(request)
            if not read_result["success"]:
                return read_result
            code = read_result["output"]
        else:
            code = request

        if not self.llm_client:
            return {"success": False, "error": "LLM not connected.", "agent": self.name}

        try:
            response = self.llm_client.chat.completions.create(
                model=settings.ollama_model,
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer. Analyze the code, explain what it does, identify bugs or issues, and suggest improvements. Be concise. Do NOT use <think> tags."},
                    {"role": "user", "content": f"Analyze this code:\n\n{code[:5000]}"}
                ],
                temperature=0.3,
                max_tokens=1024
            )

            text = response.choices[0].message.content.strip()
            if "<think>" in text:
                text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

            return {
                "success": True,
                "summary": text,
                "output": text,
                "agent": self.name
            }
        except Exception as e:
            return {"success": False, "error": str(e), "agent": self.name}

    # ─────────────────────────────────────────────
    # PROJECT SCAFFOLDING
    # ─────────────────────────────────────────────

    def create_project(self, request: str) -> Dict[str, Any]:
        """Create a new project structure."""
        lower = request.lower()

        # Extract project name
        name_match = re.search(r'(?:called?|named?|project)\s+["\']?(\w[\w-]*)["\']?', request, re.IGNORECASE)
        project_name = name_match.group(1) if name_match else "new_project"
        project_path = os.path.join(self.workspace, project_name)

        if os.path.exists(project_path):
            return {"success": False, "error": f"Directory already exists: {project_path}", "agent": self.name}

        # Detect project type
        if any(kw in lower for kw in ["web", "html", "website"]):
            return self._scaffold_web(project_name, project_path)
        elif any(kw in lower for kw in ["python", "py"]):
            return self._scaffold_python(project_name, project_path)
        elif any(kw in lower for kw in ["node", "javascript", "js", "express"]):
            return self._scaffold_node(project_name, project_path)
        else:
            return self._scaffold_python(project_name, project_path)

    def _scaffold_python(self, name: str, path: str) -> Dict[str, Any]:
        """Create a Python project."""
        os.makedirs(path, exist_ok=True)
        os.makedirs(os.path.join(path, name.replace("-", "_")), exist_ok=True)
        os.makedirs(os.path.join(path, "tests"), exist_ok=True)

        files = {
            "main.py": f'"""\n{name} - Main Entry Point\n"""\n\n\ndef main():\n    print("Hello from {name}!")\n\n\nif __name__ == "__main__":\n    main()\n',
            f"{name.replace('-', '_')}/__init__.py": f'"""{name}"""\n\n__version__ = "0.1.0"\n',
            "tests/__init__.py": "",
            "tests/test_main.py": f'"""Tests for {name}."""\n\nimport unittest\n\n\nclass TestMain(unittest.TestCase):\n    def test_placeholder(self):\n        self.assertTrue(True)\n\n\nif __name__ == "__main__":\n    unittest.main()\n',
            "requirements.txt": "# Add dependencies here\n",
            "README.md": f"# {name}\n\nA new Python project.\n\n## Setup\n```bash\npip install -r requirements.txt\npython main.py\n```\n",
            ".gitignore": "__pycache__/\n*.pyc\n.env\nvenv/\n*.egg-info/\ndist/\nbuild/\n",
        }

        for fname, content in files.items():
            fpath = os.path.join(path, fname)
            Path(fpath).parent.mkdir(parents=True, exist_ok=True)
            Path(fpath).write_text(content, encoding="utf-8")

        return {
            "success": True,
            "summary": f"🎉 Python project created: {path}\n\nFiles:\n" + "\n".join(f"  📄 {f}" for f in files.keys()),
            "agent": self.name
        }

    def _scaffold_web(self, name: str, path: str) -> Dict[str, Any]:
        """Create a basic web project."""
        os.makedirs(path, exist_ok=True)
        os.makedirs(os.path.join(path, "css"), exist_ok=True)
        os.makedirs(os.path.join(path, "js"), exist_ok=True)
        os.makedirs(os.path.join(path, "assets"), exist_ok=True)

        files = {
            "index.html": f'<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>{name}</title>\n    <link rel="stylesheet" href="css/style.css">\n</head>\n<body>\n    <h1>Welcome to {name}</h1>\n    <script src="js/main.js"></script>\n</body>\n</html>\n',
            "css/style.css": "* { margin: 0; padding: 0; box-sizing: border-box; }\n\nbody {\n    font-family: 'Inter', system-ui, sans-serif;\n    background: #0a0a0f;\n    color: #f0e6d3;\n    min-height: 100vh;\n    display: flex;\n    align-items: center;\n    justify-content: center;\n}\n\nh1 {\n    font-size: 3rem;\n    background: linear-gradient(135deg, #f59e0b, #f97316);\n    -webkit-background-clip: text;\n    -webkit-text-fill-color: transparent;\n}\n",
            "js/main.js": f'// {name} - Main JavaScript\nconsole.log("{name} loaded!");\n',
            "README.md": f"# {name}\n\nA web project.\n\n## Usage\nOpen `index.html` in your browser.\n",
        }

        for fname, content in files.items():
            fpath = os.path.join(path, fname)
            Path(fpath).parent.mkdir(parents=True, exist_ok=True)
            Path(fpath).write_text(content, encoding="utf-8")

        return {
            "success": True,
            "summary": f"🎉 Web project created: {path}\n\nFiles:\n" + "\n".join(f"  📄 {f}" for f in files.keys()),
            "agent": self.name
        }

    def _scaffold_node(self, name: str, path: str) -> Dict[str, Any]:
        """Create a Node.js project."""
        os.makedirs(path, exist_ok=True)
        os.makedirs(os.path.join(path, "src"), exist_ok=True)

        pkg = f'{{\n  "name": "{name}",\n  "version": "1.0.0",\n  "description": "A new Node.js project",\n  "main": "src/index.js",\n  "scripts": {{\n    "start": "node src/index.js",\n    "dev": "node --watch src/index.js"\n  }}\n}}\n'
        files = {
            "package.json": pkg,
            "src/index.js": f'// {name} - Main Entry Point\nconsole.log("Hello from {name}!");\n',
            "README.md": f"# {name}\n\nA Node.js project.\n\n## Setup\n```bash\nnpm install\nnpm start\n```\n",
            ".gitignore": "node_modules/\n.env\ndist/\n",
        }

        for fname, content in files.items():
            fpath = os.path.join(path, fname)
            Path(fpath).parent.mkdir(parents=True, exist_ok=True)
            Path(fpath).write_text(content, encoding="utf-8")

        return {
            "success": True,
            "summary": f"🎉 Node.js project created: {path}\n\nFiles:\n" + "\n".join(f"  📄 {f}" for f in files.keys()),
            "agent": self.name
        }

    def shutdown(self):
        """Shutdown KARNA gracefully."""
        self.status = "offline"
        print(f"[{self.name}] 💤 Coder Agent going offline.")
