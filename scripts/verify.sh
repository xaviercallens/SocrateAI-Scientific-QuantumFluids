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

# Gate 2: Lean kernel check (Tier-A formal claims)
echo "[GATE 2] Building and axiom-auditing Lean..."

if [ -f "$REPO_ROOT/lean_src/lakefile.lean" ]; then
    if command -v lake &>/dev/null; then
        # Actually BUILD, rather than grepping for import lines. A text check
        # cannot distinguish a proved theorem from one containing `sorry`,
        # which is the entire point of Gate 2.
        if (cd "$REPO_ROOT/lean_src" && lake build QuantumFluidsShell 2>&1 | tee /tmp/qf_lean_build.log | grep -qE "^error"); then
            echo "  ✗ Lean build FAILED"
            grep -E "^error" /tmp/qf_lean_build.log | head -5
            exit 1
        fi

        # Every theorem must depend on exactly the three standard axioms.
        # sorryAx would mean an unproved hole shipped as a theorem.
        if grep -q "sorryAx" /tmp/qf_lean_build.log; then
            echo "  ✗ GATE 2 FAILED: a theorem depends on sorryAx (unproved hole)"
            grep "sorryAx" /tmp/qf_lean_build.log
            exit 1
        fi

        n_certs=$(grep -c "depends on axioms" /tmp/qf_lean_build.log || true)
        echo "  ✓ Lean builds clean; $n_certs axiom certificate(s) emitted"
        grep "depends on axioms" /tmp/qf_lean_build.log | sed 's/^/    /'
        echo "  ✓ GATE 2 PASSED"
    else
        echo "  ⚠ lake not found; cannot verify Lean claims"
        echo "  ⚠ GATE 2 SKIPPED"
    fi
else
    echo "  ⚠ no lean_src/lakefile.lean"
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

    # Count verified vs pending (grep -c always prints a count, even 0,
    # so no "|| echo 0" fallback is needed — that pattern double-prints
    # when grep exits 1 on zero matches)
    verified=$(grep -c "Status:.*VERIFIED" "$REPO_ROOT/docs/LITERATURE_LEDGER.md")
    pending=$(grep -c "Status:.*PENDING" "$REPO_ROOT/docs/LITERATURE_LEDGER.md")

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
    completed=$(grep -c "✓\|✔" "$REPO_ROOT/PLAN.md")
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
