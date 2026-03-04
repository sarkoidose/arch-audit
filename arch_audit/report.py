"""Report generation - terminal, JSON, and HTML."""

import json
from datetime import datetime
from typing import List, Dict, Any, Tuple
from .analyzer import Finding


class Report:
    """Generate professional audit reports."""

    @staticmethod
    def save(report_data: Dict[str, Any], directory: str = ".") -> Tuple[str, str]:
        """Save JSON and HTML reports."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        json_path = f"{directory}/report_{timestamp}.json"
        html_path = f"{directory}/report_{timestamp}.html"

        with open(json_path, "w") as f:
            f.write(Report.json(report_data))

        with open(html_path, "w") as f:
            f.write(Report.html(report_data))

        return json_path, html_path

    @staticmethod
    def json(report_data: Dict[str, Any]) -> str:
        """Generate JSON report."""
        data = {
            "timestamp": report_data.get("timestamp", ""),
            "executive_summary": report_data.get("executive_summary", ""),
            "findings": {
                "critical": [f.to_dict() for f in report_data.get("critical", [])],
                "high": [f.to_dict() for f in report_data.get("high", [])],
                "medium": [f.to_dict() for f in report_data.get("medium", [])],
                "low": [f.to_dict() for f in report_data.get("low", [])],
            },
            "maintenance_commands": report_data.get("maintenance_commands", []),
            "preventive_measures": report_data.get("preventive_measures", []),
        }
        return json.dumps(data, indent=2)

    @staticmethod
    def html(report_data: Dict[str, Any]) -> str:
        """Generate HTML report."""
        critical = report_data.get("critical", [])
        high = report_data.get("high", [])
        medium = report_data.get("medium", [])
        low = report_data.get("low", [])
        timestamp = report_data.get("timestamp", "")
        executive_summary = report_data.get("executive_summary", "")
        maintenance_commands = report_data.get("maintenance_commands", [])
        preventive_measures = report_data.get("preventive_measures", [])

        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            '    <meta charset="utf-8">',
            '    <meta name="viewport" content="width=device-width, initial-scale=1">',
            "    <title>ARCH-AUDIT Report</title>",
            "    <style>",
            "        * { margin: 0; padding: 0; box-sizing: border-box; }",
            "        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; background: #f5f5f5; color: #333; line-height: 1.6; }",
            "        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }",
            "        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 8px; margin-bottom: 40px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }",
            "        .header h1 { font-size: 2.5em; margin-bottom: 10px; }",
            "        .header .timestamp { opacity: 0.9; font-size: 0.95em; }",
            "        .executive-summary { background: white; padding: 30px; border-radius: 8px; margin-bottom: 40px; border-left: 4px solid #667eea; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }",
            "        .executive-summary h2 { margin-bottom: 15px; color: #667eea; }",
            "        .severity-section { background: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }",
            "        .severity-section h2 { padding-bottom: 15px; border-bottom: 2px solid #eee; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }",
            "        .severity-critical { color: #dc3545; }",
            "        .severity-high { color: #fd7e14; }",
            "        .severity-medium { color: #ffc107; }",
            "        .severity-low { color: #28a745; }",
            "        .finding { margin-bottom: 25px; padding: 15px; border: 1px solid #eee; border-radius: 4px; background: #fafafa; }",
            "        .finding-title { font-weight: 600; font-size: 1.1em; margin-bottom: 8px; }",
            "        .finding-meta { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-bottom: 10px; font-size: 0.9em; }",
            "        .finding-meta-item { color: #666; }",
            "        .finding-section { margin-top: 12px; }",
            "        .finding-section strong { color: #333; display: block; margin-bottom: 4px; }",
            "        .finding-section p { color: #555; background: white; padding: 8px 12px; border-radius: 4px; border-left: 3px solid #ddd; }",
            "        .solution-code { background: #1e1e1e; color: #d4d4d4; padding: 12px; border-radius: 4px; font-family: 'Courier New', monospace; font-size: 0.9em; overflow-x: auto; margin-top: 8px; }",
            "        .maintenance-section { background: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }",
            "        .maintenance-section h2 { margin-bottom: 20px; color: #333; }",
            "        .command-item { background: #f8f9fa; padding: 15px; margin-bottom: 12px; border-left: 3px solid #667eea; border-radius: 4px; }",
            "        .command-item .priority { font-weight: 600; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; }",
            "        .priority-critical { background: #dc3545; color: white; }",
            "        .priority-high { background: #fd7e14; color: white; }",
            "        .command-item .code { font-family: 'Courier New', monospace; background: #1e1e1e; color: #d4d4d4; padding: 8px 12px; border-radius: 3px; margin-top: 8px; font-size: 0.9em; }",
            "        .preventive-section { background: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }",
            "        .preventive-section h2 { margin-bottom: 20px; color: #333; }",
            "        .measure-item { padding: 10px 15px; background: #e8f5e9; border-left: 3px solid #28a745; border-radius: 4px; margin-bottom: 8px; }",
            "        .footer { text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #999; font-size: 0.9em; }",
            "        @media print { body { background: white; } .container { padding: 0; } .severity-section, .maintenance-section, .preventive-section { page-break-inside: avoid; } }",
            "    </style>",
            "</head>",
            "<body>",
            "    <div class='container'>",
            "        <div class='header'>",
            "            <h1>🔍 ARCH-AUDIT Report</h1>",
            f"            <div class='timestamp'>{timestamp}</div>",
            "        </div>",
        ]

        # Executive Summary
        if executive_summary:
            html_parts.extend([
                "        <div class='executive-summary'>",
                "            <h2>Executive Summary</h2>",
                f"            <pre style='font-family: monospace; white-space: pre-wrap; word-wrap: break-word;'>{executive_summary}</pre>",
                "        </div>",
            ])

        # Critical findings
        if critical:
            html_parts.append(Report._html_severity_section("🔴 CRITICAL", critical, "critical"))

        # High findings
        if high:
            html_parts.append(Report._html_severity_section("🟠 HIGH", high, "high"))

        # Medium findings
        if medium:
            html_parts.append(Report._html_severity_section("🟡 MEDIUM", medium, "medium"))

        # Low findings
        if low:
            html_parts.append(Report._html_severity_section("🟢 LOW", low, "low"))

        # Maintenance commands
        if maintenance_commands:
            html_parts.extend([
                "        <div class='maintenance-section'>",
                "            <h2>Priority Maintenance Commands</h2>",
            ])
            for cmd in maintenance_commands:
                priority_class = f"priority-{cmd['priority'].lower()}"
                html_parts.extend([
                    "            <div class='command-item'>",
                    f"                <span class='priority {priority_class}'>{cmd['priority']}</span>",
                    f"                <div style='margin-top: 8px; font-size: 0.9em;'>{cmd['description']}</div>",
                    f"                <div class='code'>{cmd['command']}</div>",
                    "            </div>",
                ])
            html_parts.append("        </div>")

        # Preventive measures
        if preventive_measures:
            html_parts.extend([
                "        <div class='preventive-section'>",
                "            <h2>Preventive Measures</h2>",
            ])
            for measure in preventive_measures:
                html_parts.append(f"            <div class='measure-item'>{measure}</div>")
            html_parts.append("        </div>")

        html_parts.extend([
            "        <div class='footer'>",
            "            <p>Generated by ARCH-AUDIT - Professional System Auditing Tool</p>",
            "        </div>",
            "    </div>",
            "</body>",
            "</html>",
        ])

        return "\n".join(html_parts)

    @staticmethod
    def _html_severity_section(title: str, findings: List[Finding], severity: str) -> str:
        """Generate HTML for a severity section."""
        html_parts = [
            "        <div class='severity-section'>",
            f"            <h2 class='severity-{severity}'>{title} ({len(findings)} finding(s))</h2>",
        ]

        for finding in findings:
            html_parts.extend([
                "            <div class='finding'>",
                f"                <div class='finding-title'>{finding.title}</div>",
                "                <div class='finding-meta'>",
                f"                    <div class='finding-meta-item'><strong>Category:</strong> {finding.category}</div>",
                f"                    <div class='finding-meta-item'><strong>ID:</strong> {finding.name}</div>",
                "                </div>",
                "                <div class='finding-section'>",
                "                    <strong>Description</strong>",
                f"                    <p>{finding.description}</p>",
                "                </div>",
                "                <div class='finding-section'>",
                "                    <strong>Problem</strong>",
                f"                    <p>{finding.problem}</p>",
                "                </div>",
                "                <div class='finding-section'>",
                "                    <strong>Solution</strong>",
                f"                    <div class='solution-code'>{finding.solution}</div>",
                "                </div>",
                "                <div class='finding-section'>",
                "                    <strong>Impact if Not Addressed</strong>",
                f"                    <p>{finding.impact}</p>",
                "                </div>",
                "                <div class='finding-section'>",
                "                    <strong>How to Undo</strong>",
                f"                    <p>{finding.rollback}</p>",
                "                </div>",
                "            </div>",
            ])

        html_parts.append("        </div>")
        return "\n".join(html_parts)
