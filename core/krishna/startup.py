"""
KRISHNA Startup Script
Auto-launches on Windows login. Speaks time-aware greeting.
"""

import sys
import os
import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import settings


def get_greeting() -> str:
    """Generate time-aware greeting."""
    hour = datetime.datetime.now().hour
    name = settings.user_name

    if 6 <= hour < 12:
        return f"Good morning, {name}."
    elif 12 <= hour < 17:
        return f"Welcome back, {name}. Good afternoon."
    else:
        return f"Good evening, {name}. Ready when you are."


def run_startup():
    """Full startup sequence."""
    from core.krishna.orchestrator import KrishnaOrchestrator

    krishna = KrishnaOrchestrator()
    krishna.initialize()

    # Startup greeting
    greeting = krishna.startup_greeting()
    print(f"\n🕉️  {greeting}\n")

    # Enter voice/text loop
    krishna.voice_loop()

    # Shutdown
    krishna.shutdown()


def register_windows_startup():
    """Register this script to run on Windows login via startup folder."""
    import shutil

    startup_folder = os.path.join(
        os.environ.get("APPDATA", ""),
        r"Microsoft\Windows\Start Menu\Programs\Startup"
    )

    script_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_path)))
    python_exe = sys.executable

    bat_content = f'''@echo off
cd /d "{project_root}"
"{python_exe}" "{script_path}"
'''

    bat_path = os.path.join(startup_folder, "MahabharataSystem.bat")
    try:
        with open(bat_path, "w") as f:
            f.write(bat_content)
        print(f"[STARTUP] ✅ Registered in Windows Startup: {bat_path}")
    except Exception as e:
        print(f"[STARTUP] ❌ Failed to register: {e}")


if __name__ == "__main__":
    if "--register" in sys.argv:
        register_windows_startup()
    else:
        run_startup()
