import json
import shutil
import threading
from pathlib import Path
from typing import Any

from SamaCTLI.ui import print_error

MODULES_DIR = Path("tools/modules")
_cache: dict[str, dict[str, Any]] | None = None
_cache_lock = threading.Lock()


def get_active_tools(force_refresh: bool = False) -> dict[str, dict[str, Any]]:
    global _cache
    with _cache_lock:
        if _cache is not None and not force_refresh:
            return _cache

        detected: dict[str, dict[str, Any]] = {}

        if not MODULES_DIR.exists():
            _cache = detected
            return detected

        for json_file in MODULES_DIR.glob("*.json"):
            try:
                content = json_file.read_text(encoding="utf-8")
                module_data = json.loads(content)
                for tool_name, info in module_data.items():
                    cmd = info.get("cmd")
                    if not isinstance(cmd, str):
                        continue
                    if shutil.which(cmd):
                        detected[tool_name] = info
                        _ensure_output_dir(tool_name)
            except (json.JSONDecodeError, OSError) as e:
                print_error(f"Error parsing {json_file.name}: {e}")
                continue

        _cache = detected
        return detected


def _ensure_output_dir(tool_name: str) -> None:
    output_dir = Path("tool_results") / tool_name
    output_dir.mkdir(parents=True, exist_ok=True)


def invalidate_cache() -> None:
    global _cache
    with _cache_lock:
        _cache = None
