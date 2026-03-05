# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project: arch-audit

Professional system audit tool for Arch Linux with comprehensive analysis across 8 domains:
- **Packages**: orphans, cache, AUR, updates, broken dependencies
- **Services**: failed services, disabled services, service errors
- **Security**: open ports, firewall status, SUID files, users with shell access
- **Disk**: usage per mount, large log files, journal size, /tmp usage
- **Performance**: memory usage, swap, top processes, load average
- **Logs**: critical errors, error messages, warnings from journalctl
- **Boot/Kernel**: kernel version, boot time, dmesg errors, failed units
- **Config**: important configs, system info (hostname, uptime, architecture)

Generates structured reports with Executive Summary / Critical / High / Medium / Low findings.

## Running the Tool

```bash
# Launch interactive menu (default)
./run.sh

# CLI Commands
./run.sh --history           # List recent audits (max 5)
./run.sh --stats             # Show statistics and trends
./run.sh --diff              # Compare current with previous audit
./run.sh --auto-fix          # Interactive auto-fix mode
./run.sh --preview           # Preview fixes without executing
./run.sh --export csv|md|json # Export latest report
./run.sh --config            # Show configuration
./run.sh --create-config     # Create default config
./run.sh --help              # Show all options
```

### Interactive Menu

When launched without arguments (`./run.sh`), displays interactive menu:
```
┌─────┬────────────────────────┬──────────────────────────────────────────┐
│ Key │       Command          │              Description                 │
├─────┼────────────────────────┼──────────────────────────────────────────┤
│  1  │ Audit System           │ Run full system audit with TUI viewer    │
│  2  │ View History           │ List recent audits from history          │
│  3  │ Show Statistics        │ View audit trends and statistics         │
│  4  │ Compare Audits         │ Compare current with previous audit      │
│  5  │ Preview Fixes          │ Preview auto-fix commands                │
│  6  │ Auto-Fix Mode          │ Interactive auto-fix with confirmation   │
│  7  │ Export Report          │ Export latest report (CSV/MD/JSON)       │
│  8  │ Configuration          │ View or create configuration             │
│  Q  │ Quit                   │ Exit the program                         │
└─────┴────────────────────────┴──────────────────────────────────────────┘
```

**Audit Output:**
1. Analyzes system across 8 domains
2. Generates JSON report (`report_*.json`)
3. Generates HTML report (`report_*.html`)
4. Saves to history (`~/.local/share/arch-audit/history/`)
5. Auto-cleans old audits (keeps max 5)
6. Launches interactive TUI for browsing findings

**TUI Navigation:**
- Main menu: Select severity level [1-4] or view reports [5]
- Category view: Browse findings by number or [n]ext/[p]rev
- Detail view: Full finding analysis with solution, impact, rollback
- [q] to quit any view

## Architecture (Current)

### Module Structure

```
arch_audit/
├── main.py           # Entry point: CLI + menu + orchestration
├── menu.py           # Interactive command menu
├── config.py         # Configuration management
├── history.py        # Audit history & persistence
├── autofix.py        # Auto-fix interactive mode
├── export.py         # Export formats: CSV/MD/JSON
├── collector.py      # System data collector (8 domains)
├── analyzer.py       # Audit engine (Finding dataclass + Analyzer)
├── report.py         # Report generation (JSON + HTML)
├── tui.py            # Interactive TUI with ModernTUI class
├── constants.py      # Global configuration values (v2.1)
└── arch_api.py       # Official Arch Linux API client
```

### Features (v2.1)

**Core Features (v2.0):**
- **menu.py**: Interactive command menu with TUI table display
- **config.py**: Load/save configuration from `~/.config/arch-audit/config.yaml`
- **history.py**: Persistent audit database in `~/.local/share/arch-audit/history/`
- **autofix.py**: Interactive auto-fix with preview + confirmation
- **export.py**: Multi-format export (CSV, Markdown, JSON)

**Security & Quality Improvements (v2.1):**
- **constants.py**: Centralized configuration values
  - All magic numbers in one place
  - Thresholds, timeouts, limits defined globally
  - Easy to customize and maintain
- **Security Hardening**:
  - Safe subprocess execution: `shlex.split()` instead of `shell=True`
  - Path traversal protection: `validate_output_path()` in export.py
  - Input validation for Finding objects
  - Specific exception handling (not broad Exception catches)
- **Performance**:
  - Fixed N+1 problem in `_get_large_logs()` (1 cmd instead of 50+)
  - Optimized command execution
- **Logging**:
  - Global logging setup in main.py (stderr + file)
  - Error tracking in all modules
  - Corrupted file handling with warnings
  - Command failures logged with context
- **Code Quality**:
  - Python 3.8+ compatibility (type hints fixed)
  - Recursion depth limits to prevent infinite loops
  - Consistent error handling patterns

### Data Pipeline

