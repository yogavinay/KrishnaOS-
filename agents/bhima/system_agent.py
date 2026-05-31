"""
BHIMA - System Operator Agent (The Executor)
Full OS access. Executes commands, opens/closes apps, manages files,
monitors system health, takes screenshots, installs software.
No restrictions — user has granted full access.
"""

import subprocess
import platform
import os
import shutil
import glob
from typing import Dict, Any, List, Optional
from pathlib import Path


class BhimaAgent:
    """System Operator Agent — full OS access granted by user."""

    def __init__(self):
        self.name = "BHIMA"
        self.status = "initializing"
        self.os_type = platform.system()
        print(f"[{self.name}] ⚡ Initializing System Operator Agent on {self.os_type}...")

    def initialize(self):
        self.status = "active"
        print(f"[{self.name}] ✅ System Agent ready. Full OS access enabled.")

    # ─────────────────────────────────────────────
    # COMMAND EXECUTION
    # ─────────────────────────────────────────────

    def execute_command(self, command: str, timeout: int = 300, cwd: str = None) -> Dict[str, Any]:
        """Execute any shell command with no restrictions."""
        try:
            work_dir = cwd or os.path.expanduser("~")
            print(f"[{self.name}] ⚡ Executing: {command}")

            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                timeout=timeout, cwd=work_dir
            )
            output = (result.stdout or "").strip()
            error = (result.stderr or "").strip()

            return {
                "success": result.returncode == 0,
                "output": output[:5000] if output else "Command completed.",
                "error": error[:2000] if error and result.returncode != 0 else None,
                "return_code": result.returncode,
                "command": command,
                "agent": self.name
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Command timed out ({timeout}s).", "agent": self.name}
        except Exception as e:
            return {"success": False, "error": str(e), "agent": self.name}

    def execute_powershell(self, script: str, timeout: int = 300) -> Dict[str, Any]:
        """Execute a PowerShell command or script."""
        cmd = f'powershell -NoProfile -ExecutionPolicy Bypass -Command "{script}"'
        return self.execute_command(cmd, timeout=timeout)

    # ─────────────────────────────────────────────
    # APPLICATION MANAGEMENT
    # ─────────────────────────────────────────────

    def open_application(self, app_name: str) -> Dict[str, Any]:
        """Open an application by name. Extensive app mapping."""
        app_map = {
            # Browsers
            "chrome": "start chrome", "google chrome": "start chrome",
            "firefox": "start firefox", "edge": "start msedge",
            "browser": "start chrome", "brave": "start brave",
            # Editors & IDEs
            "notepad": "notepad", "code": "code", "vscode": "code",
            "visual studio code": "code", "vs code": "code",
            "sublime": "subl", "notepad++": "start notepad++",
            # System Tools
            "calculator": "calc", "calc": "calc",
            "terminal": "start wt", "cmd": "start cmd",
            "powershell": "start powershell", "task manager": "taskmgr",
            "control panel": "control", "settings": "start ms-settings:",
            "registry": "regedit", "device manager": "devmgmt.msc",
            # File Management
            "explorer": "explorer", "file explorer": "explorer",
            "downloads": f'explorer "{Path.home() / "Downloads"}"',
            "documents": f'explorer "{Path.home() / "Documents"}"',
            "desktop": f'explorer "{Path.home() / "Desktop"}"',
            # Media
            "spotify": "start spotify:", "vlc": "start vlc",
            "photos": "start ms-photos:", "camera": "start microsoft.windows.camera:",
            # Communication
            "teams": "start msteams:", "discord": "start discord",
            "slack": "start slack", "telegram": "start telegram",
            "whatsapp": "start whatsapp:",
            # Microsoft Office
            "word": "start winword", "excel": "start excel",
            "powerpoint": "start powerpnt", "outlook": "start outlook",
            # Others
            "paint": "mspaint", "snipping tool": "start snippingtool",
            "screen snip": "start ms-screenclip:",
            "clock": "start ms-clock:", "store": "start ms-windows-store:",
            "maps": "start bingmaps:", "weather": "start bingweather:",
        }

        clean_name = app_name.lower().strip()
        cmd = app_map.get(clean_name, f"start {app_name}")

        result = self.execute_command(cmd)
        if result["success"] or result.get("return_code") == 0:
            result["summary"] = f"Opened {app_name}."
            result["success"] = True
        return result

    def kill_process(self, process_name: str) -> Dict[str, Any]:
        """Kill a running process by name."""
        clean = process_name.strip().lower()
        # Add .exe if not present
        if not clean.endswith(".exe"):
            clean += ".exe"

        result = self.execute_command(f'taskkill /IM "{clean}" /F')
        if result["success"]:
            result["summary"] = f"Killed process: {process_name}"
        return result

    def install_app(self, app_name: str) -> Dict[str, Any]:
        """Install an app using winget."""
        print(f"[{self.name}] 📦 Installing: {app_name}")
        return self.execute_command(f'winget install --accept-package-agreements --accept-source-agreements "{app_name}"', timeout=600)

    # ─────────────────────────────────────────────
    # SYSTEM INFORMATION
    # ─────────────────────────────────────────────

    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        try:
            import psutil

            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            # Memory
            mem = psutil.virtual_memory()
            mem_used_gb = round(mem.used / (1024**3), 1)
            mem_total_gb = round(mem.total / (1024**3), 1)

            # Disk
            disk = psutil.disk_usage('/')
            disk_used_gb = round(disk.used / (1024**3), 1)
            disk_total_gb = round(disk.total / (1024**3), 1)

            # Battery
            battery_info = "N/A"
            try:
                battery = psutil.sensors_battery()
                if battery:
                    battery_info = f"{battery.percent}% {'(Charging)' if battery.power_plugged else '(Battery)'}"
            except:
                pass

            # Network
            net = psutil.net_if_addrs()
            ip_addresses = []
            for iface, addrs in net.items():
                for addr in addrs:
                    if addr.family.name == 'AF_INET' and not addr.address.startswith('127.'):
                        ip_addresses.append(f"{iface}: {addr.address}")

            info = {
                "os": f"{platform.system()} {platform.release()}",
                "version": platform.version(),
                "machine": platform.machine(),
                "hostname": platform.node(),
                "cpu": f"{cpu_percent}% ({cpu_count} cores)",
                "ram": f"{mem_used_gb}/{mem_total_gb} GB ({mem.percent}%)",
                "disk": f"{disk_used_gb}/{disk_total_gb} GB ({disk.percent}%)",
                "battery": battery_info,
                "ip": ", ".join(ip_addresses[:3]) if ip_addresses else "N/A",
                "python": platform.python_version(),
            }

            summary = (
                f"💻 System: {info['os']} | {info['hostname']}\n"
                f"🧠 CPU: {info['cpu']}\n"
                f"📊 RAM: {info['ram']}\n"
                f"💾 Disk: {info['disk']}\n"
                f"🔋 Battery: {info['battery']}\n"
                f"🌐 IP: {info['ip']}"
            )

            return {
                "success": True,
                "info": info,
                "summary": summary,
                "agent": self.name
            }
        except ImportError:
            # Fallback without psutil
            return {
                "success": True,
                "summary": f"OS: {platform.system()} {platform.release()} | Host: {platform.node()} | Machine: {platform.machine()}",
                "info": {
                    "os": platform.system(), "version": platform.version(),
                    "machine": platform.machine(), "hostname": platform.node(),
                },
                "agent": self.name
            }

    def get_running_processes(self, top_n: int = 15) -> Dict[str, Any]:
        """Get top running processes by memory usage."""
        try:
            import psutil
            procs = []
            for p in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
                try:
                    info = p.info
                    procs.append(info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            procs.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
            top = procs[:top_n]

            lines = [f"{'PID':<8} {'Name':<30} {'RAM %':<8} {'CPU %':<8}"]
            lines.append("-" * 56)
            for p in top:
                lines.append(f"{p['pid']:<8} {(p['name'] or 'N/A')[:29]:<30} {p.get('memory_percent', 0):<8.1f} {p.get('cpu_percent', 0):<8.1f}")

            return {
                "success": True,
                "output": "\n".join(lines),
                "summary": "\n".join(lines),
                "agent": self.name
            }
        except ImportError:
            return self.execute_command("tasklist /FO TABLE /NH")

    # ─────────────────────────────────────────────
    # FILE OPERATIONS
    # ─────────────────────────────────────────────

    def list_directory(self, path: str = "~") -> Dict[str, Any]:
        """List contents of a directory."""
        try:
            target = os.path.expanduser(path)
            if not os.path.exists(target):
                return {"success": False, "error": f"Path not found: {target}", "agent": self.name}

            entries = []
            for item in sorted(os.listdir(target)):
                full = os.path.join(target, item)
                if os.path.isdir(full):
                    entries.append(f"📁 {item}/")
                else:
                    size = os.path.getsize(full)
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024 * 1024:
                        size_str = f"{size/1024:.1f} KB"
                    else:
                        size_str = f"{size/(1024*1024):.1f} MB"
                    entries.append(f"📄 {item} ({size_str})")

            return {
                "success": True,
                "output": "\n".join(entries),
                "summary": f"Contents of {target}:\n" + "\n".join(entries[:30]),
                "agent": self.name
            }
        except Exception as e:
            return {"success": False, "error": str(e), "agent": self.name}

    def create_file(self, filepath: str, content: str = "") -> Dict[str, Any]:
        """Create a file with optional content."""
        try:
            path = Path(os.path.expanduser(filepath))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return {"success": True, "summary": f"Created file: {path}", "agent": self.name}
        except Exception as e:
            return {"success": False, "error": str(e), "agent": self.name}

    def read_file(self, filepath: str) -> Dict[str, Any]:
        """Read a file's contents."""
        try:
            path = Path(os.path.expanduser(filepath))
            if not path.exists():
                return {"success": False, "error": f"File not found: {path}", "agent": self.name}
            content = path.read_text(encoding="utf-8", errors="replace")
            return {
                "success": True,
                "output": content[:10000],
                "summary": f"File: {path} ({len(content)} chars)\n\n{content[:3000]}",
                "agent": self.name
            }
        except Exception as e:
            return {"success": False, "error": str(e), "agent": self.name}

    def delete_file(self, filepath: str) -> Dict[str, Any]:
        """Delete a file or directory."""
        try:
            path = Path(os.path.expanduser(filepath))
            if path.is_dir():
                shutil.rmtree(str(path))
                return {"success": True, "summary": f"Deleted directory: {path}", "agent": self.name}
            elif path.is_file():
                path.unlink()
                return {"success": True, "summary": f"Deleted file: {path}", "agent": self.name}
            else:
                return {"success": False, "error": f"Not found: {path}", "agent": self.name}
        except Exception as e:
            return {"success": False, "error": str(e), "agent": self.name}

    def move_file(self, source: str, destination: str) -> Dict[str, Any]:
        """Move or rename a file/directory."""
        try:
            src = Path(os.path.expanduser(source))
            dst = Path(os.path.expanduser(destination))
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            return {"success": True, "summary": f"Moved: {src} → {dst}", "agent": self.name}
        except Exception as e:
            return {"success": False, "error": str(e), "agent": self.name}

    def copy_file(self, source: str, destination: str) -> Dict[str, Any]:
        """Copy a file or directory."""
        try:
            src = Path(os.path.expanduser(source))
            dst = Path(os.path.expanduser(destination))
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(str(src), str(dst))
            else:
                shutil.copy2(str(src), str(dst))
            return {"success": True, "summary": f"Copied: {src} → {dst}", "agent": self.name}
        except Exception as e:
            return {"success": False, "error": str(e), "agent": self.name}

    def find_files(self, pattern: str, directory: str = "~") -> Dict[str, Any]:
        """Find files matching a glob pattern."""
        try:
            base = os.path.expanduser(directory)
            matches = glob.glob(os.path.join(base, "**", pattern), recursive=True)
            matches = matches[:50]  # Limit results
            if matches:
                lines = [os.path.relpath(m, base) for m in matches]
                return {
                    "success": True,
                    "output": "\n".join(lines),
                    "summary": f"Found {len(matches)} files matching '{pattern}':\n" + "\n".join(lines[:20]),
                    "agent": self.name
                }
            return {"success": True, "summary": f"No files found matching '{pattern}'.", "agent": self.name}
        except Exception as e:
            return {"success": False, "error": str(e), "agent": self.name}

    # ─────────────────────────────────────────────
    # SCREENSHOTS & CLIPBOARD
    # ─────────────────────────────────────────────

    def take_screenshot(self, filename: str = None) -> Dict[str, Any]:
        """Take a screenshot and save it."""
        try:
            import pyautogui
            if not filename:
                import datetime
                ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = str(Path.home() / "Desktop" / f"screenshot_{ts}.png")

            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            return {
                "success": True,
                "summary": f"Screenshot saved: {filename}",
                "output": filename,
                "agent": self.name
            }
        except Exception as e:
            return {"success": False, "error": f"Screenshot failed: {e}", "agent": self.name}

    def get_clipboard(self) -> Dict[str, Any]:
        """Get clipboard contents."""
        try:
            result = self.execute_powershell("Get-Clipboard")
            if result["success"]:
                result["summary"] = f"Clipboard: {result.get('output', '')[:500]}"
            return result
        except Exception as e:
            return {"success": False, "error": str(e), "agent": self.name}

    def set_clipboard(self, text: str) -> Dict[str, Any]:
        """Set clipboard contents."""
        try:
            escaped = text.replace("'", "''")
            result = self.execute_powershell(f"Set-Clipboard -Value '{escaped}'")
            result["summary"] = "Text copied to clipboard."
            return result
        except Exception as e:
            return {"success": False, "error": str(e), "agent": self.name}

    # ─────────────────────────────────────────────
    # NETWORK
    # ─────────────────────────────────────────────

    def get_wifi_info(self) -> Dict[str, Any]:
        """Get current WiFi connection info."""
        return self.execute_command("netsh wlan show interfaces")

    def get_ip_info(self) -> Dict[str, Any]:
        """Get IP address info."""
        return self.execute_command("ipconfig")

    def ping(self, host: str = "google.com") -> Dict[str, Any]:
        """Ping a host."""
        return self.execute_command(f"ping -n 4 {host}")

    # ─────────────────────────────────────────────
    # POWER & SYSTEM CONTROL
    # ─────────────────────────────────────────────

    def shutdown_system(self, delay: int = 30) -> Dict[str, Any]:
        """Shutdown the computer."""
        return self.execute_command(f"shutdown /s /t {delay}")

    def restart_system(self, delay: int = 30) -> Dict[str, Any]:
        """Restart the computer."""
        return self.execute_command(f"shutdown /r /t {delay}")

    def lock_screen(self) -> Dict[str, Any]:
        """Lock the screen."""
        return self.execute_command("rundll32.exe user32.dll,LockWorkStation")

    def sleep_system(self) -> Dict[str, Any]:
        """Put the system to sleep."""
        return self.execute_powershell("Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState('Suspend', $false, $false)")

    # ─────────────────────────────────────────────
    # VOLUME CONTROL
    # ─────────────────────────────────────────────

    def set_volume(self, level: int) -> Dict[str, Any]:
        """Set system volume (0-100)."""
        level = max(0, min(100, level))
        script = f"""
$wshell = New-Object -ComObject wscript.shell
# Mute first, then set
(1..50) | ForEach-Object {{ $wshell.SendKeys([char]174) }}
$steps = [math]::Round({level} / 2)
(1..$steps) | ForEach-Object {{ $wshell.SendKeys([char]175) }}
"""
        return self.execute_powershell(script)

    def mute(self) -> Dict[str, Any]:
        """Toggle mute."""
        return self.execute_powershell("$wshell = New-Object -ComObject wscript.shell; $wshell.SendKeys([char]173)")

    def shutdown(self):
        self.status = "offline"
        print(f"[{self.name}] 💤 System Agent offline.")
