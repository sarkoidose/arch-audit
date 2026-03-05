#!/usr/bin/env python3
"""ARCH-AUDIT - Professional system audit tool."""

import sys
import os
import glob
import argparse
import logging
from pathlib import Path
from .collector import Collector
from .analyzer import Analyzer
from .report import Report
from .tui import ModernTUI
from .config import Config
from .history import History
from .autofix import AutoFix
from .export import Exporter
from .menu import MenuTUI

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path.home() / ".local" / "share" / "arch-audit" / "audit.log"),
        logging.StreamHandler(sys.stderr),
    ]
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Professional system audit tool for Arch Linux",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    Run audit and show TUI
  %(prog)s --auto-fix         Interactive auto-fix mode
  %(prog)s --preview          Preview fixes without executing
  %(prog)s --export csv       Export latest report as CSV
  %(prog)s --diff             Compare with previous audit
  %(prog)s --stats            Show audit history trends
  %(prog)s --config           Show current configuration
  %(prog)s --create-config    Create default config file
        """,
    )

    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Interactive auto-fix mode for identified issues",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview auto-fix commands without executing",
    )
    parser.add_argument(
        "--export",
        choices=["json", "csv", "md", "html"],
        help="Export latest report in specified format",
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Compare current audit with previous one",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show audit history statistics and trends",
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="List recent audits from history",
    )
    parser.add_argument(
        "--config",
        action="store_true",
        help="Show current configuration",
    )
    parser.add_argument(
        "--create-config",
        action="store_true",
        help="Create default config file",
    )

    return parser.parse_args()


def run_audit():
    """Run the full audit analysis."""
    print("\n🔍 Analyzing system...\n")

    # Load configuration
    config = Config()
    print(f"  Config: {config.config_path}")
    print(f"  Domains: {', '.join(config.get_domains())}")

    # Step 1: Collect system data
    print("  Collecting system data...")
    collector = Collector()
    data = collector.collect()

    # Step 2: Analyze findings
    print("  Analyzing findings...")
    analyzer = Analyzer(data)
    report_data = analyzer.analyze()

    # Step 3: Save reports
    print("  Saving reports...")
    os.makedirs("reports", exist_ok=True)
    json_path, html_path = Report.save(report_data, directory="reports")

    print(f"\n✓ Reports generated:")
    print(f"  JSON: {json_path}")
    print(f"  HTML: {html_path}\n")

    # Save to history
    history = History()
    history_path = history.save_report(report_data)
    print(f"  History: {history_path}\n")

    # Cleanup old history - keep only last 5
    deleted = history.delete_old_reports(keep=5)
    if deleted > 0:
        print(f"  Cleaned up {deleted} old audit(s)\n")

    # Cleanup old reports - keep only last 10
    all_reports = sorted(glob.glob("reports/report_*.html")) + sorted(
        glob.glob("reports/report_*.json")
    )
    if len(all_reports) > 20:  # 10 HTML + 10 JSON pairs
        to_delete = all_reports[:-20]
        for old_report in to_delete:
            try:
                os.remove(old_report)
            except Exception:
                pass

    return report_data


def main():
    """Main entry point."""
    args = parse_args()

    # Show interactive menu if no arguments provided
    if len(sys.argv) == 1:
        command = MenuTUI.display_menu()
        if command == "quit":
            print("\n✓ Goodbye!\n")
            return
        elif command == "audit":
            args.auto_fix = False
            args.preview = False
            args.export = None
            args.diff = False
            args.stats = False
            args.history = False
            args.config = False
            args.create_config = False
        elif command == "history":
            args.history = True
        elif command == "stats":
            args.stats = True
        elif command == "diff":
            args.diff = True
        elif command == "preview":
            args.preview = True
        elif command == "autofix":
            args.auto_fix = True
        elif command == "export":
            export_format = MenuTUI.handle_export_menu()
            if export_format:
                args.export = export_format
            else:
                return
        elif command == "config":
            args.config = True

    # Handle config commands first (no audit needed)
    if args.config:
        config = Config()
        config.show_config()
        return

    if args.create_config:
        config = Config()
        config.create_default_config()
        return

    if args.history:
        history = History()
        reports = history.list_reports()
        if reports:
            print("\n📜 Recent Audits:\n")
            for r in reports:
                print(f"  [{r['index']}] {r['timestamp']} " +
                      f"(🔴 {r['critical']} 🟠 {r['high']})")
            print()
        else:
            print("\n❌ No audit history found.\n")
        return

    if args.stats:
        history = History()
        stats = history.get_stats()
        if "error" in stats:
            print(f"\n❌ {stats['error']}\n")
        else:
            print("\n📊 Audit History Statistics:\n")
            print(f"Total audits: {stats['total_audits']}")
            print(f"Date range: {stats['date_range']['first']} to {stats['date_range']['last']}")
            print("\nTrends (last 5 audits):")
            for severity in ["critical", "high", "medium", "low"]:
                trend = stats["trends"][severity][-5:]
                counts = [str(t["count"]) for t in trend]
                print(f"  {severity.upper():8}: {' → '.join(counts)}")
            print()
        return

    # Run audit for remaining commands
    report_data = run_audit()

    # Handle diff before other audit commands (uses latest history, not new audit)
    if args.diff:
        history = History()
        comparison = history.compare_reports(0, 1)
        if "error" in comparison:
            print(f"\n❌ {comparison['error']}\n")
        else:
            print("\n📊 Audit Comparison:\n")
            print(f"Report 1: {comparison['report1']['timestamp']}")
            print(f"Report 2: {comparison['report2']['timestamp']}")
            print("\nChanges:")
            for severity, change in comparison["changes"].items():
                symbol = "↑" if change > 0 else "↓" if change < 0 else "→"
                print(f"  {severity.upper():8}: {symbol} {abs(change):+d}")
            print()
        return

    # Handle audit commands
    if args.auto_fix:
        autofix = AutoFix()
        autofix.interactive_fix(report_data.get("all", []))
        autofix.summary()
        return

    if args.preview:
        autofix = AutoFix()
        autofix.preview_fixes(report_data.get("all", []))
        return

    if args.export:
        print(f"📤 Exporting as {args.export.upper()}...\n")
        os.makedirs("reports", exist_ok=True)
        try:
            filepath = Exporter.export_format(report_data, args.export, "reports")
            print(f"✅ Exported: {Path(filepath).name}\n")
        except Exception as e:
            print(f"❌ Export failed: {e}\n")
        return

    # Default: Start TUI
    print("📊 Starting interactive report viewer...\n")
    tui = ModernTUI(report_data)
    tui.run()

    print("\n✓ Thank you for using ARCH-AUDIT\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Program interrupted by user")
        print("\n\nInterrupted by user.\n")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}\n")
        import traceback

        traceback.print_exc()
        sys.exit(1)
