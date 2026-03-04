"""System utilities - minimal, focused."""

import subprocess
import json
from typing import List, Dict


def run_cmd(cmd: str) -> str:
    """Run shell command safely."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return result.stdout.strip()
    except:
        return ""


class Pacman:
    """Pacman operations."""

    @staticmethod
    def orphans() -> List[Dict]:
        """Get orphan packages with details."""
        output = run_cmd("pacman -Qdt --quiet")
        return [{"name": p} for p in output.split('\n') if p]

    @staticmethod
    def depends_on(pkg: str) -> List[str]:
        """What packages depend on this one."""
        output = run_cmd(f"pacman -Si {pkg} 2>/dev/null | grep 'Required By'")
        if "Required By" not in output:
            return []
        deps = output.split("Required By:")[1].strip()
        return deps.split() if deps != "None" else []

    @staticmethod
    def cache_size() -> int:
        """Cache size in bytes."""
        output = run_cmd("du -sb /var/cache/pacman/pkg/ 2>/dev/null")
        try:
            return int(output.split()[0])
        except:
            return 0


class Systemd:
    """Systemd operations."""

    @staticmethod
    def disabled_services() -> List[str]:
        """Get disabled services."""
        output = run_cmd("systemctl list-unit-files --state=disabled --no-pager --no-legend")
        return [line.split()[0] for line in output.split('\n') if '.service' in line]

    @staticmethod
    def active_services() -> set:
        """Get running services."""
        output = run_cmd("systemctl list-units --state=running --type=service --no-pager --no-legend")
        return {line.split()[0].replace('.service', '') for line in output.split('\n') if '.service' in line}

    @staticmethod
    def required_by(service: str) -> List[str]:
        """What requires this service."""
        output = run_cmd(f"systemctl list-dependencies {service} --reverse 2>/dev/null")
        deps = []
        for line in output.split('\n'):
            if '.service' in line or '.target' in line:
                unit = line.strip().replace('├──', '').replace('└──', '').replace('●', '').strip()
                if unit and unit != service:
                    deps.append(unit)
        return deps


def format_size(b: int) -> str:
    """Format bytes to human readable."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if b < 1024:
            return f"{b:.1f}{unit}"
        b /= 1024
    return f"{b:.1f}TB"
