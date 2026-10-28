"""Make edited copies of the FO-001 FigJam export so the demo can show intake deciding.

The real export (workflows/front-office/FO-001/board.json) is never touched. Each scenario
writes a copy to .demo-tmp/ (git-ignored), simulating what an author would change on the
FigJam board before re-running intake:

  wording  - a task is reworded            -> intake accepts it and computes a PATCH bump
  broken   - a library placeholder is left in a label, and the decision is no longer
             a question                    -> intake rejects it (R9 error, W7 warning)

Usage: python demo/board_scenarios.py wording|broken
Prints the path of the copy it wrote.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / "workflows" / "front-office" / "FO-001" / "board.json"
OUT = REPO / ".demo-tmp"


def set_label(board: dict, old: str, new: str) -> None:
    """Find the instance whose label/question is `old` and change it to `new`."""
    for inst in board["instances"]:
        for prop in ("Etiqueta", "Pregunta"):
            if inst.get("props", {}).get(prop) == old:
                inst["props"][prop] = new
                return
    raise SystemExit(f"label not found on the board: {old!r}")


def main() -> int:
    scenario = sys.argv[1] if len(sys.argv) > 1 else ""
    board = copy.deepcopy(json.loads(SOURCE.read_text(encoding="utf-8")))

    if scenario == "wording":
        # Wording only: same node, same flows. No behaviour change -> patch.
        set_label(board, "Check room status", "Check room status in OPERA Cloud")
        # The author also bumps the header's "Versión". Intake checks it against the
        # version it computes; leave it at v0.1.0 and intake asks for v0.1.1.
        header = next(i for i in board["instances"] if "Versión" in i.get("props", {}))
        header["props"]["Versión"] = "v0.1.1"
    elif scenario == "broken":
        # R9: the library's placeholder text was never replaced.
        set_label(board, "Inspect room", "Verbo + objeto")
        # W7: a decision must be phrased as a question.
        set_label(board, "Room clean and inspected?", "Room clean")
    else:
        print(__doc__)
        return 2

    OUT.mkdir(exist_ok=True)
    target = OUT / f"FO-001-{scenario}.board.json"
    target.write_text(json.dumps(board, ensure_ascii=False, indent=2), encoding="utf-8")
    print(target.relative_to(REPO).as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())
