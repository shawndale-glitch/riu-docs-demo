"""Apply the repository governance kept in governance/ to a GitHub repository.

Works on github.com and GitHub Enterprise Server. Idempotent: run it again after any change
to the files below and it brings the repository back in line.

  governance/labels.yaml          labels (+ one area:<folder> label per prefix in areas.yaml)
  governance/rulesets/*.json      branch rulesets (falls back to classic branch protection)
  governance/teams.yaml           with --teams: create missing teams, grant repository permission

Usage:
  GHES_TOKEN=... python tooling/apply_governance.py --host github.riu.example --repo riu-docs/RIU-Documentation --dry-run
  GHES_TOKEN=... python tooling/apply_governance.py --host github.riu.example --repo riu-docs/RIU-Documentation
  GITHUB_TOKEN=... python tooling/apply_governance.py --repo shawndale-glitch/riu-docs-demo --only labels

Token: repository admin for rulesets and protection; org owner for --teams.
--prune also deletes labels that aren't in labels.yaml (GitHub's default labels, for example).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
GOV = REPO / "governance"


class Api:
    def __init__(self, host: str, token: str, dry: bool):
        self.base = "https://api.github.com" if host in ("", "github.com") else f"https://{host}/api/v3"
        self.token, self.dry = token, dry

    def call(self, method: str, path: str, body: dict | None = None):
        if self.dry and method != "GET":
            print(f"  (dry run) {method} {path}" + (f"  {json.dumps(body)[:160]}" if body else ""))
            return 200, None
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base + path, data=data, method=method, headers={
            "Accept": "application/vnd.github+json", "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "riu-docs-governance"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read()
                return r.status, json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.loads(e.read() or b"null")
            except ValueError:
                return e.code, None

    def paged(self, path: str) -> list:
        out, page = [], 1
        while True:
            sep = "&" if "?" in path else "?"
            code, items = self.call("GET", f"{path}{sep}per_page=100&page={page}")
            if code != 200 or not items:
                return out
            out += items
            if len(items) < 100:
                return out
            page += 1


def wanted_labels() -> list[dict]:
    cfg = yaml.safe_load((GOV / "labels.yaml").read_text(encoding="utf-8"))
    labels = list(cfg["labels"])
    areas = yaml.safe_load((GOV / "areas.yaml").read_text(encoding="utf-8")).get("prefixes", {})
    al = cfg.get("area_label", {})
    for prefix, folder in sorted(areas.items(), key=lambda kv: kv[1]):
        labels.append({"name": f"{al.get('prefix', 'area:')}{folder}", "color": al.get("color", "BFD4F2"),
                       "description": f"Process area {prefix} ({folder})"})
    return labels


def apply_labels(api: Api, repo: str, prune: bool) -> None:
    print("Labels")
    have = {l["name"]: l for l in api.paged(f"/repos/{repo}/labels")}
    want = wanted_labels()
    for l in want:
        cur = have.get(l["name"])
        body = {"color": l["color"].lstrip("#"), "description": l.get("description", "")[:100]}
        if not cur:
            api.call("POST", f"/repos/{repo}/labels", {"name": l["name"], **body})
            print(f"  + {l['name']}")
        elif cur.get("color", "").lower() != body["color"].lower() or (cur.get("description") or "") != body["description"]:
            api.call("PATCH", f"/repos/{repo}/labels/{urllib.parse.quote(l['name'], safe='')}", body)
            print(f"  ~ {l['name']}")
    if prune:
        names = {l["name"] for l in want}
        for name in sorted(set(have) - names):
            api.call("DELETE", f"/repos/{repo}/labels/{urllib.parse.quote(name, safe='')}")
            print(f"  - {name}")


def protection_from_ruleset(rs: dict) -> dict:
    """Classic branch protection equivalent of a ruleset, for instances without rulesets."""
    rules = {r["type"]: r.get("parameters", {}) for r in rs["rules"]}
    pr = rules.get("pull_request", {})
    checks = rules.get("required_status_checks", {})
    return {
        "required_status_checks": {
            "strict": checks.get("strict_required_status_checks_policy", True),
            "contexts": [c["context"] for c in checks.get("required_status_checks", [])],
        } if checks else None,
        "enforce_admins": True,
        "required_pull_request_reviews": {
            "required_approving_review_count": pr.get("required_approving_review_count", 1),
            "require_code_owner_reviews": pr.get("require_code_owner_review", True),
            "dismiss_stale_reviews": pr.get("dismiss_stale_reviews_on_push", True),
            "require_last_push_approval": pr.get("require_last_push_approval", False),
        } if pr else None,
        "restrictions": None,
        "allow_force_pushes": "non_fast_forward" not in rules,
        "allow_deletions": "deletion" not in rules,
        "required_conversation_resolution": pr.get("required_review_thread_resolution", False),
    }


def apply_rulesets(api: Api, repo: str) -> None:
    print("Rulesets")
    code, existing = api.call("GET", f"/repos/{repo}/rulesets")
    for f in sorted((GOV / "rulesets").glob("*.json")):
        rs = json.loads(f.read_text(encoding="utf-8"))
        if code == 200:
            match = next((r for r in existing or [] if r.get("name") == rs["name"]), None)
            if match:
                api.call("PUT", f"/repos/{repo}/rulesets/{match['id']}", rs)
                print(f"  ~ {rs['name']}")
            else:
                api.call("POST", f"/repos/{repo}/rulesets", rs)
                print(f"  + {rs['name']}")
        elif code == 404:
            _, info = api.call("GET", f"/repos/{repo}")
            branch = (info or {}).get("default_branch", "main")
            print(f"  rulesets not available on this instance; applying '{rs['name']}' as branch protection on {branch}")
            pc, body = api.call("PUT", f"/repos/{repo}/branches/{branch}/protection", protection_from_ruleset(rs))
            if pc not in (200, 201):
                print(f"  ! branch protection failed ({pc}): {body}")
        else:
            print(f"  ! could not read rulesets ({code}): {existing}")
            return


def apply_teams(api: Api, repo: str) -> None:
    print("Teams")
    org = repo.split("/")[0]
    for t in yaml.safe_load((GOV / "teams.yaml").read_text(encoding="utf-8"))["teams"]:
        code, _ = api.call("GET", f"/orgs/{org}/teams/{t['slug']}")
        if code == 404:
            api.call("POST", f"/orgs/{org}/teams", {"name": t["slug"], "description": t["description"], "privacy": "closed"})
            print(f"  + @{org}/{t['slug']}")
        api.call("PUT", f"/orgs/{org}/teams/{t['slug']}/repos/{repo}", {"permission": t["permission"]})
        print(f"  = @{org}/{t['slug']} → {t['permission']}")


def main() -> int:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # Windows consoles default to cp1252
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="github.com", help="github.com (default) or the Enterprise Server host name")
    ap.add_argument("--repo", required=True, help="OWNER/NAME")
    ap.add_argument("--only", choices=["labels", "rulesets", "teams"], help="apply one part only")
    ap.add_argument("--teams", action="store_true", help="also create teams and grant permissions (org owner)")
    ap.add_argument("--prune", action="store_true", help="delete labels not in labels.yaml")
    ap.add_argument("--dry-run", action="store_true", help="read the repository, print the writes, change nothing")
    a = ap.parse_args()
    token = os.environ.get("GHES_TOKEN") or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN", "")
    if not token:
        print("Set GHES_TOKEN (or GITHUB_TOKEN) to a token with admin on the repository.", file=sys.stderr)
        return 2
    api = Api(a.host, token, a.dry_run)
    code, _ = api.call("GET", f"/repos/{a.repo}")
    if code != 200:
        print(f"Repository {a.repo} not reachable on {api.base} ({code}).", file=sys.stderr)
        return 1
    if a.only in (None, "labels"):
        apply_labels(api, a.repo, a.prune)
    if a.only in (None, "rulesets"):
        apply_rulesets(api, a.repo)
    if a.only == "teams" or (a.only is None and a.teams):
        apply_teams(api, a.repo)
    return 0


if __name__ == "__main__":
    sys.exit(main())
