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
./run.sh
# Or directly:
python3 -m arch_audit.main
```

**Output:**
1. Analyzes system across 8 domains
2. Generates JSON report (`report_*.json`)
3. Generates HTML report (`report_*.html`)
4. Launches interactive TUI for browsing findings

**Navigation:**
- Main menu: Select severity level [1-4] or view reports [5]
- Category view: Browse findings by number or [n]ext/[p]rev
- Detail view: Full finding analysis with solution, impact, rollback
- [q] to quit any view

## Architecture (Post-Refactor)

### Module Structure

```
arch_audit/
├── main.py           # Entry point: collect → analyze → save → TUI
├── collector.py      # System data collector (8 domains)
├── analyzer.py       # Audit engine (Finding dataclass + Analyzer)
├── report.py         # Report generation (JSON + HTML)
├── tui.py           # Interactive TUI with ModernTUI class
├── arch_api.py       # Official Arch Linux API client (unchanged)
└── utils.py          # (DEPRECATED - absorbed into collector.py)
```

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

## Development Notes

- `collector.py` replaces `utils.py` with comprehensive data collection
- `Finding` is now a dataclass with `severity` instead of boolean `safe`
- `Analyzer` takes optional `data` parameter (defaults to auto-collect)
- `Report` methods refactored to work with new `report_data` dict structure
- `TUI` renamed from `ProfessionalTUI` to `ModernTUI` (legacy wrapper kept for compatibility)
- All system calls have 15-second timeout with graceful fallbacks
