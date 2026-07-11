#!/usr/bin/env bash
# cleanup-scanner.sh -- Check the data directory for stale or inconsistent artifacts.
#
# This script examines the application's data directory for:
# - Orphaned content files (content without metadata)
# - Dangling chunk files (chunks without index entries)
# - Missing content files (metadata without content)
# - Inconsistent metadata (indexed docs without chunks)
# - Stale Q&A references (history referencing deleted docs)
#
# Usage: bash scripts/cleanup-scanner.sh [data-dir]
#
# If data-dir is not provided, uses the default Electron userData path:
#   macOS: ~/Library/Application Support/knowledge-base/knowledge-base-data
#   Linux: ~/.config/knowledge-base/knowledge-base-data
set -euo pipefail

# Determine data directory
if [ $# -ge 1 ]; then
  DATA_DIR="$1"
else
  # Default paths based on OS
  if [ "$(uname)" = "Darwin" ]; then
    DATA_DIR="$HOME/Library/Application Support/knowledge-base/knowledge-base-data"
  else
    DATA_DIR="$HOME/.config/knowledge-base/knowledge-base-data"
  fi
fi

echo "=== Cleanup Scanner ==="
echo "Data directory: $DATA_DIR"
echo ""

ISSUE_COUNT=0

# Check if data directory exists
if [ ! -d "$DATA_DIR" ]; then
  echo "[INFO] Data directory does not exist. Nothing to scan."
  echo "This is normal for a fresh installation."
  exit 0
fi

# ---- Check 1: Orphaned content files ----

echo "[Check 1] Orphaned content files (content without metadata)"

if [ -f "$DATA_DIR/documents-meta.json" ]; then
  # Get list of document IDs from metadata
  doc_ids=$(python3 -c "
import json, sys
try:
    with open('$DATA_DIR/documents-meta.json') as f:
        docs = json.load(f)
    for doc in docs:
        print(doc['id'])
except:
    pass
" 2>/dev/null || echo "")

  # Check each content file
  orphaned_count=0
  if [ -d "$DATA_DIR/content" ]; then
    for content_file in "$DATA_DIR/content"/*.txt; do
      if [ -f "$content_file" ]; then
        basename_file=$(basename "$content_file" .txt)
        if echo "$doc_ids" | grep -qx "$basename_file"; then
          : # OK, has metadata
        else
          echo "  ORPHANED: content/$basename_file.txt (no matching document metadata)"
          orphaned_count=$((orphaned_count + 1))
          ISSUE_COUNT=$((ISSUE_COUNT + 1))
        fi
      fi
    done
  fi

  if [ "$orphaned_count" -eq 0 ]; then
    echo "  OK: No orphaned content files"
  fi
else
  echo "  SKIP: No documents-meta.json found"
fi
echo ""

# ---- Check 2: Dangling chunk files ----

echo "[Check 2] Dangling chunk files (chunks without index entries)"

if [ -f "$DATA_DIR/index-meta.json" ] && [ -d "$DATA_DIR/chunks" ]; then
  indexed_ids=$(python3 -c "
import json
try:
    with open('$DATA_DIR/index-meta.json') as f:
        index = json.load(f)
    for doc_id in index.keys():
        print(doc_id)
except:
    pass
" 2>/dev/null || echo "")

  dangling_count=0
  for chunk_file in "$DATA_DIR/chunks"/*.json; do
    if [ -f "$chunk_file" ]; then
      basename_file=$(basename "$chunk_file" .json)
      if echo "$indexed_ids" | grep -qx "$basename_file"; then
        : # OK, has index entry
      else
        echo "  DANGLING: chunks/$basename_file.json (no index entry)"
        dangling_count=$((dangling_count + 1))
        ISSUE_COUNT=$((ISSUE_COUNT + 1))
      fi
    fi
  done

  if [ "$dangling_count" -eq 0 ]; then
    echo "  OK: No dangling chunk files"
  fi
else
  echo "  SKIP: No index data found"
fi
echo ""

# ---- Check 3: Missing content files ----

echo "[Check 3] Missing content files (metadata without content)"

if [ -f "$DATA_DIR/documents-meta.json" ] && [ -d "$DATA_DIR/content" ]; then
  missing_count=0
  python3 -c "
import json
try:
    with open('$DATA_DIR/documents-meta.json') as f:
        docs = json.load(f)
    for doc in docs:
        import os
        content_path = '$DATA_DIR/content/' + doc['id'] + '.txt'
        if not os.path.exists(content_path):
            print(doc['id'])
except:
    pass
" 2>/dev/null | while read -r missing_id; do
    echo "  MISSING: content/$missing_id.txt (document exists in metadata)"
    ISSUE_COUNT=$((ISSUE_COUNT + 1))
  done

  missing_count=$(python3 -c "
import json, os
count = 0
try:
    with open('$DATA_DIR/documents-meta.json') as f:
        docs = json.load(f)
    for doc in docs:
        content_path = '$DATA_DIR/content/' + doc['id'] + '.txt'
        if not os.path.exists(content_path):
            count += 1
except:
    pass
print(count)
" 2>/dev/null || echo "0")

  if [ "$missing_count" -eq 0 ]; then
    echo "  OK: No missing content files"
  fi
else
  echo "  SKIP: No documents metadata or content directory found"
fi
echo ""

# ---- Check 4: Inconsistent metadata ----

echo "[Check 4] Inconsistent metadata (indexed docs without chunk files)"

if [ -f "$DATA_DIR/documents-meta.json" ]; then
  inconsistent=$(python3 -c "
import json, os
count = 0
try:
    with open('$DATA_DIR/documents-meta.json') as f:
        docs = json.load(f)
    for doc in docs:
        if doc.get('status') == 'indexed':
            chunk_path = '$DATA_DIR/chunks/' + doc['id'] + '.json'
            if not os.path.exists(chunk_path):
                print('  INCONSISTENT: ' + doc['id'] + ' (status=indexed but no chunks)')
                count += 1
    if count == 0:
        print('OK')
except:
    print('ERROR: Could not parse metadata')
" 2>/dev/null || echo "SKIP")

  if echo "$inconsistent" | grep -q "INCONSISTENT"; then
    ISSUE_COUNT=$((ISSUE_COUNT + 1))
  elif echo "$inconsistent" | grep -q "OK"; then
    echo "  OK: All indexed documents have chunk files"
  else
    echo "  $inconsistent"
  fi
else
  echo "  SKIP: No documents metadata found"
fi
echo ""

# ---- Check 5: Stale Q&A references ----

echo "[Check 5] Stale Q&A references (history referencing deleted docs)"

if [ -f "$DATA_DIR/qa-history.json" ] && [ -f "$DATA_DIR/documents-meta.json" ]; then
  stale_count=$(python3 -c "
import json
count = 0
try:
    with open('$DATA_DIR/qa-history.json') as f:
        history = json.load(f)
    with open('$DATA_DIR/documents-meta.json') as f:
        docs = json.load(f)
    doc_ids = {d['id'] for d in docs}
    for entry in history:
        resp = entry.get('response', {})
        for citation in resp.get('citations', []):
            if citation.get('documentId') not in doc_ids:
                count += 1
except:
    pass
print(count)
" 2>/dev/null || echo "0")

  if [ "$stale_count" -gt 0 ]; then
    echo "  STALE: $stale_count Q&A citations reference deleted documents"
    ISSUE_COUNT=$((ISSUE_COUNT + 1))
  else
    echo "  OK: No stale Q&A references"
  fi
else
  echo "  SKIP: No Q&A history or documents metadata found"
fi
echo ""

# ---- Summary ----

echo "=== Scan Complete ==="
if [ "$ISSUE_COUNT" -eq 0 ]; then
  echo "Result: CLEAN (0 issues found)"
  echo ""
  echo "The data directory is consistent. No cleanup needed."
else
  echo "Result: ISSUES FOUND ($ISSUE_COUNT)"
  echo ""
  echo "Recommended actions:"
  echo "  1. Use the in-app Reset button to clear all data"
  echo "  2. Re-import documents from data/sample-documents/"
  echo "  3. Re-run this scanner to verify cleanup"
fi
