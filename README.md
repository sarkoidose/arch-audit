```
╔════════════════════════════════════════════════════════════════╗
║                        ARCH-AUDIT                              ║
║           Professional System Audit Tool for Arch Linux        ║
╚════════════════════════════════════════════════════════════════╝
```

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Arch Linux](https://img.shields.io/badge/Target-Arch%20Linux-1793D1?logo=archlinux)](https://archlinux.org)

**Smart system auditor that identifies real cleanup candidates, not false positives**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Examples](#-examples) • [Architecture](#-architecture)

</div>

---

## 🎯 Overview

`arch-audit` is a **professional, intelligent system auditor** for Arch Linux. It audits 8 critical domains and identifies what can be safely optimized — without the noise of naive size-based checks.

**Key Insight:** Bigger ≠ Worse. arch-audit analyzes:
- **What's really old** (not just large)
- **What's actually orphaned** (not used)
- **What's truly problematic** (actionable)

---

## ✨ Features

### 📊 **8 Audit Domains**
- **Packages**: orphans, old cache versions, AUR packages, updates, broken deps
- **Services**: failed, disabled, error states
- **Security**: open ports, firewall, SUID files, shell users
- **Disk**: usage per mount, large logs, journal size, /tmp
- **Performance**: memory, swap, top processes, load average
- **Logs**: critical errors, error messages, warnings
- **Boot/Kernel**: version, boot time, dmesg errors, failed units
- **Config**: configs, system info (hostname, uptime, arch)

### 🧠 **Smart Detection**
- Identifies **real cleanup candidates** (orphans, old packages, logs)
- Ignores **false positives** (current packages in cache)
- **Actionable findings** with exact commands
- **Impact assessment** for each issue
- **Customizable thresholds** via config file

### 🔧 **Full-Featured CLI**
- **Interactive mode** with TUI browser
- **Auto-fix mode** for safe issues
- **Export formats**: CSV, Markdown, JSON
- **History tracking** with comparisons
- **Configuration system** for customization
- **Trend analysis** across audits

### 📈 **Report Generation**
- Beautiful **HTML reports** (browser-friendly)
- **CSV exports** (spreadsheet analysis)
- **Markdown reports** (documentation)
- **JSON exports** (automation & scripting)

### 📊 **History & Trends**
- Persistent audit history database
- Compare audits over time
- Track improvements/regressions
- Trend statistics (cache growth, errors, etc.)

---

## 🚀 Installation

### Quick Start

```bash
# Clone into your GitHub directory
cd ~/GitHub/configs
git clone https://github.com/sarkoidose/arch-audit.git
cd arch-audit
```

### Requirements

- **Arch Linux** (with pacman)
- **Python 3.10+**
- Standard tools: `pacman`, `systemctl`, `journalctl`, etc.

---

## 📖 Usage

### Basic Commands

```bash
# Run interactive audit with TUI
./run.sh

# Show help
./run.sh --help
```

### Configuration

```bash
# Show current configuration
./run.sh --config

# Create default config file
./run.sh --create-config
```

Then edit: `~/.config/arch-audit/config.yaml`

```yaml
audit:
  domains:
    - packages
    - services
    # Skip any domains you want to ignore
  skip: []

thresholds:
  cache_size_mb: 100        # Alert if cache > 100MB
  open_ports_max: 5         # Alert if > 5 ports open
  memory_percent: 75        # Alert if RAM > 75%

actions:
  safe:                     # Safe to auto-fix
    - orphan_packages
    - old_cached_packages
    - large_log_files
```

### Auto-Fix Mode

```bash
# Interactive auto-fix menu
./run.sh --auto-fix

# Preview commands before executing
./run.sh --preview
```

**Features:**
- Review all fixable issues
- Pick which ones to fix
- See exact commands before running
- Automatic rollback info

### Export Reports

```bash
# Export as CSV (spreadsheet)
./run.sh --export csv

# Export as Markdown (documentation)
./run.sh --export md

# Export as JSON (scripting/automation)
./run.sh --export json
```

### History & Comparisons

```bash
# List recent audits
./run.sh --history

# Compare current audit with previous
./run.sh --diff

# Show statistics and trends
./run.sh --stats
```

**History Storage:** `~/.local/share/arch-audit/history/`

---

## 🎓 Examples

### Example 1: Routine Audit

```bash
# Run full audit
$ ./run.sh

# In TUI:
# [1] View CRITICAL issues
# [2] View HIGH issues
# [5] Open HTML report in browser
# [q] Quit
```

### Example 2: Auto-Fix Workflow

```bash
# Preview what would be fixed
$ ./run.sh --preview

# See output:
# 📋 Fixable Issues (Preview Mode)
# 1. 4 orphan packages
#    Command: sudo pacman -Rns $(pacman -Qdtq)
# 2. 1 old package versions in cache
#    Command: sudo paccache -rk1
# 3. 4 large log files
#    Command: sudo journalctl --vacuum=30d

# Execute fixes interactively
$ ./run.sh --auto-fix

# Menu:
# [a] Fix all safe issues
# [p] Preview commands
# [s] Select specific issues
# [q] Cancel
```

### Example 3: Export for Analysis

```bash
# Export as CSV for spreadsheet analysis
$ ./run.sh --export csv
✅ CSV: report_2026-03-04_195436.csv

# Open in your favorite tool
$ libreoffice report_*.csv

# Or export as Markdown for documentation
$ ./run.sh --export md
✅ Markdown: report_2026-03-04_195436.md
```

### Example 4: Track Improvements

```bash
# Run first audit
$ ./run.sh
[TUI opens]

# Run second audit (after fixes)
$ ./run.sh

# Compare results
$ ./run.sh --diff

# Output:
# 📊 Audit Comparison
# Report 1: 2026-03-04_194656
# Report 2: 2026-03-04_195436
#
# Changes:
#   CRITICAL:  ↓ -1
#   HIGH:      → 0
#   MEDIUM:    ↓ -2
#   LOW:       → 0

# View full trends
$ ./run.sh --stats

# Output:
# 📊 Audit History Statistics
# Total audits: 5
# Date range: 2026-03-04_194342 to 2026-03-04_195436
#
# Trends (last 5 audits):
#   CRITICAL: 2 → 1 → 1 → 1 → 0
#   HIGH:     4 → 4 → 2 → 2 → 2
#   MEDIUM:   6 → 6 → 4 → 4 → 3
#   LOW:      3 → 3 → 3 → 3 → 3
```

---

## 🔧 How It Works

### 1. **Collection Phase** (`collector.py`)
- Runs standard Arch Linux commands (`pacman`, `systemctl`, `journalctl`)
- Gathers data across 8 domains
- Parses output for analysis

### 2. **Analysis Phase** (`analyzer.py`)
- Evaluates metrics against **intelligent thresholds**
- Key insight: Only alerts on **actionable issues**
  - Old packages ≠ large cache
  - Orphans ≠ all packages
  - Recent errors ≠ noise

### 3. **Configuration Phase** (`config.py`)
- Load custom settings from `~/.config/arch-audit/config.yaml`
- Customize thresholds, skip domains, define "safe" actions
- Fallback to sensible defaults

### 4. **History Phase** (`history.py`)
- Store reports in `~/.local/share/arch-audit/history/`
- Compare audits over time
- Track trends and improvements

### 5. **Auto-Fix Phase** (`autofix.py`)
- Interactive menu for fixing issues
- Preview mode (show commands, don't execute)
- Mark actions as "safe" vs "risky"

### 6. **Export Phase** (`export.py`)
- Generate CSV, Markdown, JSON reports
- Compatible with spreadsheets and documentation tools

### 7. **Reporting Phase** (`report.py`)
- Create professional HTML reports
- Interactive browser viewer
- Full finding details with solutions

---

## 📁 Project Structure

```
arch-audit/
├── arch_audit/              # Python source code
│   ├── collector.py         # System data collection
│   ├── analyzer.py          # Finding analysis & severity
│   ├── config.py            # Configuration management
│   ├── history.py           # Audit history & comparisons
│   ├── autofix.py           # Interactive auto-fix mode
│   ├── export.py            # Export formats (CSV, MD, JSON)
│   ├── report.py            # HTML report generation
│   ├── tui.py               # Interactive terminal UI
│   └── main.py              # CLI & orchestration
├── reports/                 # Generated reports (gitignored)
├── run.sh                   # Main launcher
├── cleanup.sh               # Old report cleanup
├── CLAUDE.md                # Claude Code instructions
└── README.md                # This file
```

---

## 🎓 Design Principles

- **Smart over Simple**: Analyze, don't just measure
- **Actionable over Alarming**: Real problems, not false positives
- **Clear over Clever**: Easy to understand findings
- **Reversible over Risky**: Always show how to undo
- **Manual over Automatic**: User controls execution
- **Customizable over Opinionated**: Configure your thresholds

---

## 📊 Sample Report Output

```
System Audit Report - 10 findings

  🔴 CRITICAL:  1 issue(s) - require immediate action
  🟠 HIGH:      2 issue(s) - address soon
  🟡 MEDIUM:    4 issue(s) - plan resolution
  🟢 LOW:       3 issue(s) - monitor

Critical Issues:
  • 20 critical log entries
```

Each finding includes:
- **Description**: What this is
- **Problem**: Why it matters
- **Solution**: Exact command to fix
- **Impact**: What happens if ignored
- **Undo**: How to revert changes

---

## 🛠️ Commands Reference

| Command | Purpose |
|---------|---------|
| `./run.sh` | Run audit with TUI |
| `./run.sh --auto-fix` | Interactive auto-fix mode |
| `./run.sh --preview` | Preview fixes without executing |
| `./run.sh --export csv\|md\|json` | Export report in format |
| `./run.sh --diff` | Compare with previous audit |
| `./run.sh --stats` | Show history and trends |
| `./run.sh --history` | List recent audits |
| `./run.sh --config` | Show current configuration |
| `./run.sh --create-config` | Create default config file |
| `./run.sh --help` | Show all options |

---

## 📋 Requirements

- **OS**: Arch Linux
- **Python**: 3.10 or later
- **Tools**: pacman, systemctl, journalctl (standard on Arch)

---

## 📜 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Found a bug? Have an idea?
- Open an issue on [GitHub](https://github.com/sarkoidose/arch-audit/issues)
- Submit a pull request
- Share feedback and feature requests

---

<div align="center">

**Made with ❤️ for Arch Linux users**

[GitHub](https://github.com/sarkoidose/arch-audit) • [Issues](https://github.com/sarkoidose/arch-audit/issues)

</div>
