"""
File Manager Integration
Organize downloads, search files, bulk rename, disk analysis, temp cleanup.
"""

import os
import shutil
import glob
from typing import Dict, Any, List
from pathlib import Path
from collections import defaultdict


class FileManager:
    """Advanced file management utilities."""

    # File type categories for organization
    CATEGORIES = {
        "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff"},
        "Videos": {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v"},
        "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"},
        "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"},
        "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"},
        "Code": {".py", ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c", ".go", ".rs", ".rb", ".php", ".sh", ".bat"},
        "Data": {".json", ".xml", ".yaml", ".yml", ".sql", ".db", ".sqlite"},
        "Executables": {".exe", ".msi", ".appx"},
        "Fonts": {".ttf", ".otf", ".woff", ".woff2"},
    }

    def organize_downloads(self, directory: str = None) -> Dict[str, Any]:
        """Sort files in a directory by type into folders."""
        target = directory or str(Path.home() / "Downloads")

        if not os.path.exists(target):
            return {"success": False, "error": f"Directory not found: {target}"}

        try:
            moved = defaultdict(list)
            for item in os.listdir(target):
                full_path = os.path.join(target, item)
                if not os.path.isfile(full_path):
                    continue

                ext = Path(item).suffix.lower()
                category = "Other"
                for cat, exts in self.CATEGORIES.items():
                    if ext in exts:
                        category = cat
                        break

                cat_dir = os.path.join(target, category)
                os.makedirs(cat_dir, exist_ok=True)
                dest = os.path.join(cat_dir, item)

                # Handle duplicates
                if os.path.exists(dest):
                    name, ext_part = os.path.splitext(item)
                    counter = 1
                    while os.path.exists(dest):
                        dest = os.path.join(cat_dir, f"{name}_{counter}{ext_part}")
                        counter += 1

                shutil.move(full_path, dest)
                moved[category].append(item)

            summary_lines = [f"📁 Organized {target}:"]
            total = 0
            for cat, files in sorted(moved.items()):
                summary_lines.append(f"  {cat}: {len(files)} files")
                total += len(files)
            summary_lines.append(f"\nTotal: {total} files organized.")

            return {
                "success": True,
                "summary": "\n".join(summary_lines),
                "moved": dict(moved)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def find_files(self, pattern: str, directory: str = None, max_results: int = 50) -> Dict[str, Any]:
        """Search for files matching a pattern."""
        base = directory or str(Path.home())

        try:
            matches = glob.glob(os.path.join(base, "**", pattern), recursive=True)
            matches = matches[:max_results]

            if matches:
                lines = []
                for m in matches:
                    size = os.path.getsize(m)
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024 * 1024:
                        size_str = f"{size/1024:.1f} KB"
                    else:
                        size_str = f"{size/(1024*1024):.1f} MB"
                    lines.append(f"  📄 {m} ({size_str})")

                return {
                    "success": True,
                    "summary": f"Found {len(matches)} files matching '{pattern}':\n" + "\n".join(lines[:30]),
                    "files": matches
                }
            return {"success": True, "summary": f"No files matching '{pattern}' found."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def bulk_rename(self, directory: str, pattern: str, replacement: str) -> Dict[str, Any]:
        """Rename files in a directory using find-replace on filenames."""
        try:
            renamed = []
            for item in os.listdir(directory):
                if pattern in item:
                    old_path = os.path.join(directory, item)
                    new_name = item.replace(pattern, replacement)
                    new_path = os.path.join(directory, new_name)
                    os.rename(old_path, new_path)
                    renamed.append(f"  {item} → {new_name}")

            if renamed:
                return {
                    "success": True,
                    "summary": f"Renamed {len(renamed)} files:\n" + "\n".join(renamed[:20])
                }
            return {"success": True, "summary": f"No files matching '{pattern}' found."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage analysis."""
        try:
            import psutil
            partitions = psutil.disk_partitions()
            lines = ["💾 Disk Usage:"]

            for p in partitions:
                try:
                    usage = psutil.disk_usage(p.mountpoint)
                    total_gb = usage.total / (1024**3)
                    used_gb = usage.used / (1024**3)
                    free_gb = usage.free / (1024**3)
                    lines.append(
                        f"  {p.device} ({p.mountpoint}): "
                        f"{used_gb:.1f}/{total_gb:.1f} GB used "
                        f"({usage.percent}%) — {free_gb:.1f} GB free"
                    )
                except:
                    pass

            return {"success": True, "summary": "\n".join(lines)}
        except ImportError:
            return {"success": True, "summary": "Install psutil for detailed disk analysis."}

    def cleanup_temp(self) -> Dict[str, Any]:
        """Clean temporary files."""
        import tempfile
        temp_dir = tempfile.gettempdir()

        try:
            cleaned = 0
            freed = 0
            errors = 0

            for item in os.listdir(temp_dir):
                path = os.path.join(temp_dir, item)
                try:
                    if os.path.isfile(path):
                        size = os.path.getsize(path)
                        os.unlink(path)
                        cleaned += 1
                        freed += size
                    elif os.path.isdir(path):
                        size = sum(
                            os.path.getsize(os.path.join(dp, f))
                            for dp, _, fns in os.walk(path)
                            for f in fns
                        )
                        shutil.rmtree(path, ignore_errors=True)
                        cleaned += 1
                        freed += size
                except:
                    errors += 1

            freed_mb = freed / (1024 * 1024)
            return {
                "success": True,
                "summary": f"🧹 Cleaned {cleaned} items, freed {freed_mb:.1f} MB. ({errors} items skipped)"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_folder_size(self, directory: str) -> Dict[str, Any]:
        """Get the total size of a directory."""
        try:
            total = 0
            for dp, _, fns in os.walk(directory):
                for f in fns:
                    try:
                        total += os.path.getsize(os.path.join(dp, f))
                    except:
                        pass

            if total < 1024:
                size_str = f"{total} B"
            elif total < 1024 * 1024:
                size_str = f"{total/1024:.1f} KB"
            elif total < 1024**3:
                size_str = f"{total/(1024*1024):.1f} MB"
            else:
                size_str = f"{total/(1024**3):.2f} GB"

            return {"success": True, "summary": f"📁 {directory}: {size_str}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
