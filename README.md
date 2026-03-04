# arch-audit

Outil d'audit pour Arch Linux - identifie ce qui est inutile et peut être optimisé.

## Objectifs

- Détecter paquets orphelins
- Identifier services/daemons inutilisés
- Analyser cache et fichiers temporaires
- Trouver espace disque anormal
- Proposer nettoyage

## Usage

```bash
python main.py
```

Interface TUI minimaliste pour naviguer les résultats et appliquer optimisations.

## Philosophie

Suckless : code simple, lisible, pas de dépendances inutiles.
