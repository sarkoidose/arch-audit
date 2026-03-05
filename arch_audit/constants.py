"""Global constants and configuration values."""

# ============ TIMEOUTS ============
# Temps maximum pour les commandes système
COLLECTOR_COMMAND_TIMEOUT = 15  # 15 secondes pour collecter les données
AUTOFIX_COMMAND_TIMEOUT = 300   # 5 minutes pour les fixes auto

# ============ FILE MANAGEMENT ============
# Limites de fichiers pour éviter les accumulations
MAX_REPORT_FILES = 20           # Max 20 fichiers de rapports (10 JSON + 10 HTML)
MAX_HISTORY_REPORTS = 5         # Max 5 audits en historique

# ============ AUDIT THRESHOLDS ============
# Ces seuils sont utilisés par l'analyzer pour décider des sévérités
CACHE_SIZE_THRESHOLD_MB = 100   # Alert si cache pacman > 100MB
LARGE_LOG_FILE_THRESHOLD_MB = 50  # Alert si fichier log > 50MB
OPEN_PORTS_THRESHOLD = 5        # Alert si > 5 ports ouverts
MEMORY_USAGE_THRESHOLD_PERCENT = 75  # Alert si RAM > 75%
MEMORY_CRITICAL_PERCENT = 90    # Alert CRITIQUE si RAM > 90%
DISK_USAGE_HIGH_PERCENT = 85    # Alert si disque > 85%
DISK_USAGE_CRITICAL_PERCENT = 95  # Alert CRITIQUE si disque > 95%
SUID_FILES_THRESHOLD = 50       # Alert si > 50 fichiers SUID
SHELL_USERS_THRESHOLD = 5       # Alert si > 5 utilisateurs avec shell
SERVICE_ERRORS_THRESHOLD = 5    # Alert si > 5 erreurs services
ERROR_MESSAGES_THRESHOLD = 20   # Alert si > 20 messages d'erreur en 24h
WARNING_MESSAGES_THRESHOLD = 30 # Alert si > 30 warnings en 24h
AUR_PACKAGES_THRESHOLD = 10     # Alert si > 10 packages AUR
OLD_PACKAGES_THRESHOLD = 50     # Severity = HIGH si > 50 vieux packages
OLD_PACKAGES_THRESHOLD_MEDIUM = 10  # Severity = MEDIUM si > 10 vieux packages

# ============ FILE SIZES ============
# Limites de taille pour les fichiers
LARGE_LOG_SEARCH_SIZE = 50      # Chercher logs > 50MB
CACHE_VERY_LARGE_SIZE_BYTES = 500_000_000  # 500MB = très gros cache

# ============ LIMITS ============
# Limites pour les résultats affichés
MAX_SUID_FILES_DISPLAY = 20     # Max 20 fichiers SUID à afficher
MAX_LOGS_DISPLAY = 10           # Max 10 fichiers logs à afficher
MAX_ERRORS_DISPLAY = 20         # Max 20 erreurs à afficher
MAX_PORTS_DISPLAY = 20          # Max 20 ports à afficher
MAX_PROCESSES_DISPLAY = 10      # Max 10 processus à afficher

# ============ PATHS ============
# Répertoires pour les recherches
PACMAN_CACHE_PATH = "/var/cache/pacman/pkg/"
LOG_SEARCH_PATH = "/var/log"
TMP_PATH = "/tmp"
VAR_TMP_PATH = "/var/tmp"

# ============ CONFIG DEPTH ============
# Limite de récursion pour éviter les boucles infinies
MAX_CONFIG_NESTING_DEPTH = 10
