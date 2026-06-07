# SAMATCLI - User Manual and System Documentation

This document serves as the official reference for SAMATCLI (Sama Command Line Interface), an interactive, modular terminal dashboard designed to centralize and automate security reconnaissance and pentesting workflows. It covers terminal navigation, core system logic, and the persistence architecture.

---

## 1. User Manual and Navigation

SAMATCLI relies on a nested hierarchy of interactive terminal menus. The interface maintains a clean workspace by executing an automated screen clearance command at the beginning of each cycle, preventing the accumulation of historical text output.

### Main Menu (Central Orchestrator)
Executing `python3 samatclimenu.py` launches the central control panel, which exposes the following global routing paths:

* **Tools**: References the dynamic catalog of security scripts currently available in the project environment.
* **Source**: Spawns a background process to open the local default web browser directly to the project's official code repository.
* **Help**: Renders this reference manual directly within the active terminal buffer.
* **Results**: Opens the forensic historical viewer, allowing users to browse saved execution logs sorted alphabetically by tool name.
* **Exit**: Terminates the Python interpreter process cleanly, returning control to the system shell.

### Tool Submenu Architecture
To ensure a predictable operator experience, every security tool integrated into the platform (such as nmap, katana, or ffuf) inherits an identical, standardized control matrix:

* **Help**: Performs a rapid read-and-print operations (equivalent to a localized cat command) of the specific tool's native syntax guidelines and runtime flags.
* **Source**: Resolves the upstream documentation or official repository URL via the system browser, falling back to plaintext terminal rendering if a graphical user interface environment is unavailable.
* **Results**: Filters the historical log directory to display execution reports belonging exclusively to that specific tool.
* **Run Command**: Initializes the execution engine, prompting the operator for target parameters and a unique alphanumeric string to name the resulting evidence file.
* **Back**: Termitanes the current local sub-loop, destroying its runtime context and shifting execution up to the SAMA main menu.
* **Exit**: Issues an absolute system shutdown signal, forcing the entire application to terminate immediately from any depth.

---

## 2. Core System Architecture and Automation Logic

The defining feature of SAMATCLI is its decoupled architecture; it contains no hardcoded lists of tools within the main orchestrator. The engine maps the runtime environment dynamically using the following background processes:

### Automated Directory Discovery
Whenever the Tools menu is invoked, the backend executes an on-the-fly inspection of the local file system structure:
1. **Directory Enumeration**: The system queries the OS filesystem layer to retrieve a raw list of all entries inside the `tools/` directory.
2. **Type and Extension Filtering**: The backend iterates through the raw strings, explicitly discarding subdirectories, hidden system assets, or files lacking a valid `.py` extension.
3. **Extension Slicing**: Valid scripts undergo a trailing string slice truncation (`[:-3]`) to strip the `.py` characters, isolating the clean string name for proper interface presentation.
4. **Case-Insensitive Unicode Normalization**: To prevent alphabetical sorting discrepancies caused by upper and lowercase ASCII value offsets (where characters like uppercase 'O' evaluate ahead of lowercase 'k'), the system applies a lowercase key transformation during the sort process. This guarantees an intuitive alphabetical order for human readability.
5. **Dynamic Key Mapping**: The sorted list is compiled into a runtime key-value dictionary (e.g., `"1": "katana"`). When an operator submits a numeric choice, the orchestrator performs a hash lookup against this map to determine precisely which module file to call.

### Visual Short-Name Hash Generation
To preserve visual identity across submenus without manually designing text assets, the framework processes tool string inputs through a uniform slice filter. The engine isolates exactly the first five characters (`[:5]`), shifts them to an uppercase state (`.upper()`), and projects the shortened string as a prominent banner tracking the operator's current workspace.

### Isolated Process Execution
When an operator triggers a tool's execution pathway via `Run Command`, the system delegates the process to the operating system using a secure isolation pattern:
* **Command Injection Countermeasures**: Commands are never passed to the system as concatenated strings, which would leave the terminal vulnerable to shell-escape manipulation. Instead, instructions are parsed into strict token lists and executed directly, bypassing intermediate shell evaluation.
* **Stream Redirection**: The engine intercepts the target process's standard output (stdout) and standard error (stderr) streams, capturing the raw binary stream to prevent foreign tool text from corrupting the core menu interface display.

---

## 3. Data Persistence and Report Management

Data generated during security audits is treated as forensic artifacts rather than volatile console output. SAMA forces structured persistence across a deterministic directory hierarchy.

### Idempotent Storage Layout
The filesystem layer writes and retrieves tool evidence using strict directory validation routines:

```plain
results/
├── ffuf/
│   ├── recon_target_a.txt
│   └── subdomains_phase1.txt
├── katana/
│   └── extracted_endpoints.txt
└── nmap/
    └── local_network_scan.txt