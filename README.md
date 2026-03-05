```
 _____ ____  ____ _   _   ___   _   _ _____ ___ _____
|_   _|  _ \/ ___| | | | / _ \ | | | |_   _|_ _|_   _|
  | | | |_) \___ \ |_| || | | || | | | | |  | |  | |
  | | |  _ < ___) |  _  || |_| || |_| | | |  | |  | |
  |_| |_| \_\____/|_| |_| \__\_\ \___/  |_| |___|  |_|

Professional system audit tool for Arch Linux
```

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Arch Linux](https://img.shields.io/badge/Target-Arch%20Linux-1793D1)](https://archlinux.org)

Analyzes system health across 8 domains and identifies actionable issues with exact solutions.

---

## Overview

arch-audit audits your Arch Linux system to identify real problems—not false positives. It distinguishes between:

- **Large cache** vs **old packages to clean**
- **All packages** vs **orphaned dependencies**
- **System activity** vs **genuine errors**

Each finding includes the exact command to fix it, impact assessment, and how to undo changes.

---

## Features

### Audit Domains

- **Packages**: Orphaned packages, old cache versions, AUR packages, pending updates, broken dependencies
- **Services**: Failed services, disabled services, recent service errors
- **Security**: Open ports, firewall status, SUID files, users with shell access
- **Disk**: Disk usage per mount point, large log files, journal size, /tmp usage
- **Performance**: Memory usage, swap configuration, top processes, load average
- **Logs**: Critical errors, error messages, warnings from past 24 hours
- **Boot/Kernel**: Kernel version, boot time, kernel errors, failed systemd units
- **Configuration**: Important config file status, system info (hostname, uptime, architecture)

### Capabilities

- Intelligent detection: Only alerts on actionable issues
- Customizable thresholds via configuration file
- Interactive CLI with TUI navigation
- Auto-fix mode for safe operations (preview before executing)
- Export to CSV, Markdown, JSON formats
- Audit history with comparison and trend analysis
- Persistent database of past audits

### Reports

- HTML reports (browser-viewable)
- CSV exports (spreadsheet analysis)
- Markdown reports (documentation)
- JSON exports (automation/scripting)

---

## Installation

### Quick Start

```bash
cd ~/GitHub/configs
git clone https://github.com/sarkoidose/arch-audit.git
cd arch-audit
```

### Requirements

- Arch Linux (with pacman)
- Python 3.8 or later
- Standard tools: pacman, systemctl, journalctl (included with Arch)

---

## Usage

### Basic Commands

Run interactive audit:
```bash
./run.sh
```

Show all options:
```bash
./run.sh --help
```

### Configuration

Create default configuration:
```bash
./run.sh --create-config
```

This creates `~/.config/arch-audit/config.yaml` with customizable thresholds:

```yaml
audit:
  domains:
    - packages
    - services
    - security
    - disk
    - performance
    - logs
    - boot
    - config
  skip: []  # List domains to skip

thresholds:
  cache_size_mb: 100
  open_ports_max: 5
  memory_percent: 75
  disk_percent: 85

actions:
  safe:              # Will be run by --auto-fix
    - orphan_packages
    - old_cached_packages
    - large_log_files
```

View current configuration:
```bash
./run.sh --config
```

### Auto-Fix Mode

Preview what would be fixed without executing:
```bash
./run.sh --preview
```

Interactive mode to select and fix issues:
```bash
./run.sh --auto-fix
```

### Export Reports

Export latest audit in different formats:
```bash
./run.sh --export csv       # Spreadsheet format
./run.sh --export md        # Markdown documentation
./run.sh --export json      # JSON for scripting
```

### History and Comparisons

List recent audits:
```bash
./run.sh --history
```

Compare current audit with previous one:
```bash
./run.sh --diff
```

Show trends across audit history:
```bash
./run.sh --stats
```

Audits are stored in `~/.local/share/arch-audit/history/`

---

## How It Works

### Data Collection

The collector runs standard Arch Linux commands (pacman, systemctl, journalctl) to gather system data across 8 domains. Each command has a 15-second timeout to prevent hangs.

### Analysis

The analyzer evaluates metrics against intelligent thresholds:
- Identifies real cleanup candidates (old packages, orphans)
- Ignores false positives (current packages in cache)
- Generates findings with severity levels (critical, high, medium, low)

### Configuration

User can customize audit domains, thresholds, and safe actions via config file. Defaults are reasonable for most systems.

### History

Past audits are saved to a persistent database. Compare reports to track improvements or regressions over time.

### Auto-Fix

Safe fixes can be selected and previewed before execution. Each fix includes rollback instructions.

### Export

Reports can be generated in multiple formats for analysis, documentation, or automation.

---

## Project Structure

```
arch-audit/
├── arch_audit/
│   ├── main.py          CLI entry point and orchestration
│   ├── collector.py     System data collection
│   ├── analyzer.py      Finding analysis and severity
│   ├── config.py        Configuration management
│   ├── history.py       Audit history and comparisons
│   ├── autofix.py       Interactive auto-fix mode
│   ├── export.py        Export to CSV, Markdown, JSON
│   ├── report.py        HTML report generation
│   ├── tui.py           Terminal user interface
│   ├── constants.py     Global configuration values
│   └── arch_api.py      Arch Linux API integration
├── run.sh               Main launcher script
├── cleanup.sh           Cleanup old reports
├── CLAUDE.md            Development notes
└── README.md            This file
```

---

## Commands Reference

| Command | Purpose |
|---------|---------|
| `./run.sh` | Run audit with interactive menu |
| `./run.sh --auto-fix` | Interactive fix mode with confirmation |
| `./run.sh --preview` | Show fixes without executing them |
| `./run.sh --export csv\|md\|json` | Export latest report |
| `./run.sh --diff` | Compare current with previous audit |
| `./run.sh --stats` | Show trends across audit history |
| `./run.sh --history` | List recent audits |
| `./run.sh --config` | Show current configuration |
| `./run.sh --create-config` | Create default config file |

---

## Sample Output

```
System Audit Report - 10 findings

  CRITICAL:  1 issue(s)
  HIGH:      2 issue(s)
  MEDIUM:    4 issue(s)
  LOW:       3 issue(s)

Each finding includes:
  - Description of the issue
  - Why it matters
  - Exact command to fix it
  - Impact if not addressed
  - How to undo the fix
```

---

## Security

Recent improvements (v2.1):
- Safe command execution: no shell interpretation
- Path traversal protection in exports
- Input validation and error handling
- Specific exception catching (not broad catches)
- Comprehensive logging for debugging

---

## Requirements

- OS: Arch Linux
- Python: 3.8 or later
- Pacman, systemctl, journalctl (standard on Arch)

---

## License

MIT License

---

## Contributing

Found an issue? Have a suggestion?

- Report bugs: [GitHub Issues](https://github.com/sarkoidose/arch-audit/issues)
- Submit improvements: [GitHub Pull Requests](https://github.com/sarkoidose/arch-audit)
