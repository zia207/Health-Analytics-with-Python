#!/usr/bin/env python3
"""Prepare notebooks for Quarto website rendering."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from generate_quarto_yml import NB_LABELS
BANNER = '![](Images/banner_health_analytics.png){fig-align="center" width="100%"}\n\n'
BANNER_MARKER = "Images/banner_health_analytics.png"


def cell_text(cell: dict) -> str:
    return "".join(cell.get("source", []))


def set_cell_text(cell: dict, text: str) -> None:
    if not text.endswith("\n"):
        text += "\n"
    cell["source"] = [line + "\n" for line in text.split("\n")[:-1]]


def headings_from_markdown(nb: dict) -> tuple[str | None, str | None]:
    title: str | None = None
    subtitle: str | None = None
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        for line in cell_text(cell).splitlines():
            if line.startswith("# ") and not line.startswith("## "):
                title = line[2:].strip()
            elif line.startswith("## ") and subtitle is None:
                subtitle = line[3:].strip()
        if title:
            return title, subtitle
    return None, None


def notebook_headings(nb: dict, path: Path) -> tuple[str, str | None]:
    title, subtitle = headings_from_markdown(nb)
    if title:
        return title, subtitle

    name = path.name
    if name == "MOD00_NTRO_HealthPy_Tutorial_Series.ipynb":
        return "Health Analytics with Python", "A Comprehensive Tutorial Series"

    mod = name[3:5]
    if name in NB_LABELS:
        return NB_LABELS[name], f"Module {mod} — Health Analytics with Python"

    return "Notebook", None


def ensure_yaml_cell(nb: dict, title: str, subtitle: str | None) -> bool:
    yaml_lines = ["---", f'title: "{title}"']
    if subtitle:
        yaml_lines.append(f'subtitle: "{subtitle}"')
    yaml_lines.append("---")
    desired = "\n".join(yaml_lines) + "\n"

    if nb.get("cells") and nb["cells"][0].get("cell_type") == "raw":
        meta = nb["cells"][0].setdefault("metadata", {})
        if meta.get("format") == "yaml":
            text = cell_text(nb["cells"][0])
            if text != desired:
                set_cell_text(nb["cells"][0], desired)
                return True
            return False

    nb["cells"].insert(
        0,
        {
            "cell_type": "raw",
            "id": "quarto-front-matter",
            "metadata": {"format": "yaml"},
            "source": [line + "\n" for line in yaml_lines],
        },
    )
    return True


def first_markdown_cell(nb: dict) -> dict | None:
    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "markdown":
            return cell
    return None


def prepare_first_cell(text: str, title: str, subtitle: str | None) -> str:
    if "<div style=" in text:
        return fix_horizontal_rules(text)

    lines = text.splitlines()
    kept: list[str] = []
    for line in lines:
        if line.startswith("# ") and not line.startswith("## "):
            if line[2:].strip() == title:
                continue
        elif subtitle and line.startswith("## ") and line[3:].strip() == subtitle:
            continue
        kept.append(line)

    body = "\n".join(kept).lstrip("\n")
    if BANNER_MARKER not in body:
        body = BANNER + body
    return fix_horizontal_rules(body)


def fix_horizontal_rules(text: str) -> str:
    return re.sub(r"(?m)^---\s*$", "***", text)


def prepare_notebook(path: Path) -> bool:
    with path.open(encoding="utf-8") as f:
        nb = json.load(f)

    changed = False
    title, subtitle = notebook_headings(nb, path)
    metadata = nb.setdefault("metadata", {})
    quarto_meta = metadata.setdefault("quarto", {})
    desired_meta = {"title": title}
    if subtitle:
        desired_meta["subtitle"] = subtitle
    if quarto_meta != desired_meta:
        quarto_meta.clear()
        quarto_meta.update(desired_meta)
        changed = True

    if ensure_yaml_cell(nb, title, subtitle):
        changed = True

    first_md = first_markdown_cell(nb)
    if first_md is not None:
        text = cell_text(first_md)
        prepared = prepare_first_cell(text, title, subtitle)
        if prepared != text:
            set_cell_text(first_md, prepared)
            changed = True

    for cell in nb.get("cells", []):
        if cell is first_md or cell.get("cell_type") != "markdown":
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
