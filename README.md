<div align="center">

# Netra Recon

**A modular command-line toolkit for authorized network, domain, and web reconnaissance.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-2ea44f.svg)](https://opensource.org/license/mit/)

</div>

---

## Overview

Netra Recon brings domain intelligence, DNS analysis, web inspection, and security
research utilities together in an interactive terminal application. Browse its
module catalog, configure a target and options, run individual modules, and review
or export results.

The project is intended for **authorized assessment, defensive security work, and
education**. Some modules actively send requests or probes. Only run them against
systems you own or are explicitly authorized to test, and follow the target
owner's rules of engagement.

## Highlights

- Interactive CLI for discovering, selecting, and running modules.
- Search by keyword or regular expression; filter modules by category or tag.
- Per-module and global options, configurable profiles, and favorites.
- DNS, RDAP, IP metadata, HTTP, TLS, and web-application analysis modules.
- TXT and CSV reports, with structured JSON output for Domain Info.
- Optional API integrations for modules that support external data providers.
- Docker support for an isolated runtime.

Module availability and descriptions come from the bundled catalog. Run
`modules` in the CLI to see the modules available in your checkout.

## Requirements

- Python 3.10 or newer.
- Internet access for network lookups and modules that call external services.
- Optional API credentials for provider-backed modules.
- On Debian/Kali systems, install virtual-environment support if needed:

  ```bash
  sudo apt update
  sudo apt install python3-venv
  ```

Do not install project dependencies into a system-managed Python interpreter.
Use a virtual environment to comply with PEP 668.

## Installation

Clone the repository and change into its directory:

```bash
git clone https://github.com/divinelabio/Argus.git netra-recon
cd netra-recon
```

### Virtual environment (recommended)

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Launch the interactive application:

```bash
netra-recon
```

Alternatively, run it as a Python module:

```bash
python -m netra_recon
```

To install the project and its declared dependencies in editable mode:

```bash
python -m pip install -e .
```

### Global launcher

The installer creates a dedicated virtual environment under `/opt/netra-recon`
and installs the launcher at `/usr/local/bin/netra-recon`. It requires `sudo`:

```bash
chmod +x install.sh
sudo ./install.sh
```

This does not install Python packages into the operating system's managed
interpreter. To remove this installation, run `sudo netra-recon uninstall` and
confirm the prompt.

### Docker

Build and launch the container from the repository root:

```bash
docker build -t netra-recon:latest .
docker run --rm -it \
  -v "$(pwd)/results:/app/results" \
  netra-recon:latest
```

The container runs as a non-root user. Add other mounts only when you need them.
Docker Compose is also available:

```bash
docker compose up --build
```

## Quick start

Start the CLI and explore its built-in help:

```text
netra-recon> help
netra-recon> modules
netra-recon> search dns
netra-recon> searchre ^Domain
```

Select a module, set an authorized target, then run it:

```text
netra-recon> use 5
netra-recon> set target example.com
netra-recon> opts
netra-recon> run
```

The module ID is catalog-dependent; verify it with `modules` or `search` before
using it. `helpmod <id|name>` shows a module's purpose and options.

### Domain Info example

The Domain Info module performs DNS queries, requests RDAP registration data,
and retrieves basic IP metadata for discovered addresses:

```text
netra-recon> use Domain Info
netra-recon> set target example.com
netra-recon> run
```

It can also be run directly without opening the interactive CLI:

```bash
python -m netra_recon.modules.domain_info example.com 4 '{"timeout":10}'
```

The optional positional values are the maximum concurrent IP lookups and a JSON
object of module options. The timeout must be between 1 and 120 seconds.
Domain Info writes `domain_info.txt` and `domain_info.json` under
`results/<domain>/` when exports are enabled. The IP metadata lookup uses the
external `ip-api.com` service; its availability and returned data are subject
to that service's terms and limits.

## Common CLI commands

| Command | Purpose | Example |
| --- | --- | --- |
| `modules [infra\|web\|sec]` | Browse the module catalog | `modules web -d` |
| `search <keyword>` | Search module names and descriptions | `search dns` |
| `searchre <pattern>` | Search module names with a regular expression | `searchre ^DNS` |
| `use <id\|name>` | Select a module | `use Domain Info` |
| `helpmod <id\|name>` | Show module documentation | `helpmod 5` |
| `set target <value>` | Set the current target | `set target example.com` |
| `set threads <number>` | Set worker count where supported | `set threads 4` |
| `opts` | Show current options | `opts` |
| `profile safe\|speed\|deep` | Apply a preset | `profile safe` |
| `run` | Run the selected module | `run` |
| `runall <infrastructure\|web\|security>` | Run a category | `runall web` |
| `fav add\|del\|list` | Manage favorite modules | `fav add 5` |
| `show api_status` | Show provider-key availability | `show api_status` |
| `viewout` | Review cached output from the latest run | `viewout` |
| `exit` | Close the CLI | `exit` |

For command-specific syntax, use `help <command>` inside the CLI.

## Configuration and API credentials

Modules that integrate with external providers may require API credentials.
Configure only the keys needed for the modules you intend to use, preferably
through environment variables:

```bash
export VIRUSTOTAL_API_KEY="..."
export SHODAN_API_KEY="..."
export CENSYS_API_ID="..."
export CENSYS_API_SECRET="..."
export GOOGLE_API_KEY="..."
export HIBP_API_KEY="..."
```

Do not commit credentials to the repository or include them in screenshots,
logs, or bug reports. Use `show api_status` to review whether supported keys
are present.

Project defaults, export settings, and request headers are defined in
[`netra_recon/config/settings.py`](./netra_recon/config/settings.py). Review
module-specific options with `helpmod` before changing defaults.

## Reports and output

Results are written beneath the configured results directory, normally
`results/`. Many modules produce text reports; CSV export is available where
configured. Domain Info additionally produces a JSON document containing the
query timestamp, DNS answers, RDAP details, IP metadata, elapsed time, and
lookup warnings.

Treat results as potentially sensitive: reconnaissance may reveal internal
names, infrastructure, contact details, or security configuration. Protect
output files and remove them when they are no longer needed.

## Development

Install the project and development tools in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run the focused Domain Info tests:

```bash
python -m pytest -q tests/test_domain_info.py
```

Build a distribution (with the `build` development extra installed):

```bash
python -m build
```

## Responsible use

You are responsible for ensuring that you have explicit authorization before
running Netra Recon modules against a target. Respect rate limits, applicable
laws, provider terms, and the target's engagement scope. Prefer passive lookup
modules when active testing is not authorized. This project is provided
without a guarantee that every module or external data source is accurate or
available.

## Contributing and support

Bug reports should include the operating system, Python version, installation
method, the exact command (with secrets removed), and relevant error output.
For security-sensitive reports, use a private reporting channel where one is
available instead of publishing exploit details.
