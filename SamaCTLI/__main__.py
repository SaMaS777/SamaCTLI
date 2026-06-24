import asyncio
import sys
from pathlib import Path

from SamaCTLI.menus import run_apikeys_menu, run_models_menu, run_results_menu, run_tools_menu
from SamaCTLI.tools import get_active_tools
from SamaCTLI.ui import (
    clear,
    print_banner,
    print_error,
    print_info,
    print_menu,
    print_success,
    print_warning,
    prompt_input,
    wait_for_enter,
)


def print_main_banner() -> None:
    print_banner(
        "SAMA CTLI",
        "Recon & Pentesting Dashboard"
    )


async def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("SamaCTLI - Recon & Pentesting Dashboard")
        print("Usage: python -m SamaCTLI")
        return

    while True:
        clear()
        get_active_tools()
        print_main_banner()

        print_menu(
            [
                ("1", "Tools"),
                ("2", "Source"),
                ("3", "Help"),
                ("4", "Results"),
                ("A", "API Keys (New Multi-Provider AI)"),
                ("M", "AI Models & Chat"),
            ],
            "Exit",
        )

        choice = prompt_input("Choose").strip().upper()

        if choice == "0":
            clear()
            print_success("Goodbye!")
            break
        elif choice == "1":
            await run_tools_menu()
        elif choice == "2":
            print_info("Opening Sama Repo...")
            wait_for_enter()
        elif choice == "3":
            clear()
            help_file = Path("menus/help.md")
            if help_file.exists():
                print(help_file.read_text(encoding="utf-8"))
            else:
                print_error("Help file not found")
            wait_for_enter()
        elif choice == "4":
            await run_results_menu()
        elif choice == "A":
            await run_apikeys_menu()
        elif choice == "M":
            await run_models_menu()
        else:
            print_error("Invalid option")
            wait_for_enter()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        clear()
        print_success("\nGoodbye!")
