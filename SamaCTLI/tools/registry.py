import json
import re
import shutil
from pathlib import Path

from SamaCTLI.tools.detection import invalidate_cache
from SamaCTLI.ui import print_error, print_info, print_success, prompt_input

MODULES_DIR = Path("tools/modules")
SAFE_NAME_PATTERN = re.compile(r"^[a-z0-9_-]+$")


def sanitize_tool_name(name: str) -> str:
    return name.lower().replace(" ", "_").strip()


def validate_tool_name(name: str) -> bool:
    return bool(SAFE_NAME_PATTERN.match(name))


def validate_command(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def add_tool(name: str, description: str, cmd: str) -> bool:
    clean_name = sanitize_tool_name(name)

    if not validate_tool_name(clean_name):
        print_error("Invalid tool name. Use only lowercase letters, numbers, hyphens, underscores.")
        return False

    if not validate_command(cmd):
        print_error(f"Command '{cmd}' not found in PATH")
        return False

    MODULES_DIR.mkdir(parents=True, exist_ok=True)
    module_file = MODULES_DIR / f"{clean_name}.json"

    if module_file.exists():
        print_error(f"Tool '{clean_name}' already exists")
        return False

    data = {
        clean_name: {
            "desc": description,
            "cmd": cmd,
            "conf_path": "",
        }
    }

    try:
        module_file.write_text(json.dumps(data, indent=4), encoding="utf-8")
        invalidate_cache()
        print_success(f"Tool '{clean_name}' added to {module_file}")
        return True
    except OSError as e:
        print_error(f"Failed to write tool: {e}")
        return False


def interactive_add_tool() -> None:
    print_info("====== ADD NEW TOOL MODULE ======")

    name = prompt_input("Tool name").strip()
    if not name:
        print_error("Name required")
        return

    description = prompt_input("Description").strip()
    if not description:
        print_error("Description required")
        return

    cmd = prompt_input("System command (e.g., nmap)").strip()
    if not cmd:
        print_error("Command required")
        return

    add_tool(name, description, cmd)
