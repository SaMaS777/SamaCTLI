from pathlib import Path

from SamaCTLI.ui import (
    clear,
    print_banner,
    print_error,
    print_info,
    prompt_input,
    wait_for_enter,
)


def print_results_banner() -> None:
    print_banner("RESULTS MENU", "View tool output files")


async def run_results_menu() -> None:
    while True:
        clear()
        print_results_banner()

        results_dir = Path("tool_results")
        if not results_dir.exists():
            print_error("No results directory found")
            wait_for_enter()
            return

        tool_dirs = [d for d in results_dir.iterdir() if d.is_dir()]
        if not tool_dirs:
            print_info("No results yet. Run some tools first.")
            wait_for_enter()
            return

        for i, tool_dir in enumerate(tool_dirs, 1):
            output_files = list(tool_dir.glob("*.txt"))
            print(f"  [{i}] {tool_dir.name.upper()} ({len(output_files)} output file(s))")
        print("  [0] Back")

        choice = prompt_input("Choose tool to view")
        if choice == "0":
            break

        try:
            idx = int(choice) - 1
            if not 0 <= idx < len(tool_dirs):
                print_error("Invalid selection")
                wait_for_enter()
                continue
        except ValueError:
            print_error("Invalid input")
            wait_for_enter()
            continue

        selected_dir = tool_dirs[idx]
        await view_tool_results(selected_dir)


async def view_tool_results(tool_dir: Path) -> None:
    while True:
        clear()
        print_banner(f"RESULTS: {tool_dir.name.upper()}")

        output_files = sorted(tool_dir.glob("*.txt"))
        if not output_files:
            print_info("No output files in this directory")
            wait_for_enter()
            return

        for i, f in enumerate(output_files, 1):
            size = f.stat().st_size
            print(f"  [{i}] {f.name} ({size} bytes)")
        print("  [0] Back")

        choice = prompt_input("Choose file to view")
        if choice == "0":
            break

        try:
            idx = int(choice) - 1
            if not 0 <= idx < len(output_files):
                print_error("Invalid selection")
                wait_for_enter()
                continue
        except ValueError:
            print_error("Invalid input")
            wait_for_enter()
            continue

        selected_file = output_files[idx]
        await view_file(selected_file)


async def view_file(file_path: Path) -> None:
    clear()
    print_banner(f"FILE: {file_path.name}")

    try:
        content = file_path.read_text(encoding="utf-8")
        if not content:
            print_info("(empty file)")
        else:
            lines = content.splitlines()
            for i, line in enumerate(lines, 1):
                if i > 200:
                    print_info(f"... ({len(lines) - 200} more lines)")
                    break
                print(f"{i:4} | {line}")
    except Exception as e:
        print_error(f"Failed to read file: {e}")

    wait_for_enter()
