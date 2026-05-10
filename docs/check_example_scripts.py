#!/usr/bin/env python
"""Validate consistency between RST doc files and docs/example_scripts/.

Rules (hard errors):
  - Every active ``.. script location: PATH`` reference must point to an
    existing file under docs/.
  - Every code block that immediately follows a ``.. script location:`` comment
    must appear verbatim as a substring of the referenced script file.

Warnings (non-fatal):
  - Any .py file in example_scripts/ that is neither actively referenced
    (``.. script location:``) nor explicitly excluded (``.. .. script location:``)
    is reported so it can be documented or excluded deliberately.

RST convention used in this project:

    .. script location: example_scripts/some_script.py
    .. code-block:: python

        code here ...

The ``.. script location:`` line must be immediately followed by the
``.. code-block:: python`` directive.  The indented block (4 spaces) is
extracted and its content is searched for in the .py file.
"""

import re
import sys
from pathlib import Path

DOCS_DIR = Path(__file__).parent
SCRIPTS_DIR = DOCS_DIR / "example_scripts"

# Collect RST source files, skipping build output
rst_files = sorted(f for f in DOCS_DIR.rglob("*.rst") if "build" not in f.parts)


def extract_code_blocks(rst_file: Path) -> list[tuple[str, str]]:
    """Return (script_path, code_block_text) pairs from *rst_file*.

    Only active (single ``..``) script-location comments are included.
    The code block text has its 4-space RST indent stripped and trailing
    blank lines removed.
    """
    lines = rst_file.read_text().splitlines()
    pairs: list[tuple[str, str]] = []
    i = 0
    while i < len(lines):
        # Active script location — single dot-dot, NOT double dot-dot
        m = re.match(r"\.\.\s+script location:\s+(\S+)", lines[i])
        if m:
            script_path = m.group(1)
            i += 1
            # The very next line must be the code-block directive
            if i < len(lines) and re.match(r"\.\.\s+code-block::\s+python", lines[i]):
                i += 1  # skip the code-block line
                # Skip blank lines before the indented content
                while i < len(lines) and not lines[i].strip():
                    i += 1
                # Collect lines that are indented (≥4 spaces) or blank
                code_lines: list[str] = []
                while i < len(lines) and (lines[i].startswith("    ") or not lines[i].strip()):
                    code_lines.append(lines[i])
                    i += 1
                # Strip trailing blank lines
                while code_lines and not code_lines[-1].strip():
                    code_lines.pop()
                # Remove the 4-space RST indent
                code_text = "\n".join(line[4:] if line.startswith("    ") else "" for line in code_lines)
                pairs.append((script_path, code_text))
            continue
        i += 1
    return pairs


def normalise(text: str) -> str:
    """Strip trailing whitespace from each line for robust comparison."""
    return "\n".join(line.rstrip() for line in text.splitlines())


# ── Collect all references ────────────────────────────────────────────────────

all_code_blocks: list[tuple[Path, str, str]] = []  # (rst_file, script_path, code)
active_names: set[str] = set()
excluded_names: set[str] = set()

for rst_file in rst_files:
    for line in rst_file.read_text().splitlines():
        m = re.match(r"\.\.\s+\.\.\s+script location:\s+(\S+)", line)
        if m:
            excluded_names.add(Path(m.group(1)).name)
    for script_path, code in extract_code_blocks(rst_file):
        active_names.add(Path(script_path).name)
        all_code_blocks.append((rst_file, script_path, code))

# ── Checks ────────────────────────────────────────────────────────────────────

errors: list[str] = []
warnings: list[str] = []

for rst_file, script_path, code_block in all_code_blocks:
    full_path = DOCS_DIR / script_path

    # 1. Referenced file must exist
    if not full_path.exists():
        errors.append(f"{rst_file.name}: referenced script not found: docs/{script_path}")
        continue

    # 2. Code block must appear verbatim in the script
    script_text = normalise(full_path.read_text())
    norm_block = normalise(code_block)
    if norm_block not in script_text:
        # Find first differing line for a useful error message
        block_lines = norm_block.splitlines()
        errors.append(
            f"{rst_file.name}: code block not found in docs/{script_path}\n"
            + "\n".join(f"  | {line}" for line in block_lines[:8])
            + ("\n  | ..." if len(block_lines) > 8 else "")
        )

# Warning: script exists but has no reference of any kind
for script in sorted(SCRIPTS_DIR.glob("*.py")):
    if script.name not in active_names and script.name not in excluded_names:
        warnings.append(
            f"Script has no doc reference — add '.. script location:' or "
            f"'.. .. script location:' to mark it excluded: example_scripts/{script.name}"
        )

# ── Report ────────────────────────────────────────────────────────────────────

for w in warnings:
    print(f"WARNING: {w}")

if errors:
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)

print(
    f"OK: {len(active_names)} active script(s), {len(excluded_names)} excluded"
    + (f", {len(warnings)} warning(s)" if warnings else "")
)
