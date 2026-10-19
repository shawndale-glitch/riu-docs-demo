"""Import a RUMBO to OPERA Cloud shell workbook into its building-block page.

Decision D-001 (docs/mapping/decision-log.md): the workbook is authoritative for field-level rows.
This script regenerates the generated blocks of the page (summary, field mapping, rules and code
lookups) and leaves every hand-written section as it is. A new page is created with the hand-written
sections stubbed as TBC.

Usage:
  python tooling/mapping_import.py path/to/shell-workbook.xlsx [--slug guest-profile] [--dry-run] [--report r.md]

Exit 1 and nothing written if the workbook breaks a rule (M1-M7). The workbook itself never enters
the repository: the page records its file name, version, date and SHA-256 instead.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent.parent
MAPPING = ROOT / "docs" / "mapping"
LOG = MAPPING / "decision-log.md"
INDEX = MAPPING / "index.md"

GEN_START = "<!-- generated:start {name} (tooling/mapping_import.py; edit the workbook, not this block) -->"
GEN_END = "<!-- generated:end {name} -->"

# Sheet and column names: Spanish as delivered, English accepted too.
SHEETS = {"cover": ("Portada", "Cover"), "fields": ("Campos", "Fields"), "rules": ("Reglas y códigos", "Rules and codes")}
COVER = {
    "block": ("Bloque RUMBO", "RUMBO building block"),
    "module": ("Módulo RUMBO", "RUMBO module"),
    "target": ("Objeto OPERA Cloud", "OPERA Cloud object"),
    "api": ("API OPERA Cloud", "OPERA Cloud API"),
    "scope": ("Alcance", "Scope"),
    "sor": ("Sistema de registro tras la migración", "System of record after migration"),
    "sme": ("Responsable (SME)", "SME"),
    "version": ("Versión", "Version"),
    "date": ("Fecha", "Date"),
    "status": ("Estado", "Status"),
}
FIELD_COLS = {
    "rumbo": ("Campo RUMBO", "RUMBO field"),
    "desc": ("Descripción", "Description"),
    "opera": ("Campo OPERA Cloud", "OPERA Cloud field"),
    "rule": ("Regla", "Rule"),
    "idtype": ("Tipo de identificador", "Identifier type"),
    "required": ("Obligatorio en OPERA", "Required in OPERA Cloud"),
    "status": ("Estado", "Status"),
    "ref": ("Gap / Decisión", "Gap / Decision"),
    "notes": ("Notas", "Notes"),
}
RULE_COLS = {
    "id": ("Regla", "Rule"),
    "name": ("Nombre", "Name"),
    "from": ("Valor RUMBO", "RUMBO value"),
    "meaning": ("Significado", "Meaning"),
    "to": ("Valor OPERA Cloud", "OPERA Cloud value"),
    "notes": ("Notas", "Notes"),
}
FIELD_STATUS = {"Mapped", "Transform", "Gap", "Not migrated", "TBC"}
PAGE_STATUS = {"Sin empezar": "Not started", "En curso": "In progress", "En revisión": "In review",
               "Validado": "Validated", "Not started": "Not started", "In progress": "In progress",
               "In review": "In review", "Validated": "Validated"}
REQUIRED_COVER = ("block", "target", "version", "date")
REQUIRED_COLS = ("rumbo", "opera", "rule", "status", "ref")


# ---------------------------------------------------------------- reading

def _s(v) -> str:
    if v is None:
        return ""
    if isinstance(v, (datetime, date)):
        return v.strftime("%Y-%m-%d")
    return re.sub(r"\s+", " ", str(v)).strip()


def _sheet(wb, key):
    for name in SHEETS[key]:
        if name in wb.sheetnames:
            return wb[name]
    return None


def _table(ws, cols: dict, findings: list, sheet: str) -> list[dict]:
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []
    head = [_s(h) for h in rows[0]]
    idx = {}
    for key, names in cols.items():
        hit = next((head.index(n) for n in names if n in head), None)
        if hit is not None:
            idx[key] = hit
    out = []
    for n, r in enumerate(rows[1:], start=2):
        if not any(_s(v) for v in r):
            continue
        rec = {k: _s(r[i]) if i < len(r) else "" for k, i in idx.items()}
        rec["_row"] = n
        out.append(rec)
    return out, idx


def read(path: Path) -> tuple[dict, list[str]]:
    errors: list[str] = []
    wb = load_workbook(path, read_only=True, data_only=True)
    sheets = {k: _sheet(wb, k) for k in SHEETS}
    for k, ws in sheets.items():
        if ws is None:
            errors.append(f"M1 Missing sheet '{SHEETS[k][0]}'")
    if errors:
        return {}, errors

    cover = {}
    for r in sheets["cover"].iter_rows(min_row=2, values_only=True):
        k, v = _s(r[0]) if r else "", _s(r[1]) if len(r) > 1 else ""
        for key, names in COVER.items():
            if k in names:
                cover[key] = v
    for key in REQUIRED_COVER:
        if not cover.get(key):
            errors.append(f"M1 Cover field '{COVER[key][0]}' is empty")
    if cover.get("date") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", cover["date"]):
        errors.append(f"M1 Cover date '{cover['date']}' is not YYYY-MM-DD")
    if cover.get("status") and cover["status"] not in PAGE_STATUS:
        errors.append(f"M1 Cover status '{cover['status']}' is not one of {sorted(set(PAGE_STATUS.values()))}")

    fields, fidx = _table(sheets["fields"], FIELD_COLS, errors, "fields")
    for key in REQUIRED_COLS:
        if key not in fidx:
            errors.append(f"M2 Sheet '{SHEETS['fields'][0]}' has no column '{FIELD_COLS[key][0]}'")
    rules, _ = _table(sheets["rules"], RULE_COLS, errors, "rules")
    return {"cover": cover, "fields": fields, "rules": rules, "sheet": sheets["fields"].title}, errors


# ---------------------------------------------------------------- rules M3-M7

def log_ids() -> set[str]:
    return {m.upper() for m in re.findall(r"\{#([dg]-\d{3})\}", LOG.read_text(encoding="utf-8"))}


def lint(wb: dict) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    known = log_ids()
    rule_ids = {r.get("id", "") for r in wb["rules"]}
    seen = set()
    for f in wb["fields"]:
        where = f"row {f['_row']} `{f.get('rumbo') or '?'}`"
        st, ref, rule = f.get("status", ""), f.get("ref", "").upper(), f.get("rule", "")
        if f.get("rumbo") in seen:
            warnings.append(f"W1 {where}: RUMBO field listed twice")
        seen.add(f.get("rumbo"))
        if st not in FIELD_STATUS:
            errors.append(f"M3 {where}: status '{st}' is not one of {', '.join(sorted(FIELD_STATUS))}")
            continue
        if st == "Gap" and not re.fullmatch(r"G-\d{3}", ref):
            errors.append(f"M4 {where}: a Gap row needs a G-nnn entry in the decision and gap log")
        if st == "Not migrated" and not re.fullmatch(r"D-\d{3}", ref):
            errors.append(f"M4 {where}: a Not migrated row needs a D-nnn entry in the decision and gap log")
        if ref and ref not in known:
            errors.append(f"M5 {where}: {ref} is not in docs/mapping/decision-log.md; add it there first")
        if st in ("Mapped", "Transform") and not f.get("opera"):
            errors.append(f"M6 {where}: {st} row has no OPERA Cloud field")
        if st == "Transform" and not re.fullmatch(r"[TL]\d+", rule):
            errors.append(f"M7 {where}: Transform row needs a rule (T1, L1…), got '{rule or 'none'}'")
        elif re.fullmatch(r"[TL]\d+", rule) and rule not in rule_ids:
            errors.append(f"M7 {where}: rule {rule} is not defined in sheet '{SHEETS['rules'][0]}'")
        if st == "TBC":
            warnings.append(f"W2 {where}: TBC; the page stays In progress until it's resolved")
    return errors, warnings


# ---------------------------------------------------------------- rendering

def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _cell(v: str) -> str:
    return v.replace("|", "\\|") if v else ""


def _code(v: str) -> str:
    return f"`{v}`" if v else "—"


def _rule_link(r: str) -> str:
    return f"[{r}](#{r.lower()})" if re.fullmatch(r"[TL]\d+", r) else (r or "—")


def _ref_link(ref: str) -> str:
    ref = ref.upper()
    return f"[{ref}](decision-log.md#{ref.lower()})" if ref else ""


def block(name: str, body: str) -> str:
    return f"{GEN_START.format(name=name)}\n\n{body.strip()}\n\n{GEN_END.format(name=name)}"


def render_blocks(wb: dict, source: dict) -> dict[str, str]:
    c = wb["cover"]
    summary = "\n".join([
        "| | RUMBO | OPERA Cloud |",
        "|---|---|---|",
        f"| Object | {c.get('block', 'TBC')} | {c.get('target', 'TBC')} |",
        f"| Module / API | {c.get('module') or 'TBC'} | {c.get('api') or 'TBC'} |",
        f"| Business-object scope | {c.get('scope') or 'TBC'} | |",
        f"| System of record after migration | | {c.get('sor') or 'TBC'} |",
        "",
        "| | |",
        "|---|---|",
        f"| Source workbook | `{source['file']}`, sheet `{wb['sheet']}`, version `{c['version']}` ({c['date']}) |",
        f"| Workbook SHA-256 | `{source['sha256'][:16]}…` |",
        f"| Page status | {PAGE_STATUS.get(c.get('status', ''), 'In progress')} |",
        f"| SME | {c.get('sme') or 'TBC'} |",
    ])

    counts = {s: sum(1 for f in wb["fields"] if f.get("status") == s) for s in sorted(FIELD_STATUS)}
    rows = [
        "| RUMBO field | OPERA Cloud field | Rule | Identifier type | Required in OPERA Cloud | Status | Notes |",
        "|---|---|---|---|---|---|---|",
    ]
    for f in wb["fields"]:
        notes = "; ".join(x for x in (_ref_link(f.get("ref", "")), _cell(f.get("notes", ""))) if x)
        rows.append(
            f"| `{f['rumbo']}` | {_code(f.get('opera', ''))} | {_rule_link(f.get('rule', ''))} "
            f"| {f.get('idtype') or '—'} | {f.get('required') or '—'} | {f['status']} | {notes} |"
        )
    tally = ", ".join(f"{n} {s}" for s, n in counts.items() if n)
    fields = f"{len(wb['fields'])} fields: {tally}.\n\n" + "\n".join(rows)

    groups: dict[str, list[dict]] = {}
    for r in wb["rules"]:
        groups.setdefault(r.get("id", "?"), []).append(r)
    rules_md = []
    for kind, title in (("T", "Transformation rules"), ("L", "Code lookups")):
        rules_md.append(f"## {title}\n")
        ids = [k for k in groups if k.startswith(kind)]
        if not ids:
            rules_md.append("None.\n")
        for rid in ids:
            g = groups[rid]
            rules_md.append(f"### {rid}\n\n{g[0].get('name', '')}.\n")
            if kind == "T":
                rules_md += ["| RUMBO value | OPERA Cloud value | Notes |", "|---|---|---|"]
                rules_md += [f"| {_cell(r.get('from', ''))} | {_cell(r.get('to', ''))} | {_cell(r.get('notes', ''))} |" for r in g]
            else:
                rules_md += ["| RUMBO code | Meaning | OPERA Cloud code | Notes |", "|---|---|---|---|"]
                rules_md += [f"| `{r.get('from', '')}` | {_cell(r.get('meaning', ''))} | {_code(r.get('to', '')) if r.get('to') not in ('—', '') else '—'} | {_cell(r.get('notes', ''))} |" for r in g]
            rules_md.append("")
    return {"summary": summary, "fields": fields, "rules": "\n".join(rules_md)}


def new_page(wb: dict, blocks: dict[str, str]) -> str:
    c = wb["cover"]
    refs = sorted({f["ref"].upper() for f in wb["fields"] if f.get("ref")})
    gaps = "\n".join(f"- {_ref_link(r)}" for r in refs) or "None yet."
    return f"""# {c['block']} to {c['target']}

