"""Arch Linux official API client."""

import urllib.request
import json
from typing import Dict, Optional, List


class ArchAPI:
    """Interact with official Arch Linux API."""

    BASE_URL = "https://archlinux.org/api/v1"

    @staticmethod
    def get_package(name: str) -> Optional[Dict]:
        """Get package info from official API."""
        try:
            # Search across all repos
            url = f"{ArchAPI.BASE_URL}/packages/search/?q={name}&limit=1"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read())
                if data.get('results'):
                    return data['results'][0]
            return None
        except:
            return None

    @staticmethod
    def get_package_depends(pkg_info: Dict) -> List[str]:
        """Get direct dependencies of a package."""
        depends = []

        if pkg_info:
            # Depends
            for dep in pkg_info.get('depends', []):
                # Remove version constraints (e.g., "glibc>=2.2")
                dep_name = dep.split('>=')[0].split('<=')[0].split('=')[0].split('>')[0].split('<')[0]
                depends.append(dep_name)

            # OptDepends might also be useful
            for opt in pkg_info.get('optdepends', []):
                # Format is usually "name: description"
                dep_name = opt.split(':')[0].strip()
                dep_name = dep_name.split('>=')[0].split('<=')[0].split('=')[0]
                if dep_name and dep_name not in depends:
                    depends.append(dep_name)

        return depends

    @staticmethod
    def get_package_info(name: str) -> Dict:
        """Get complete package information."""
        pkg = ArchAPI.get_package(name)

        if not pkg:
            return {
                'name': name,
                'exists': False,
                'depends': [],
                'popularity': 0
            }

        return {
            'name': pkg.get('pkgname', name),
            'exists': True,
            'repo': pkg.get('repo', 'unknown'),
            'depends': ArchAPI.get_package_depends(pkg),
            'popularity': pkg.get('popularity', 0),
            'description': pkg.get('pkgdesc', ''),
            'maintainers': pkg.get('maintainers', [])
        }

    @staticmethod
    def is_core_package(name: str) -> bool:
        """Check if package is core/essential."""
        pkg = ArchAPI.get_package(name)

        if not pkg:
            return False

        # Core packages usually in 'core' or 'base' repos
        repo = pkg.get('repo', '').lower()
        return repo in ['core', 'base']

    @staticmethod
    def get_popularity(name: str) -> float:
        """Get package popularity (0-1)."""
        pkg = ArchAPI.get_package(name)

        if not pkg:
            return 0.0

        popularity = pkg.get('popularity', 0)
        # Normalize to 0-1 range (popularity goes up to ~10)
        return min(1.0, popularity / 10.0)
