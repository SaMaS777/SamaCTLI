import subprocess
import sys

from SamaCTLI.constants import BLUE, GREEN, RED, RESET, WHITE, YELLOW

CLEAR_SCREEN = "\033[H\033[2J"


def clear() -> None:
    try:
        subprocess.run(["reset"], check=False, capture_output=True)
    except Exception:
        sys.stdout.write(CLEAR_SCREEN)
        sys.stdout.flush()


def print_banner(title: str, subtitle: str = "") -> None:
    clear()
    border = "█" * 60
    print(f"{GREEN}{border}{RESET}")
    print(f"{GREEN}█{' ' * 58}█{RESET}")
    print(f"{GREEN}█  {WHITE}{title.center(54)}{GREEN}  █{RESET}")
    if subtitle:
        print(f"{GREEN}█  {WHITE}{subtitle.center(54)}{GREEN}  █{RESET}")
    print(f"{GREEN}█{' ' * 58}█{RESET}")
    print(f"{GREEN}{border}{RESET}\n")


def print_menu(options: list[tuple[str, str]], exit_text: str = "Exit") -> None:
    for key, desc in options:
        print(f"  {GREEN}[{key}]{RESET} {desc}")
    print(f"  {GREEN}[0]{RESET} {exit_text}")
    print(f"{BLUE}{'-' * 60}{RESET}")


def prompt_input(prompt: str) -> str:
    return input(f"{WHITE}{prompt}{RESET} ").strip()


def print_info(msg: str) -> None:
    print(f"{BLUE}[*]{RESET} {msg}")


def print_success(msg: str) -> None:
    print(f"{GREEN}[+]{RESET} {msg}")


def print_error(msg: str) -> None:
    print(f"{RED}[-]{RESET} {msg}")


def print_warning(msg: str) -> None:
    print(f"{YELLOW}[!]{RESET} {msg}")


def wait_for_enter(msg: str = "Press Enter to continue...") -> None:
    input(f"\n{WHITE}{msg}{RESET}")
