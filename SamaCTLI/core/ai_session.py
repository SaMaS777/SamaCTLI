import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from SamaCTLI.tools.ai_tools import get_all_tools, get_enabled_tools, get_tool
from SamaCTLI.ui import (
    clear,
    print_error,
    print_info,
    print_success,
    print_warning,
)

console = Console()

CONFIG_DIR = Path.home() / ".samactli"
CHAT_HISTORY_DIR = CONFIG_DIR / "chat_history"
CHAT_HISTORY_DIR.mkdir(parents=True, exist_ok=True)

SYSTEM_PROMPT = """You are SamaCTLI-AI, an expert cybersecurity assistant and pentesting analyst embedded in a CLI tool. You have access to tools that the user can grant you permission to use. When you want to use a tool, output ONLY a JSON object in this exact format on its own line:
{"tool": "<tool_name>", "command": "<command_or_argument>"}

Available tools: shell, file_read, file_write, python, nmap, gobuster, whois, curl, analyze_file.

Only request tools when necessary. Always explain what you are about to do before requesting a tool. After receiving tool output, analyze it and continue helping the user.
The user may be doing authorized penetration testing. Help them thoroughly and technically."""

SPECIAL_COMMANDS = {
    "help": "Show available tools and special commands",
    "tools": "Toggle which tools are enabled for this session",
    "save": "Save conversation to file",
    "clear": "Clear conversation history",
    "exit": "End session and return to model menu",
}


