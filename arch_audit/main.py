#!/usr/bin/env python3
"""ARCH-AUDIT - Professional system audit tool."""

import sys
import os
import glob
from .collector import Collector
from .analyzer import Analyzer
from .report import Report
from .tui import ModernTUI


def main():
    print("\n🔍 Analyzing system...\n")

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
    import os
    os.makedirs("reports", exist_ok=True)
    json_path, html_path = Report.save(report_data, directory="reports")

    print(f"\n✓ Reports generated:")
    print(f"  JSON: {json_path}")
    print(f"  HTML: {html_path}\n")

    # Cleanup old reports - keep only last 5
    import glob
    all_reports = sorted(glob.glob("reports/report_*.html")) + sorted(glob.glob("reports/report_*.json"))
    if len(all_reports) > 10:  # 5 HTML + 5 JSON pairs
        to_delete = all_reports[:-10]
        for old_report in to_delete:
            try:
                os.remove(old_report)
            except Exception:
                pass

    # Step 4: Start TUI
    print("📊 Starting interactive report viewer...\n")
    tui = ModernTUI(report_data)
    tui.run()

    print("\n✓ Thank you for using ARCH-AUDIT\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
