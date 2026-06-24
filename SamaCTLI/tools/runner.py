import asyncio
import shlex
from pathlib import Path

from SamaCTLI.ui import print_error, print_info


async def run_tool_async(
    tool_name: str,
    base_command: str,
    target: str = "",
    timeout: int = 60,
    output_filename: str | None = None,
) -> tuple[int, str, str]:
    full_cmd = f"{base_command} {target}".strip() if target else base_command

    if output_filename:
        output_file = Path(f"tool_results/{tool_name}/{output_filename}")
    else:
        output_file = Path(f"tool_results/{tool_name}/output_{tool_name}.txt")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    print_info(f"Running: {full_cmd}")
    print_info(f"Saving to: {output_file}")

    try:
        args = shlex.split(full_cmd)
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=float(timeout))

        output = stdout.decode("utf-8", errors="replace")
        error = stderr.decode("utf-8", errors="replace")

        output_file.write_text(output, encoding="utf-8")
        if error:
            output_file.write_text(output + "\n--- STDERR ---\n" + error, encoding="utf-8")

        return process.returncode or 0, output, error

    except TimeoutError:
        print_error("Command timed out (60s)")
        return -1, "", "Timeout"
    except FileNotFoundError:
        print_error(f"Command not found: {base_command}")
        return -1, "", "Command not found"
    except Exception as e:
        print_error(f"Execution error: {e}")
        return -1, "", str(e)


def run_tool_sync(
    tool_name: str,
    base_command: str,
    target: str = "",
    timeout: int = 60,
    output_filename: str | None = None,
) -> tuple[int, str, str]:
    return asyncio.run(run_tool_async(tool_name, base_command, target, timeout, output_filename))
