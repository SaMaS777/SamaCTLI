from dataclasses import dataclass

from openai import AsyncOpenAI
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from SamaCTLI.config import get_settings
from SamaCTLI.constants import GREEN, RED, RESET
from SamaCTLI.ui import (
    clear,
    print_banner,
    print_error,
    print_info,
    print_success,
    prompt_input,
    wait_for_enter,
)

console = Console()


@dataclass
class ChatMessage:
    role: str
    content: str

    def to_param(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass
class RoleConfig:
    key: str
    name: str
    model: str
    system_prompt: str


class AIManager:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = AsyncOpenAI(
            base_url=self.settings.base_url,
            api_key=self.settings.nvidia_api_key,
        )
        self.histories: dict[str, list[ChatMessage]] = {}
        self._init_histories()

    def _init_histories(self) -> None:
        for key, role in self.settings.roles.items():
            self.histories[key] = [ChatMessage(role="system", content=role.system_prompt)]

    def get_roles(self) -> list[RoleConfig]:
        return [
            RoleConfig(key=key, name=role.name, model=role.model, system_prompt=role.system_prompt)
            for key, role in self.settings.roles.items()
        ]

    async def chat(self, role_key: str, user_prompt: str) -> str:
        if role_key not in self.histories:
            return f"{RED}[-] Invalid role: {role_key}{RESET}"

        self.histories[role_key].append(ChatMessage(role="user", content=user_prompt))

        try:
            completion = await self.client.chat.completions.create(
                model=self.settings.roles[role_key].model,
                messages=[m.to_param() for m in self.histories[role_key]],  # type: ignore[misc]
                temperature=0.2,
            )
            response = completion.choices[0].message.content or ""
            self.histories[role_key].append(ChatMessage(role="assistant", content=response))
            return response
        except Exception as e:
            return f"{RED}[-] Error: {e}{RESET}"

    def reset_history(self, role_key: str) -> bool:
        if role_key in self.histories:
            role = self.settings.roles.get(role_key)
            system_prompt = role.system_prompt if role else ""
            self.histories[role_key] = [ChatMessage(role="system", content=system_prompt)]
            return True
        return False


async def run_ai_menu() -> None:
    manager = AIManager()
    roles = manager.get_roles()

    while True:
        clear()
        print_banner("SAMACTLI - AI INTELLIGENCE", "Select a role to chat with")

        for i, role in enumerate(roles, 1):
            print(f"  {GREEN}[{i}]{RESET} {role.name} ({role.model})")
        print(f"  {GREEN}[0]{RESET} Back to Main Menu")
        print()

        choice = prompt_input("Choose")
        if choice == "0":
            break

        try:
            idx = int(choice) - 1
            if not 0 <= idx < len(roles):
                print_error("Invalid option")
                wait_for_enter()
                continue
        except ValueError:
            print_error("Invalid input")
            wait_for_enter()
            continue

        role = roles[idx]
        await run_chat_session(manager, role)


async def run_chat_session(manager: AIManager, role: RoleConfig) -> None:
    clear()
    print_banner(f"Chat: {role.name}", f"Model: {role.model}")
    print_info("Commands: 'back' = return, 'clear' = reset memory, 'exit' = quit")

    while True:
        user_input = prompt_input("YOU")
        if not user_input:
            continue

        cmd = user_input.lower()
        if cmd in ("back", "exit"):
            break
        if cmd == "clear":
            manager.reset_history(role.key)
            print_success("Memory cleared")
            continue

        print_info(f"Connecting to {role.name}...")
        response = await manager.chat(role.key, user_input)

        console.print(Panel(Markdown(response), title=f"[green]{role.name}[/green]", border_style="green"))
