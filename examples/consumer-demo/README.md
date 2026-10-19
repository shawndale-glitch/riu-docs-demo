# Consumer demo: checking an application against a process

A fictional front-desk application that implements FO-001. It shows conformance layer C1 (traceability): every step on the process's happy path must be bound to something real in the application's API or event specs.

| File | Role |
|---|---|
| `bindings.yaml` | Written by the app's developers: which operation or event implements each FO-001 node |
| `../../docs/api/specs/front-desk.openapi.yaml` | The app's API spec (sample) |
| `../../docs/api/specs/front-desk.asyncapi.yaml` | The app's events (sample) |

## Run it

The check needs a **validated** release of FO-001. In a real app repository, `workflow_conformance.py resolve` downloads the newest release in the pinned range. Here, point `--model` at the `workflow.yaml` of a validated FO-001.

```bash
python tooling/workflow_conformance.py check \
  --model path/to/FO-001/workflow.yaml \
  --bindings examples/consumer-demo/bindings.yaml \
  --range ^1.0.0 \
  --openapi "docs/api/specs/*.openapi.yaml" \
  --asyncapi "docs/api/specs/*.asyncapi.yaml"
```

As committed, the check **fails**. The API renamed `checkInGuest` to `checkInReservation` in 0.3.0, and the binding for "Check in guest" still uses the old name. Change `operation_id: checkInGuest` to `checkInReservation` and the check passes.
