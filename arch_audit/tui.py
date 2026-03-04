"""Modern TUI using rich library for formatted output."""

import os
import subprocess
from typing import List, Dict, Any
from .analyzer import Finding


class ModernTUI:
    """Modern terminal UI with rich formatting."""

    def __init__(self, report_data: Dict[str, Any]):
        self.report_data = report_data
        self.view = "main"  # "main" | "category" | "finding_detail"
        self.selected_category = None
        self.selected_finding_index = 0

    def run(self):
        """Start TUI."""
        try:
            while self.view != "exit":
                self._clear()
                if self.view == "main":
                    self._show_main()
                elif self.view == "category":
                    self._show_category()
                elif self.view == "finding_detail":
                    self._show_finding_detail()
        except KeyboardInterrupt:
            pass
        finally:
            self._clear()

    # ============ MAIN MENU ============

    def _show_main(self):
        """Show main dashboard."""
        critical = self.report_data.get("critical", [])
        high = self.report_data.get("high", [])
        medium = self.report_data.get("medium", [])
        low = self.report_data.get("low", [])
        executive_summary = self.report_data.get("executive_summary", "")

        print(self._header("ARCH-AUDIT Professional System Analysis"))
        print()

        # Executive Summary
        if executive_summary:
            print(f"📋 EXECUTIVE SUMMARY\n")
            for line in executive_summary.split("\n"):
                print(f"  {line}")
            print()

        # Findings by severity
        print(f"📊 FINDINGS OVERVIEW\n")
        print(f"  🔴 CRITICAL   {len(critical):3d} issue(s) - require immediate action")
        print(f"  🟠 HIGH       {len(high):3d} issue(s) - address soon")
        print(f"  🟡 MEDIUM     {len(medium):3d} issue(s) - plan resolution")
        print(f"  🟢 LOW        {len(low):3d} issue(s) - monitor")
        print()

        # Navigation
        print(f"🎯 SELECT SEVERITY LEVEL TO REVIEW\n")
        print(f"  [1] 🔴 CRITICAL ({len(critical)})")
        print(f"  [2] 🟠 HIGH ({len(high)})")
        print(f"  [3] 🟡 MEDIUM ({len(medium)})")
        print(f"  [4] 🟢 LOW ({len(low)})")
        print(f"  [5] 📋 View full report (JSON file)")
        print(f"  [q] Quit")
        print()

        choice = input("→ ").strip().lower()

        if choice == "1" and critical:
            self.selected_category = "critical"
            self.selected_finding_index = 0
            self.view = "category"
        elif choice == "2" and high:
            self.selected_category = "high"
            self.selected_finding_index = 0
            self.view = "category"
        elif choice == "3" and medium:
            self.selected_category = "medium"
            self.selected_finding_index = 0
            self.view = "category"
        elif choice == "4" and low:
            self.selected_category = "low"
            self.selected_finding_index = 0
            self.view = "category"
        elif choice == "5":
            print("\n📄 Opening Full Report in Browser...\n")
            # Get the latest HTML report file from reports/ directory
            latest_report = subprocess.run(
                "ls -t reports/report_*.html 2>/dev/null | head -1",
                shell=True, capture_output=True, text=True, cwd=os.path.dirname(__file__) + "/.."
            ).stdout.strip()
            if latest_report:
                # Convert to absolute path
                abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", latest_report))
                print(f"📁 Opening: {os.path.basename(latest_report)}")
                subprocess.run(f"xdg-open '{abs_path}' 2>/dev/null &", shell=True)
                print(f"✅ Report opened in your default browser")
                input("\nPress Enter to continue...")
            else:
                print("❌ No HTML report found yet.")
                input("\nPress Enter to continue...")
        elif choice == "q":
            self.view = "exit"

    # ============ CATEGORY VIEW ============

    def _show_category(self):
        """Show findings in a category."""
        findings = self.report_data.get(self.selected_category, [])

        if not findings:
            print(self._header(f"No {self.selected_category.upper()} findings"))
            input("Press Enter to return...")
            self.view = "main"
            return

        # Display findings list
        category_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(self.selected_category, "❓")
        print(self._header(f"{category_emoji} {self.selected_category.upper()} FINDINGS"))
        print()

        # Show findings list
        print(f"📌 SELECT A FINDING TO VIEW DETAILS\n")
        for i, finding in enumerate(findings):
            marker = "→ " if i == self.selected_finding_index else "  "
            print(f"{marker}[{i+1}] {finding.title}")

        print()
        print(f"Use [number] to select, [n]ext, [p]rev, [m]enu, [q]uit\n")

        # Navigation
        choice = input("→ ").strip().lower()

        if choice == "m":
            self.view = "main"
        elif choice == "q":
            self.view = "exit"
        elif choice == "n":
            self.selected_finding_index = min(self.selected_finding_index + 1, len(findings) - 1)
        elif choice == "p":
            self.selected_finding_index = max(self.selected_finding_index - 1, 0)
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(findings):
                self.selected_finding_index = idx
                self.view = "finding_detail"
        else:
            # Enter on empty = view selected finding
            self.view = "finding_detail"

    # ============ FINDING DETAIL VIEW ============

    def _show_finding_detail(self):
        """Show detailed finding information."""
        findings = self.report_data.get(self.selected_category, [])

        if not findings or self.selected_finding_index >= len(findings):
            self.view = "category"
            return

        finding = findings[self.selected_finding_index]
        category_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(self.selected_category, "❓")

        print(self._header(f"{category_emoji} {finding.title}"))
        print()

        # Metadata
        print(f"📍 ID: {finding.name}")
        print(f"📂 Category: {finding.category}")
        print(f"🎯 Severity: {self.selected_category.upper()}")
        print()

        # Description
        print(f"📝 DESCRIPTION")
        print(f"  {finding.description}")
        print()

        # Problem
        print(f"⚠️  PROBLEM")
        print(f"  {finding.problem}")
        print()

        # Solution
        print(f"✅ SOLUTION")
        print(f"  {finding.solution}")
        print()

        # Impact
        print(f"💥 IMPACT IF NOT ADDRESSED")
        print(f"  {finding.impact}")
        print()

        # Rollback
        print(f"🔄 HOW TO UNDO")
        print(f"  {finding.rollback}")
        print()

        # Evidence
        if finding.evidence:
            print(f"📊 EVIDENCE")
            print(f"  {finding.evidence}")
            print()

        # Navigation
        findings_count = len(findings)
        current_num = self.selected_finding_index + 1

        print(f"[{current_num}/{findings_count}]  [n]ext  [p]rev  [back] return to list  [q]uit\n")

        choice = input("→ ").strip().lower()

        if choice in ["back", "b", ""]:
            self.view = "category"
        elif choice == "n":
            if self.selected_finding_index < findings_count - 1:
                self.selected_finding_index += 1
            else:
                self.view = "category"
        elif choice == "p":
            if self.selected_finding_index > 0:
                self.selected_finding_index -= 1
            else:
                self.view = "category"
        elif choice == "q":
            self.view = "exit"

    # ============ UTILITIES ============

    def _header(self, title: str) -> str:
        """Create a formatted header."""
        width = 70
        line = "─" * width
        title_str = f"  {title}  "
        padding = (width - len(title_str)) // 2
        side = " " * padding

        return f"\n┌{line}┐\n│{side}{title_str}{' ' * (width - padding - len(title_str))}│\n└{line}┘"

    @staticmethod
    def _clear():
        """Clear screen."""
        os.system("clear" if os.name == "posix" else "cls")


# Legacy compatibility class
class ProfessionalTUI(ModernTUI):
    """Backwards compatibility wrapper."""

    def __init__(self, findings: List[Finding] = None, recommendations: Dict = None):
        """Initialize with old or new interface."""
        if findings is not None and recommendations is not None:
            # Old interface - convert to new
            report_data = {
                "critical": [f for f in findings if hasattr(f, "type") and f.type == "critical"],
                "high": [f for f in findings if hasattr(f, "type") and f.type == "high"],
                "medium": [f for f in findings if hasattr(f, "type") and f.type == "medium"],
                "low": [f for f in findings if hasattr(f, "type") and f.type == "low"],
                "executive_summary": recommendations.get("summary", ""),
            }
        else:
            report_data = {}

        super().__init__(report_data)
