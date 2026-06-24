import asyncio
import shlex
import shutil
import socket
from pathlib import Path
from typing import Any

import httpx

TOOL_TIMEOUT = 30


class AITool:
    name: str
    description: str
    enabled: bool = True

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

    async def execute(self, command: str) -> str:
        raise NotImplementedError

    def get_schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
        }


class ShellTool(AITool):
    name = "shell"
    description = "Run any shell command and return output"

    async def execute(self, command: str) -> str:
        try:
            args = shlex.split(command)
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=TOOL_TIMEOUT
                )
            except TimeoutError:
                process.kill()
                await process.wait()
                return f"Error: Command timed out after {TOOL_TIMEOUT}s"

            output = stdout.decode("utf-8", errors="replace")
            error = stderr.decode("utf-8", errors="replace")

            if error:
                return f"STDOUT:\n{output}\nSTDERR:\n{error}"
            return output or "(no output)"

        except FileNotFoundError:
            return f"Error: Command not found: {command.split()[0] if command else 'empty'}"
        except Exception as e:
            return f"Error executing command: {e}"


class FileReadTool(AITool):
    name = "file_read"
    description = "Read a file from disk and pass content to AI"

    async def execute(self, command: str) -> str:
        try:
            path = Path(command.strip()).expanduser()
            if not path.exists():
                return f"Error: File not found: {path}"
            if not path.is_file():
                return f"Error: Not a file: {path}"

            content = path.read_text(encoding="utf-8")
            return f"File: {path}\nSize: {len(content)} bytes\n\n{content}"
        except UnicodeDecodeError:
            return f"Error: Cannot read binary file: {command}"
        except Exception as e:
            return f"Error reading file: {e}"


class FileWriteTool(AITool):
    name = "file_write"
    description = "Write AI output to a file"

    async def execute(self, command: str) -> str:
        try:
            parts = command.strip().split("\n", 1)
            if len(parts) < 2:
                return "Error: Usage: file_write <filepath>\n<content>"

            filepath = Path(parts[0].strip()).expanduser()
            content = parts[1]

            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(content, encoding="utf-8")

            return f"Successfully wrote {len(content)} bytes to {filepath}"
        except Exception as e:
            return f"Error writing file: {e}"


class PythonTool(AITool):
    name = "python"
    description = "Execute Python code and return result"

    async def execute(self, command: str) -> str:
        try:
            process = await asyncio.create_subprocess_exec(
                "python3",
                "-c",
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=TOOL_TIMEOUT
                )
            except TimeoutError:
                process.kill()
                await process.wait()
                return f"Error: Python execution timed out after {TOOL_TIMEOUT}s"

            output = stdout.decode("utf-8", errors="replace")
            error = stderr.decode("utf-8", errors="replace")

            if error:
                return f"STDOUT:\n{output}\nSTDERR:\n{error}"
            return output or "(no output)"

        except Exception as e:
            return f"Error executing Python: {e}"


class NmapTool(AITool):
    name = "nmap"
    description = "Run nmap scan with AI-chosen flags"

    async def execute(self, command: str) -> str:
        if not shutil.which("nmap"):
            return "Error: nmap not found in PATH"

        return await ShellTool().execute(f"nmap {command}")


class GobusterTool(AITool):
    name = "gobuster"
    description = "Run gobuster directory/DNS brute force"

    async def execute(self, command: str) -> str:
        if not shutil.which("gobuster"):
            return "Error: gobuster not found in PATH"

        return await ShellTool().execute(f"gobuster {command}")


class WhoisTool(AITool):
    name = "whois"
    description = "Run whois lookup"

    async def execute(self, command: str) -> str:
        if not shutil.which("whois"):
            return "Error: whois not found in PATH"

        return await ShellTool().execute(f"whois {command}")


