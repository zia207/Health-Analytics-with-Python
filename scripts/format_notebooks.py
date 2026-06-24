#!/usr/bin/env python3
"""Format all module notebooks to match MOD01_NB01 style."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"MOD00_NTRO_HealthPy_Tutorial_Series.ipynb"}

MODULE_LINE = re.compile(
    r"^### Health Analytics with Python · Module (\d{2}): .+$",
    re.MULTILINE,
)
MODULE_LINE_ALT = re.compile(
    r"^## Module (\d{2}) [—-] Health Analytics with Python$",
    re.MULTILINE,
)
CAPSTONE_TITLE = re.compile(
    r"^# MOD-(\d{2}) · NB-(\d{2}) — (.+)$",
    re.MULTILINE,
)
META_PIPE = re.compile(
    r"\*\*Estimated time:\*\*\s*([^|]+)\s*\|\s*\*\*Level:\*\*\s*([^|]+)"
    r"(?:\s*\|\s*\*\*Libraries:\*\*\s*(.+))?$"
)
NEXT_ANY = re.compile(
    r"\*\*Next(?::|\s*(?:→|->|→))\s*(.+?)(?:\*\*|\n)",
    re.MULTILINE,
)


def cell_text(cell: dict) -> str:
    return "".join(cell.get("source", []))


def set_cell_text(cell: dict, text: str) -> None:
    if not text.endswith("\n"):
        text += "\n"
    cell["source"] = [line + "\n" for line in text.split("\n")[:-1]]


def notebook_title(path: Path) -> str:
    with path.open(encoding="utf-8") as f:
        nb = json.load(f)
    for cell in nb.get("cells", []):
        if cell["cell_type"] != "markdown":
            continue
        text = cell_text(cell)
        for line in text.splitlines():
            if line.startswith("# ") and not line.startswith("## "):
                return line[2:].strip()
    return path.stem


def learning_objective_bullets(header_text: str) -> list[str]:
    bullets: list[str] = []
    in_objectives = False
    for line in header_text.splitlines():
        if line.strip() == "**Learning objectives**":
            in_objectives = True
            continue
        if in_objectives:
            if line.startswith("- "):
                bullets.append(line[2:].strip())
            elif line.startswith("**") or line.strip() == "---":
                break
    return bullets


def first_objective(path: Path) -> str:
    with path.open(encoding="utf-8") as f:
        nb = json.load(f)
    for cell in nb.get("cells", []):
        if cell["cell_type"] != "markdown":
            continue
        text = cell_text(cell)
        bullets = learning_objective_bullets(text)
        if bullets:
            obj = bullets[0].rstrip(".")
            return obj[0].lower() + obj[1:] if obj else ""
    return "continue the module sequence."


def build_index() -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    for path in sorted(ROOT.glob("MOD*.ipynb")):
        m = re.match(r"MOD(\d{2})_NB(\d{2})_", path.name)
        if not m:
            continue
        mod, nb = m.group(1), m.group(2)
        info = {
            "mod": mod,
            "title": notebook_title(path),
            "objective": first_objective(path),
            "file": path.name,
        }
        index[f"MOD{mod}_NB{nb}"] = info
        index[f"{mod}_NB{nb}"] = info
    module_names = {
        "01": "Python Foundations",
        "02": "EDA in Healthcare",
        "03": "Statistical Inference",
        "04": "Machine Learning for Clinical Prediction",
        "05": "NLP for Clinical Text",
        "06": "Causal Inference in Health Research",
        "07": "Geospatial & Spatial Epidemiology",
        "08": "Reproducible Research & Deployment",
    }
    for mod, name in module_names.items():
        index[f"Module {mod}"] = {"title": name, "objective": f"begin Module {mod}."}
    return index


def notebook_lookup(nb_key: str, current_path: Path) -> dict[str, str]:
    cur = re.match(r"MOD(\d{2})_NB(\d{2})_", current_path.name)
    nb_num = re.search(r"NB-(\d{2})", nb_key)
    if cur and nb_num:
        scoped = INDEX.get(f"MOD{cur.group(1)}_NB{nb_num.group(1)}", {})
        if scoped:
            return scoped
    return {}


INDEX = build_index()


def format_header(text: str) -> str:
    text = CAPSTONE_TITLE.sub(r"# \3", text)

    m = MODULE_LINE.search(text)
    if m:
        mod = m.group(1)
        text = MODULE_LINE.sub(f"## Module {mod} - Health Analytics with Python", text)
    else:
        m_alt = MODULE_LINE_ALT.search(text)
        if m_alt:
            mod = m_alt.group(1)
            text = MODULE_LINE_ALT.sub(
                f"## Module {mod} - Health Analytics with Python", text
            )

    for match in META_PIPE.finditer(text):
        time_part = match.group(1).strip()
        level_part = match.group(2).strip()
        libs_part = (match.group(3) or "").strip()
        replacement = f"**Estimated time:** {time_part}  \n**Level:** {level_part}  "
        if libs_part:
            replacement += f"\n**Libraries:** {libs_part}"
        text = text.replace(match.group(0), replacement)

    text = re.sub(
        r"\*\*Estimated time:\*\* ([^\n|]+) \| \*\*Level:\*\* ([^\n]+)\n",
        r"**Estimated time:** \1  \n**Level:** \2  \n",
        text,
    )
    return text


def standardize_next(raw: str, current_path: Path) -> str:
    raw = raw.strip().rstrip("*").strip()
    raw = raw.replace("**", "").replace("`", "").strip()
    raw = re.sub(r"\.+$", "", raw).strip()

    mod_match = re.match(r"Module (\d{2})\s*[—\-:·]\s*(.+)", raw, re.I)
    if not mod_match:
        mod_match = re.match(r"Module (\d{2}):\s*(.+)", raw, re.I)
    if mod_match:
        mod, title = mod_match.group(1), mod_match.group(2).strip().rstrip(".")
        if " — " in title:
            title = title.split(" — ", 1)[0].strip()
        return f"**Next:** `Module {mod} · {title}` — begin the next module."

    if raw.startswith("Capstone") or "Capstone ·" in raw:
        title = re.sub(r"^Capstone\s*[—\-·]\s*", "", raw).strip().rstrip(".")
        if " — " in title:
            title, desc = title.split(" — ", 1)
            return f"**Next:** `Capstone · {title.strip()}` — {desc.strip().rstrip('.')}."
        return f"**Next:** `Capstone · {title}` — end-to-end integration notebook."

    nb_match = re.match(r"(NB-\d{2})\s*·\s*(.+)", raw)
    if not nb_match:
        nb_match = re.match(r"(NB-\d{2}):\s*(.+)", raw)
    if nb_match:
        nb_key, rest = nb_match.group(1), nb_match.group(2).strip()
        if " — " in rest:
            title = rest.split(" — ", 1)[0].strip().rstrip(".")
        else:
            title = rest.rstrip(".")
        info = notebook_lookup(nb_key, current_path)
        if not title and info:
            title = info.get("title", title)
        desc = info.get("objective", "continue the module sequence.").rstrip(".")
        return f"**Next:** `{nb_key} · {title}` — {desc}."

    parts = raw.split(":", 1)
    if parts[0].strip().startswith("NB-"):
        nb_key = parts[0].strip()
        info = notebook_lookup(nb_key, current_path)
        title = parts[1].strip().rstrip(".") if len(parts) > 1 else info.get("title", "")
        desc = info.get("objective", "continue the module sequence.").rstrip(".")
        return f"**Next:** `{nb_key} · {title}` — {desc}."

    cur = re.match(r"MOD(\d{2})_NB(\d{2})_", current_path.name)
    if cur:
        mod, nb_num = int(cur.group(1)), int(cur.group(2))
        next_key = f"NB-{nb_num + 1:02d}"
        info = INDEX.get(f"MOD{mod:02d}_NB{nb_num + 1:02d}", {})
        if info:
            desc = info.get("objective", "continue the module sequence.").rstrip(".")
            return f"**Next:** `{next_key} · {info['title']}` — {desc}."

    return f"**Next:** {raw}."


def infer_next_line(current_path: Path) -> str:
    cur = re.match(r"MOD(\d{2})_NB(\d{2})_", current_path.name)
    if not cur:
        return ""
    mod, nb_num = int(cur.group(1)), int(cur.group(2))
    next_info = INDEX.get(f"MOD{mod:02d}_NB{nb_num + 1:02d}")
    if next_info:
        next_key = f"NB-{nb_num + 1:02d}"
        desc = next_info.get("objective", "continue the module sequence.").rstrip(".")
        return f"**Next:** `{next_key} · {next_info['title']}` — {desc}."
    if mod < 8:
        next_mod = f"{mod + 1:02d}"
        mod_info = INDEX.get(f"Module {next_mod}", {})
        title = mod_info.get("title", f"Module {next_mod}")
        return f"**Next:** `Module {next_mod} · {title}` — begin the next module."
    return ""


def capstone_bullets(header_text: str) -> list[str]:
    bullets: list[str] = []
    in_stages = False
    for line in header_text.splitlines():
        if "**Pipeline stages:**" in line or "**Capstone deliverables:**" in line:
            in_stages = True
            continue
        if in_stages:
            if re.match(r"^\d+\.\s+", line.strip()):
                bullets.append(re.sub(r"^\d+\.\s+", "", line.strip()))
            elif line.startswith("**") or line.strip() == "":
                if bullets:
                    break
    return bullets


def past_tense_bullet(text: str) -> str:
    replacements = [
        (r"^Set up\b", "Set up"),
        (r"^Understand\b", "Understood"),
        (r"^Compute\b", "Computed"),
        (r"^Produce\b", "Produced"),
        (r"^Interpret\b", "Interpreted"),
        (r"^Apply\b", "Applied"),
        (r"^Build\b", "Built"),
        (r"^Generate\b", "Generated"),
        (r"^Create\b", "Created"),
        (r"^Load\b", "Loaded"),
        (r"^Read\b", "Read"),
        (r"^Identify\b", "Identified"),
        (r"^Navigate\b", "Navigated"),
        (r"^Decode\b", "Decoded"),
        (r"^Flag\b", "Flagged"),
        (r"^Simulate\b", "Simulated"),
        (r"^Run\b", "Ran"),
        (r"^Use\b", "Used"),
        (r"^Extract\b", "Extracted"),
        (r"^Customise\b", "Customised"),
        (r"^Train\b", "Trained"),
        (r"^Evaluate\b", "Evaluated"),
        (r"^Tune\b", "Tuned"),
        (r"^Fit\b", "Fitted"),
        (r"^Compare\b", "Compared"),
        (r"^Visuali[sz]e\b", "Visualised"),
        (r"^Implement\b", "Implemented"),
        (r"^Deploy\b", "Deployed"),
        (r"^Serve\b", "Served"),
        (r"^Track\b", "Tracked"),
        (r"^Test\b", "Tested"),
        (r"^Document\b", "Documented"),
    ]
    for pattern, repl in replacements:
        if re.match(pattern, text):
            return re.sub(pattern, repl, text, count=1)
    return text


def format_summary_cell(text: str, header_text: str, current_path: Path) -> str:
    bullets = []
    if "## Summary" in text:
        in_summary = False
        for line in text.splitlines():
            if line.strip() == "## Summary":
                in_summary = True
                continue
            if in_summary and line.startswith("- "):
                bullets.append(line[2:].strip())
            elif in_summary and line.startswith("**Next:"):
                break

        next_line = ""
        for line in text.splitlines():
            if line.startswith("**Next:"):
                raw = re.sub(r"^\*\*Next:\*\*\s*", "", line).strip()
                next_line = standardize_next(raw, current_path)
                break

        if bullets or next_line:
            past = [past_tense_bullet(b) for b in bullets] if bullets else []
            if not next_line:
                next_line = infer_next_line(current_path)
            rebuilt = "---\n## Summary\n\n"
            if past:
                rebuilt += "In this notebook you:\n"
                rebuilt += "".join(f"- {b}\n" for b in past)
                rebuilt += "\n"
            if next_line:
                rebuilt += f"{next_line}\n"
            if rebuilt != text:
                return rebuilt
        return text

    bullets = capstone_bullets(header_text) or learning_objective_bullets(header_text)
    next_match = re.search(r"\*\*Next:.*", text)
    next_line = next_match.group(0).strip() if next_match else ""

    if not bullets and not next_line:
        next_line = infer_next_line(current_path)
        if not next_line:
            return text

    summary = "---\n## Summary\n\n"
    if bullets:
        summary += "In this notebook you:\n"
        summary += "".join(f"- {past_tense_bullet(b)}\n" for b in bullets[:7])
        summary += "\n"
    if next_line:
        summary += f"{next_line}\n"
    return summary


def split_semicolon_lines(line: str) -> list[str]:
    if ";" not in line:
        return [line]
    parts = []
    for part in line.split(";"):
        part = part.strip()
        if part:
            parts.append(part)
    return parts


def expand_import_line(line: str) -> list[str]:
    if not line.startswith("import ") or "," not in line:
        return [line]
    body = line[len("import ") :].strip()
    out = []
    for part in body.split(","):
        part = part.strip()
        if part:
            out.append(f"import {part}")
    return out


def normalize_setup_cell(text: str) -> str:
    if "import " not in text:
        return text

    lines = text.splitlines()
    expanded: list[str] = []
    for line in lines:
        if line.startswith("#") or not line.strip():
            expanded.append(line)
            continue
        for sub in split_semicolon_lines(line):
            for imp in expand_import_line(sub):
                expanded.append(imp)

    text = "\n".join(expanded)

    if "warnings.filterwarnings" not in text:
        if "import warnings" not in text:
            # Insert after imports block
            new_lines = []
            inserted = False
            for i, line in enumerate(text.splitlines()):
                new_lines.append(line)
                if not inserted and line.startswith(("import ", "from ")):
                    nxt = text.splitlines()[i + 1] if i + 1 < len(text.splitlines()) else ""
                    if not nxt.startswith(("import ", "from ")):
                        new_lines.append("import warnings")
                        new_lines.append("warnings.filterwarnings('ignore')")
                        inserted = True
            if not inserted:
                new_lines = ["import warnings", "warnings.filterwarnings('ignore')", ""] + new_lines
            text = "\n".join(new_lines)

    if "print(\"Library versions:\")" not in text and "print('Library versions:')" not in text:
        version_lines = []
        if re.search(r"\bimport pandas\b|\bas pd\b", text) and "pd.__version__" not in text:
            version_lines.append('print(f"  pandas  : {pd.__version__}")')
        if re.search(r"\bimport numpy\b|\bas np\b", text) and "np.__version__" not in text:
            version_lines.append('print(f"  numpy   : {np.__version__}")')
        if version_lines:
            text = text.rstrip() + '\n\nprint("Library versions:")\n' + "\n".join(version_lines)
            if "Environment ready" not in text:
                text += '\nprint("Environment ready.")'

    # Ensure pip install comment at top when try/except import pattern exists
    if "except ImportError" in text and not text.lstrip().startswith("# Install"):
        text = "# Install any missing packages (run once)\n# !pip install <packages>\n\n" + text

    text = re.sub(
        r'print\(f?"pandas version: \{pd\.__version__\}"\)\s*\n+print\("Library versions:"\)\s*\n'
        r'print\(f?"  pandas  : \{pd\.__version__\}"\)\s*\n',
        'print("Library versions:")\nprint(f"  pandas  : {pd.__version__}")\n',
        text,
    )

    return text


def format_notebook(path: Path) -> bool:
    with path.open(encoding="utf-8") as f:
        nb = json.load(f)

    changed = False
    cells = nb.get("cells", [])
    if not cells:
        return False

    header_text = cell_text(cells[0]) if cells[0]["cell_type"] == "markdown" else ""
    if cells[0]["cell_type"] == "markdown":
        new_header = format_header(header_text)
        if new_header != header_text:
            set_cell_text(cells[0], new_header)
            header_text = new_header
            changed = True

    for cell in cells[1:5]:
        if cell["cell_type"] == "code" and "import " in cell_text(cell):
            old = cell_text(cell)
            new = normalize_setup_cell(old)
            if new != old:
                set_cell_text(cell, new)
                changed = True
            break

    if cells[-1]["cell_type"] == "markdown":
        old_end = cell_text(cells[-1])
        new_end = format_summary_cell(old_end, header_text, path)
        if new_end != old_end:
            set_cell_text(cells[-1], new_end)
            changed = True

    meta = nb.setdefault("metadata", {})
    ks = meta.setdefault("kernelspec", {})
    target_ks = {"display_name": "Python 3", "language": "python", "name": "python3"}
    if ks != target_ks:
        meta["kernelspec"] = target_ks
        changed = True
    li = meta.setdefault("language_info", {})
    target_li = {"name": "python", "version": "3.10.0"}
    if li != target_li:
        meta["language_info"] = target_li
        changed = True
    if nb.get("nbformat") != 4:
        nb["nbformat"] = 4
        changed = True
    if nb.get("nbformat_minor") != 5:
        nb["nbformat_minor"] = 5
        changed = True

    if changed:
        with path.open("w", encoding="utf-8") as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
            f.write("\n")

    return changed


def main() -> None:
    notebooks = sorted(ROOT.glob("MOD*.ipynb"))
    updated = []
    for path in notebooks:
        if path.name in SKIP:
            continue
        if format_notebook(path):
            updated.append(path.name)

    print(f"Formatted {len(updated)} notebooks:")
    for name in updated:
        print(f"  - {name}")


if __name__ == "__main__":
    main()
