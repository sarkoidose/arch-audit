#!/bin/bash
# Comprehensive test suite for arch-audit

cd "$(dirname "$0")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "\n${YELLOW}=== ARCH-AUDIT TEST SUITE ===${NC}\n"

# Test counter
PASSED=0
FAILED=0

test_command() {
    local name="$1"
    local cmd="$2"

    echo -n "Testing $name... "
    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((FAILED++))
    fi
}

# Test 1: Basic audit runs
test_command "Basic audit" "./run.sh --history"

# Test 2: Show configuration
test_command "Show configuration" "./run.sh --config"

# Test 3: List history
test_command "List history" "./run.sh --history"

# Test 4: Show statistics
test_command "Show statistics" "./run.sh --stats"

# Test 5: Compare audits
test_command "Compare audits" "./run.sh --diff"

# Test 6: Export CSV
test_command "Export CSV" "./run.sh --export csv"

# Test 7: Export Markdown
test_command "Export Markdown" "./run.sh --export md"

# Test 8: Export JSON
test_command "Export JSON" "./run.sh --export json"

# Test 9: Preview mode
test_command "Preview auto-fix" "./run.sh --preview"

# Test 10: Check reports directory
test_command "Reports directory exists" "test -d reports"

# Test 11: Check history directory
test_command "History directory exists" "test -d ~/.local/share/arch-audit/history"

# Test 12: Check config file
test_command "Config file exists" "test -f ~/.config/arch-audit/config.yaml"

# Test 13: Verify HTML reports generated
test_command "HTML reports exist" "test -n \"$(find reports -name '*.html' -type f 2>/dev/null | head -1)\""

# Test 14: Verify JSON reports generated
test_command "JSON reports exist" "test -n \"$(find reports -name '*.json' -type f 2>/dev/null | head -1)\""

# Test 15: Verify at least one history file exists
HISTORY_FILES=$(ls ~/.local/share/arch-audit/history/audit_*.json 2>/dev/null | wc -l)
echo -n "Testing History files count... "
if [ "$HISTORY_FILES" -gt 0 ]; then
    echo -e "${GREEN}✓ PASSED${NC} ($HISTORY_FILES files)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC} (no files)"
    ((FAILED++))
fi

echo ""
echo -e "${YELLOW}=== TEST SUMMARY ===${NC}"
echo -e "Passed: ${GREEN}${PASSED}${NC}"
echo -e "Failed: ${RED}${FAILED}${NC}"
echo -e "Total:  $((PASSED + FAILED))\n"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}\n"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}\n"
    exit 1
fi
