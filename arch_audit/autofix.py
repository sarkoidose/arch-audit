"""Auto-fix mode - interactively fix identified issues."""

import subprocess
from typing import List, Dict, Any
from .analyzer import Finding
from .config import Config


class AutoFix:
    """Execute fixes for audit findings."""

    FIXES = {
        "orphan_packages": {
            "command": "sudo pacman -Rns $(pacman -Qdtq)",
            "description": "Remove orphan packages",
            "safe": True,
        },
        "old_cached_packages": {
            "command": "sudo paccache -rk1",
            "description": "Remove old package versions from cache",
            "safe": True,
        },
        "large_log_files": {
            "command": "sudo journalctl --vacuum=30d",
            "description": "Vacuum old journal logs (>30 days)",
            "safe": True,
        },
    }

    def __init__(self):
        """Initialize auto-fix module."""
        self.config = Config()
        self.executed = []
        self.skipped = []

    def preview_fixes(self, findings: List[Finding]) -> None:
        """Show commands that would be executed (dry-run)."""
        fixable = self._get_fixable_findings(findings)

        if not fixable:
            print("\n✅ No automatically fixable issues found.\n")
            return

        print("\n📋 Fixable Issues (Preview Mode)\n")
        for i, (finding, fix_info) in enumerate(fixable, 1):
            print(f"{i}. {finding.title}")
            print(f"   Command: {fix_info['command']}")
            print()

    def interactive_fix(self, findings: List[Finding]) -> None:
        """Interactive mode to select and execute fixes."""
        fixable = self._get_fixable_findings(findings)

        if not fixable:
            print("\n✅ No automatically fixable issues found.\n")
            return

        print("\n🔧 Auto-Fix Mode (Interactive)\n")
        print(f"Found {len(fixable)} fixable issue(s):\n")

        for i, (finding, fix_info) in enumerate(fixable, 1):
            print(f"{i}. {finding.title}")

        print()
        print("Options:")
        print("  [a] Fix all safe issues")
        print("  [p] Preview commands")
        print("  [s] Select specific issues")
        print("  [q] Cancel")
        print()

        choice = input("→ ").strip().lower()

        if choice == "a":
            self._execute_all(fixable)
        elif choice == "p":
            self.preview_fixes(findings)
        elif choice == "s":
            self._select_and_fix(fixable)
        elif choice == "q":
            print("\nCancelled.\n")
        else:
            print("\nInvalid choice.\n")

    def _get_fixable_findings(
        self, findings: List[Finding]
    ) -> List[tuple[Finding, Dict[str, Any]]]:
        """Get findings that have auto-fix solutions."""
        fixable = []
        safe_actions = self.config.data.get("actions", {}).get("safe", [])

        for finding in findings:
            if finding.name in safe_actions and finding.name in self.FIXES:
                fixable.append((finding, self.FIXES[finding.name]))

        return fixable

    def _execute_all(self, fixable: List[tuple[Finding, Dict[str, Any]]]) -> None:
        """Execute all fixes after confirmation."""
        print("\n⚠️  About to execute the following commands:\n")

        for finding, fix_info in fixable:
            print(f"  • {fix_info['description']}")
            print(f"    $ {fix_info['command']}\n")

        confirm = input("Proceed? [y/n]: ").strip().lower()

        if confirm == "y":
            for finding, fix_info in fixable:
                self._execute_fix(finding.name, fix_info)
        else:
            print("\nCancelled.\n")

    def _select_and_fix(
        self, fixable: List[tuple[Finding, Dict[str, Any]]]
    ) -> None:
        """Let user select which fixes to apply."""
        print("\nSelect issues to fix (comma-separated numbers, e.g. 1,3):\n")

        selections = input("→ ").strip().split(",")

        try:
            indices = [int(s.strip()) - 1 for s in selections if s.strip()]
        except ValueError:
            print("\nInvalid selection.\n")
            return

        selected = [fixable[i] for i in indices if 0 <= i < len(fixable)]

        if not selected:
            print("\nNo valid selections.\n")
            return

        print("\n⚠️  About to execute:\n")
        for finding, fix_info in selected:
            print(f"  • {fix_info['description']}")
            print(f"    $ {fix_info['command']}\n")

        confirm = input("Proceed? [y/n]: ").strip().lower()

        if confirm == "y":
            for finding, fix_info in selected:
                self._execute_fix(finding.name, fix_info)
        else:
            print("\nCancelled.\n")

    def _execute_fix(self, issue_id: str, fix_info: Dict[str, Any]) -> None:
        """Execute a single fix command."""
        try:
            print(f"Executing: {fix_info['description']}...")
            result = subprocess.run(
                fix_info["command"], shell=True, capture_output=True, text=True, timeout=300
            )

            if result.returncode == 0:
                print(f"  ✅ Success\n")
                self.executed.append(issue_id)
            else:
                print(f"  ❌ Failed: {result.stderr[:100]}\n")
                self.skipped.append(issue_id)
        except subprocess.TimeoutExpired:
            print(f"  ⏱️ Timeout\n")
            self.skipped.append(issue_id)
        except Exception as e:
            print(f"  ❌ Error: {str(e)}\n")
            self.skipped.append(issue_id)

    def summary(self) -> None:
        """Show summary of executed fixes."""
        if not self.executed and not self.skipped:
            return

        print("\n" + "=" * 50)
        print("AUTO-FIX SUMMARY")
        print("=" * 50)
        print(f"✅ Executed: {len(self.executed)}")
        print(f"⚠️  Skipped:  {len(self.skipped)}")
        print("=" * 50 + "\n")
