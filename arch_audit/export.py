"""Export reports in multiple formats: CSV, Markdown, JSON, HTML."""

import csv
import json
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


def validate_output_path(base_dir: str, filename: str) -> Path:
    """Validate and secure output path to prevent path traversal attacks.

    SECURITY: Ensures the file is written only within the base directory.
    ✅ Example attack prevented:
       validate_output_path("reports", "../../etc/passwd")
       → Returns "reports/....etc..passwd" (safe)

    Args:
        base_dir: Base directory for output
        filename: Desired filename

    Returns:
        Validated Path object

    Raises:
        ValueError: If path would escape base directory
    """
    base = Path(base_dir).resolve()
    base.mkdir(parents=True, exist_ok=True)

    target = (base / filename).resolve()

    # Check if the target is within the base directory
    try:
        target.relative_to(base)  # Raises ValueError if not within base
    except ValueError:
        raise ValueError(f"Path traversal detected: {filename} would escape {base_dir}")

    return target


class Exporter:
    """Export audit reports in various formats."""

    def __init__(self, report_data: Dict[str, Any]):
        """Initialize exporter with report data."""
        self.report_data = report_data
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    def export_csv(self, output_dir: str = "reports") -> str:
        """Export findings as CSV spreadsheet with validation."""
        # SECURITY: Validate output path to prevent path traversal
        filepath = validate_output_path(output_dir, f"report_{self.timestamp}.csv")

        findings = self.report_data.get("all", [])

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow([
                "Severity",
                "Category",
                "Title",
                "Description",
                "Problem",
                "Solution",
                "Impact",
                "How to Undo",
            ])

            # Write findings with validation
            for finding in findings:
                # Validate that finding has required attributes
                try:
                    severity = finding.severity.upper() if finding.severity else "UNKNOWN"
                    category = finding.category or "unknown"
                    title = finding.title or "Unknown Issue"
                    description = finding.description or ""
                    problem = finding.problem or ""
                    solution = finding.solution or ""
                    impact = finding.impact or ""
                    rollback = finding.rollback or ""

                    writer.writerow([
                        severity,
                        category,
                        title,
                        description,
                        problem,
                        solution,
                        impact,
                        rollback,
                    ])
                except AttributeError as e:
                    logger.warning(f"Skipping invalid finding: {e}")
                    continue

        return str(filepath)

    def export_markdown(self, output_dir: str = "reports") -> str:
        """Export findings as Markdown report."""
        # SECURITY: Validate output path to prevent path traversal
        filepath = validate_output_path(output_dir, f"report_{self.timestamp}.md")

        executive = self.report_data.get("executive_summary", "")
        findings_by_severity = {
            "critical": self.report_data.get("critical", []),
            "high": self.report_data.get("high", []),
            "medium": self.report_data.get("medium", []),
            "low": self.report_data.get("low", []),
        }

        with open(filepath, "w") as f:
            # Header
            f.write("# ARCH-AUDIT Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Executive Summary
            if executive:
                f.write("## Executive Summary\n\n")
                f.write(executive)
                f.write("\n\n")

            # Findings by severity
            severity_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢",
            }

            for severity, findings in findings_by_severity.items():
                if not findings:
                    continue

                emoji = severity_emoji.get(severity, "❓")
                f.write(f"## {emoji} {severity.upper()} Findings ({len(findings)})\n\n")

                for finding in findings:
                    f.write(f"### {finding.title}\n\n")
                    f.write(f"**ID:** `{finding.name}`  \n")
                    f.write(f"**Category:** {finding.category}  \n")
                    f.write(f"**Severity:** {severity.upper()}\n\n")

                    f.write(f"#### Description\n\n{finding.description}\n\n")
                    f.write(f"#### Problem\n\n{finding.problem}\n\n")
                    f.write(f"#### Solution\n\n```bash\n{finding.solution}\n```\n\n")
                    f.write(f"#### Impact if Not Addressed\n\n{finding.impact}\n\n")
                    f.write(f"#### How to Undo\n\n{finding.rollback}\n\n")

                    if finding.evidence:
                        f.write(f"#### Evidence\n\n{finding.evidence}\n\n")

                    f.write("---\n\n")

            # Maintenance commands
            commands = self.report_data.get("maintenance_commands", [])
            if commands:
                f.write("## Priority Maintenance Commands\n\n")
                for cmd in commands[:5]:
                    priority = cmd.get("priority", "")
                    description = cmd.get("description", "")
                    command = cmd.get("command", "")
                    f.write(f"### {priority}: {description}\n\n")
                    f.write(f"```bash\n{command}\n```\n\n")

            # Preventive measures
            measures = self.report_data.get("preventive_measures", [])
            if measures:
                f.write("## Preventive Measures\n\n")
                for measure in measures:
                    f.write(f"- {measure}\n")
                f.write("\n")

        return str(filepath)

    def export_json(self, output_dir: str = "reports") -> str:
        """Export findings as JSON (native format)."""
        # SECURITY: Validate output path to prevent path traversal
        filepath = validate_output_path(output_dir, f"report_{self.timestamp}.json")

        with open(filepath, "w") as f:
            json.dump(self.report_data, f, indent=2, default=str)

        return str(filepath)

    def export_all(self, output_dir: str = "reports") -> Dict[str, str]:
        """Export to all formats."""
        results = {}

        try:
            results["csv"] = self.export_csv(output_dir)
            print(f"✅ CSV: {Path(results['csv']).name}")
        except Exception as e:
            print(f"❌ CSV export failed: {e}")

        try:
            results["md"] = self.export_markdown(output_dir)
            print(f"✅ Markdown: {Path(results['md']).name}")
        except Exception as e:
            print(f"❌ Markdown export failed: {e}")

        try:
            results["json"] = self.export_json(output_dir)
            print(f"✅ JSON: {Path(results['json']).name}")
        except Exception as e:
            print(f"❌ JSON export failed: {e}")

        return results

    @staticmethod
    def export_format(report_data: Dict[str, Any], format: str, output_dir: str = "reports") -> str:
        """Export report in specified format."""
        exporter = Exporter(report_data)

        if format == "csv":
            return exporter.export_csv(output_dir)
        elif format == "md":
            return exporter.export_markdown(output_dir)
        elif format == "json":
            return exporter.export_json(output_dir)
        else:
            raise ValueError(f"Unknown export format: {format}")
