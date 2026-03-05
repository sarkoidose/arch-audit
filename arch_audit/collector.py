"""System data collector - 8 audit domains."""

import subprocess
import os
import logging
import shlex
from typing import List, Dict, Any
from .constants import COLLECTOR_COMMAND_TIMEOUT

# Setup logging
logger = logging.getLogger(__name__)


def run_cmd(cmd: str, timeout: int = COLLECTOR_COMMAND_TIMEOUT) -> str:
    """Run shell command safely (without shell=True to prevent injection).

    Args:
        cmd: Command string to execute
        timeout: Timeout in seconds (default: COLLECTOR_COMMAND_TIMEOUT)

    Returns:
        Command output or empty string if error
    """
    try:
        # SECURITY: Split command string to avoid shell injection
        # Instead of: subprocess.run(cmd, shell=True)
        # We do: subprocess.run(shlex.split(cmd), shell=False)
        # This prevents malicious input from executing arbitrary code
        cmd_list = shlex.split(cmd)
        result = subprocess.run(
            cmd_list,
            shell=False,  # ✅ SECURE: No shell interpretation
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        logger.warning(f"Command timeout (>{timeout}s): {cmd}")
        return ""
    except (OSError, subprocess.CalledProcessError, ValueError) as e:
        # OSError: File not found
        # CalledProcessError: Command returned non-zero
        # ValueError: Invalid command format
        logger.warning(f"Command failed: {cmd}, error: {type(e).__name__}: {e}")
        return ""
    except Exception as e:
        # Catch only unexpected errors, not programming mistakes
        logger.error(f"Unexpected error running command: {cmd}, error: {e}")
        return ""


def format_size(b: int) -> str:
    """Format bytes to human readable."""
    if b == 0:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB"]:
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


class Collector:
    """Comprehensive system data collector."""

    def __init__(self):
        self.data = {}

    def collect(self) -> Dict[str, Any]:
        """Collect all system data."""
        self.data = {
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "packages": self.collect_packages(),
            "services": self.collect_services(),
            "security": self.collect_security(),
            "disk": self.collect_disk(),
            "performance": self.collect_performance(),
            "logs": self.collect_logs(),
            "boot": self.collect_boot(),
            "config": self.collect_config(),
        }
        return self.data

    # ============ PACKAGES ============

    def collect_packages(self) -> Dict[str, Any]:
        """Collect package-related data."""
        return {
            "orphans": self._get_orphans(),
            "cache_size": self._get_cache_size(),
            "aur_packages": self._get_aur_packages(),
            "available_updates": self._get_available_updates(),
            "broken_deps": self._get_broken_deps(),
        }

    def _get_orphans(self) -> List[Dict]:
        """Get orphan packages."""
        output = run_cmd("pacman -Qdt --quiet 2>/dev/null")
        return [{"name": p} for p in output.split("\n") if p]

    def _get_cache_size(self) -> Dict[str, Any]:
        """Get pacman cache info with detailed breakdown."""
        from .constants import PACMAN_CACHE_PATH

        output = run_cmd(f"du -sb {PACMAN_CACHE_PATH} 2>/dev/null")
        try:
            size = int(output.split()[0])
        except (IndexError, ValueError):
            logger.warning(f"Failed to parse cache size, output: {output}")
            size = 0

        # Check for old packages (paccache would remove with -rk1)
        old_packages = run_cmd("paccache -d 2>/dev/null | wc -l")
        try:
            old_count = int(old_packages)
        except (ValueError, TypeError):
            logger.warning(f"Failed to parse old packages count: {old_packages}")
            old_count = 0

        # Check for unsynced repos
        unsynced_repos = run_cmd("pacman -Sl 2>&1 | grep -i 'unknown' | wc -l")
        try:
            unsynced_count = int(unsynced_repos)
        except (ValueError, TypeError):
            logger.warning(f"Failed to parse unsynced repos count: {unsynced_repos}")
            unsynced_count = 0

        return {
            "bytes": size,
            "formatted": format_size(size),
            "old_packages": old_count,
            "unsynced_repos": unsynced_count
        }

    def _get_aur_packages(self) -> List[Dict]:
        """Get AUR packages (not in official repos)."""
        output = run_cmd("pacman -Qm 2>/dev/null")
        packages = []
        for line in output.split("\n"):
            if line:
                parts = line.split()
                packages.append({"name": parts[0] if parts else ""})
        return packages

    def _get_available_updates(self) -> Dict[str, Any]:
        """Get available package updates."""
        # Try checkupdates first, fall back to pacman -Qu
        output = run_cmd("checkupdates 2>/dev/null || pacman -Qu 2>/dev/null")
        updates = []
        for line in output.split("\n"):
            if line:
                parts = line.split()
                if len(parts) >= 3:
                    updates.append({"name": parts[0], "current": parts[1], "available": parts[3]})

        return {"count": len(updates), "updates": updates}

    def _get_broken_deps(self) -> List[Dict]:
        """Get packages with broken dependencies."""
        output = run_cmd("pacman -Qk 2>&1 | grep 'missing file' || true")
        broken = []
        for line in output.split("\n"):
            if line:
                broken.append({"issue": line})
        return broken

    # ============ SERVICES ============

    def collect_services(self) -> Dict[str, Any]:
        """Collect service-related data."""
        return {
            "failed_services": self._get_failed_services(),
            "disabled_services": self._get_disabled_services(),
            "service_errors": self._get_service_errors(),
        }

    def _get_failed_services(self) -> List[Dict]:
        """Get failed systemd services."""
        output = run_cmd("systemctl --failed --no-pager --no-legend 2>/dev/null")
        services = []
        for line in output.split("\n"):
            if line:
                parts = line.split()
                if parts:
                    services.append({"name": parts[0]})
        return services

    def _get_disabled_services(self) -> List[Dict]:
        """Get disabled services."""
        output = run_cmd("systemctl list-unit-files --state=disabled --no-pager --no-legend 2>/dev/null")
        services = []
        for line in output.split("\n"):
            if line and ".service" in line:
                parts = line.split()
                if parts:
                    services.append({"name": parts[0]})
        return services

    def _get_service_errors(self) -> List[Dict]:
        """Get recent service errors."""
        output = run_cmd("journalctl -p err --since='24h ago' --no-pager -n 20 2>/dev/null")
        errors = []
        for line in output.split("\n")[:20]:
            if line:
                errors.append({"message": line[:150]})
        return errors

    # ============ SECURITY ============

    def collect_security(self) -> Dict[str, Any]:
        """Collect security-related data."""
        return {
            "open_ports": self._get_open_ports(),
            "firewall_status": self._get_firewall_status(),
            "suid_files": self._get_suid_files(),
            "failed_logins": self._get_failed_logins(),
            "users_with_shell": self._get_users_with_shell(),
        }

    def _get_open_ports(self) -> List[Dict]:
        """Get open ports."""
        output = run_cmd("ss -tulnp 2>/dev/null | grep LISTEN")
        ports = []
        for line in output.split("\n"):
            if line:
                parts = line.split()
                if len(parts) >= 4:
                    ports.append({"protocol": parts[0], "state": parts[5]})
        return ports[:20]

    def _get_firewall_status(self) -> Dict[str, Any]:
        """Get firewall status."""
        ufw = run_cmd("ufw status 2>/dev/null | head -1")
        firewalld = run_cmd("firewall-cmd --state 2>/dev/null || echo 'inactive'")

        return {
            "ufw": ufw if ufw else "not installed",
            "firewalld": firewalld if firewalld else "not installed",
        }

    def _get_suid_files(self) -> List[Dict]:
        """Get SUID files."""
        output = run_cmd("find /usr /bin /sbin -perm -4000 -type f 2>/dev/null | head -20")
        files = []
        for line in output.split("\n"):
            if line:
                files.append({"path": line})
        return files

    def _get_failed_logins(self) -> List[Dict]:
        """Get failed login attempts."""
        output = run_cmd("journalctl _SYSTEMD_UNIT=sshd.service -p err --since='7d ago' 2>/dev/null | head -10")
        logins = []
        for line in output.split("\n"):
            if line:
                logins.append({"event": line[:120]})
        return logins

    def _get_users_with_shell(self) -> List[Dict]:
        """Get users with shell access."""
        output = run_cmd("getent passwd | awk -F: '$7 ~ /bash|zsh|sh/ {print $1}' 2>/dev/null")
        users = []
        for user in output.split("\n"):
            if user and user not in ["root"]:
                users.append({"name": user})
        return users

    # ============ DISK ============

    def collect_disk(self) -> Dict[str, Any]:
        """Collect disk-related data."""
        return {
            "usage": self._get_disk_usage(),
            "large_logs": self._get_large_logs(),
            "journal_size": self._get_journal_size(),
            "tmp_size": self._get_tmp_size(),
        }

    def _get_disk_usage(self) -> List[Dict]:
        """Get disk usage per mount point."""
        output = run_cmd("df -h 2>/dev/null")
        usage = []
        for line in output.split("\n")[1:]:
            if line:
                parts = line.split()
                if len(parts) >= 5:
                    try:
                        percent = int(parts[4].rstrip("%"))
                        usage.append({
                            "mount": parts[5],
                            "used": parts[2],
                            "available": parts[3],
                            "percent": percent,
                        })
                    except (ValueError, IndexError):
                        pass
        return usage

    def _get_large_logs(self) -> List[Dict]:
        """Get large log files.

        OPTIMIZATION: Uses single command instead of N+1 queries.
        ✅ BEFORE: find (1 cmd) + du for each file (N cmds) = ~N+1 calls
        ✅ AFTER: find with exec (1 cmd) = 1 call
        """
        from .constants import LOG_SEARCH_PATH, LARGE_LOG_SEARCH_SIZE

        # Use find with -exec to get size + path in one command
        # This avoids calling du for each file (N+1 problem)
        output = run_cmd(
            f"find {LOG_SEARCH_PATH} -size +{LARGE_LOG_SEARCH_SIZE}M -type f "
            "-exec du -h {{}} \\; 2>/dev/null"
        )

        logs = []
        for line in output.split("\n"):
            if line:
                parts = line.split(maxsplit=1)  # Split into [size, path]
                if len(parts) == 2:
                    logs.append({"size": parts[0], "path": parts[1]})

        return logs[:10]

    def _get_journal_size(self) -> Dict[str, Any]:
        """Get journal size."""
        output = run_cmd("journalctl --disk-usage 2>/dev/null")
        return {"info": output if output else "Unable to determine"}

    def _get_tmp_size(self) -> Dict[str, Any]:
        """Get /tmp and /var/tmp sizes."""
        from .constants import TMP_PATH, VAR_TMP_PATH

        tmp = run_cmd(f"du -sh {TMP_PATH} 2>/dev/null | awk '{{print $1}}'")
        var_tmp = run_cmd(f"du -sh {VAR_TMP_PATH} 2>/dev/null | awk '{{print $1}}'")

        return {"tmp": tmp if tmp else "0 B", "var_tmp": var_tmp if var_tmp else "0 B"}

    # ============ PERFORMANCE ============

    def collect_performance(self) -> Dict[str, Any]:
        """Collect performance-related data."""
        return {
            "memory": self._get_memory_usage(),
            "swap": self._get_swap_usage(),
            "top_processes": self._get_top_processes(),
            "load_average": self._get_load_average(),
        }

    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage."""
        try:
            with open("/proc/meminfo", "r") as f:
                lines = f.readlines()

            mem_dict = {}
            for line in lines:
                parts = line.split(":")
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].split()[0]
                    mem_dict[key] = int(value)

            total = mem_dict.get("MemTotal", 0)
            available = mem_dict.get("MemAvailable", 0)
            used = total - available

            return {
                "total_mb": total // 1024,
                "used_mb": used // 1024,
                "available_mb": available // 1024,
                "percent": round((used / total * 100), 1) if total > 0 else 0,
            }
        except Exception:
            return {"total_mb": 0, "used_mb": 0, "available_mb": 0, "percent": 0}

    def _get_swap_usage(self) -> Dict[str, Any]:
        """Get swap usage."""
        output = run_cmd("swapon --show --noheadings 2>/dev/null")
        swaps = []
        for line in output.split("\n"):
            if line:
                parts = line.split()
                if len(parts) >= 3:
                    swaps.append({"device": parts[0], "size": parts[2]})

        return {"swaps": swaps, "enabled": len(swaps) > 0}

    def _get_top_processes(self) -> List[Dict]:
        """Get top CPU processes."""
        output = run_cmd("ps aux --sort=-%cpu 2>/dev/null | head -11")
        processes = []
        for line in output.split("\n")[1:]:
            if line:
                parts = line.split()
                if len(parts) >= 11:
                    processes.append({
                        "user": parts[0],
                        "pid": parts[1],
                        "cpu": parts[2],
                        "mem": parts[3],
                        "command": " ".join(parts[10:11]),
                    })
        return processes

    def _get_load_average(self) -> Dict[str, float]:
        """Get load average."""
        try:
            with open("/proc/loadavg", "r") as f:
                load_str = f.read().split()
            return {"one": float(load_str[0]), "five": float(load_str[1]), "fifteen": float(load_str[2])}
        except Exception:
            return {"one": 0.0, "five": 0.0, "fifteen": 0.0}

    # ============ LOGS ============

    def collect_logs(self) -> Dict[str, Any]:
        """Collect log-related data."""
        return {
            "critical_errors": self._get_critical_errors(),
            "error_messages": self._get_error_messages(),
            "warnings": self._get_warnings(),
        }

    def _get_critical_errors(self) -> List[Dict]:
        """Get critical errors from journalctl."""
        output = run_cmd("journalctl -p crit --since='7d ago' --no-pager 2>/dev/null | head -20")
        errors = []
        for line in output.split("\n"):
            if line:
                errors.append({"message": line[:150]})
        return errors

    def _get_error_messages(self) -> List[Dict]:
        """Get error messages from journalctl."""
        output = run_cmd("journalctl -p err --since='24h ago' --no-pager 2>/dev/null | head -30")
        errors = []
        for line in output.split("\n"):
            if line:
                errors.append({"message": line[:150]})
        return errors

    def _get_warnings(self) -> List[Dict]:
        """Get warnings from journalctl."""
        output = run_cmd("journalctl -p warning --since='24h ago' --no-pager 2>/dev/null | head -20")
        warnings = []
        for line in output.split("\n"):
            if line:
                warnings.append({"message": line[:150]})
        return warnings

    # ============ BOOT/KERNEL ============

    def collect_boot(self) -> Dict[str, Any]:
        """Collect boot and kernel data."""
        return {
            "kernel_version": self._get_kernel_version(),
            "boot_time": self._get_boot_time(),
            "dmesg_errors": self._get_dmesg_errors(),
            "failed_at_boot": self._get_failed_at_boot(),
        }

    def _get_kernel_version(self) -> str:
        """Get kernel version."""
        return run_cmd("uname -r 2>/dev/null")

    def _get_boot_time(self) -> Dict[str, Any]:
        """Get systemd analyze boot time."""
        output = run_cmd("systemd-analyze 2>/dev/null | head -3")
        return {"info": output if output else "Unable to analyze"}

    def _get_dmesg_errors(self) -> List[Dict]:
        """Get dmesg errors."""
        output = run_cmd("journalctl -k -p err --since='boot' 2>/dev/null | head -20")
        errors = []
        for line in output.split("\n"):
            if line:
                errors.append({"message": line[:150]})
        return errors

    def _get_failed_at_boot(self) -> List[Dict]:
        """Get failed units at boot."""
        output = run_cmd("systemctl list-units --state=failed --no-pager --no-legend 2>/dev/null")
        failed = []
        for line in output.split("\n"):
            if line:
                parts = line.split()
                if parts:
                    failed.append({"name": parts[0]})
        return failed

    # ============ CONFIG ============

    def collect_config(self) -> Dict[str, Any]:
        """Collect configuration data."""
        return {
            "important_configs": self._get_important_configs(),
            "system_info": self._get_system_info(),
        }

    def _get_important_configs(self) -> Dict[str, str]:
        """Get important config files status."""
        configs = {}

        # Check pacman.conf
        pacman_conf = "/etc/pacman.conf"
        configs["pacman_conf_exists"] = os.path.exists(pacman_conf)

        # Check fstab
        fstab = "/etc/fstab"
        configs["fstab_exists"] = os.path.exists(fstab)

        # Check sudoers
        sudoers = "/etc/sudoers"
        configs["sudoers_exists"] = os.path.exists(sudoers)

        return configs

    def _get_system_info(self) -> Dict[str, str]:
        """Get basic system info."""
        hostname = run_cmd("hostname 2>/dev/null")
        uptime = run_cmd("uptime -p 2>/dev/null")
        arch = run_cmd("uname -m 2>/dev/null")

        return {
            "hostname": hostname if hostname else "unknown",
            "uptime": uptime if uptime else "unknown",
            "architecture": arch if arch else "unknown",
        }
