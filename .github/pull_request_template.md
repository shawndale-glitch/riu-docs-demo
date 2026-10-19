## What changes

<!-- One or two sentences. Link the issue: "Closes #12". -->

## Type

- [ ] Content (docs pages, mapping, reference)
- [ ] Process model (FigJam intake; usually opened by the intake workflow)
- [ ] Governance (rules, schemas, tooling, CI, CODEOWNERS)

## Checks

- [ ] `mkdocs build --strict` passes locally
- [ ] New pages are in `nav` in `mkdocs.yml`
- [ ] Unvalidated content is marked `DRAFT` or `TBC`
- [ ] No personal data, and no company data while the repo is a POC (`python tooling/sensitive_scan.py`)
- [ ] Governance changes: `rules_version` bumped and `python tooling/selftest.py` passes

## Who validated the content

<!-- Name the SME or source (spec, workbook + sheet + version) that confirms the technical content. "Not yet" is a valid answer for a DRAFT. -->