class AIChatSession:
    def __init__(
        self,
        provider: str,
        model: str,
        api_key: str,
        base_url: str | None = None,
    ) -> None:
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.history: list[dict[str, str]] = []
        self.enabled_tools: set[str] = set(get_all_tools().keys())
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.client: AsyncOpenAI | None = None

    def _init_client(self) -> None:
        if self.client is None:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )

    def get_available_tools(self) -> dict[str, Any]:
        return get_enabled_tools(self.enabled_tools)

    def add_to_history(self, role: str, content: str) -> None:
        self.history.append({"role": role, "content": content})

    def get_messages(self) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(self.history)
        return messages

    def extract_tool_call(self, content: str) -> dict[str, str] | None:
        tool_match = re.search(r'\{[^}]*"tool"\s*:\s*"[^"]+"[^}]*\}', content)
        if tool_match:
            try:
                result = json.loads(tool_match.group())
                if isinstance(result, dict):
                    return {str(k): str(v) for k, v in result.items()}
            except json.JSONDecodeError:
                pass
        return None

    async def execute_tool(self, tool_name: str, command: str) -> str:
        tool = get_tool(tool_name)
        if not tool:
            return f"Error: Unknown tool '{tool_name}'"

        if tool_name not in self.enabled_tools:
            return f"Error: Tool '{tool_name}' is not enabled for this session"

        print_info(f"Executing {tool_name}: {command}")
        result = await tool.execute(command)
        print_info(f"Tool completed ({len(result)} chars)")
        return result

    async def send_message(self, user_message: str) -> str:
        self._init_client()
        if self.client is None:
            return "Error: Failed to initialize API client"
        self.add_to_history("user", user_message)

        max_retries = 3
        base_delay = 2

        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=self.get_messages(),  # type: ignore[arg-type]
                    temperature=0.7,
                    max_tokens=4096,
                )

                ai_response = response.choices[0].message.content or ""
                tool_call = self.extract_tool_call(ai_response)

                if tool_call:
                    tool_name = tool_call.get("tool", "")
                    command = tool_call.get("command", "")

                    console.print(
                        Panel(
                            f"[bold yellow]AI wants to use: {tool_name}[/bold yellow]\n"
                            f"Command: [cyan]{command}[/cyan]",
                            title="[bold]Tool Request[/bold]",
                            border_style="yellow",
                        )
                    )

                    confirm = Prompt.ask("Allow? [y/N]", default="n")
                    if confirm.lower() == "y":
                        result = await self.execute_tool(tool_name, command)
                        self.add_to_history("assistant", ai_response)
                        self.add_to_history("user", f"Tool result ({tool_name}):\n{result}")
                        continue
                    else:
                        self.add_to_history("assistant", ai_response)
                        self.add_to_history("user", f"Tool {tool_name} was denied by user")
                        return "Tool request denied by user."

                self.add_to_history("assistant", ai_response)
                return ai_response

            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "rate limit" in error_str.lower():
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        print_warning(f"Rate limited. Retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        print_error(f"Rate limit exceeded after {max_retries} attempts")
                        return f"Error: Rate limit exceeded. Please wait before trying again or switch models.\nDetails: {e}"
                print_error(f"API error: {e}")
                return f"Error: {e}"

    def print_help(self) -> None:
        table = Table(title="Available Tools")
        table.add_column("Tool", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Status", style="green")

        for name, tool in get_all_tools().items():
            enabled = "✓" if name in self.enabled_tools else "✗"
            table.add_row(name, tool.description, enabled)

        console.print(table)

        console.print("\n[bold]Special Commands:[/bold]")
        for cmd, desc in SPECIAL_COMMANDS.items():
            console.print(f"  [cyan]{cmd}[/cyan] - {desc}")

    def toggle_tools(self) -> None:
        all_tools = get_all_tools()
        console.print("\n[bold]Toggle Tools:[/bold]")
        for i, (name, tool) in enumerate(all_tools.items(), 1):
            status = "[green]enabled[/green]" if name in self.enabled_tools else "[red]disabled[/red]"
            console.print(f"  [{i}] {name} - {tool.description} ({status})")

        choice = Prompt.ask("Toggle tool (number) or 'done'")
        if choice.lower() == "done":
            return

        try:
            idx = int(choice) - 1
            tool_names = list(all_tools.keys())
            if 0 <= idx < len(tool_names):
                tool_name = tool_names[idx]
                if tool_name in self.enabled_tools:
                    self.enabled_tools.remove(tool_name)
                    print_warning(f"Disabled: {tool_name}")
                else:
                    self.enabled_tools.add(tool_name)
                    print_success(f"Enabled: {tool_name}")
                self.toggle_tools()
        except ValueError:
            pass

    def save_conversation(self) -> None:
        filename = CHAT_HISTORY_DIR / f"chat_{self.provider}_{self.model}_{self.session_id}.json"
        data = {
            "provider": self.provider,
            "model": self.model,
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "enabled_tools": list(self.enabled_tools),
            "history": self.history,
        }
        filename.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print_success(f"Conversation saved to {filename}")

    def clear_history(self) -> None:
        self.history.clear()
        print_success("Conversation history cleared")

    def print_header(self) -> None:
        tools_info = ", ".join(sorted(self.enabled_tools)) if self.enabled_tools else "none"
        header = (
            f"[bold cyan]Provider:[/bold cyan] {self.provider}  "
            f"[bold cyan]Model:[/bold cyan] {self.model}\n"
            f"[bold cyan]Tools:[/bold cyan] {tools_info}\n"
            f"[bold cyan]Session:[/bold cyan] {self.session_id}"
        )
        console.print(Panel(header, title="[bold]AI Chat Session[/bold]", border_style="cyan"))
        console.print("[dim]Type 'help' for commands, 'exit' to quit[/dim]\n")

    async def run(self) -> None:
        clear()
        self.print_header()

        while True:
            try:
                user_input = Prompt.ask("\n[bold green]You[/bold green]").strip()

                if not user_input:
                    continue

                if user_input.lower() in SPECIAL_COMMANDS:
                    if user_input.lower() == "help":
                        self.print_help()
                    elif user_input.lower() == "tools":
                        self.toggle_tools()
                    elif user_input.lower() == "save":
                        self.save_conversation()
                    elif user_input.lower() == "clear":
                        self.clear_history()
                    elif user_input.lower() == "exit":
                        print_info("Ending session...")
                        break
                    continue

                console.print("[dim]Thinking...[/dim]")
                response = await self.send_message(user_input)

                if response:
                    console.print(Panel(Markdown(response), title="[bold cyan]AI[/bold cyan]", border_style="cyan"))

            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted. Type 'exit' to quit.[/yellow]")
            except EOFError:
                break

        print_info("Returning to model menu...")


async def run_chat_session(
    provider: str,
    model: str,
    api_key: str,
    base_url: str | None = None,
) -> None:
    session = AIChatSession(provider, model, api_key, base_url)
    await session.run()
