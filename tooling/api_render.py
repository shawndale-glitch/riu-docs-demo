"""Render an OpenAPI spec (and optionally its AsyncAPI events) into an API reference page.

The spec under docs/api/specs/ is the source of truth. This script regenerates the block between
the generated markers and keeps any hand-written text around it, so the reference can't drift from
the spec and is searchable on the site. The raw spec files are published next to the page.

Usage:
  python tooling/api_render.py docs/api/specs/<name>.openapi.yaml [--asyncapi docs/api/specs/<name>.asyncapi.yaml]
                               [--out docs/api/<name>.md] [--check]

--check exits 1 if the page is out of date (for CI) instead of writing it.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
GEN_START = "<!-- generated:start api (tooling/api_render.py; edit the spec, not this block) -->"
GEN_END = "<!-- generated:end api -->"
METHODS = ("get", "post", "put", "patch", "delete")


def _resolve(spec: dict, node):
    while isinstance(node, dict) and "$ref" in node:
        cur = spec
        for part in node["$ref"].lstrip("#/").split("/"):
            cur = cur[part]
        node = cur
    return node


def _type(spec: dict, s) -> str:
    s = _resolve(spec, s or {})
    if "enum" in s:
        return " \\| ".join(f"`{v}`" for v in s["enum"])
    if s.get("type") == "array":
        return f"array of {_type(spec, s.get('items'))}"
    t = s.get("type", "object")
    return f"{t} ({s['format']})" if s.get("format") else t


def _props(spec: dict, schema) -> list[str]:
    schema = _resolve(spec, schema or {})
    req = set(schema.get("required", []))
    rows = []
    for name, p in (schema.get("properties") or {}).items():
        rows.append(f"| `{name}` | {_type(spec, p)} | {'Yes' if name in req else 'No'} | {_resolve(spec, p).get('description', '')} |")
    return rows


def _rel(p: Path, out: Path) -> str:
    return Path(*([".."] * (len(out.relative_to(ROOT / "docs").parts) - 1)), p.relative_to(ROOT / "docs")).as_posix()


def render(spec_path: Path, async_path: Path | None, out: Path) -> str:
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    info = spec.get("info", {})
    digest = hashlib.sha256(spec_path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:12]  # same on Windows and Linux checkouts
    L = [
        "| | |", "|---|---|",
        f"| Spec | [`{spec_path.name}`]({_rel(spec_path, out)}) (OpenAPI {spec.get('openapi', '?')}) |",
        f"| API version | `{info.get('version', '?')}` |",
        f"| Base URL | `{(spec.get('servers') or [{}])[0].get('url', 'TBC')}` |",
        f"| Spec SHA-256 | `{digest}…` |",
        "",
        "## Operations", "",
        "| Operation ID | Method and path | Summary |", "|---|---|---|",
    ]
    ops = []
    for path, item in (spec.get("paths") or {}).items():
        for m in METHODS:
            if m in (item or {}):
                ops.append((path, m, item[m]))
    for path, m, op in ops:
        oid = op.get("operationId", "?")
        L.append(f"| [`{oid}`](#{oid.lower()}) | `{m.upper()} {path}` | {op.get('summary', '')} |")
    L.append("")
    for path, m, op in ops:
        oid = op.get("operationId", "?")
        L += [f"### {oid}", "", f"`{m.upper()} {path}`", ""]
        if op.get("description"):
            L += [op["description"].strip(), ""]
        params = [_resolve(spec, p) for p in op.get("parameters", [])]
        if params:
            L += ["| Parameter | In | Type | Required | Description |", "|---|---|---|---|---|"]
            L += [f"| `{p['name']}` | {p['in']} | {_type(spec, p.get('schema'))} | {'Yes' if p.get('required') else 'No'} | {p.get('description', '')} |" for p in params]
            L.append("")
        body = (((op.get("requestBody") or {}).get("content") or {}).get("application/json") or {}).get("schema")
        if body:
            L += ["Request body:", "", "| Field | Type | Required | Description |", "|---|---|---|---|"] + _props(spec, body) + [""]
        L += ["| Response | Description |", "|---|---|"]
        for code, r in (op.get("responses") or {}).items():
            L.append(f"| `{code}` | {_resolve(spec, r).get('description', '')} |")
        L.append("")

    schemas = (spec.get("components") or {}).get("schemas") or {}
    if schemas:
        L += ["## Schemas", ""]
        for name, s in schemas.items():
            L += [f"### {name}", "", "| Field | Type | Required | Description |", "|---|---|---|---|"]
            L += _props(spec, s) + [""]

    if async_path:
        a = yaml.safe_load(async_path.read_text(encoding="utf-8"))
        L += ["## Events", "",
              f"From [`{async_path.name}`]({_rel(async_path, out)}) (AsyncAPI {a.get('asyncapi', '?')}, version `{a.get('info', {}).get('version', '?')}`).", "",
              "| Channel | Message | Description |", "|---|---|---|"]
        for ch, c in (a.get("channels") or {}).items():
            msg = _resolve(a, ((c.get("subscribe") or c.get("publish") or {}).get("message")) or {})
            L.append(f"| `{ch}` | `{msg.get('name', '?')}` | {c.get('description', '')} |")
        L.append("")
    return f"{GEN_START}\n\n" + "\n".join(L).strip() + f"\n\n{GEN_END}"


def page(spec_path: Path, block: str) -> str:
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    info = spec.get("info", {})
    return f"""# {info.get('title', spec_path.stem)}

{(info.get('description') or '').strip()}

{block}

## Related topics

- [API reference](index.md)
- [Identifier glossary](../reference/identifier-glossary.md)
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("spec")
    ap.add_argument("--asyncapi")
    ap.add_argument("--out")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    spec = Path(a.spec).resolve()
    out = Path(a.out).resolve() if a.out else ROOT / "docs" / "api" / (spec.name.split(".")[0] + ".md")
    block = render(spec, Path(a.asyncapi).resolve() if a.asyncapi else None, out)
    before = out.read_text(encoding="utf-8") if out.exists() else None
    if before and GEN_START in before:
        after = re.sub(re.escape(GEN_START) + r".*?" + re.escape(GEN_END), lambda _m: block, before, flags=re.S)
    else:
        after = page(spec, block)
    rel = out.relative_to(ROOT).as_posix()
    if before == after:
        print(f"{rel} is up to date")
        return 0
    if a.check:
        print(f"{rel} is out of date with {spec.name}; run tooling/api_render.py", file=sys.stderr)
        return 1
    out.write_text(after, encoding="utf-8", newline="\n")
    print(f"Wrote {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
