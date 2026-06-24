#!/usr/bin/env bash
# Execute all MOD*.ipynb notebooks and export HTML with code + outputs to docs/
set -uo pipefail
cd "$(dirname "$0")/.."

PYTHON=/home/zia207/.pyenv/versions/3.11.14/bin/python3
LOG=scripts/nbconvert_final.log
TIMEOUT=1200
mkdir -p docs

: > "$LOG"
ok=0
fail=0
failed=()

for nb in MOD*.ipynb; do
  echo "==> $(date -Iseconds) Processing $nb" | tee -a "$LOG"
  if "$PYTHON" -m jupyter nbconvert \
      --execute \
      --to html \
      --ExecutePreprocessor.timeout="$TIMEOUT" \
      --output-dir docs \
      "$nb" >> "$LOG" 2>&1; then
    echo "OK: $nb" | tee -a "$LOG"
    ok=$((ok + 1))
  else
    echo "FAIL: $nb" | tee -a "$LOG"
    fail=$((fail + 1))
    failed+=("$nb")
  fi
done

echo "==> Done: $ok succeeded, $fail failed" | tee -a "$LOG"
if ((${#failed[@]})); then
  echo "Failed notebooks:" | tee -a "$LOG"
  printf '  %s\n' "${failed[@]}" | tee -a "$LOG"
fi
