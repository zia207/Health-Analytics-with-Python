#!/usr/bin/env python3
"""Prepare notebooks for Quarto website rendering."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def cell_text(cell: dict) -> str:
    return "".join(cell.get("source", []))


def set_cell_text(cell: dict, text: str) -> None:
    if not text.endswith("\n"):
        text += "\n"
    cell["source"] = [line + "\n" for line in text.split("\n")[:-1]]


def notebook_title(nb: dict) -> str:
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        for line in cell_text(cell).splitlines():
            if line.startswith("# ") and not line.startswith("## "):
                return line[2:].strip()
    return "Notebook"


def fix_horizontal_rules(text: str) -> str:
    return re.sub(r"(?m)^---\s*$", "***", text)


def prepare_notebook(path: Path) -> bool:
    with path.open(encoding="utf-8") as f:
        nb = json.load(f)

    changed = False
    title = notebook_title(nb)
    metadata = nb.setdefault("metadata", {})
    quarto_meta = metadata.setdefault("quarto", {})
    if quarto_meta.get("title") != title:
        quarto_meta["title"] = title
        changed = True

    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        text = cell_text(cell)
        fixed = fix_horizontal_rules(text)
        if fixed != text:
            set_cell_text(cell, fixed)
            changed = True

    if changed:
        with path.open("w", encoding="utf-8") as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
            f.write("\n")
    return changed


def main() -> None:
    updated = 0
    for path in sorted(ROOT.glob("MOD*.ipynb")):
        if prepare_notebook(path):
            updated += 1
            print(f"Updated {path.name}")
    print(f"Prepared {updated} notebooks")


if __name__ == "__main__":
    main()
