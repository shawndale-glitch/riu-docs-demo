"""Check product names and house terms in Markdown. Rules: governance/terms.yaml.

Usage:
  python tooling/terms_check.py                  # docs/, README.md, CONTRIBUTING.md, governance/*.md
  python tooling/terms_check.py FILE [FILE...]   # given Markdown files (pre-commit)

Skips fenced code blocks, inline `code`, URLs and the generated regions of process pages
(their text comes from FigJam labels; fix it on the board). Exit 1 on any error-severity finding.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
DEFAULT = ["docs/**/*.md", "README.md", "CONTRIBUTING.md", "governance/**/*.md"]
GEN_START, GEN_END = "<!-- generated:start", "<!-- generated:end"
STRIP = re.compile(r"\"[^\"\n]*\"|`[^`]*`|\]\([^)]*\)|<https?://[^>]*>|https?://\S+")


def files(args: list[str]) -> list[Path]:
    if args:
        return [Path(a).resolve() for a in args if a.endswith(".md") and Path(a).is_file()]
    out: list[Path] = []
    for g in DEFAULT:
        out += sorted(REPO.glob(g))
    return out


def check(path: Path, rules: list[dict]) -> list[tuple[str, str]]:
    found = []
    fence = generated = False
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        s = line.strip()
        if s.startswith(GEN_START):
            generated = True
        if s.startswith(GEN_END):
            generated = False
            continue
        if s.startswith(("```", "~~~")):
            fence = not fence
            continue
        if fence or generated:
            continue
        text = STRIP.sub(" ", line)
        for r in rules:
            for m in r["rx"].finditer(text):
                try:
                    rel = path.relative_to(REPO).as_posix()
                except ValueError:
                    rel = path.as_posix()
                found.append((r["severity"], f"{rel}:{n}: \"{m.group(0)}\" → {r['right']}"))
    return found


def main() -> int:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # Windows consoles default to cp1252
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*")
    a = ap.parse_args()
    cfg = yaml.safe_load((REPO / "governance" / "terms.yaml").read_text(encoding="utf-8"))
    rules = [{**t, "rx": re.compile(t["wrong"], re.I if t.get("ignore_case") else 0)} for t in cfg["terms"]]
    findings = [f for p in files(a.files) for f in check(p, rules)]
    errors = [m for s, m in findings if s == "error"]
    warnings = [m for s, m in findings if s != "error"]
    for m in errors:
        print("error    " + m)
    for m in warnings:
        print("warning  " + m)
    print(f"Terms check: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
