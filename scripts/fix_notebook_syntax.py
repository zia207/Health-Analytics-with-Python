#!/usr/bin/env python3
"""Fix broken multi-line string literals and invalid ± operators in code cells."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def strip_comments(line: str) -> str:
    """Remove # comments while preserving quoted strings."""
    out = []
    i = 0
    in_single = in_double = False
    while i < len(line):
        ch = line[i]
        if ch == "\\" and (in_single or in_double):
            out.append(ch)
            if i + 1 < len(line):
                out.append(line[i + 1])
                i += 2
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
            out.append(ch)
        elif ch == '"' and not in_single:
            in_double = not in_double
            out.append(ch)
        elif ch == "#" and not in_single and not in_double:
            break
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def quote_balance(line: str) -> bool:
    s = d = 0
    for ch in strip_comments(line):
        if ch == "'":
            s ^= 1
        elif ch == '"':
            d ^= 1
    return bool(s or d)


def merge_broken_strings(lines: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if quote_balance(line) and i + 1 < len(lines):
            merged = line.rstrip("\n")
            j = i + 1
            while j < len(lines) and quote_balance(merged):
                merged = merged + " " + lines[j].rstrip("\n").lstrip()
                j += 1
            out.append(merged + "\n")
            i = j
        else:
            out.append(line)
            i += 1
    return out


def fix_invalid_plusminus(text: str) -> str:
    return text.replace(
        "np.exp(np.log(RR)±1.96*se_log_rr)",
        "np.exp(np.log(RR)-1.96*se_log_rr), np.exp(np.log(RR)+1.96*se_log_rr)",
    ).replace(
        "np.exp(np.log(OR)±1.96*se_log_or)",
        "np.exp(np.log(OR)-1.96*se_log_or), np.exp(np.log(OR)+1.96*se_log_or)",
    )


def fix_cell_source(source: list[str]) -> list[str]:
    if isinstance(source, str):
        source = [source]
    text = fix_invalid_plusminus("".join(source))
    return merge_broken_strings(text.splitlines(keepends=True))


def fix_notebook(path: Path) -> bool:
    with path.open(encoding="utf-8") as f:
        nb = json.load(f)

    changed = False
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        old = cell.get("source", [])
        new = fix_cell_source(old)
        if new != old:
            cell["source"] = new
            changed = True

    if changed:
        with path.open("w", encoding="utf-8") as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
            f.write("\n")
    return changed


def main() -> None:
    updated = []
    for path in sorted(ROOT.glob("MOD*.ipynb")):
        if fix_notebook(path):
            updated.append(path.name)
            print(f"Fixed {path.name}")
    print(f"Updated {len(updated)} notebooks")


if __name__ == "__main__":
    main()
