#!/usr/bin/env bash
# Build GitHub Pages site with Quarto (matches python-beginners layout).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Preparing notebooks for Quarto..."
python3 scripts/prepare_quarto_notebooks.py

echo "==> Generating _quarto.yml sidebar..."
python3 scripts/generate_quarto_yml.py

echo "==> Rendering Quarto website to docs/..."
quarto render

touch docs/.nojekyll
echo "==> Done. Site output: docs/"
