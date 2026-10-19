# Examples

Reference material for the workflow pipeline. Not published to the site and not part of `workflows/`.

| Folder | Contents |
|---|---|
| `library-selftest/` | Boards that use every published library component; `tooling/selftest.py` runs them through intake. |
| `_archive/DOPV-001/` | **Archived 2026-10-15.** PoC export of the "Dieta de mi perra" practice process from the FigJitsu board (`Test 2` page): the raw extraction (`board.json`), the generated `workflow.yaml` and `README.md`, and the lint report inside the README. It **fails** lint on purpose (17 errors, 3 warnings), which shows what the rejection path reports. Its `board.json` predates the `figjam_extract.js` format, so the current intake can't read it; kept for history only. See [`governance/figjam-export-viability.md`](../governance/figjam-export-viability.md). |