1. **Collector** (`collector.py`)
   - `collect()` returns dict with 8 domain keys
   - Each domain has specialized methods (e.g., `_get_orphans()`, `_get_disk_usage()`)
   - All system calls wrapped with error handling + timeouts

2. **Finding Model** (`analyzer.py` - dataclass)
   ```python
   @dataclass
   class Finding:
       name: str                # unique ID
       category: str           # packages|services|security|disk|performance|logs|boot|config
       severity: str           # critical|high|medium|low
       title: str              # short title
       description: str        # what it is
       problem: str            # why it's an issue
       solution: str           # exact command(s)
       impact: str             # consequence if unaddressed
       rollback: str           # how to undo
       evidence: str = ""      # what we found
   ```

3. **Analyzer** (`analyzer.py`)
   - `analyze()` → runs all 8 audit methods
   - Returns dict with: critical/high/medium/low findings, executive_summary, maintenance_commands, preventive_measures
   - Each finding has complete severity assessment

4. **Report Generation** (`report.py`)
   - `Report.save()` → writes JSON and HTML
   - JSON: structured data for automation
   - HTML: beautiful formatted report with CSS styling

5. **ModernTUI** (`tui.py`)
   - Menu-driven navigation with numbered selections
   - Shows findings grouped by severity
   - Full detail view with description/problem/solution/impact/rollback

### Key Design Principles

- **Comprehensive audit**: 8 independent audit domains cover system health
- **Severity-based organization**: Critical/High/Medium/Low for quick prioritization
- **Pure stdlib**: No external dependencies (only subprocess + built-in modules)
- **Structured findings**: Dataclass ensures consistent Finding format
- **Export formats**: JSON for automation, HTML for stakeholders
- **Professional reports**: Executive summary + detailed findings + maintenance commands
- **Simple navigation**: Number-based menu, [n]/[p] for pagination

## Data & Configuration

### File Locations

```
~/.config/arch-audit/config.yaml          # User configuration (create with --create-config)
~/.local/share/arch-audit/history/        # Persistent audit history (max 5 audits)
./reports/                                # Generated reports (auto-cleaned, gitignored)
```

### Configuration (config.yaml)

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
  skip: []                              # Domains to skip

thresholds:
  cache_size_mb: 100                    # Alert if cache > 100MB
  disk_percent: 85                      # Alert if disk > 85%
  large_logs_mb: 50                     # Alert if logs > 50MB
  memory_percent: 75                    # Alert if RAM > 75%
  open_ports_max: 5                     # Alert if > 5 ports open

actions:
  safe:                                 # Auto-fix safe actions
    - orphan_packages
    - old_cached_packages
    - large_log_files
  preview_only:                         # Preview-only actions
    - failed_services
    - critical_errors_in_logs
```

### History Management

- Audits saved as JSON: `audit_YYYY-MM-DD_HHMMSS.json`
- Auto-cleanup after each audit keeps only last 5
- Compare reports: `history.compare_reports(0, 1)` (0=latest, 1=previous)
- Statistics: `history.get_stats()` (trends across all audits)

### JSON Serialization

- All Finding objects converted to dicts before saving (method: `_make_serializable()`)
- Handles nested lists/dicts recursively
- Corrupted files skipped gracefully (error handling in list_reports, get_latest, get_stats)

## Development Notes

### Design Principles
- **Smart detection**: Only alerts on actionable issues (not raw size metrics)
- **Finding model**: Dataclass with severity (critical/high/medium/low)
- **Pure stdlib**: No external dependencies beyond standard library
- **Reversible**: Every fix includes rollback instructions
- **User control**: Interactive menus, no automatic execution without confirmation

### Implementation Details
- **Safe execution**: `shlex.split()` for all subprocess calls (prevents injection)
- **Path security**: All file paths validated before write operations
- **Timeouts**: All system calls have configurable timeouts
  - Collector: 15 seconds per command
  - Auto-fix: 300 seconds per fix operation
- **Error handling**:
  - Specific exception catching (OSError, ValueError, etc.)
  - Corrupted files skipped gracefully
  - All errors logged for debugging
- **Configuration**: Centralized constants (constants.py)
  - All thresholds configurable
  - Magic numbers eliminated
  - Easy to customize behavior
- **Menu system**: Interactive TUI for command selection (MenuTUI class)
- **CLI arguments**: Full argparse support for scripting
- **Logging**: File + stderr logging for operational visibility
- **Version**: v2.1 (security hardening, performance optimizations)

### Constants (constants.py)
All configurable values defined in one place:
- Timeouts: COLLECTOR_COMMAND_TIMEOUT, AUTOFIX_COMMAND_TIMEOUT
- Thresholds: Disk, memory, ports, cache, logs, etc.
- Limits: Max files, max history, max displays
- Paths: Standard Arch Linux paths (pacman cache, logs, tmp, etc.)
- Recursion: MAX_CONFIG_NESTING_DEPTH (prevents infinite loops)

When modifying behavior, check constants.py first.
