#!/usr/bin/env bash
# Execute all MOD*.ipynb notebooks in-place so Quarto can render outputs.
set -uo pipefail
cd "$(dirname "$0")/.."

PYTHON="${PYTHON:-python3}"
LOG=scripts/nbconvert_final.log
TIMEOUT=1200

: > "$LOG"
ok=0
fail=0
failed=()

for nb in MOD*.ipynb; do
  echo "==> $(date -Iseconds) Executing $nb" | tee -a "$LOG"
  if "$PYTHON" -m jupyter nbconvert \
      --execute \
      --to notebook \
      --inplace \
      --ExecutePreprocessor.timeout="$TIMEOUT" \
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
