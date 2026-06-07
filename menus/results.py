#Important imports
import os
from pathlib import Path
import shutil
import markdown


#colors for terminal
RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
WHITE = '\033[37m'
RESET = '\033[0m'

def banner_result():
    print(f"""{GREEN}
██████╗ ███████╗███████╗██╗   ██╗██╗  ████████╗███████╗
██╔══██╗██╔════╝██╔════╝██║   ██║██║  ╚══██╔══╝██╔════╝
██████╔╝█████╗  ███████╗██║   ██║██║     ██║   ███████╗
██╔══██╗██╔══╝  ╚════██║██║   ██║██║     ██║   ╚════██║
██║  ██║███████╗███████║╚██████╔╝███████╗██║   ███████║
╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚══════╝╚═╝   ╚══════╝ 
          This Is the Results Menu here are the results right?...
"""
)
clear = lambda: os.system('reset')

def menu_results() :
    clear()
    while True:
        banner_result()
        detection()
        print(f"{GREEN}[0]Back")
        print(f"{BLUE} {GREEN}", f"------------THANKS FOR USING SAMA PEOPLE------------\n{RESET}")
        chooseOption = input("Choose: ").strip()

        if chooseOption == "0" :
            clear()
            break
        elif chooseOption == "exit" :
            print("BYE from results")
            break
        clear()

def detection():
    # 1. Creamos un diccionario vacío (el baúl) en la RAM
    tool_catalog = []
    list_tool = Path('tool_results')
    # Si la carpeta no existe todavía, evitamos que falle el script
    if not list_tool.exists():
        print("[-] No modules folder found.")
        print("[0] back")
        return
    # 2. Activamos el radar .glob() con el patrón de búsqueda
    for result_dir_detection in list_tool.glob('*'):
        if result_dir_detection.is_dir():
            tool_catalog.append(result_dir_detection.name)
    if not tool_catalog:
        print(f"{RED}[*] any result folders here sorry...{RESET}")
    else:
        for index, list_tool in enumerate(tool_catalog, start=1):
            print(f"{RED}[{index}] {BLUE}{list_tool.upper()}{RESET} - View text outputs")

        # 6. Tu bucle original de pintado (este queda intacto, solo lee de tool_catalog)
        #for detection, (name, info) in enumerate(tool_catalog.items(), start=1):
         #   print(f"{RED}[{detection}] {BLUE}{name.upper()}{RESET} - {RED}{info['desc']}{RESET}\n")
           # list_tool.append(name)       
        #print("[0] back")