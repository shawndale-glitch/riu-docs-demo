# API reference

Each API has a spec under `docs/api/specs/`. Its reference page is generated from the spec by `tooling/api_render.py`, so the page can't drift from the spec, and CI fails if it does.

| API | Spec | Status |
|---|---|---|
| [Front Desk API (sample)](front-desk.md) | OpenAPI 3.0 + AsyncAPI 2.6 | Fictional sample for the demo |

!!! warning "Genesis specs"
    Real Genesis API specifications are not yet in this repository.

## Adding an API

1. Put the spec in `docs/api/specs/` (for example `genesis-reservations.openapi.yaml`, and `genesis-reservations.asyncapi.yaml` for its events).
2. Run `python tooling/api_render.py docs/api/specs/<name>.openapi.yaml --asyncapi docs/api/specs/<name>.asyncapi.yaml`.
3. Add the generated page to `nav` in `mkdocs.yml`.
4. Write by hand, outside the generated block, only what a spec can't express: authentication, error-handling conventions, pagination, and identifier semantics (link to the [identifier glossary](../reference/identifier-glossary.md)).

The same specs are what process bindings are checked against: a bound `operationId` that disappears from the spec fails the application's conformance check (C1).

## Conventions to document per endpoint

- Owning system of every ID in the request and response
- Idempotency behavior and which header or field carries the correlation ID
- Events (Kafka topics) emitted as a side effect, if any
