#Important imports
import os
from pathlib import Path
import shutil
import markdown
from menus.results import menu_results
from menus.toolmenu import menu_tool
from SamaCTLI.toolDetection import get_active_tools

#colors for terminal
RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
WHITE = '\033[37m'
RESET = '\033[0m'
# here is the lobby of everything here is every function called.
#samabanner just a basic def for print the banner
def bannersama():
    print(f"""{GREEN}
███████╗ █████╗ ███╗   ███╗ █████╗     
██╔════╝██╔══██╗████╗ ████║██╔══██╗    
███████╗███████║██╔████╔██║███████║    
╚════██║██╔══██║██║╚██╔╝██║██╔══██║    
███████║██║  ██║██║ ╚═╝ ██║██║  ██║    
╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝ 
          SAMA IS A RECON AND PENTESTING DASHBOARD JUST TO HELP.. made by SamAs
"""
)
clear = lambda: os.system('reset')
clear_win = lambda: os.system('cls')
#Here is the basic menu for the options
while True:
    clear()
    get_active_tools()
    bannersama()
    print(f"{BLUE} [1]Tools\n", "[2]Source\n", "[3]Help\n", "[4]Results\n", f"[5]Exit\n{GREEN}", f"------------THANKS FOR USING SAMA PEOPLE------------\n{RESET}")
    chooseOption = input("Choose: ").strip()
    if chooseOption == "1" :
        clear()
        print("Opening Tools Menu wait a sec...")
        get_active_tools()
        menu_tool()
    if chooseOption == "2" :
        clear()
        print("Opening Sama Repo")
        input("Press enter to go back...")
    if chooseOption == "3" :
        #rute_help = Path('help.md')
        #if rute_help.exists():
            #help_content = rute_help.read_text
        #else: 
            #print("This Archive Doesn't exist or isn't here...")
        clear()
        clear_win()
        help_file = Path('menus/help.md').read_text()
        print("Showing Sama Help")
        #print(rute_help)
        print(help_file)
        input("Press enter to go back...")
    if chooseOption == "4" :
        clear()
        print("Opening Results Menu wait a sec...")
        menu_results()
    elif chooseOption == "5" :
        print("BYE from SAMA")
        break
    