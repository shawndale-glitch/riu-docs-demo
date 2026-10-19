"""Repoint the repository at a new GitHub host, organization and repository name.

Run once, on a branch, right after the repository is pushed to its new home
(for example RIU's GitHub Enterprise Server). It rewrites every tracked text file
that names the old location, then lists anything it couldn't handle.

Usage:
  python tooling/repoint_repo.py --host github.riu.example --org riu-docs --repo RIU-Documentation --dry-run
  python tooling/repoint_repo.py --host github.riu.example --org riu-docs --repo RIU-Documentation
  python tooling/repoint_repo.py --host github.riu.example --org riu-docs --repo RIU-Documentation --artifact-actions v3
  python tooling/repoint_repo.py --check --host github.riu.example --org riu-docs --repo RIU-Documentation

What it rewrites:
  https://github.com/<old-org>/<old-repo>   -> https://<host>/<org>/<repo>
  <old-org>/<old-repo>                      -> <org>/<repo>          (reusable-workflow refs, docs_repo defaults)
  @<old-team-org>/<team>                    -> @<team-org>/<team>    (CODEOWNERS, rules, consumers.yaml)
  actions/upload-artifact@v4, download-artifact@v4 -> @<v>   (only with --artifact-actions)

Exit codes: 0 = clean (or changes written), 1 = --check found leftovers, 2 = usage error.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OLD_HOST = "github.com"
OLD_ORG = "shawndale-glitch"
OLD_REPO = "RIU-Documentation"
OLD_TEAM_ORG = "riu-docs"
TEXT_SUFFIXES = {".md", ".yml", ".yaml", ".json", ".py", ".js", ".txt", ".feature", ""}
SKIP_PARTS = {".git", "site", "dist", ".venv", "node_modules"}
# Files that name the old location on purpose (the runbook's "From" and mirror-clone steps).
KEEP_AS_IS = {"governance/ghes-migration-runbook.md"}


def tracked_files() -> list[Path]:
    try:
        out = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True, check=True).stdout
        files = [REPO / f for f in out.splitlines()]
    except (OSError, subprocess.CalledProcessError):
        files = [p for p in REPO.rglob("*") if p.is_file()]
    return [f for f in files if f.suffix in TEXT_SUFFIXES and not (SKIP_PARTS & set(f.relative_to(REPO).parts))
            and f.name != Path(__file__).name and f.relative_to(REPO).as_posix() not in KEEP_AS_IS]


def rules(a: argparse.Namespace) -> list[tuple[re.Pattern, str]]:
    team_org = a.team_org or a.org
    out = [
        (re.compile(rf"https://{re.escape(OLD_HOST)}/{re.escape(OLD_ORG)}/{re.escape(OLD_REPO)}"),
         f"https://{a.host}/{a.org}/{a.repo}"),
        (re.compile(rf"\b{re.escape(OLD_ORG)}/{re.escape(OLD_REPO)}\b"), f"{a.org}/{a.repo}"),
        (re.compile(rf"@{re.escape(OLD_TEAM_ORG)}/"), f"@{team_org}/"),
    ]
    if a.artifact_actions:
        out.append((re.compile(r"actions/(upload|download)-artifact@v4\b"), rf"actions/\1-artifact@{a.artifact_actions}"))
    return out


def main() -> int:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # Windows consoles default to cp1252
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", required=True, help="new host, e.g. github.riu.example (no https://)")
    ap.add_argument("--org", required=True, help="new organization (owner) of the docs repository")
    ap.add_argument("--repo", default=OLD_REPO, help=f"new repository name (default {OLD_REPO})")
    ap.add_argument("--team-org", default="", help="organization that owns the CODEOWNERS teams (default: --org)")
    ap.add_argument("--artifact-actions", default="", metavar="VERSION",
                    help="rewrite upload/download-artifact@v4 to this version (e.g. v3 on Enterprise Server versions without v4)")
    ap.add_argument("--dry-run", action="store_true", help="show what would change; write nothing")
    ap.add_argument("--check", action="store_true", help="only report references to the old location; exit 1 if any")
    a = ap.parse_args()
    if a.host.startswith("http"):
        print("--host is a host name, without https://", file=sys.stderr)
        return 2

    if a.check:
        old = re.compile(rf"{re.escape(OLD_ORG)}|@{re.escape(OLD_TEAM_ORG)}/" if (a.team_org or a.org) != OLD_TEAM_ORG
                         else rf"{re.escape(OLD_ORG)}")
        left = []
        for f in tracked_files():
            for n, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if old.search(line):
                    left.append(f"{f.relative_to(REPO).as_posix()}:{n}: {line.strip()[:120]}")
        print("\n".join(left) or "No references to the old location.")
        return 1 if left else 0

    changed = 0
    for f in tracked_files():
        text = f.read_text(encoding="utf-8", errors="replace")
        new = text
        hits = 0
        for pat, rep in rules(a):
            new, n = pat.subn(rep, new)
            hits += n
        if hits:
            changed += 1
            print(f"{'would change' if a.dry_run else 'changed'}  {f.relative_to(REPO).as_posix()}  ({hits})")
            if not a.dry_run:
                f.write_text(new, encoding="utf-8", newline="")
    print(f"\n{changed} file(s) {'would change' if a.dry_run else 'changed'}.")
    if not a.dry_run:
        print("Next: python tooling/repoint_repo.py --check ...; mkdocs build --strict; python tooling/selftest.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
