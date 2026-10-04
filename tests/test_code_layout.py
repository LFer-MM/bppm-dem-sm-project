"""Enforce the file layout in docs/source/docstring_style.rst on every Python file.

Top-level code after the imports must follow a fixed section order, and files
with more than one section must label each one with a standard divider.
"""

from __future__ import annotations

import ast
from pathlib import Path
import re

import pytest

# --- Setup -------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_SECTIONS = [
    "Constants",
    "Module state",
    "Public classes",
    "Public functions",
    "Private classes",
    "Private helper functions",
    "Script entry point",
]
TEST_SECTIONS = ["Setup", "Helpers", "Tests"]
DIVIDER = re.compile(r"^# --- (?P<name>[^:]+?)(?:: (?P<qualifier>.+?))? -+$")
# Scripts whose top-level statements must run in a fixed order.
EXEMPT = {"bppm_dem_sm/__main__.py"}
FILES = sorted(
    p.relative_to(REPO_ROOT).as_posix()
    for root in ("bppm_dem_sm", "tests")
    for p in (REPO_ROOT / root).rglob("*.py")
)


# --- Helpers -----------------------------------------------------------------


def _allowed_sections(node, is_test):
    """Return the sections a top-level statement may belong to."""
    if isinstance(node, ast.If) and "__name__" in ast.unparse(node.test):
        return set() if is_test else {"Script entry point"}
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        if is_test:
            return {"Tests"} if node.name.startswith(("test_", "Test")) else {"Helpers"}
        private = node.name.startswith("_")
        if isinstance(node, ast.ClassDef):
            return {"Private classes" if private else "Public classes"}
        return {"Private helper functions" if private else "Public functions"}
    if isinstance(node, (ast.Assign, ast.AnnAssign)):
        return {"Setup"} if is_test else {"Constants", "Module state"}
    return set()


def _layout_problems(rel):
    """Return a list of layout violations in the file at ``rel``."""
    is_test = Path(rel).name.startswith("test_")
    order = TEST_SECTIONS if is_test else PACKAGE_SECTIONS
    lines = (REPO_ROOT / rel).read_text().splitlines()
    tree = ast.parse("\n".join(lines))
    imports = [i for i, n in enumerate(tree.body) if isinstance(n, (ast.Import, ast.ImportFrom))]
    first = imports[-1] + 1 if imports else (1 if ast.get_docstring(tree) else 0)
    body = tree.body[first:]
    preamble_end = tree.body[first - 1].end_lineno if first else 0

    problems = []
    dividers = {}  # line number -> section name
    for i, line in enumerate(lines, 1):
        if line.startswith("# ---"):
            m = DIVIDER.match(line)
            if not m or m["name"] not in order or len(line) != 79:
                problems.append(f"line {i}: malformed or unknown divider {line!r}")
            elif i <= preamble_end:
                problems.append(f"line {i}: divider inside the import preamble")
            else:
                dividers[i] = m["name"]

    allowed = [_allowed_sections(n, is_test) for n in body]
    for n, sections in zip(body, allowed):
        if not sections:
            problems.append(f"line {n.lineno}: top-level statement fits no section")
    if problems:
        return problems

    kinds = {next(iter(s)) for s in allowed if len(s) == 1}
    # Assignments fit two sections, so constants plus any other kind means "several".
    multi = len(kinds) > 1 or (any(len(s) > 1 for s in allowed) and len(kinds) > 0)
    if not dividers:
        if multi:
            problems.append("file has several sections but no dividers")
        # Single section without dividers: still check nothing is out of order.
        return problems

    last_rank = -1
    for n, sections in zip(body, allowed):
        above = [ln for ln in dividers if ln < n.lineno]
        if not above:
            problems.append(f"line {n.lineno}: statement before the first divider")
            continue
        section = dividers[max(above)]
        if section not in sections:
            problems.append(f"line {n.lineno}: belongs in {sorted(sections)}, found under {section!r}")
        rank = order.index(section)
        if rank < last_rank:
            problems.append(f"line {n.lineno}: section {section!r} is out of order")
        last_rank = max(last_rank, rank)
    if len(set(dividers.values())) == 1:
        problems.append("single-section file should not have dividers")
    return problems


# --- Tests -------------------------------------------------------------------


@pytest.mark.parametrize("rel", [f for f in FILES if f not in EXEMPT])
def test_file_follows_section_layout(rel):
    assert _layout_problems(rel) == []
