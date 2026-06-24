#!/usr/bin/env bash
# Build GitHub Pages site with Quarto (matches python-beginners layout).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Preparing notebooks for Quarto..."
python3 scripts/prepare_quarto_notebooks.py

echo "==> Generating _quarto.yml sidebar..."
python3 scripts/generate_quarto_yml.py

if [[ "${SKIP_EXECUTE:-}" != "1" ]]; then
  echo "==> Executing notebooks in-place (set SKIP_EXECUTE=1 to skip)..."
  bash scripts/execute_and_export_html.sh
fi

echo "==> Rendering Quarto website to docs/..."
quarto render

touch docs/.nojekyll
echo "==> Done. Site output: docs/"
