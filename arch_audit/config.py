"""Configuration management for arch-audit."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List


class Config:
    """Load and manage arch-audit configuration."""

    DEFAULT_CONFIG = {
        "audit": {
            "domains": [
                "packages",
                "services",
                "security",
                "disk",
                "performance",
                "logs",
                "boot",
                "config",
            ],
            "skip": [],
        },
        "thresholds": {
            "cache_size_mb": 100,
            "open_ports_max": 5,
            "memory_percent": 75,
            "disk_percent": 85,
            "large_logs_mb": 50,
        },
        "actions": {
            "safe": [
                "orphan_packages",
                "old_cached_packages",
                "large_log_files",
            ],
            "preview_only": [
                "failed_services",
                "critical_errors_in_logs",
            ],
        },
    }

    def __init__(self):
        """Initialize config from file or defaults."""
        self.config_path = Path.home() / ".config" / "arch-audit" / "config.yaml"
        self.data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load config from file or return defaults."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    user_config = yaml.safe_load(f) or {}
                # Merge with defaults
                return self._merge_configs(self.DEFAULT_CONFIG, user_config)
            except Exception as e:
                print(f"⚠️  Error loading config: {e}")
                print(f"   Using defaults from {self.config_path}")
                return self.DEFAULT_CONFIG
        return self.DEFAULT_CONFIG

    @staticmethod
    def _merge_configs(defaults: Dict, user: Dict) -> Dict:
        """Deep merge user config with defaults."""
        merged = defaults.copy()
        for key, value in user.items():
            if isinstance(value, dict) and key in merged:
                merged[key] = Config._merge_configs(merged[key], value)
            else:
                merged[key] = value
        return merged

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by dot-notation path."""
        keys = key.split(".")
        value = self.data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def get_domains(self) -> List[str]:
        """Get list of domains to audit."""
        all_domains = self.data.get("audit", {}).get("domains", [])
        skip_domains = self.data.get("audit", {}).get("skip", [])
        return [d for d in all_domains if d not in skip_domains]

    def is_safe_action(self, action_id: str) -> bool:
        """Check if action is marked as 'safe' for auto-fix."""
        safe_actions = self.data.get("actions", {}).get("safe", [])
        return action_id in safe_actions

    def create_default_config(self) -> None:
        """Create a default config file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            yaml.dump(self.DEFAULT_CONFIG, f, default_flow_style=False)
        print(f"✅ Created default config at {self.config_path}")

    def show_config(self) -> None:
        """Display current configuration."""
        print("\n📋 Current Configuration:")
        print(yaml.dump(self.data, default_flow_style=False))
