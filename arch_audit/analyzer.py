"""Professional audit analyzer - 8 domains with severity levels."""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from .collector import Collector
from .constants import (
    OLD_PACKAGES_THRESHOLD,
    OLD_PACKAGES_THRESHOLD_MEDIUM,
    CACHE_VERY_LARGE_SIZE_BYTES,
    AUR_PACKAGES_THRESHOLD,
    OPEN_PORTS_THRESHOLD,
    SUID_FILES_THRESHOLD,
    SHELL_USERS_THRESHOLD,
    DISK_USAGE_HIGH_PERCENT,
    DISK_USAGE_CRITICAL_PERCENT,
    LARGE_LOG_SEARCH_SIZE,
    MEMORY_CRITICAL_PERCENT,
    MEMORY_USAGE_THRESHOLD_PERCENT,
    SERVICE_ERRORS_THRESHOLD,
    ERROR_MESSAGES_THRESHOLD,
    WARNING_MESSAGES_THRESHOLD,
)

logger = logging.getLogger(__name__)


@dataclass
class Finding:
    """Single finding with complete analysis."""

    name: str  # unique identifier
    category: str  # "packages" | "services" | "security" | "disk" | "performance" | "logs" | "boot" | "config"
    severity: str  # "critical" | "high" | "medium" | "low"
    title: str  # short title
    description: str  # what it is
    problem: str  # why it's an issue
    solution: str  # exact command(s)
    impact: str  # what happens if not addressed
    rollback: str  # how to undo
    evidence: str = ""  # what we found

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "problem": self.problem,
            "solution": self.solution,
            "impact": self.impact,
            "rollback": self.rollback,
            "evidence": self.evidence,
        }


