"""
MAHABHARATA SYSTEM - Windows Install Script (Python version)
Sets up the environment, installs deps, and optionally registers startup.
"""

import subprocess
import sys
import os


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    req_path = os.path.join(project_root, "requirements.txt")

    print("=" * 50)
    print("  🕉️  MAHABHARATA SYSTEM - Installer")
    print("=" * 50)

    # Step 1: Install Python dependencies
    print("\n[1/3] Installing Python dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_path], check=True)

    # Step 2: Check for .env
    env_path = os.path.join(project_root, ".env")
    if not os.path.exists(env_path):
        example = os.path.join(project_root, ".env.example")
        if os.path.exists(example):
            import shutil
            shutil.copy(example, env_path)
            print("\n[2/3] Created .env from .env.example — please fill in your API keys!")
        else:
            print("\n[2/3] ⚠️ No .env file found. Create one from .env.example.")
    else:
        print("\n[2/3] .env already exists.")

    # Step 3: Register startup (optional)
    print("\n[3/3] Register for Windows auto-startup? (y/n)")
    choice = input("> ").strip().lower()
    if choice == "y":
        startup_script = os.path.join(project_root, "core", "krishna", "startup.py")
        subprocess.run([sys.executable, startup_script, "--register"])

    print("\n✅ Installation complete!")
    print(f"   Run: cd {project_root} && python main.py")


if __name__ == "__main__":
    main()
