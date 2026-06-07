#Important imports
import os
from pathlib import Path
import shutil
import markdown
import json
from .results import menu_results
from SamaCTLI.toolDetection import get_active_tools
from SamaCTLI.resultRedirect import run_tool_with_redirect

#colors for terminal
RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
WHITE = '\033[37m'
RESET = '\033[0m'

def banner_tools():
    print(f"""{GREEN}
████████╗ ██████╗  ██████╗ ██╗     ███████╗
╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
   ██║   ██║   ██║██║   ██║██║     ███████╗
   ██║   ██║   ██║██║   ██║██║     ╚════██║
   ██║   ╚██████╔╝╚██████╔╝███████╗███████║
   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝ 
          This Is the Tools menu where you may choose your tool for usage or resutls of each...
"""
)

def banner_list():
    print(f"""{GREEN}
██╗     ██╗███████╗████████╗
██║     ██║██╔════╝╚══██╔══╝
██║     ██║███████╗   ██║   
██║     ██║╚════██║   ██║   
███████╗██║███████║   ██║   
╚══════╝╚═╝╚══════╝   ╚═╝                        
          This are the list of tools menu where you may choose your tool for usage...
"""
)
    
clear = lambda: os.system('reset')

def menu_tool():
    clear()
    while True:
        clear()
        banner_tools()
        print(f"{BLUE} [1]Tools-list\n", "[2]Results\n", f"[3]Add Tool\n", f"[4]Back\n", f"{GREEN}------------THANKS FOR USING SAMA PEOPLE------------\n{RESET}")
        chooseOption = input("Choose: ").strip()
        if chooseOption == "1":
            smart_tool_selector()
        elif chooseOption == "2":
            clear()
            print("Opening Tool Results")
            menu_results()
        elif chooseOption == "3":
            clear()
            print(f"{RED}======ADD NEW TOOL MODULE======{RESET}\n")

            ask_name_tool = input("Enter the name of your tool: ").strip()
            ask_description_tool = input("Enter a short description of the tool: ").strip()
            ask_cmd_tool = input("Enter the System Command line (e.g. nmap): ").strip()
            clean_name = ask_name_tool.lower().replace(" ", "_")

            if shutil.which(ask_cmd_tool):
                print(f"{GREEN}Command Verified successfully in system!{RESET}")
                
                new_data = {
                    clean_name: {
                        "desc": ask_description_tool,
                        "cmd": ask_cmd_tool,
                        "conf_path": ""
                    }
                }
                module_dir = Path('tools/modules')
                module_dir.mkdir(parents=True, exist_ok=True)
                module_file = module_dir / f"{clean_name}.json"
                module_file.write_text(json.dumps(new_data, indent=4))
                print(f"{GREEN} Module written to: {module_file}{RESET}")
                input("\nPress Enter to return...")
            else:
                print(f"{RED}[-] Error: Command '{ask_cmd_tool}' is not installed on Linux.{RESET}")
                input("\nPress Enter to return...")
        elif chooseOption == "4":
            clear()
            break
def smart_tool_selector():
    while True:
        clear()
        banner_list()
        tool_catalog = {}
        detected_tools = []
        list_tool = Path('tools/modules')
        if not list_tool.exists():
            print("[-] No modules folder found.")
            print("[0] back")
            input("\nPress Enter to return...")
            return
        for json_file in list_tool.glob('*.json'):
            try:
                help_content = json_file.read_text()
                mini_data = json.loads(help_content)
                tool_catalog.update(mini_data)
            except Exception:
                continue
        for index, (name, info) in enumerate(tool_catalog.items(), start=1):
            print(f"{RED}[{index}] {BLUE}{name.upper()}{RESET} - {RED}{info['desc']}{RESET}\n")
            detected_tools.append(name)       
        print("[0] back\n")
        choose_from_list = input("Choose the tool you may use: ").strip()
        if choose_from_list == "0":
            break
        if choose_from_list.isdigit():
            idx = int(choose_from_list) - 1
            if 0 <= idx < len(detected_tools):
                selected_tool_name = detected_tools[idx]
                base_command = tool_catalog[selected_tool_name]['cmd']
                target = input(f"\nEnter targets/arguments for {selected_tool_name.upper()}: ").strip()
                full_command = f"{base_command} {target}" if target else base_command
                clear()
                run_tool_with_redirect(selected_tool_name, full_command)
                input("\nExecution finished. Press Enter to return to tools list...")