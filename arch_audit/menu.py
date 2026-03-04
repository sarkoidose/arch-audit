"""Interactive command menu TUI."""

import sys
from typing import Optional


class MenuTUI:
    """Display interactive command menu."""

    COMMANDS = [
        {
            "key": "1",
            "cmd": "audit",
            "title": "Audit System",
            "desc": "Run full system audit with TUI viewer",
        },
        {
            "key": "2",
            "cmd": "history",
            "title": "View History",
            "desc": "List recent audits from history",
        },
        {
            "key": "3",
            "cmd": "stats",
            "title": "Show Statistics",
            "desc": "View audit trends and statistics",
        },
        {
            "key": "4",
            "cmd": "diff",
            "title": "Compare Audits",
            "desc": "Compare current with previous audit",
        },
        {
            "key": "5",
            "cmd": "preview",
            "title": "Preview Fixes",
            "desc": "Preview auto-fix commands",
        },
        {
            "key": "6",
            "cmd": "autofix",
            "title": "Auto-Fix Mode",
            "desc": "Interactive auto-fix with confirmation",
        },
        {
            "key": "7",
            "cmd": "export",
            "title": "Export Report",
            "desc": "Export latest report (CSV/MD/JSON)",
        },
        {
            "key": "8",
            "cmd": "config",
            "title": "Configuration",
            "desc": "View or create configuration",
        },
        {
            "key": "q",
            "cmd": "quit",
            "title": "Quit",
            "desc": "Exit the program",
        },
    ]

    @staticmethod
    def draw_box(width: int = 80) -> str:
        """Draw a simple box border."""
        return "─" * width

    @staticmethod
    def display_menu() -> Optional[str]:
        """Display interactive menu and return selected command."""
        print("\n")
        print("┌" + MenuTUI.draw_box(78) + "┐")
        print("│" + " " * 78 + "│")
        print("│" + "ARCH-AUDIT - System Audit Tool".center(78) + "│")
        print("│" + " " * 78 + "│")
        print("└" + MenuTUI.draw_box(78) + "┘")
        print()

        # Display commands table
        print("┌─────┬────────────────────────┬──────────────────────────────────────────┐")
        print("│ Key │       Command          │              Description                 │")
        print("├─────┼────────────────────────┼──────────────────────────────────────────┤")

        for cmd in MenuTUI.COMMANDS:
            key = cmd["key"].upper()
            title = cmd["title"]
            desc = cmd["desc"]
            print(
                f"│ {key:^3} │ {title:<22} │ {desc:<40} │"
            )

        print("└─────┴────────────────────────┴──────────────────────────────────────────┘")
        print()

        # Get user input
        valid_keys = [c["key"].lower() for c in MenuTUI.COMMANDS]
        while True:
            choice = input("Choose an option: ").lower().strip()
            if choice in valid_keys:
                for cmd in MenuTUI.COMMANDS:
                    if cmd["key"].lower() == choice:
                        return cmd["cmd"]
            else:
                print(f"Invalid choice. Please enter one of: {', '.join(valid_keys)}")

    @staticmethod
    def handle_export_menu() -> str:
        """Display export format menu."""
        print("\n")
        print("┌─────────────────────────────────────────┐")
        print("│       Export Format                     │")
        print("├─────┬───────────────────────────────────┤")
        print("│  1  │ CSV (Spreadsheet format)          │")
        print("│  2  │ Markdown (Documentation)          │")
        print("│  3  │ JSON (Automation/Scripting)       │")
        print("│  q  │ Cancel                            │")
        print("└─────┴───────────────────────────────────┘")
        print()

        while True:
            choice = input("Choose format: ").lower().strip()
            if choice == "1":
                return "csv"
            elif choice == "2":
                return "md"
            elif choice == "3":
                return "json"
            elif choice == "q":
                return None
            else:
                print("Invalid choice. Please enter 1, 2, 3, or q")
