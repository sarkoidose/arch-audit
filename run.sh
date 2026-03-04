#!/bin/bash
cd "$(dirname "$0")"
./cleanup.sh
python3 -m arch_audit.main "$@"
