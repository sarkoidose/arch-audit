"""Audit history management - store and compare past audits."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional


class History:
    """Manage audit history database."""

    def __init__(self):
        """Initialize history storage."""
        self.history_dir = Path.home() / ".local" / "share" / "arch-audit" / "history"
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def save_report(self, report_data: Dict[str, Any]) -> str:
        """Save audit report to history with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = self.history_dir / f"audit_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(report_data, f, indent=2)

        return str(filename)

    def get_latest(self) -> Optional[Dict[str, Any]]:
        """Get the latest audit report."""
        reports = sorted(self.history_dir.glob("audit_*.json"), reverse=True)
        if not reports:
            return None

        with open(reports[0]) as f:
            return json.load(f)

    def get_report(self, index: int = 0) -> Optional[Dict[str, Any]]:
        """Get report by index (0 = latest, 1 = previous, etc.)."""
        reports = sorted(self.history_dir.glob("audit_*.json"), reverse=True)
        if index >= len(reports):
            return None

        with open(reports[index]) as f:
            return json.load(f)

    def list_reports(self, limit: int = 10) -> List[Dict[str, str]]:
        """List recent audit reports."""
        reports = sorted(self.history_dir.glob("audit_*.json"), reverse=True)[:limit]
        result = []

        for i, report_file in enumerate(reports):
            with open(report_file) as f:
                data = json.load(f)

            timestamp = report_file.stem.replace("audit_", "")
            critical_count = len(data.get("critical", []))
            high_count = len(data.get("high", []))

            result.append({
                "index": i,
                "timestamp": timestamp,
                "file": report_file.name,
                "critical": critical_count,
                "high": high_count,
            })

        return result

    def compare_reports(self, index1: int = 0, index2: int = 1) -> Dict[str, Any]:
        """Compare two audit reports and show differences."""
        report1 = self.get_report(index1)
        report2 = self.get_report(index2)

        if not report1 or not report2:
            return {"error": "Could not load reports to compare"}

        # Extract findings for comparison
        def count_findings(report, severity):
            return len(report.get(severity, []))

        comparison = {
            "report1": {"timestamp": self._extract_timestamp(report1), "counts": {}},
            "report2": {"timestamp": self._extract_timestamp(report2), "counts": {}},
            "changes": {},
        }

        for severity in ["critical", "high", "medium", "low"]:
            count1 = count_findings(report1, severity)
            count2 = count_findings(report2, severity)

            comparison["report1"]["counts"][severity] = count1
            comparison["report2"]["counts"][severity] = count2
            comparison["changes"][severity] = count2 - count1

        return comparison

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics across all audits."""
        reports = list(self.history_dir.glob("audit_*.json"))

        if not reports:
            return {"error": "No audit history found"}

        stats = {
            "total_audits": len(reports),
            "date_range": {
                "first": reports[-1].stem.replace("audit_", ""),
                "last": reports[0].stem.replace("audit_", ""),
            },
            "trends": {
                "critical": [],
                "high": [],
                "medium": [],
                "low": [],
            },
        }

        for report_file in sorted(reports):
            with open(report_file) as f:
                data = json.load(f)

            for severity in ["critical", "high", "medium", "low"]:
                count = len(data.get(severity, []))
                stats["trends"][severity].append({
                    "timestamp": report_file.stem.replace("audit_", ""),
                    "count": count,
                })

        return stats

    @staticmethod
    def _extract_timestamp(report: Dict[str, Any]) -> str:
        """Extract timestamp from report."""
        return report.get("timestamp", "unknown")

    def delete_old_reports(self, keep: int = 20) -> int:
        """Delete old reports, keep only recent ones."""
        reports = sorted(self.history_dir.glob("audit_*.json"), reverse=True)
        deleted = 0

        for report_file in reports[keep:]:
            report_file.unlink()
            deleted += 1

        return deleted
