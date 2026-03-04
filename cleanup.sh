#!/bin/bash
# Cleanup old reports - keep only the 5 latest pairs

cd "$(dirname "$0")/reports" || exit 1

# Count current reports
total=$(ls -1 report_*.html report_*.json 2>/dev/null | wc -l)

if [ "$total" -gt 10 ]; then
    echo "🧹 Cleaning old reports (keeping 5 latest pairs)..."
    ls -t report_*.html report_*.json | tail -n +11 | xargs rm -f
    echo "✅ Cleanup done"
else
    echo "✅ Reports folder is clean ($(($total / 2)) pairs)"
fi