!!! warning "DRAFT"
    Not yet validated. Remove this block when an SME has reviewed the page.

Generated tables come from the shell workbook ([D-001](decision-log.md#d-001)). Change a mapping row in the workbook and re-run `tooling/mapping_import.py`; edit the other sections here.

## Summary

{block("summary", blocks["summary"])}

## Relationship

TBC: cardinality and ownership after migration.

## Field mapping

{block("fields", blocks["fields"])}

{block("rules", blocks["rules"])}

## Identifiers

TBC: list every RUMBO identifier and where it's stored in OPERA Cloud. See the [identifier glossary](../reference/identifier-glossary.md).

## Gaps and decisions

{gaps}

## Open questions

- [ ] TBC

## Related topics

- [RUMBO to OPERA Cloud mapping](index.md)
- [Decision and gap log](decision-log.md)
"""


def replace_blocks(text: str, blocks: dict[str, str]) -> str:
    for name, body in blocks.items():
        pat = re.compile(re.escape(GEN_START.format(name=name)) + r".*?" + re.escape(GEN_END.format(name=name)), re.S)
        if not pat.search(text):
            raise SystemExit(f"Page has no generated block '{name}'; restore its markers or delete the page to recreate it")
        text = pat.sub(lambda _m: block(name, body), text)
    return text


def index_row(wb: dict, slug: str, source: dict) -> str:
    c = wb["cover"]
    return (f"| {c['block']} | {c['target']} | `{source['file']}` / {wb['sheet']} ({c['version']}) "
            f"| {PAGE_STATUS.get(c.get('status', ''), 'In progress')} | [{c['block']}]({slug}.md) |")


def update_index(text: str, row: str, slug: str) -> str:
    start, end = GEN_START.format(name="blocks"), GEN_END.format(name="blocks")
    head = "| RUMBO building block | OPERA Cloud target | Workbook / sheet | Status | Page |\n|---|---|---|---|---|"
    m = re.search(re.escape(start) + r"(.*?)" + re.escape(end), text, re.S)
    if m:
        rows = [ln for ln in m.group(1).strip().splitlines()[2:] if f"]({slug}.md)" not in ln and ln.strip()]
    else:
        old = re.search(r"\| RUMBO building block \|.*?\n\|---.*?\n(?:\|.*\n?)*", text)
        if not old:
            raise SystemExit("docs/mapping/index.md has no building-block table")
        text = text.replace(old.group(0), start + "\n" + end + "\n")
        rows = []
    rows = sorted(rows + [row])
    return re.sub(re.escape(start) + r".*?" + re.escape(end), lambda _m: block("blocks", head + "\n" + "\n".join(rows)), text, flags=re.S)


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("workbook")
    ap.add_argument("--slug", help="page file name without .md (default: from the RUMBO building block)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--report")
    a = ap.parse_args()

    path = Path(a.workbook)
    source = {"file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    wb, errors = read(path)
    warnings: list[str] = []
    if not errors:
        e2, warnings = lint(wb)
        errors += e2

    out = ["# Mapping import report", "", "## Source", "",
           f"- `{path.name}` (SHA-256 `{source['sha256'][:16]}…`)"]
    if wb:
        c = wb["cover"]
        out.append(f"- Building block **{c.get('block', '?')}** → **{c.get('target', '?')}**, version `{c.get('version', '?')}` ({c.get('date', '?')})")
        out.append(f"- {len(wb['fields'])} field rows, {len({r.get('id') for r in wb['rules']})} rules and lookups")
    out += ["", f"## Findings: {len(errors)} errors, {len(warnings)} warnings", ""]
    out += [f"- ❌ {e}" for e in errors] + [f"- ⚠️ {w}" for w in warnings]
    if not errors and not warnings:
        out.append("None.")

    status = 1 if errors else 0
    out += ["", "## Result", ""]
    if errors:
        out.append("**Rejected.** Nothing was written. Fix the workbook and run the import again.")
    else:
        slug = a.slug or slugify(wb["cover"]["block"])
        page = MAPPING / f"{slug}.md"
        blocks = render_blocks(wb, source)
        before = page.read_text(encoding="utf-8") if page.exists() else None
        after = replace_blocks(before, blocks) if before else new_page(wb, blocks)
        idx_before = INDEX.read_text(encoding="utf-8")
        idx_after = update_index(idx_before, index_row(wb, slug, source), slug)
        verb = "Would write" if a.dry_run else "Wrote"
        if before == after and idx_before == idx_after:
            out.append(f"**Accepted.** `docs/mapping/{slug}.md` is already up to date; nothing written.")
        else:
            if not a.dry_run:
                page.write_text(after, encoding="utf-8", newline="\n")
                INDEX.write_text(idx_after, encoding="utf-8", newline="\n")
            what = "created" if before is None else "generated blocks replaced; hand-written sections kept"
            out.append(f"**Accepted.** {verb} `docs/mapping/{slug}.md` ({what}) and the building-block row in `docs/mapping/index.md`.")
        nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
        if f"mapping/{slug}.md" not in nav:
            out.append(f"\n- Add `mapping/{slug}.md` to `nav` in `mkdocs.yml`, or `mkdocs build --strict` fails.")
    out += ["", "> A clean import means the workbook is consistent with the page rules. It is **not** SME validation."]

    report = "\n".join(out) + "\n"
    if a.report:
        Path(a.report).write_text(report, encoding="utf-8")
    sys.stdout.buffer.write(report.encode("utf-8"))
    return status


if __name__ == "__main__":
    sys.exit(main())