class CurlTool(AITool):
    name = "curl"
    description = "Make HTTP requests"

    async def execute(self, command: str) -> str:
        if not shutil.which("curl"):
            async with httpx.AsyncClient(timeout=TOOL_TIMEOUT) as client:
                try:
                    parts = shlex.split(command)
                    if not parts:
                        return "Error: No URL provided"
                    url = parts[0]
                    method = "GET"
                    headers = {}
                    data = None

                    i = 1
                    while i < len(parts):
                        if parts[i] == "-X" and i + 1 < len(parts):
                            method = parts[i + 1]
                            i += 2
                        elif parts[i] == "-H" and i + 1 < len(parts):
                            h = parts[i + 1]
                            if ":" in h:
                                k, v = h.split(":", 1)
                                headers[k.strip()] = v.strip()
                            i += 2
                        elif parts[i] == "-d" and i + 1 < len(parts):
                            data = parts[i + 1]
                            i += 2
                        else:
                            i += 1

                    response = await client.request(method, url, headers=headers, content=data)
                    return f"Status: {response.status_code}\nHeaders: {dict(response.headers)}\n\n{response.text}"
                except Exception as e:
                    return f"Error making HTTP request: {e}"

        return await ShellTool().execute(f"curl {command}")


class PortScanTool(AITool):
    name = "port_scan"
    description = "Simple socket-based port scan"

    async def execute(self, command: str) -> str:
        try:
            parts = shlex.split(command)
            if not parts:
                return "Error: Usage: port_scan <host> [ports]"

            host = parts[0]
            ports: list[int] = []
            if len(parts) > 1:
                for p in parts[1].split(","):
                    if "-" in p:
                        start, end = map(int, p.split("-"))
                        ports.extend(range(start, end + 1))
                    else:
                        ports.append(int(p))
            else:
                ports = list(range(1, 1025))

            open_ports = []
            for port in ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex((host, port))
                    sock.close()
                    if result == 0:
                        open_ports.append(port)
                except OSError:
                    pass

            if open_ports:
                return f"Open ports on {host}: {', '.join(map(str, open_ports))}"
            return f"No open ports found on {host} (scanned {len(ports)} ports)"

        except ValueError:
            return "Error: Invalid port specification"
        except Exception as e:
            return f"Error during port scan: {e}"


class AnalyzeFileTool(AITool):
    name = "analyze_file"
    description = "Pass file content to AI for analysis"

    async def execute(self, command: str) -> str:
        try:
            filepath = Path(command.strip()).expanduser()
            if not filepath.exists():
                return f"Error: File not found: {filepath}"

            content = filepath.read_text(encoding="utf-8")
            return f"File: {filepath}\nSize: {len(content)} bytes\n\nContent:\n{content}"
        except UnicodeDecodeError:
            return f"Error: Cannot analyze binary file: {command}"
        except Exception as e:
            return f"Error analyzing file: {e}"


def get_all_tools() -> dict[str, AITool]:
    return {
        "shell": ShellTool(),
        "file_read": FileReadTool(),
        "file_write": FileWriteTool(),
        "python": PythonTool(),
        "nmap": NmapTool(),
        "gobuster": GobusterTool(),
        "whois": WhoisTool(),
        "curl": CurlTool(),
        "port_scan": PortScanTool(),
        "analyze_file": AnalyzeFileTool(),
    }


def get_tool(name: str) -> AITool | None:
    return get_all_tools().get(name)


def get_enabled_tools(enabled_names: set[str] | None = None) -> dict[str, AITool]:
    all_tools = get_all_tools()
    if enabled_names is None:
        return {k: v for k, v in all_tools.items() if v.enabled}
    return {k: v for k, v in all_tools.items() if k in enabled_names and v.enabled}


def format_tools_for_prompt(tools: dict[str, AITool]) -> str:
    lines = []
    for name, tool in tools.items():
        status = "enabled" if tool.enabled else "disabled"
        lines.append(f"- {name}: {tool.description} [{status}]")
    return "\n".join(lines)
