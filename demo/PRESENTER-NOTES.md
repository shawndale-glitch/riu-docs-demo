# RIU Docs Demo: presenter notes

Audience: RIU IT (Informática / Nuevos desarrollos), economic-financial and HR systems. She has started the docs-as-code journey at RIU and wants a closer look at how this POC works. Not published to the site (this folder is outside `docs/`).

## Before the call (5 minutes)

1. Close other apps that use port 8000 (the script moves to the next free port anyway).
2. Check internet access: Mermaid diagrams load their renderer from a CDN. Without it, diagrams show as text; everything else works.
3. Rehearse at speed if you like: `demo\RUN-DEMO.cmd -Pace 0 -NoBrowser`, then press Enter to clean up.
4. Share the whole screen, not one window: the demo moves from the console to Chrome.

## Push the button

Double-click `demo\RUN-DEMO.cmd` for English, or `demo\RUN-DEMO-ES.cmd` for Spanish. The Spanish button translates the console narration and the browser tour captions; the reports printed by the Python tools (intake, conformance) stay in English.

Only the browser tour, without the console part: `demo\OPEN-TOUR.cmd` or `demo\OPEN-TOUR-ES.cmd`. Opening the **POC walkthrough** page also starts the tour after an 8-second countdown (**Stay on this page** or Esc cancels it for that browser tab).

| Option | Use it when |
|---|---|
| `-Lang es` | Tour captions in Spanish from the start (the ES/EN button switches at any time) |
| `-Pace 1.3` | You want slower console narration |
| `-Interactive` | You want to talk between acts; press Enter to move on |
| `-NoBrowser` | You'll open the address yourself |

Total run: about 4 minutes in the console, about 8 in the browser. The browser opens in Chrome (Firefox as a fallback). Edge is never used.

## Talk track

| Act | What she sees | What to say | Time |
|---|---|---|---|
| 0 Preflight | Python and dependencies | "Same environment CI uses. Nothing to install on the reader's side." | 0:15 |
| 1 Repository | Annotated folder list, last commits | "Content, rules and tooling are all text files under version control. The history is the audit trail." Point at commit `b42ecbc`: an earlier guardrails demo PR. | 0:30 |
| 2 Checks | Five green checks | "These run on every pull request. A red check blocks the merge. Authors can run them before they commit." | 0:45 |
| 3 Guardrail | A payroll-style example with a fake DNI, IBAN and `@riu.com` address is blocked, values masked | Strong point for finance/HR: personal identifiers and bank accounts are blocked in every phase. Company domains are blocked only while the repo lives outside RIU. | 0:30 |
| 4 Intake | Unchanged board → no-op; reworded board → patch 0.1.1; broken board → rejected with links to FigJam | "Business authors stay in FigJam. The rules, not a reviewer's memory, decide if a diagram is publishable. The version is computed." | 1:00 |
| 5 Conformance | App bindings fail on a renamed API operation, then pass after a one-line fix | "The documentation caught a broken integration before a test environment did. That's the payoff for developers." | 0:45 |
| 6 Build | Strict build, page count | "One broken link and the site isn't published." | 0:15 |
| 7 Tour | Chrome opens the self-running tour | Let it run. Pause (Space) whenever she asks a question. | 8:00 |

Tour stops: Home → walkthrough (big picture, guardrails) → FO-001 (diagram, conformance) → late check-out (AI draft) → identifier glossary → Perfil de huésped (Excel import) → decision log → Front Desk API → FigJam author guide → style guide → "what's real and what's next".

## Likely questions

| Question | Answer |
|---|---|
| Do business users need Git? | No. Process authors work in FigJam, mapping teams in Excel. Anyone else uses **Edit this page**, which opens a pull request in the browser. |
| Who approves what? | `.github/CODEOWNERS`: process SMEs for processes, engineering for bindings, doc owners for the rest. The branch ruleset requires an approval and green checks. |
| Where does the site live? | Open decision. Options: GitHub Enterprise Cloud private Pages, the MkDocs build behind company SSO, or PDFs for externals. GitHub can't restrict *read* access per folder, so restricted content needs its own repository. |
| Can it hold real RIU data now? | Not until it moves to RIU's GitHub Enterprise Server. The scan enforces it. `tooling/repoint_repo.py` and `tooling/ghes_preflight.py` prepare the move. |
| Could finance or HR use it? | Yes. Add an area prefix in `governance/areas.yaml`, a code owner team, and a `nav` entry. Spreadsheet-driven docs follow the RUMBO mapping pattern: the workbook stays authoritative, a script generates the pages. |
| What does AI do? | Drafts pages from unstructured sources, marked `DRAFT` and `TBC`, with provenance. It never merges and never resolves a contradiction. Structured sources are converted by deterministic scripts, not AI. |
| What about the MkDocs 2.0 warning? | Material for MkDocs announced that MkDocs 2.0 breaks plugins and themes. `requirements.txt` pins `mkdocs<2`, so builds are stable; the long-term path is a decision to make, not an emergency. |
| How do versions work? | Per process SemVer, computed from a diff of the model against the last release using FigJam node IDs. Wording = patch, additions = minor, removals or rerouting = major (consumers get an issue). |

## If something goes wrong

| Symptom | Fix |
|---|---|
| Script window closes immediately | Run `powershell -ExecutionPolicy Bypass -File demo\run-demo.ps1` from a terminal to see the error |
| `UnicodeEncodeError` | The script sets UTF-8 itself; if you run tools by hand, first run `$env:PYTHONUTF8=1` |
| `pymarkdown` fails with "DLL load failed ... Control de aplicaciones" | Windows App Control blocked a compiled `tomli` wheel. Fixed on this machine with `pip install --force-reinstall --no-deps --no-binary tomli tomli` |
| Browser doesn't open | Open `http://127.0.0.1:8000/?tour=1` in Chrome |
| Diagrams show as text | No internet for the Mermaid CDN. Talk over the steps table instead |
| Need to stop the site | Press Enter in the console window. It stops the server and deletes `.demo-tmp\` |

## What the demo adds to the repository

| File | Purpose |
|---|---|
| `demo/RUN-DEMO.cmd` | The button |
| `demo/run-demo.ps1` | The narrated console demo (acts 0–7) |
| `demo/board_scenarios.py` | Makes edited copies of the FO-001 board for act 4; never touches the real one |
| `docs/demo/poc-walkthrough.md` | Published page explaining the POC's logic, layer by layer |
| `docs/demo/tour.js`, `docs/demo/tour.css` | The self-running tour, inert unless the URL has `?tour=` |
| `mkdocs.yml`, `docs/index.md`, `.gitignore` | Nav entry, tour assets, home page link, `.demo-tmp/` ignored |
