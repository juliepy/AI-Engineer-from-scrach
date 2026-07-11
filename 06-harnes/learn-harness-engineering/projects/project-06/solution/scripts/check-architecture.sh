#!/usr/bin/env bash
#
# check-architecture.sh - Verify layer boundary constraints
#
# Checks that:
# 1. No Node.js core modules (fs, path, os, child_process) in renderer code
# 2. No Electron IPC imports in service code
# 3. No React imports in services or main process code
#
# Exit code 0 = all checks pass
# Exit code 1 = violations found

set -euo pipefail

VIOLATIONS=0

echo "=== Architecture Boundary Checks ==="
echo ""

# Check 1: No fs/path imports in renderer
echo "Checking renderer for Node.js core module imports..."
RENDERER_FILES=$(find src/renderer -name '*.ts' -o -name '*.tsx' 2>/dev/null || true)
if [ -n "$RENDERER_FILES" ]; then
  while IFS= read -r file; do
    if grep -qE "import.*\b(fs|path|os|child_process)\b" "$file" 2>/dev/null; then
      echo "  VIOLATION: $file imports Node.js core module"
      VIOLATIONS=$((VIOLATIONS + 1))
    fi
  done <<< "$RENDERER_FILES"
fi
if [ "$VIOLATIONS" -eq 0 ]; then
  echo "  PASS: No Node.js core imports in renderer"
fi
echo ""

# Check 2: No Electron IPC in services
echo "Checking services for Electron IPC imports..."
SERVICE_FILES=$(find src/services -name '*.ts' 2>/dev/null || true)
SVIO=0
if [ -n "$SERVICE_FILES" ]; then
  while IFS= read -r file; do
    if grep -qE "import.*from\s+['\"]electron['\"]" "$file" 2>/dev/null; then
      echo "  VIOLATION: $file imports from electron"
      VIOLATIONS=$((VIOLATIONS + 1))
      SVIO=$((SVIO + 1))
    fi
    if grep -qE "\bipcMain\b|\bipcRenderer\b|\bBrowserWindow\b" "$file" 2>/dev/null; then
      echo "  VIOLATION: $file uses Electron IPC"
      VIOLATIONS=$((VIOLATIONS + 1))
      SVIO=$((SVIO + 1))
    fi
  done <<< "$SERVICE_FILES"
fi
if [ "$SVIO" -eq 0 ]; then
  echo "  PASS: No Electron IPC in services"
fi
echo ""

# Check 3: No React imports in services or main
echo "Checking services and main for React imports..."
BACKEND_FILES=$(find src/services src/main -name '*.ts' 2>/dev/null || true)
RVIO=0
if [ -n "$BACKEND_FILES" ]; then
  while IFS= read -r file; do
    if grep -qE "import.*from\s+['\"]react['\"]" "$file" 2>/dev/null; then
      echo "  VIOLATION: $file imports React"
      VIOLATIONS=$((VIOLATIONS + 1))
      RVIO=$((RVIO + 1))
    fi
  done <<< "$BACKEND_FILES"
fi
if [ "$RVIO" -eq 0 ]; then
  echo "  PASS: No React imports in services/main"
fi
echo ""

# Summary
echo "=== Summary ==="
if [ "$VIOLATIONS" -gt 0 ]; then
  echo "FAIL: $VIOLATIONS violation(s) found"
  exit 1
else
  echo "PASS: All architecture boundary checks passed"
  exit 0
fi
