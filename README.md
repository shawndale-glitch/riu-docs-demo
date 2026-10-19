# RIU Genesis Documentation (public demo)

> **Demo snapshot.** A public copy of the docs-as-code proof of concept, made for a stakeholder demo. All content is fictional sample content; no company data. Internal planning documents (decision brief, migration runbook) are kept in the private repository.

Docs-as-code source for the RIU Hotels **Genesis** platform documentation, maintained by Mindata.

Content is written in Markdown, built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/), and published to GitHub Pages by GitHub Actions.

> **Status:** pre-build / small slice. Structure, build pipeline, and a first sample topic are in place. Content marked `DRAFT` or `TBC` still needs SME validation.

## Repository layout

```text
.
├── docs/                    # Everything published to the site
│   ├── index.md             # Landing page
│   ├── guides/              # Task and concept guides (integration, onboarding)
│   ├── reference/           # Glossaries, data dictionaries, lookup tables
│   ├── mapping/             # RUMBO to OPERA Cloud mapping, decision and gap log
│   ├── api/                 # API reference (placeholder until specs are available)
│   ├── release-notes/       # Release notes, newest first
│   └── contributing/        # Style guide, published for writers and reviewers
├── governance/              # Rules, decisions, runbooks; labels, teams, ruleset as code
├── tooling/                 # Pipeline, quality and migration scripts (see tooling/README.md)
├── templates/               # Topic templates (not published)
├── mkdocs.yml               # Site configuration and navigation
├── requirements.txt         # Python build dependencies
└── .github/workflows/       # CI: build on PR, deploy on main
```

## Preview locally

Requires Python 3.10+.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

Open <http://127.0.0.1:8000>. The site reloads as you save.

Before opening a pull request, run the same checks CI runs (Docs and Quality workflows):

```bash
mkdocs build --strict
python tooling/sensitive_scan.py
python tooling/terms_check.py
pymarkdown --config .pymarkdown.json scan -r docs README.md CONTRIBUTING.md governance
```

Or run them on every commit: `pip install pre-commit && pre-commit install`.

> **POC rule:** this repository is on a personal GitHub account until it moves to RIU's GitHub Enterprise Server. No RIU company data until then; `sensitive_scan.py` enforces it.

## Publishing

- **Pull requests** → the site is built with `--strict`. Broken links or missing nav entries fail the check.
- **Merge to `main`** → the site is built with `--strict`. It is deployed to GitHub Pages only when the repository variable `PAGES_ENABLED` is `true`.

Publishing is off until site hosting is decided (decision 1 in the decision brief, kept in the private repository). Repository variables (**Settings → Secrets and variables → Actions → Variables**) control it:

| Variable | Values | Default |
|---|---|---|
| `PAGES_ENABLED` | `true` to publish on merge to `main` | off |
| `PAGES_MODE` | `actions` (deploy with `actions/deploy-pages`; set **Settings → Pages → Source** to **GitHub Actions**) or `branch` (push to `gh-pages`; set the source to that branch) | `actions` |
| `RUNNER_LABELS` | JSON list of runner labels, e.g. `["self-hosted","linux"]` on Enterprise Server | `["ubuntu-latest"]` |

## Governance

- The decision brief and the migration runbook are kept in the private repository.
- Labels, teams, branch ruleset and the people map live in `governance/` and are applied with `tooling/apply_governance.py`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and the [style guide](docs/contributing/style-guide.md).
