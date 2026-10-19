"""Block personal data, and (during the POC) RIU company data, from entering the repository.

Rules: governance/sensitive-data.yaml.

Usage:
  python tooling/sensitive_scan.py                 # every tracked file
  python tooling/sensitive_scan.py FILE [FILE...]  # given files (pre-commit passes staged files)
  python tooling/sensitive_scan.py --report sensitive-report.md

Exit 1 when anything is found. Findings print as path:line, the rule, and a masked value,
so the report itself never repeats the data.
"""
from __future__ import annotations

import argparse
import fnmatch
import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
CONFIG = REPO / "governance" / "sensitive-data.yaml"
BINARY_SKIP = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".svg", ".woff", ".woff2", ".zip", ".bundle"}


def luhn_ok(digits: str) -> bool:
    d = [int(c) for c in digits][::-1]
    total = sum(d[0::2]) + sum(sum(divmod(2 * x, 10)) for x in d[1::2])
    return total % 10 == 0


def mask(v: str) -> str:
    v = v.strip()
    return v if len(v) <= 4 else v[:2] + "*" * (len(v) - 4) + v[-2:]


def allowed(rel: str, globs: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel, g) for g in globs)


def files_to_scan(args: list[str]) -> list[Path]:
    if args:
        return [Path(a).resolve() for a in args if Path(a).is_file()]
    out = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True, check=True).stdout
    return [REPO / f for f in out.splitlines() if (REPO / f).is_file()]


def scan(paths: list[Path], cfg: dict) -> list[str]:
    poc = cfg.get("phase", "poc") == "poc"
    poc_cfg = cfg.get("poc_only", {}) if poc else {}
    allow_paths = cfg.get("allow_paths", [])
    allow_values = set(cfg.get("allow_values", []))
    pats = {k: (re.compile(v["regex"]), v) for k, v in cfg.get("patterns", {}).items()}
    if poc_cfg.get("company_email_domains"):
        doms = "|".join(re.escape(d) for d in poc_cfg["company_email_domains"])
        pats["company_email"] = (re.compile(rf"\b[\w.+-]+@(?:[\w-]+\.)*(?:{doms})\b", re.I), {"what": "company e-mail address"})
    markers = [m.lower() for m in poc_cfg.get("classification_markers", [])]
    blocked_types = {t.lower() for t in poc_cfg.get("blocked_file_types", [])}

    findings = []
    for p in paths:
        try:
            rel = p.relative_to(REPO).as_posix()
        except ValueError:
            rel = p.as_posix()
        if allowed(rel, allow_paths):
            continue
        if p.suffix.lower() in blocked_types:
            findings.append(f"{rel}: blocked file type `{p.suffix}` (POC phase: source documents stay out of this repo)")
            continue
        if p.suffix.lower() in BINARY_SKIP:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            low = line.lower()
            for m in markers:
                if m in low:
                    findings.append(f"{rel}:{n}: classification marker \"{m.upper()}\"")
            for key, (rx, meta) in pats.items():
                for hit in rx.finditer(line):
                    v = hit.group(0)
                    if v in allow_values:
                        continue
                    if meta.get("luhn"):
                        digits = re.sub(r"\D", "", v)
                        if not (13 <= len(digits) <= 19 and luhn_ok(digits)):
                            continue
                    findings.append(f"{rel}:{n}: {meta.get('what', key)} `{mask(v)}`")
    return findings


def main() -> int:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # Windows consoles default to cp1252
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*")
    ap.add_argument("--report", help="also write a Markdown report")
    a = ap.parse_args()
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    findings = scan(files_to_scan(a.files), cfg)
    head = f"Sensitive-data scan ({cfg.get('phase', 'poc')} phase): {len(findings)} finding(s)"
    print(head)
    for f in findings:
        print("  " + f)
    if a.report:
        body = [f"## {head}", ""] + [f"- {f}" for f in findings]
        if findings:
            body += ["", "Remove the data, or — if it is a false positive — add the exact value to `allow_values` "
                     "in `governance/sensitive-data.yaml` in the same pull request, with a reason."]
        Path(a.report).write_text("\n".join(body) + "\n", encoding="utf-8")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
