#!/usr/bin/env python3
"""Join lines where a string literal was incorrectly split across source lines."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TARGETS = [
    "MOD03_NB03_Survival_Analysis.ipynb",
    "MOD03_NB04_Linear_Regression.ipynb",
    "MOD03_NB07_Confounding_EffectModification.ipynb",
    "MOD04_NB07_Clinical_Prediction_Models.ipynb",
    "MOD06_NB03_DiD_EventStudy.ipynb",
    "MOD07_NB03_Spatial_Regression_GWR.ipynb",
]


def cell_text(cell: dict) -> str:
    return "".join(cell.get("source", []))


def set_cell_text(cell: dict, text: str) -> None:
    if not text.endswith("\n"):
        text += "\n"
    cell["source"] = [line + "\n" for line in text.split("\n")[:-1]]


def in_string_balance(line: str) -> tuple[bool, bool]:
    in_single = in_double = False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "\\" and (in_single or in_double):
            i += 2
            continue
        if ch == "#" and not in_single and not in_double:
            break
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        i += 1
    return in_single, in_double


def has_unclosed_string(line: str) -> bool:
    return any(in_string_balance(line))


def fix_splits(text: str) -> str:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if has_unclosed_string(line) and i + 1 < len(lines):
            merged = line.rstrip("\n")
            j = i + 1
            while j < len(lines) and has_unclosed_string(merged):
                merged += "\\n" + lines[j].lstrip().rstrip("\n")
                j += 1
            out.append(merged + "\n")
            i = j
        else:
            out.append(line)
            i += 1
    return "".join(out)


def repair_notebook(path: Path) -> bool:
    with path.open(encoding="utf-8") as f:
        nb = json.load(f)
    changed = False
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        old = cell_text(cell)
        new = fix_splits(old)
        if new != old:
            try:
                ast.parse(new)
                set_cell_text(cell, new)
                changed = True
            except SyntaxError:
                pass
    if changed:
        with path.open("w", encoding="utf-8") as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
            f.write("\n")
    return changed


def main() -> None:
    for name in TARGETS:
        path = ROOT / name
        if path.exists() and repair_notebook(path):
            print(f"Fixed splits in {name}")


if __name__ == "__main__":
    main()
