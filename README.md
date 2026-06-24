# SamaCTLI

**SamaCTLI** (Sama Command Line Interface) is a pentesting and reconnaissance dashboard built for security professionals. It provides a unified interface for managing tools, viewing results, and getting AI-powered assistance.

## Features

- **Tool Management** - Register, list, and execute CLI tools (nmap, nikto, gobuster, etc.)
- **Results Viewer** - Browse and view saved output from tool executions
- **AI Integration System** - Full multi-provider AI support with tool access:
  - **API Key Management** - Encrypted storage for multiple providers (Google, Anthropic, custom)
  - **Automatic Model Discovery** - Fetches available models from provider APIs
  - **Interactive AI Chat** - 10 built-in pentesting tools (shell, nmap, gobuster, whois, curl, port_scan, python, file_read, file_write, analyze_file) with user confirmation
- **Secure Execution** - No shell injection, 60s timeout, input validation

## Quick Start

### Prerequisites

- Python 3.11+
- At least one AI provider API key (Google, Anthropic, or OpenAI-compatible)
- Git

### Installation (Linux/macOS)

```bash
# Clone the repository
git clone https://github.com/SaMaS777/SamaCTLI
cd SamaCTLI

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

### Installation (Windows)

```powershell
# Clone the repository
git clone https://github.com/SaMaS777/SamaCTLI
cd SamaCTLI

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### Configuration

**New AI Integration System (Multi-provider):**
API keys are managed interactively via the `[A] API Keys` menu and stored encrypted at `~/.samactli/api_keys.enc` (Linux/macOS) or `%USERPROFILE%\.samactli\api_keys.enc` (Windows). No `.env` required.

## Usage

### Launch

```bash
python -m SamaCTLI
```

### Main Menu

```
 █████████████████████████████████████████████
 █                                           █
 █           SAMA CTLI                       █
 █     Recon & Pentesting Dashboard          █
 █                                           █
 █████████████████████████████████████████████

  [1] Tools
  [2] Source
  [3] Help
  [4] Results
  [A] API Keys (Multi-Provider AI)
  [M] AI Models & Chat
  [0] Exit
```

---

## Tools Menu

### Adding a Tool

```
[1] Tools → [3] Add Tool
```

Example - Add nmap:
```
Tool name: nmap scan
Description: Network exploration and security auditing
System command: nmap
```

The tool is saved to `tools/modules/nmap_scan.json` and immediately available.

### Running a Tool

```
[1] Tools → [1] Tools List
```

Select a tool by number, then enter target/arguments:

```
[1] NMAP_SCAN - Network exploration and security auditing
[2] GOBUSTER - Directory/file brute-forcer
[0] Back

Choose tool: 1

Enter targets/args for NMAP_SCAN: 192.168.1.0/24 -p 80,443 --open
```

Output is saved to `tool_results/nmap_scan/output_nmap_scan.txt`

### Viewing Results

```
[4] Results (from main menu)
# or
[1] Tools → [2] Results
```

Browse by tool, then by output file:

```
[1] NMAP_SCAN (3 output files)
[2] GOBUSTER (1 output files)
[0] Back

Choose tool: 1

[1] output_nmap_scan.txt (2.4 KB)
[2] output_nmap_scan.txt (1.8 KB)
[0] Back
```

View any file with pagination (200 lines max per view).

---

## AI Integration System

The new AI Integration System provides multi-provider support with tool access for pentesting workflows.

### API Keys Menu

```
[A] API Keys
```

Manage encrypted API keys for multiple providers:

| Option | Action |
|--------|--------|
| `[1] Add API Key` | Enter provider name and API key (auto-triggers model discovery) |
| `[2] List Providers` | Show saved providers with masked keys (e.g., `sk-****1234`) |
| `[3] Delete Provider` | Remove a provider and its models |
| `[4] Re-sync Models` | Re-discover models for a provider |

**Supported Providers:**
- **Google** - Generative AI API (Gemini models)
- **Anthropic** - Hardcoded Claude models (no list endpoint)
- **Custom** - Any OpenAI-compatible endpoint

Keys are encrypted with Fernet (AES-256) using a machine-derived key, stored at `~/.samactli/api_keys.enc` (Linux/macOS) or `%USERPROFILE%\.samactli\api_keys.enc` (Windows).

### AI Models Menu

```
[M] AI Models
```

Dynamically lists discovered models per provider:

```
[1] Google  (3 models)
[2] Custom  (5 models)
[0] Back
```

Select a provider, then a model:

```
[1] gemini-1.5-pro
[2] gemini-1.5-flash
[3] gemini-pro
[0] Back
```

### Interactive AI Chat with Tool Access

When you select a model, a full chat session launches with tool support:

