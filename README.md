# arch-audit 🔍

Outil d'audit professionnel pour Arch Linux - analyse 8 domaines du système et détecte ce qui peut être optimisé.

## ✨ Caractéristiques

- **8 domaines d'audit** : paquets, services, sécurité, disque, performance, logs, boot, config
- **Détection intelligente** : identifie les vrais problèmes (paquets orphelins, vieux fichiers, logs surdimensionnés)
- **Interface interactive TUI** : naviguer les résultats facilement
- **Rapports HTML & JSON** : généré automatiquement pour chaque audit
- **Auto-cleanup** : garde seulement les 5 derniers rapports

## 🚀 Usage

```bash
./run.sh
```

Le script :
1. Nettoie les anciens rapports
2. Lance l'analyse du système
3. Ouvre l'interface interactive
4. Génère les rapports HTML et JSON

## 📊 Résultats

Les rapports sont sauvegardés dans le dossier `reports/` :
- `report_*.html` - Rapport interactif (ouvrir dans le navigateur)
- `report_*.json` - Données brutes (pour traitement)

## ⚙️ Structure

```
arch-audit/
├── arch_audit/          Code source Python
├── reports/             Rapports générés
├── run.sh               Script de lancement
├── cleanup.sh           Nettoyage des vieux rapports
└── README.md            Ce fichier
```
