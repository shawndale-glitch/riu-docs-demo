"""Check a GitHub Enterprise Server instance against what this repository needs, before or after migrating.

Read-only: it only calls GET endpoints. Run it from any machine that can reach the instance.

Usage:
  GHES_TOKEN=... python tooling/ghes_preflight.py --host github.riu.example
  GHES_TOKEN=... python tooling/ghes_preflight.py --host github.riu.example --repo riu-docs/RIU-Documentation --report preflight.md

Token: a personal access token on the instance. `repo` scope is enough for the checks;
`admin:org` adds the team check. Nothing is written to the instance.

Checks:
  P1  Instance reachable; version reported by /meta
  P2  Every `uses:` action in .github/workflows exists on the instance at the pinned ref
  P3  Feature thresholds by version (repository rulesets)                           [verify against release notes]
  P4  (--repo) Repository exists; default branch; Actions enabled; self-hosted runners online
  P5  (--repo) GitHub Pages configured, and whether the site is public
  P6  (--repo) CODEOWNERS teams exist in the organization
  M*  Manual items that can't be checked over the API (runner egress, Python on runners)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Minimum Enterprise Server versions for features this repo relies on.
# These are planning values: confirm each against the GHES release notes for the version RIU installs.
FEATURES = {
    "Repository rulesets (governance/rulesets/*.json)": "3.11",
}

MANUAL = [
    "M1  Runners can reach https://api.figma.com (workflow intake exports boards from Figma).",
    "M2  Runners can reach https://pypi.org and https://files.pythonhosted.org, or an internal mirror is set in pip.conf.",
    "M3  Python 3.12 is available to actions/setup-python on the runners (tool cache or GitHub Connect), or preinstalled.",
    "M4  The `gh` CLI is installed on the runners (intake, release and conformance jobs call it).",
    "M5  Repository variable RUNNER_LABELS is set to the runners' labels, e.g. [\"self-hosted\",\"linux\"].",
    "M6  Actions cache storage is configured on the instance (setup-python `cache: pip`), or remove `cache: pip`.",
]


class Api:
    def __init__(self, host: str, token: str):
        self.base = f"https://{host}/api/v3"
        self.token = token

    def get(self, path: str):
        req = urllib.request.Request(self.base + path, headers={
            "Accept": "application/vnd.github+json", "Authorization": f"Bearer {self.token}",
            "User-Agent": "riu-docs-preflight"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.status, json.loads(r.read() or b"null")
        except urllib.error.HTTPError as e:
            return e.code, None
        except (urllib.error.URLError, TimeoutError) as e:
            return 0, str(e)


def ver_tuple(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in re.findall(r"\d+", v)[:2])


def workflow_actions() -> list[tuple[str, str]]:
    seen = set()
    for f in sorted((REPO / ".github" / "workflows").glob("*.yml")):
        code = "\n".join(l for l in f.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("#"))
        for m in re.finditer(r"uses:\s*([\w.-]+/[\w.-]+)(?:/[^@\s]*)?@([\w.-]+)", code):
            if m.group(1).count("/") == 1 and not m.group(1).startswith("./"):
                seen.add((m.group(1), m.group(2)))
    return sorted(seen)


def codeowners_teams() -> list[str]:
    path = REPO / ".github" / "CODEOWNERS"
    return sorted(set(re.findall(r"@([\w-]+/[\w-]+)", path.read_text(encoding="utf-8")))) if path.exists() else []


def main() -> int:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # Windows consoles default to cp1252
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", required=True, help="instance host name, without https://")
    ap.add_argument("--repo", default="", help="OWNER/NAME of the migrated docs repository (enables P4–P6)")
    ap.add_argument("--report", help="also write a Markdown report")
    a = ap.parse_args()
    token = os.environ.get("GHES_TOKEN", "")
    if not token:
        print("Set GHES_TOKEN to a personal access token on the instance.", file=sys.stderr)
        return 2
    api = Api(a.host, token)
    lines: list[str] = []
    fails = 0

    def out(status: str, text: str):
        nonlocal fails
        fails += status == "FAIL"
        lines.append(f"| {status} | {text} |")

    code, meta = api.get("/meta")
    if code != 200:
        out("FAIL", f"P1 `{api.base}/meta` answered {code or meta}. Check the host name, VPN and token.")
        print("\n".join(lines))
        return 1
    else:
        version = (meta or {}).get("installed_version", "")
        out("PASS", f"P1 Instance reachable; version {version or 'not reported'}")

    for name, ref in workflow_actions():
        c, _ = api.get(f"/repos/{name}/commits/{ref}")
        out("PASS" if c == 200 else "FAIL",
            f"P2 `{name}@{ref}` {'available' if c == 200 else f'not found on the instance ({c}). Sync it (actions-sync / GitHub Connect) or pin a version that exists'}")

    if version:
        for feat, minv in FEATURES.items():
            ok = ver_tuple(version) >= ver_tuple(minv)
            out("PASS" if ok else "WARN", f"P3 {feat}: needs ≥ {minv} (planning value), instance has {version}")

    if a.repo:
        c, repo = api.get(f"/repos/{a.repo}")
        if c != 200:
            out("FAIL", f"P4 Repository `{a.repo}` not found ({c})")
        else:
            out("PASS", f"P4 Repository `{a.repo}` found; default branch `{repo.get('default_branch')}`")
            c, perms = api.get(f"/repos/{a.repo}/actions/permissions")
            if c == 200:
                out("PASS" if perms.get("enabled") else "FAIL", f"P4 Actions {'enabled' if perms.get('enabled') else 'disabled'} for the repository")
            c, runners = api.get(f"/repos/{a.repo}/actions/runners")
            if c == 200:
                online = [r["name"] for r in runners.get("runners", []) if r.get("status") == "online"]
                out("PASS" if online else "WARN", f"P4 Repository-level runners online: {', '.join(online) or 'none (org or enterprise runners may still serve it)'}")
            else:
                out("INFO", f"P4 Runner list not readable ({c}); needs admin on the repository")
            c, pages = api.get(f"/repos/{a.repo}/pages")
            if c == 200:
                public = pages.get("public")
                out("PASS", f"P5 Pages configured: {pages.get('html_url')} (build type {pages.get('build_type')}; "
                            f"{'PUBLIC' if public else 'visible to signed-in users only' if public is False else 'visibility not reported'})")
            else:
                out("INFO", f"P5 Pages not configured yet ({c}). See decision 1 in governance/decision-brief.md")
            org = a.repo.split("/")[0]
            for team in codeowners_teams():
                t_org, slug = team.split("/")
                c, _ = api.get(f"/orgs/{t_org}/teams/{slug}")
                out("PASS" if c == 200 else "FAIL" if c == 404 else "INFO",
                    f"P6 Team `@{team}` {'exists' if c == 200 else 'missing' if c == 404 else f'not checked ({c}); needs read:org'}"
                    + (f" (CODEOWNERS org `{t_org}` differs from repo org `{org}`)" if t_org != org else ""))

    report = ["# GHES preflight", "", f"Instance: `{a.host}`" + (f" · repository `{a.repo}`" if a.repo else ""), "",
              "| Result | Check |", "|---|---|", *lines, "", "## Manual checks", "", *[f"- [ ] {m}" for m in MANUAL]]
    text = "\n".join(report) + "\n"
    print(text)
    if a.report:
        Path(a.report).write_text(text, encoding="utf-8")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
