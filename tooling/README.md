# Tooling

Scripts for the FigJam → repository workflow pipeline. Rules: [`governance/workflow-rules.yaml`](../governance/workflow-rules.yaml). Design: [`governance/workflow-pipeline.md`](../governance/workflow-pipeline.md).

## Pipeline

```text
FigJam section ──figjam_extract.js──▶ board.json ──workflow_intake.py──▶ lint + schema + version
                                                        │
                    rejected (exit 1): report only, nothing written
                    accepted (exit 0): writes the resting point ▼
   workflows/<area>/<ID>/workflow.yaml, board.json, CHANGELOG.md
   docs/processes/<area>/<ID>.md      conformance/<ID>/scenarios.feature
```

| Script | Status | What it does |
|---|---|---|
| `figjam_extract.js` | Working (plugin API) | Reads one process section from a FigJam board and returns `board.json`: facts only (components, properties, positions, connectors). Run through the Figma MCP `use_figma` tool or a plugin. |
| `workflow_intake.py` | Working | `board.json` → lint (R1–R9, W1–W8; catalogue in `workflow-rules.yaml` → `lint`) → schema → semantic diff and version → writes the resting point. Exit 1 and a report if anything blocks. |
| `inventory_check.py` | Working | Checks the process inventory workbook (`.xlsx`) against `workflow-rules.yaml` → `inventory` (I1–I8): required columns, process IDs, ISO dates, statuses, area-column key, FigJam links, and agreement with `workflows/`. Exit 1 on errors. |
| `mapping_import.py` | Working | RUMBO to OPERA Cloud shell workbook (`.xlsx`) → checks M1–M7 (cover fields, columns, field status, gap and decision references that exist in the decision log, rules defined) → regenerates the summary, field mapping and rules blocks of `docs/mapping/<block>.md` and its row in the mapping index, keeping hand-written sections (decision D-001). Exit 1 and nothing written on errors. |
| `api_render.py` | Working | OpenAPI (+ AsyncAPI events) spec in `docs/api/specs/` → generated block of the API reference page. `--check` fails CI when the page is out of date with the spec. |
| `workflow_core.py` | Working | Shared rules: component mapping, lane assignment, lint, content hash, version bump. |
| `figma_rest.py` | Working, not yet run against the live API | Same `board.json` shape from `GET /v1/files/:key/nodes`, so CI runs without the plugin. Used by `workflow_intake.py --url`. |
| `workflow_render.py` | Working | Renders the process page (Mermaid, steps, rules) and the Gherkin scenarios; also callable on its own. |
| `workflow_release.py` | Working | After merge: releases changed `validated` workflows. Checks the merged PR was approved by someone other than its author, tags `<ID>@<semver>`, builds the bundle, creates the GitHub release, opens issues in consumer repos on a major. |
| `workflow_conformance.py` | Working | In consumer repos: `resolve` picks the newest release in the pinned range; `check` runs C1 traceability (bindings resolve to OpenAPI operationIds / AsyncAPI events, every decision exit mapped) and C4 evidence for the happy path. |
| `selftest.py` | Working | Runs the library self-test boards (`examples/library-selftest/`) through intake: every published component must pass with 0 findings. Then breaks copies on purpose: a retired arrow component, default texts (R9), a decision that isn't a question (W7), more than 15 activities (W8), and a good and a broken inventory workbook must each give the expected result. |
| `workflow_export_poc.py` | Superseded | First PoC (examples/_archive/DOPV-001, archived: its board.json predates the current extractor format). Kept for reference. |

## Quality and migration scripts

| Script | What it does |
|---|---|
| `sensitive_scan.py` | Blocks personal data (DNI/NIE, IBAN, card, phone) and, during the POC, company e-mail domains, classification markers and source documents. Rules: `governance/sensitive-data.yaml`. |
| `terms_check.py` | Product names and house terms in Markdown. Rules: `governance/terms.yaml`. |
| `repoint_repo.py` | Rewrites host, org, repo and team references after the move to GitHub Enterprise Server; `--check` lists leftovers. |
| `ghes_preflight.py` | Read-only checks of an Enterprise Server instance: version, every `uses:` action, runners, Pages, CODEOWNERS teams. |
| `apply_governance.py` | Applies `governance/labels.yaml`, `rulesets/*.json` and (with `--teams`) `teams.yaml` to a repository; idempotent. |

## Which Action calls what

| Action | Script | Trigger |
|---|---|---|
| `.github/workflows/workflow-intake.yml` | `workflow_intake.py --url` | Manual (section link). Accepted → PR `workflow/<ID>-<version>`; rejected → issue labelled `workflow:validation-failed`. |
| `.github/workflows/workflow-release.yml` | `workflow_release.py --since` | Push to `main` touching `workflows/**/workflow.yaml` |
| `.github/workflows/quality.yml` | `sensitive_scan.py`, `terms_check.py`, `pymarkdown`, `selftest.py` | Every PR and push to `main` (job `checks`, a required status check) |
| `.github/workflows/workflow-conformance.yml` | `workflow_conformance.py resolve` + `check` | Called from consumer repos (reusable workflow); C2 runs the consumer's own scenario command |

Secrets: `FIGMA_TOKEN` (required for intake), `INTAKE_BOT_TOKEN` (optional, lets docs.yml run on intake PRs), `CONSUMER_NOTIFY_TOKEN` (optional, cross-repo issues), and `docs_repo_token` in consumer repos while this repo is private.

## Run it

```bash
pip install -r requirements.txt
python tooling/workflow_intake.py path/to/board.json --report intake-report.md
FIGMA_TOKEN=... python tooling/workflow_intake.py --url "https://www.figma.com/board/<key>/...?node-id=<section>"
python tooling/workflow_release.py --since <sha> --dry-run
python tooling/workflow_conformance.py check --model workflow.yaml --bindings bindings.yaml --range ^1.0.0 --openapi "api/*.yaml"
python tooling/inventory_check.py path/to/inventory.xlsx --report inventory-report.md
python tooling/selftest.py
mkdocs build --strict
```

Run `figjam_extract.js` through `use_figma` with `FILE_KEY`, `PAGE_ID` and `SECTION_ID` filled in, save the returned object as `board.json`, then pass it to `workflow_intake.py` (add `--dry-run` to check without writing anything).

New process areas need a prefix in [`governance/areas.yaml`](../governance/areas.yaml). A new process page also needs a `nav` entry in `mkdocs.yml`; the intake report says so when it's missing.
