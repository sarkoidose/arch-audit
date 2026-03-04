```
╔════════════════════════════════════════════════════════════════╗
║                   🔍 ARCH-AUDIT 🔍                             ║
║           Professional System Audit Tool for Arch Linux        ║
║                                                                ║
║             Smart Detection • 8-Domain Analysis                ║
║          Interactive Reports • Automated Cleanup               ║
╚════════════════════════════════════════════════════════════════╝
```

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Arch Linux](https://img.shields.io/badge/Target-Arch%20Linux-1793D1?logo=archlinux)](https://archlinux.org)

**A professional, intelligent system auditor that identifies real cleanup candidates, not false positives.**

</div>

---

## 🎯 Overview

`arch-audit` is a comprehensive system analysis tool for Arch Linux that audits 8 critical domains and intelligently detects what can be safely optimized.

Unlike naive size-based checks, arch-audit analyzes:
- **What's really old** (vs. what's still in use)
- **What's actually orphaned** (not required by anything)
- **What's truly problematic** (not just large)

## ✨ Features

### 📊 **8 Audit Domains**
- **Packages**: orphans, old cache versions, AUR packages, available updates, broken dependencies
- **Services**: failed services, disabled services, service errors
- **Security**: open ports, firewall status, SUID files, shell users
- **Disk**: usage per mount, large logs, journal size, /tmp usage
- **Performance**: memory usage, swap, top processes, load average
- **Logs**: critical errors, error messages, warnings
- **Boot/Kernel**: kernel version, boot time, dmesg errors, failed units
- **Config**: important configs, system info

### 🧠 **Smart Detection**
- Identifies **real cleanup candidates** (orphans, old package versions)
- Ignores **false positives** (large cache of current packages)
- **Actionable findings** with exact commands to fix issues
- **Impact assessment** for each problem

### 📈 **Interactive Interface**
- Modern TUI for navigating findings by severity
- Automatic HTML report generation
- JSON export for automation
- Browser-based report viewer

### 🧹 **Auto-Maintenance**
- Automatic cleanup of old reports
- Keeps only 5 latest report pairs
- Organized `reports/` directory

## 🚀 Quick Start

### Installation

```bash
# Clone into your local GitHub directory
cd ~/GitHub/configs
git clone https://github.com/sarkoidose/arch-audit.git
cd arch-audit
```

### Usage

```bash
./run.sh
```

**What it does:**
1. Cleans old reports (keeps 5 latest)
2. Analyzes your entire system (30-60 seconds)
3. Displays interactive findings browser
4. Generates HTML and JSON reports

### Navigate Reports

In the TUI:
- `[1-4]` - View findings by severity (Critical, High, Medium, Low)
- `[5]` - Open full HTML report in browser
- `[n]` / `[p]` - Next/Previous finding
- `[back]` - Return to list
- `[q]` - Quit

## 📊 Sample Output

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

## 📁 Project Structure

```
arch-audit/
├── arch_audit/              # Python source code
│   ├── collector.py         # System data collection
│   ├── analyzer.py          # Finding analysis & severity
│   ├── report.py            # HTML/JSON report generation
│   ├── tui.py               # Interactive terminal UI
│   └── ...
├── reports/                 # Generated reports (gitignored)
├── run.sh                   # Main launcher
├── cleanup.sh               # Auto-cleanup script
├── CLAUDE.md                # Claude Code instructions
└── README.md                # This file
```

## 🔧 How It Works

### 1. **Collection Phase** (collector.py)
- Gathers system data across 8 domains
- Runs standard Arch Linux commands (`pacman`, `systemctl`, `journalctl`, etc.)
- Parses output for analysis

### 2. **Analysis Phase** (analyzer.py)
- Evaluates each metric against intelligent thresholds
- **Key insight**: Only alerts on actionable issues
  - Old packages (not just large cache)
  - Orphan packages (not all packages)
  - Critical errors from last 7 days

### 3. **Reporting Phase** (report.py)
- Generates professional HTML report
- Exports raw data as JSON
- Provides maintenance recommendations

### 4. **Interactive Phase** (tui.py)
- Browse findings by severity
- Get exact fix commands
- Open detailed HTML report

## 🎓 Design Principles

- **Smart over Simple**: Analyze, don't just measure
- **Actionable over Alarming**: Real problems, not false positives
- **Clear over Clever**: Easy to understand findings
- **Reversible over Risky**: Show how to undo changes

## 📋 Requirements

- **OS**: Arch Linux
- **Python**: 3.10 or later
- **Tools**: Standard Arch utils (pacman, systemctl, journalctl, etc.)

## 📜 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Found an issue? Have a suggestion?
- Open an issue on [GitHub](https://github.com/sarkoidose/arch-audit/issues)
- Submit a PR with improvements

---

<div align="center">

**Made with ❤️ for Arch Linux users**

[GitHub](https://github.com/sarkoidose/arch-audit) • [Issues](https://github.com/sarkoidose/arch-audit/issues)

</div>
