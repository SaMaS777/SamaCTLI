from pathlib import Path
import os

#colors for terminal
RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
WHITE = '\033[37m'
RESET = '\033[0m'

def run_tool_with_redirect(tool_name, base_command):
    output_file = Path(f"tool_results/{tool_name}/output_{tool_name}.txt")
    final_command = f"{base_command} > {output_file}"
    print(f"{BLUE}[*] Running command: {base_command}{RESET}")
    print(f"{BLUE}[*] Saving results directly to: {output_file}{RESET}")
    os.system(final_command)