```
┌────────────────────────────────────────────────────────────┐
│ AI Chat Session                                            │
│ Provider: Google  Model: gemini-1.5-pro                    │
│ Tools: shell, file_read, file_write, python, nmap, ...    │
│ Session: 20260115_143022                                   │
└────────────────────────────────────────────────────────────┘
Type 'help' for commands, 'exit' to quit
```

#### Available Tools

| Tool | Description |
|------|-------------|
| `shell` | Run any shell command |
| `file_read` | Read file content |
| `file_write` | Write AI output to file |
| `python` | Execute Python code |
| `nmap` | Run nmap scans |
| `gobuster` | Directory/DNS brute force |
| `whois` | WHOIS lookups |
| `curl` | HTTP requests |
| `port_scan` | Socket-based port scanner |
| `analyze_file` | Pass file to AI for analysis |

#### Tool Invocation Flow

1. AI responds with tool request:
   ```json
   {"tool": "nmap", "command": "-sV 192.168.1.1"}
   ```

2. CLI prompts for confirmation:
   ```
   AI wants to run: nmap → -sV 192.168.1.1 — Allow? [y/N]:
   ```

3. If allowed: executes, returns output to AI
4. If denied: informs AI, continues conversation

#### Special Chat Commands

| Command | Action |
|---------|--------|
| `help` | Show available tools and commands |
| `tools` | Toggle enabled tools for this session |
| `save` | Save conversation to `~/.samactli/chat_history/` |
| `clear` | Clear conversation history |
| `exit` | Return to model menu |

#### Example: Nmap Scan via AI

```
You: Scan 192.168.1.0/24 for open ports

AI: I'll run an nmap scan to discover open ports.
{"tool": "nmap", "command": "-p- --open 192.168.1.0/24"}

AI wants to run: nmap → -p- --open 192.168.1.0/24 — Allow? [y/N]: y

[Executing...]
AI: Scan complete. Found open ports: 22, 80, 443, 3306 on 192.168.1.10.
    Would you like me to run service version detection on these?
```

The new AI Integration System provides multi-provider support with tool access for pentesting workflows.

### API Keys Menu

```
[A] API Keys
```

Manage encrypted API keys for multiple providers:

| Option | Action |
|--------|--------|
| `[1] Add API Key` | Enter provider name and API key (auto-triggers model discovery) |
| `[2] List Providers` | Show saved providers with masked keys (e.g., `sk-****1234`) |
| `[3] Delete Provider` | Remove a provider and its models |
| `[4] Re-sync Models` | Re-discover models for a provider |

**Supported Providers:**
- **Google** - Generative AI API (Gemini models)
- **OpenAI** - Standard OpenAI API
- **NVIDIA** - NIM API (Llama, Mistral, etc.)
- **Anthropic** - Hardcoded Claude models (no list endpoint)
- **Custom** - Any OpenAI-compatible endpoint

Keys are encrypted with Fernet (AES-256) using a machine-derived key, stored at `~/.samactli/api_keys.enc`.

### AI Models Menu

```
[M] AI Models
```

Dynamically lists discovered models per provider:

```
[1] Google  (3 models)
[2] OpenAI  (5 models)
[3] NVIDIA  (12 models)
[0] Back
```

Select a provider, then a model:

```
[1] gemini-1.5-pro
[2] gemini-1.5-flash
[3] gemini-pro
[0] Back
```

### Interactive AI Chat with Tool Access

When you select a model, a full chat session launches with tool support:

```
┌────────────────────────────────────────────────────────────┐
│ AI Chat Session                                            │
│ Provider: Google  Model: gemini-1.5-pro                    │
│ Tools: shell, file_read, file_write, python, nmap, ...    │
│ Session: 20260115_143022                                   │
└────────────────────────────────────────────────────────────┘
Type 'help' for commands, 'exit' to quit
```

#### Available Tools

| Tool | Description |
|------|-------------|
| `shell` | Run any shell command |
| `file_read` | Read file content |
| `file_write` | Write AI output to file |
| `python` | Execute Python code |
| `nmap` | Run nmap scans |
| `gobuster` | Directory/DNS brute force |
| `whois` | WHOIS lookups |
| `curl` | HTTP requests |
| `port_scan` | Socket-based port scanner |
| `analyze_file` | Pass file to AI for analysis |

#### Tool Invocation Flow

1. AI responds with tool request:
   ```json
   {"tool": "nmap", "command": "-sV 192.168.1.1"}
   ```

2. CLI prompts for confirmation:
   ```
   AI wants to run: nmap → -sV 192.168.1.1 — Allow? [y/N]:
   ```

3. If allowed: executes, returns output to AI
4. If denied: informs AI, continues conversation

#### Special Chat Commands

