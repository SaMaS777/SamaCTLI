import json
import shutil
from pathlib import Path
def get_active_tools():
    detected_tools = {}
    modules_path = Path('tools/modules')
    if not modules_path.exists():
        return detected_tools
    for json_file in modules_path.glob('*.json'):
        try:
            content = json_file.read_text()
            module_data = json.loads(content)
            for tool_name, info in module_data.items():
                cmd = info.get("cmd")
                if cmd and shutil.which(cmd):
                    detected_tools[tool_name] = info
                    output_dir = Path(f'tool_results/{tool_name}')
                    if not output_dir.exists():
                        output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"[-] Error parsing {json_file.name}: {e}")
            continue
    return detected_tools