class Analyzer:
    """8-domain professional system audit."""

    def __init__(self, data: Dict[str, Any] = None):
        if data is None:
            collector = Collector()
            data = collector.collect()

        self.data = data
        self.findings: List[Finding] = []

    def analyze(self) -> Dict[str, Any]:
        """Run complete audit."""
        self._audit_packages()
        self._audit_services()
        self._audit_security()
        self._audit_disk()
        self._audit_performance()
        self._audit_logs()
        self._audit_boot()
        self._audit_config()

        # Group by severity
        critical = [f for f in self.findings if f.severity == "critical"]
        high = [f for f in self.findings if f.severity == "high"]
        medium = [f for f in self.findings if f.severity == "medium"]
        low = [f for f in self.findings if f.severity == "low"]

        # Generate executive summary
        executive_summary = self._generate_executive_summary(critical, high, medium, low)

        # Maintenance commands
        maintenance_commands = self._generate_maintenance_commands()

        # Preventive measures
        preventive_measures = self._generate_preventive_measures()

        return {
            "executive_summary": executive_summary,
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
            "all": self.findings,
            "maintenance_commands": maintenance_commands,
            "preventive_measures": preventive_measures,
            "timestamp": self.data.get("timestamp", ""),
        }

    # ============ PACKAGES AUDIT ============

    def _audit_packages(self):
        """Audit package management."""
        pkg_data = self.data.get("packages", {})

        # Orphan packages
        orphans = pkg_data.get("orphans", [])
        if len(orphans) > 0:
            self.findings.append(
                Finding(
                    name="orphan_packages",
                    category="packages",
                    severity="medium",
                    title=f"{len(orphans)} orphan packages",
                    description="Packages no longer required by any other package",
                    problem=f"You have {len(orphans)} orphan packages taking disk space",
                    solution="sudo pacman -Rns $(pacman -Qdtq)",
                    impact="Wasted disk space, cluttered package database",
                    rollback="Packages will be re-installed if needed",
                    evidence=f"Found {len(orphans)} orphans: {', '.join(p['name'] for p in orphans[:3])}" + ("..." if len(orphans) > 3 else ""),
                )
            )

        # Cache size - only alert if there are OLD packages to clean
        cache_info = pkg_data.get("cache_size", {})
        cache_bytes = cache_info.get("bytes", 0)
        cache_fmt = cache_info.get("formatted", "0 B")
        old_packages = cache_info.get("old_packages", 0)

        # Only show alert if there are actually old packages to remove
        if old_packages > 0:
            # Use threshold from constants instead of hardcoded 50
            severity = "high" if old_packages > OLD_PACKAGES_THRESHOLD else "medium"
            self.findings.append(
                Finding(
                    name="old_cached_packages",
                    category="packages",
                    severity=severity,
                    title=f"{old_packages} old package versions in cache",
                    description="Old package versions that can be safely removed",
                    problem=f"Cache contains {old_packages} old package versions - candidates for cleanup",
                    solution="sudo paccache -rk1 # or paccache -rk0 to clean all",
                    impact=f"Wastes disk space with unused old package versions",
                    rollback="Packages will be re-downloaded on next install/update",
                    evidence=f"Found {old_packages} removable old package versions",
                )
            )
        elif cache_bytes > CACHE_VERY_LARGE_SIZE_BYTES:  # Only warn if no old packages but cache is very large
            self.findings.append(
                Finding(
                    name="large_active_cache",
                    category="packages",
                    severity="low",
                    title=f"Large pacman cache: {cache_fmt}",
                    description="Large but active package cache",
                    problem=f"Pacman cache is {cache_fmt}, all versions are current",
                    solution="No action needed - all packages are actively used",
                    impact="Normal for systems with many packages installed",
                    rollback="N/A",
                    evidence=f"Cache size: {cache_fmt} (all current versions)",
                )
            )

        # AUR packages
        aur_packages = pkg_data.get("aur_packages", [])
        if len(aur_packages) > AUR_PACKAGES_THRESHOLD:
            self.findings.append(
                Finding(
                    name="many_aur_packages",
                    category="packages",
                    severity="low",
                    title=f"{len(aur_packages)} AUR packages",
                    description="Manually installed or AUR packages outside official repos",
                    problem=f"You have {len(aur_packages)} packages from AUR, which may lack updates",
                    solution="Review installed AUR packages periodically",
                    impact="Potential security gap if AUR packages are not maintained",
                    rollback="No action needed - AUR packages are safe",
                    evidence=f"Found {len(aur_packages)} AUR packages",
                )
            )

        # Available updates
        updates = pkg_data.get("available_updates", {})
        update_count = updates.get("count", 0)

        if update_count > 0:
            self.findings.append(
                Finding(
                    name="pending_updates",
                    category="packages",
                    severity="medium",
                    title=f"{update_count} packages can be updated",
                    description="System packages have available updates",
                    problem=f"{update_count} package updates available - may include security fixes",
                    solution="sudo pacman -Syu",
                    impact="Missing security patches, potential vulnerabilities",
                    rollback="Downgrade with: sudo pacman -U <old-package>",
                    evidence=f"{update_count} packages pending update",
                )
            )

    # ============ SERVICES AUDIT ============

    def _audit_services(self):
        """Audit systemd services."""
        svc_data = self.data.get("services", {})

        # Failed services
        failed = svc_data.get("failed_services", [])
        if len(failed) > 0:
            self.findings.append(
                Finding(
                    name="failed_services",
                    category="services",
                    severity="critical",
                    title=f"{len(failed)} failed services",
                    description="Services that failed during startup or are in error state",
                    problem=f"{len(failed)} service(s) failed and are not running",
                    solution="systemctl status <service> && sudo systemctl restart <service>",
                    impact="Services not running may break functionality, system stability",
                    rollback="systemctl restart <service>",
                    evidence=f"Failed services: {', '.join(s['name'] for s in failed[:5])}",
                )
            )

        # Service errors
        errors = svc_data.get("service_errors", [])
        if len(errors) > SERVICE_ERRORS_THRESHOLD:
            self.findings.append(
                Finding(
                    name="service_errors",
                    category="services",
                    severity="high",
                    title=f"{len(errors)} service errors in last 24h",
                    description="Services logged error-level messages",
                    problem=f"Services generated {len(errors)} error messages in the last day",
                    solution="journalctl -p err --since='24h ago' # to review",
                    impact="Service instability, potential data loss or misbehavior",
                    rollback="Review specific service issues and restart as needed",
                    evidence=f"Found {len(errors)} error messages",
                )
            )

    # ============ SECURITY AUDIT ============

    def _audit_security(self):
        """Audit security aspects."""
        sec_data = self.data.get("security", {})

        # Open ports
        ports = sec_data.get("open_ports", [])
        if len(ports) > OPEN_PORTS_THRESHOLD:
            self.findings.append(
                Finding(
                    name="many_open_ports",
                    category="security",
                    severity="medium",
                    title=f"{len(ports)} open ports",
                    description="Network services listening on multiple ports",
                    problem=f"{len(ports)} ports are listening - ensure all are intentional",
                    solution="ss -tulnp # review listening services",
                    impact="Each open port is a potential attack surface",
                    rollback="Disable unused services to close ports",
                    evidence=f"Found {len(ports)} listening ports",
                )
            )

        # Firewall status
        fw = sec_data.get("firewall_status", {})
        ufw_status = fw.get("ufw", "")
        firewalld_status = fw.get("firewalld", "")

        if "inactive" in ufw_status.lower() and "inactive" in firewalld_status.lower():
            self.findings.append(
                Finding(
                    name="no_firewall",
                    category="security",
                    severity="high",
                    title="No firewall enabled",
                    description="Neither UFW nor firewalld are active",
                    problem="System has no active firewall protection",
                    solution="sudo pacman -S ufw && sudo ufw enable",
                    impact="Network traffic completely unfiltered, exposed to attacks",
                    rollback="sudo ufw disable",
                    evidence="Both UFW and firewalld are inactive",
                )
            )

        # SUID files
        suid = sec_data.get("suid_files", [])
        if len(suid) > SUID_FILES_THRESHOLD:
            self.findings.append(
                Finding(
                    name="many_suid_files",
                    category="security",
                    severity="low",
                    title=f"{len(suid)} SUID binaries",
                    description="Files with SUID bit set (run as owner regardless of caller)",
                    problem=f"{len(suid)} SUID files - potential privilege escalation vectors",
                    solution="find / -perm -4000 -ls 2>/dev/null # review suspicious ones",
                    impact="Misconfigured SUID could allow privilege escalation",
                    rollback="No action needed for audit purposes",
                    evidence=f"Found {len(suid)} SUID files",
                )
            )

        # Users with shell
        users = sec_data.get("users_with_shell", [])
        user_count = len(users)
        if user_count > SHELL_USERS_THRESHOLD:
            self.findings.append(
                Finding(
                    name="many_shell_users",
                    category="security",
                    severity="low",
                    title=f"{user_count} users with shell access",
                    description="Non-root users with login shell capability",
                    problem=f"{user_count} users can log in - ensure all are necessary",
                    solution="Review user accounts and disable unused ones",
                    impact="More accounts = larger attack surface",
                    rollback="Re-enable shell for user: sudo usermod -s /bin/bash username",
                    evidence=f"Found {user_count} users with shell access",
                )
            )

    # ============ DISK AUDIT ============

    def _audit_disk(self):
        """Audit disk usage."""
        disk_data = self.data.get("disk", {})

        # Disk usage
        usage = disk_data.get("usage", [])
        for mount in usage:
            percent = mount.get("percent", 0)
            mount_point = mount.get("mount", "?")

            if percent >= DISK_USAGE_CRITICAL_PERCENT:
                self.findings.append(
                    Finding(
                        name=f"disk_critical_{mount_point.replace('/', '_')}",
                        category="disk",
                        severity="critical",
                        title=f"{mount_point} is {percent}% full",
                        description=f"Disk partition at {mount_point} is critically full",
                        problem=f"Disk {mount_point} has only {mount.get('available', '?')} available",
                        solution="Delete files, expand partition, or move data",
                        impact="System may fail to function with no free disk space",
                        rollback="Restore deleted files from backup if available",
                        evidence=f"{mount_point}: {mount.get('used', '?')} used, {mount.get('available', '?')} available",
                    )
                )
            elif percent >= DISK_USAGE_HIGH_PERCENT:
                self.findings.append(
                    Finding(
                        name=f"disk_high_{mount_point.replace('/', '_')}",
                        category="disk",
                        severity="high",
                        title=f"{mount_point} is {percent}% full",
                        description=f"Disk partition at {mount_point} is getting full",
                        problem=f"Disk {mount_point} usage is high, only {mount.get('available', '?')} left",
                        solution="Clean up old files, logs, caches",
                        impact="Little room for new data, system performance degradation",
                        rollback="Files are deleted - restore from backup if needed",
                        evidence=f"{mount_point}: {percent}% full",
                    )
                )

        # Large logs
        large_logs = disk_data.get("large_logs", [])
        if len(large_logs) > 0:
            log_sizes = ", ".join(f"{l['path'].split('/')[-1]} ({l['size']})" for l in large_logs[:3])
            self.findings.append(
                Finding(
                    name="large_log_files",
                    category="disk",
                    severity="medium",
                    title=f"{len(large_logs)} large log files",
                    description="Log files exceeding 50MB",
                    problem=f"Log files using significant disk space: {log_sizes}",
                    solution="sudo journalctl --vacuum=30d # or remove old logs",
                    impact=f"{len(large_logs)} large files wasting disk space",
                    rollback="Keep backups before deleting logs",
                    evidence=f"Found {len(large_logs)} large log files",
                )
            )

    # ============ PERFORMANCE AUDIT ============

    def _audit_performance(self):
        """Audit performance metrics."""
        perf_data = self.data.get("performance", {})

        # Memory usage
        mem = perf_data.get("memory", {})
        mem_percent = mem.get("percent", 0)

        if mem_percent > MEMORY_CRITICAL_PERCENT:
            self.findings.append(
                Finding(
                    name="high_memory_usage",
                    category="performance",
                    severity="high",
                    title=f"Memory {mem_percent}% in use",
                    description=f"System using {mem.get('used_mb', 0)}MB of {mem.get('total_mb', 0)}MB RAM",
                    problem=f"Only {mem.get('available_mb', 0)}MB available - system may slow down",
                    solution="systemctl stop <heavy-service> # or add more RAM",
                    impact="System slowdown, swapping to disk, application crashes",
                    rollback="Restart heavy applications if needed",
                    evidence=f"{mem_percent}% memory used",
                )
            )
        elif mem_percent > MEMORY_USAGE_THRESHOLD_PERCENT:
            self.findings.append(
                Finding(
                    name="moderate_memory_usage",
                    category="performance",
                    severity="medium",
                    title=f"Memory {mem_percent}% in use",
                    description=f"System using {mem.get('used_mb', 0)}MB of {mem.get('total_mb', 0)}MB RAM",
                    problem=f"Getting low on available memory - {mem.get('available_mb', 0)}MB free",
                    solution="Monitor applications: top -b -n 1 | head -20",
                    impact="Potential slowdown if memory pressure increases",
                    rollback="Applications will release memory when closed",
                    evidence=f"{mem_percent}% memory used",
                )
            )

        # Swap usage
        swap = perf_data.get("swap", {})
        if swap.get("enabled", False):
            swaps = swap.get("swaps", [])
            if len(swaps) > 0:
                self.findings.append(
                    Finding(
                        name="swap_enabled",
                        category="performance",
                        severity="low",
                        title=f"Swap enabled ({len(swaps)} device(s))",
                        description="System has swap space configured",
                        problem="Swap usage indicates memory is being spilled to disk (slow)",
                        solution="Monitor with: swapon --show",
                        impact="Slower than RAM but prevents OOM kills",
                        rollback="swapoff /path/to/swap",
                        evidence=f"{len(swaps)} swap device(s) enabled",
                    )
                )

    # ============ LOGS AUDIT ============

    def _audit_logs(self):
        """Audit system logs."""
        logs_data = self.data.get("logs", {})

        # Critical errors
        crit = logs_data.get("critical_errors", [])
        if len(crit) > 0:
            self.findings.append(
                Finding(
                    name="critical_errors_in_logs",
                    category="logs",
                    severity="critical",
                    title=f"{len(crit)} critical log entries",
                    description="Critical-level errors in system journal (last 7 days)",
                    problem=f"System logged {len(crit)} critical errors",
                    solution="journalctl -p crit --since='7d ago' # review each",
                    impact="Critical issues need investigation to prevent system failure",
                    rollback="Review logs and address underlying issues",
                    evidence=f"Found {len(crit)} critical entries",
                )
            )

        # Error messages
        errors = logs_data.get("error_messages", [])
        if len(errors) > ERROR_MESSAGES_THRESHOLD:
            self.findings.append(
                Finding(
                    name="many_errors_in_logs",
                    category="logs",
                    severity="high",
                    title=f"{len(errors)} error messages (24h)",
                    description="Many error-level messages in system journal",
                    problem=f"{len(errors)} errors in the last 24 hours",
                    solution="journalctl -p err --since='24h ago' --no-pager | less",
                    impact="System instability, services may be degraded",
                    rollback="Address root causes of errors",
                    evidence=f"Found {len(errors)} error entries",
                )
            )

        # Warnings
        warnings = logs_data.get("warnings", [])
        if len(warnings) > WARNING_MESSAGES_THRESHOLD:
            self.findings.append(
                Finding(
                    name="many_warnings_in_logs",
                    category="logs",
                    severity="medium",
                    title=f"{len(warnings)} warnings (24h)",
                    description="Many warning-level messages in system journal",
                    problem=f"{len(warnings)} warnings indicate potential issues",
                    solution="journalctl -p warning --since='24h ago' | less",
                    impact="Potential problems that may become critical if ignored",
                    rollback="Monitor and address warnings proactively",
                    evidence=f"Found {len(warnings)} warning entries",
                )
            )

    # ============ BOOT/KERNEL AUDIT ============

    def _audit_boot(self):
        """Audit boot and kernel."""
        boot_data = self.data.get("boot", {})

        # Dmesg errors
        dmesg_errs = boot_data.get("dmesg_errors", [])
        if len(dmesg_errs) > 0:
            self.findings.append(
                Finding(
                    name="kernel_dmesg_errors",
                    category="boot",
                    severity="medium",
                    title=f"{len(dmesg_errs)} kernel errors since boot",
                    description="Kernel logged errors since last boot",
                    problem=f"{len(dmesg_errs)} kernel-level errors detected",
                    solution="journalctl -k -p err --since='boot' # review each",
                    impact="Kernel errors may indicate hardware problems or driver issues",
                    rollback="Address hardware issues or update drivers",
                    evidence=f"Found {len(dmesg_errs)} kernel errors",
                )
            )

        # Failed at boot
        failed_boot = boot_data.get("failed_at_boot", [])
        if len(failed_boot) > 0:
            self.findings.append(
                Finding(
                    name="units_failed_at_boot",
                    category="boot",
                    severity="high",
                    title=f"{len(failed_boot)} units failed at boot",
                    description="Systemd units that failed during startup",
                    problem=f"{len(failed_boot)} service(s) failed during boot",
                    solution="sudo systemctl reset-failed && sudo systemctl restart <service>",
                    impact="Services not running, system may be degraded",
                    rollback="Investigate and restart failed services",
                    evidence=f"Failed units: {', '.join(f['name'] for f in failed_boot[:3])}",
                )
            )

    # ============ CONFIG AUDIT ============

    def _audit_config(self):
        """Audit system configuration."""
        cfg_data = self.data.get("config", {})
        sys_info = cfg_data.get("system_info", {})

        # Just info findings for now
        uptime = sys_info.get("uptime", "unknown")
        self.findings.append(
            Finding(
                name="system_uptime",
                category="config",
                severity="low",
                title=f"System uptime: {uptime}",
                description="How long system has been running",
                problem="No problem - informational only",
                solution="No action needed",
                impact="Long uptime means stable system",
                rollback="N/A",
                evidence=f"System uptime: {uptime}",
            )
        )

    # ============ REPORTING ============

    def _generate_executive_summary(self, critical: List[Finding], high: List[Finding], medium: List[Finding], low: List[Finding]) -> str:
        """Generate executive summary."""
        lines = [
            f"System Audit Report - {len(self.findings)} findings",
            "",
            f"  🔴 CRITICAL:  {len(critical)} issue(s) - require immediate action",
            f"  🟠 HIGH:      {len(high)} issue(s) - address soon",
            f"  🟡 MEDIUM:    {len(medium)} issue(s) - plan resolution",
            f"  🟢 LOW:       {len(low)} issue(s) - monitor",
            "",
        ]

        if critical:
            lines.append("Critical Issues:")
            for f in critical[:3]:
                lines.append(f"  • {f.title}")
            if len(critical) > 3:
                lines.append(f"  • ... and {len(critical) - 3} more")
            lines.append("")

        return "\n".join(lines)

    def _generate_maintenance_commands(self) -> List[Dict[str, str]]:
        """Generate priority maintenance commands."""
        commands = []

        # Group findings by type and suggest commands
        critical_findings = [f for f in self.findings if f.severity == "critical"]
        high_findings = [f for f in self.findings if f.severity == "high"]

        for finding in critical_findings[:5]:
            commands.append({"priority": "CRITICAL", "command": finding.solution, "description": finding.title})

        for finding in high_findings[:5]:
            commands.append({"priority": "HIGH", "command": finding.solution, "description": finding.title})

        return commands

    def _generate_preventive_measures(self) -> List[str]:
        """Generate preventive measures."""
        measures = [
            "Enable automatic updates: yaourt -S yay && yay --save --cleandeps",
            "Configure firewall: sudo ufw enable && sudo ufw default deny incoming",
            "Monitor logs regularly: journalctl -f",
            "Backup important data: rsync -av --delete /home /mnt/backup",
            "Keep kernel updated: sudo pacman -Syu",
            "Review systemd journal size: journalctl --vacuum=30d",
            "Run regular package audits: pacman -Qk",
            "Check disk usage monthly: df -h",
        ]
        return measures
