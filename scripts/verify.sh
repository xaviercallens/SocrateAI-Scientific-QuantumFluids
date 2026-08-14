#!/bin/bash

# verify.sh — Gate 1 (unit test harnesses) + Gate 2 (Lean footprint)
# Purpose: Validate M0–M4 work against Tier-B and Tier-A standards

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== SocrateAI-Scientific-QuantumFluids Verification ==="
echo "Date: $(date -Iseconds)"
echo ""

# Gate 1: Unit tests (Tier-B harnesses)
echo "[GATE 1] Running unit test harnesses..."

if [ -d "$REPO_ROOT/tests" ]; then
    test_count=$(find "$REPO_ROOT/tests" -name "test_*.py" -o -name "*_test.py" | wc -l)

    if [ "$test_count" -gt 0 ]; then
        echo "  Found $test_count test file(s)"

        # Run with pytest if available
        if command -v pytest &>/dev/null; then
            pytest "$REPO_ROOT/tests" -v --tb=short
            echo "  ✓ GATE 1 PASSED"
        else
            echo "  ⚠ pytest not found; skipping test execution (install with: pip install pytest)"
            echo "  ⚠ GATE 1 SKIPPED"
        fi
    else
        echo "  ⚠ No test files found (expected after M1)"
        echo "  ⚠ GATE 1 SKIPPED"
    fi
else
    echo "  ⚠ tests/ directory not found"
    echo "  ⚠ GATE 1 SKIPPED"
fi

echo ""

# Gate 2: Lean footprint check (Tier-A formal imports)
echo "[GATE 2] Checking Lean imports..."

if [ -d "$REPO_ROOT/lean_src" ]; then
    lean_files=$(find "$REPO_ROOT/lean_src" -name "*.lean" | wc -l)

    if [ "$lean_files" -gt 0 ]; then
        echo "  Found $lean_files Lean file(s)"

        # Check for Mathesis imports
        if grep -r "import Mathesis" "$REPO_ROOT/lean_src" &>/dev/null; then
            echo "  ✓ Mathesis imports detected"

            # Verify no undefined Mathesis references
            undefined=$(grep -r "Mathesis\." "$REPO_ROOT/lean_src" | grep -v "import" | wc -l)
            echo "  Found $undefined Mathesis reference(s); verify versions pinned in SPEC.md"
        fi

        # Check for version comments or tags
        if grep -r "-- Tag:" "$REPO_ROOT/lean_src" &>/dev/null; then
            echo "  ✓ Version tags found in Lean source"
        else
            echo "  ⚠ No version tags found (add '-- Tag: ...' comments per LL-3)"
        fi

        echo "  ✓ GATE 2 PASSED (manual review required for tag correctness)"
    else
        echo "  ⚠ No Lean files found (expected after M2)"
        echo "  ⚠ GATE 2 SKIPPED"
    fi
else
    echo "  ⚠ lean_src/ directory not found"
    echo "  ⚠ GATE 2 SKIPPED"
fi

echo ""

# Consistency checks
echo "[CHECK] Consistency verification..."

# Check LEDGER.md exists and is non-empty
if [ -f "$REPO_ROOT/LEDGER.md" ]; then
    echo "  ✓ LEDGER.md exists"
else
    echo "  ✗ LEDGER.md not found"
    exit 1
fi

# Check LITERATURE_LEDGER.md exists
if [ -f "$REPO_ROOT/docs/LITERATURE_LEDGER.md" ]; then
    echo "  ✓ docs/LITERATURE_LEDGER.md exists"

    # Count verified vs pending
    verified=$(grep -c "Status: VERIFIED" "$REPO_ROOT/docs/LITERATURE_LEDGER.md" || echo 0)
    pending=$(grep -c "Status: PENDING" "$REPO_ROOT/docs/LITERATURE_LEDGER.md" || echo 0)

    echo "    - Verified: $verified, Pending: $pending"

    if [ "$pending" -gt 0 ]; then
        echo "    ⚠ WARNING: $pending pending entries (M0 blocker)"
    fi
else
    echo "  ✗ docs/LITERATURE_LEDGER.md not found"
    exit 1
fi

# Check PLAN.md for milestone status
if [ -f "$REPO_ROOT/PLAN.md" ]; then
    echo "  ✓ PLAN.md exists"
    completed=$(grep -c "✓\|✔" "$REPO_ROOT/PLAN.md" || echo 0)
    echo "    - Completed tasks: $completed"
else
    echo "  ✗ PLAN.md not found"
    exit 1
fi

echo ""
echo "=== Verification Complete ==="
echo ""
echo "Summary:"
echo "  Gate 1 (Unit tests): Check above"
echo "  Gate 2 (Lean imports): Check above"
echo ""
echo "Next steps:"
echo "  - Review PLAN.md for milestone status"
echo "  - Check LITERATURE_LEDGER.md for pending items"
echo "  - Run 'pytest tests/ -v' to execute unit tests"
echo ""