| Command | Action |
|---------|--------|
| `help` | Show available tools and commands |
| `tools` | Toggle enabled tools for this session |
| `save` | Save conversation to `~/.samactli/chat_history/` |
| `clear` | Clear conversation history |
| `exit` | Return to model menu |

#### Example: Nmap Scan via AI

```
You: Scan 192.168.1.0/24 for open ports

AI: I'll run an nmap scan to discover open ports.
{"tool": "nmap", "command": "-p- --open 192.168.1.0/24"}

AI wants to run: nmap → -p- --open 192.168.1.0/24 — Allow? [y/N]: y

[Executing...]
AI: Scan complete. Found open ports: 22, 80, 443, 3306 on 192.168.1.10.
    Would you like me to run service version detection on these?
```

---

## Project Structure

```
SamaCTLI/
├── .env                     # Legacy API keys (NOT in git)
├── .env.example             # Template
├── ai_config.json           # Legacy AI role definitions
├── pyproject.toml           # Project config
├── README.md                # This file
├── SamaCTLI/
│   ├── __main__.py          # Entry point
│   ├── config.py            # Pydantic settings
│   ├── constants.py         # ANSI colors
│   ├── ui.py                # UI helpers
│   ├── ai/manager.py        # Legacy AI chat logic
│   ├── core/
│   │   ├── __init__.py
│   │   ├── api_manager.py   # Encrypted API key storage
│   │   ├── model_discovery.py  # Provider model fetching
│   │   └── ai_session.py    # Chat session with tool access
│   ├── tools/
│   │   ├── detection.py     # Tool discovery + caching
│   │   ├── runner.py        # Async subprocess execution
│   │   ├── registry.py      # Tool registration
│   │   └── ai_tools.py      # AI-accessible pentesting tools
│   └── menus/
│       ├── __init__.py
│       ├── tools.py         # Tools menu
│       ├── results.py       # Results viewer
│       ├── menu_apikeys.py  # API Keys management
│       ├── menu_models.py   # AI Models selection
│       └── menu_chat.py     # Chat session launcher
├── tools/modules/           # Tool JSON definitions
│   ├── nmap_scan.json
│   └── gobuster.json
└── tool_results/            # Tool output (auto-created)
    ├── nmap_scan/
    │   └── output_nmap_scan.txt
    └── gobuster/
        └── output_gobuster.txt

~/.samactli/                 # User config (auto-created)
├── api_keys.enc             # Encrypted API keys
├── .salt                    # Encryption salt
├── .master                  # Master key
├── models.json              # Discovered models cache
└── chat_history/            # Saved conversations
    └── chat_<provider>_<model>_<timestamp>.json
```

---

## Security Notes

- **Never commit `.env`** - Contains legacy API keys
- **Encrypted API Keys** - New system uses Fernet (AES-256) with PBKDF2 key derivation, stored at `~/.samactli/api_keys.enc`
- **Machine-derived encryption** - Salt + master key generated per machine, never shared
- **Tool validation** - Commands checked against PATH before execution
- **Input sanitization** - Tool names restricted to `[a-z0-9_-]`
- **No shell=True** - Commands executed via `create_subprocess_exec` with split args
- **Timeout** - 60s default on tool execution, 30s on AI tool execution
- **User confirmation required** - AI tools only execute after explicit user approval
- **API key in env** - Legacy only, loaded via `python-dotenv`, not hardcoded

---

## Development

### Run Linter

```bash
.venv/bin/ruff check SamaCTLI
.venv/bin/ruff check --fix SamaCTLI
```

### Run Type Checker

```bash
.venv/bin/mypy SamaCTLI
```

### Run Tests

```bash
.venv/bin/pytest
```

---

## Troubleshooting

### "No tools found"
- Run `[1] Tools → [3] Add Tool` to register tools
- Ensure the command exists in PATH (`which nmap`)

### "API key not found" (Legacy)
- Check `.env` exists in project root
- Verify `NVIDIA_API_KEY=...` is set

### "No API keys configured"
- Go to `[A] API Keys → [1] Add API Key`
- Enter provider name (Google, Nvidia, OpenAI, Anthropic, or custom)
- Enter your API key

### "No models discovered"
- After adding API key, models auto-discover
- If failed: `[A] API Keys → [4] Re-sync Models`
- Check internet connectivity and API key validity

### "Module not found" on import
- Run `pip install -e ".[dev]"` from project root
- Ensure `.venv` is activated

### "Fernet key error" / "Incorrect padding"
- Delete `~/.samactli/.salt` and `~/.samactli/.master` to reset encryption
- Re-add API keys

---

## License

MIT License - See LICENSE file for details.

---

## Author

**SamAs** - Pentesting & Recon Dashboard
