# Contributing

## Workflow

1. Create a branch from `main`: `docs/<short-topic>` (for example `docs/reservation-sync`).
2. Add or edit Markdown under `docs/`. Start new topics from a file in `templates/`.
3. Add new pages to `nav` in `mkdocs.yml`.
4. Run `mkdocs build --strict` locally. Fix every warning. With `pre-commit install`, the Quality checks (sensitive data, Markdown lint, terms) run on every commit too.
5. Open a pull request. The template asks what changed and who validated the technical content.
6. Merge after review. The site deploys automatically.

## Commit messages

Use a short, imperative summary line:

```text
docs(guides): add reservation sync overview
docs(reference): define correlation ID vs locator
build: pin mkdocs-material 9.5
```

## Content status markers

Mark unvalidated content so readers and reviewers can see it:

| Marker | Meaning |
|---|---|
| `!!! warning "DRAFT"` admonition at the top of a page | Page structure is in place; content not yet validated |
| `TBC` in a table cell or sentence | A specific fact still needs confirmation from an SME or a spec |

Remove the marker in the same pull request that validates the content.

## Style

Follow the [style guide](docs/contributing/style-guide.md). Product names and house terms are checked against [`governance/terms.yaml`](governance/terms.yaml); add a term there when reviewers keep correcting the same word.

Process diagram authors: see the [guía para autores](docs/contributing/guia-autores-figjam.md) (Spanish).
