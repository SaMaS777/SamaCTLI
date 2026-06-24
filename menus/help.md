# SamaCTLI - Help

## Main Menu Options

### [1] Tools
- **Tools List**: Browse and run available pentesting tools
- **Results**: View output from previous tool runs
- **Add Tool**: Register a new command-line tool

### [2] Source
- Opens the SamaCTLI repository link

### [3] Help
- Displays this help file

### [4] Results
- Browse and view saved tool output files
- Organized by tool name in `tool_results/`

### [5] AI Menu
- **Coder Mode** (DeepSeek v4 Pro): Expert programming assistance
- **General Assistant** (Kimi K2.6): Architecture & system design
- **Pentesting Mode** (Mistral Medium): Security analysis, exploit explanation, code auditing

## AI Chat Commands
- Type `volver` or `exit` to return to AI menu
- Type `clear` to reset conversation memory

## Adding Tools
1. Select "Add Tool" from Tools menu
2. Enter tool name (e.g., "nmap scan")
3. Enter description
4. Enter system command (must be in PATH, e.g., "nmap")
5. Tool saved to `tools/modules/<name>.json`

## Running Tools
1. Select "Tools List" from Tools menu
2. Choose a tool by number
3. Enter target/arguments (e.g., "192.168.1.1 -p 80")
4. Output saved to `tool_results/<tool>/output_<tool>.txt`

## Configuration
Create `.env` file in project root:
```bash
NVIDIA_API_KEY=your_key_here
BASE_URL=https://integrate.api.nvidia.com/v1
```

## Directory Structure
```
SamaCTLI/
├── tools/modules/       # Tool definitions (JSON)
├── tool_results/        # Tool output files
├── menus/help.md        # This file
└── .env                 # API keys (not in git)
```

## Security Notes
- Never commit `.env` or API keys
- Tool commands validated against PATH
- User input sanitized before execution
- 60-second timeout on tool execution