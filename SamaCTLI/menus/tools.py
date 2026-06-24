from pathlib import Path

from SamaCTLI.menus.results import run_results_menu
from SamaCTLI.tools import get_active_tools, interactive_add_tool, run_tool_async
from SamaCTLI.ui import (
    clear,
    print_banner,
    print_error,
    print_info,
    print_menu,
    prompt_input,
    wait_for_enter,
)


def print_tools_banner() -> None:
    print_banner("TOOLS MENU", "Select an option")


def print_tools_list_banner() -> None:
    print_banner("AVAILABLE TOOLS", "Select a tool to run")


async def select_existing_output_file() -> str | None:
    """Let user select an existing output file to use as input."""
    results_dir = Path("tool_results")
    if not results_dir.exists():
        return None

    all_files = []
    for tool_dir in results_dir.iterdir():
        if tool_dir.is_dir():
            for f in tool_dir.glob("*.txt"):
                rel_path = f.relative_to(results_dir)
                all_files.append((str(rel_path), f))

    if not all_files:
        print_info("No previous output files found")
        return None

    print_info("Select a previous output file to use as input:")
    for i, (rel_path, _) in enumerate(all_files, 1):
        size = all_files[i-1][1].stat().st_size
        print(f"  [{i}] {rel_path} ({size} bytes)")
    print("  [0] Skip - enter targets manually")

    choice = prompt_input("Choose file")
    if choice == "0":
        return None

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(all_files):
            return str(all_files[idx][1])
    except ValueError:
        pass

    print_error("Invalid selection")
    return None


async def run_tool_action(tool_name: str, base_cmd: str) -> None:
    print_info(f"Running: {tool_name} ({base_cmd})")
    print("Options for target input:")
    print("  [1] Enter targets/arguments manually")
    print("  [2] Use output file from previous tool")

    input_choice = prompt_input("Choose input method [1]").strip()
    if input_choice == "2":
        input_file = await select_existing_output_file()
        if input_file:
            target = f"-l {input_file}" if "nuclei" in base_cmd.lower() else f"< {input_file}"
            print_info(f"Using input file: {input_file}")
        else:
            target = prompt_input(f"Targets/args for {tool_name}").strip()
    else:
        target = prompt_input(f"Targets/args for {tool_name}").strip()

    output_filename = prompt_input(f"Output filename (default: output_{tool_name}.txt)").strip()
    if not output_filename:
        output_filename = None

    clear()
    await run_tool_async(tool_name, base_cmd, target, output_filename=output_filename)
    wait_for_enter("Execution finished. Press Enter to return...")


async def smart_tool_selector() -> None:
    while True:
        clear()
        print_tools_list_banner()

        tools = get_active_tools()
        if not tools:
            print_error("No tools found. Add tools first.")
            wait_for_enter()
            return

        tool_list = list(tools.items())
        for i, (name, info) in enumerate(tool_list, 1):
            print(f"  [{i}] {name.upper()} - {info.get('desc', 'No description')}")
        print("  [0] Back")

        choice = prompt_input("Choose tool")
        if choice == "0":
            break

        try:
            idx = int(choice) - 1
            if not 0 <= idx < len(tool_list):
                print_error("Invalid selection")
                wait_for_enter()
                continue
        except ValueError:
            print_error("Invalid input")
            wait_for_enter()
            continue

        tool_name, info = tool_list[idx]
        await run_tool_action(tool_name, info["cmd"])


async def run_tools_menu() -> None:
    while True:
        clear()
        print_tools_banner()
        print_menu(
            [
                ("1", "Tools List"),
                ("2", "Results"),
                ("3", "Add Tool"),
            ],
            "Back",
        )

        choice = prompt_input("Choose")
        if choice == "0":
            break

        if choice == "1":
            await smart_tool_selector()
        elif choice == "2":
            await run_results_menu()
        elif choice == "3":
            clear()
            interactive_add_tool()
            wait_for_enter()
        else:
            print_error("Invalid option")
            wait_for_enter()
