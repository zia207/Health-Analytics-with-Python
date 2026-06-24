#!/usr/bin/env python3
"""Repair code cells with SyntaxError by fixing split string literals."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Lines that clearly start a new Python statement (don't merge into prior line).
_STMT_START = re.compile(
    r"^(?:def |class |if |elif |else:|for |while |try:|except |finally:|"
    r"return |import |from |print\(|display\(|plt\.|ax\.|fig\.|sns\.|"
    r"np\.|pd\.|df\[|model_|#|[A-Z_]+\s*=)"
)


def cell_text(cell: dict) -> str:
    return "".join(cell.get("source", []))


def set_cell_text(cell: dict, text: str) -> None:
    if not text.endswith("\n"):
        text += "\n"
    cell["source"] = [line + "\n" for line in text.split("\n")[:-1]]


def _in_string_balance(line: str) -> tuple[bool, bool]:
    """Track double/single quoted regions; ignore # comments outside strings."""
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
    s, d = _in_string_balance(line)
    return s or d


def is_continuation(next_line: str) -> bool:
    """True if next line continues a broken string, not a new statement."""
    s = next_line.lstrip()
    if not s:
        return False
    if _STMT_START.match(s):
        return False
    # Continuation of split word inside quotes
    if re.match(r"^[a-z(]", s):
        return True
    if s[0] in "\"')":
        return True
    return False


def merge_broken_strings(text: str) -> str:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if has_unclosed_string(line) and i + 1 < len(lines):
            merged = line.rstrip("\n")
            j = i + 1
            while j < len(lines) and has_unclosed_string(merged):
                nxt = lines[j]
                if not is_continuation(nxt):
                    break
                merged = merged + " " + nxt.lstrip().rstrip("\n")
                j += 1
            out.append(merged + "\n")
            i = j
        else:
            out.append(line)
            i += 1
    return "".join(out)


def fix_plusminus(text: str) -> str:
    return text.replace(
        "np.exp(np.log(RR)±1.96*se_log_rr)",
        "np.exp(np.log(RR)-1.96*se_log_rr), np.exp(np.log(RR)+1.96*se_log_rr)",
    ).replace(
        "np.exp(np.log(OR)±1.96*se_log_or)",
        "np.exp(np.log(OR)-1.96*se_log_or), np.exp(np.log(OR)+1.96*se_log_or)",
    )


def try_compile(text: str) -> bool:
    try:
        ast.parse(text)
        return True
    except SyntaxError:
        return False


def repair_cell(text: str) -> str:
    text = fix_plusminus(text)
    if try_compile(text):
        return text
    fixed = merge_broken_strings(text)
    if try_compile(fixed):
        return fixed
    return text


def repair_notebook(path: Path) -> bool:
    with path.open(encoding="utf-8") as f:
        nb = json.load(f)

    changed = False
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        old = cell_text(cell)
        new = repair_cell(old)
        if new != old:
            set_cell_text(cell, new)
            changed = True

    if changed:
        with path.open("w", encoding="utf-8") as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
            f.write("\n")
    return changed


def main() -> None:
    failed = [
        "MOD03_NB01_Hypothesis_Testing.ipynb",
        "MOD03_NB03_Survival_Analysis.ipynb",
        "MOD03_NB04_Linear_Regression.ipynb",
        "MOD03_NB06_Count_Regression.ipynb",
        "MOD03_NB07_Confounding_EffectModification.ipynb",
        "MOD04_NB04_Clinical_Model_Evaluation.ipynb",
        "MOD04_NB07_Clinical_Prediction_Models.ipynb",
        "MOD05_NB08_Capstone_Clinical_NLP.ipynb",
        "MOD06_NB03_DiD_EventStudy.ipynb",
        "MOD06_NB06_GComp_TMLE.ipynb",
        "MOD07_NB02_Spatial_Autocorrelation.ipynb",
        "MOD07_NB03_Spatial_Regression_GWR.ipynb",
        "MOD07_NB06_Environmental_Epidemiology.ipynb",
        "MOD07_NB08_Capstone_Spatial_Atlas.ipynb",
        "MOD08_NB08_Capstone_Deployment.ipynb",
    ]
    for name in failed:
        path = ROOT / name
        if path.exists() and repair_notebook(path):
            print(f"Repaired {name}")


if __name__ == "__main__":
    main()
