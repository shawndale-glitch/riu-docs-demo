# Style guide

Short rules for writing Genesis documentation. When in doubt, favor precision over brevity.

## Voice and tone

- Write in US English, second person ("you"), present tense, active voice.
- Lead with what the reader needs to do or know. Put background after.
- One idea per paragraph. One action per numbered step.

## Topic types

| Type | Answers | Location | Template |
|---|---|---|---|
| Concept | What is it? How does it work? | `docs/guides/` | `templates/concept.md` |
| Task | How do I do X? | `docs/guides/` | `templates/task.md` |
| Reference | What are the exact values? | `docs/reference/`, `docs/api/` | `templates/reference.md` |
| Mapping | Where does this RUMBO data go in OPERA Cloud? | `docs/mapping/` | `templates/mapping.md` |
| Release note | What changed? | `docs/release-notes/` | — |

Don't mix types on one page. Link between them instead.

## Identifiers and relationships

Integration docs live or die on identifier precision. Always:

- Name the **owning system** of every identifier (Genesis, OPERA Cloud, a channel, a partner).
- Say whether it is an **internal ID**, an **external reference**, a **locator**, or a **correlation ID**. See the [identifier glossary](../reference/identifier-glossary.md).
- State the **business-object scope** (reservation, profile, stay, membership, business block).
- State the **relationship** when an identifier links two objects (one-to-one, one-to-many, and which side owns it).

Never write "the ID" without saying which one.

## Formatting

- Headings: sentence case. One `#` H1 per page, matching the nav title.
- Code, field names, headers, and literal values: `backticks`.
- UI labels: **bold**.
- Use tables for comparisons and field lists, not prose.
- Use admonitions (`!!! note`, `!!! warning`) sparingly.
- Diagrams: Mermaid in fenced code blocks, so they stay diffable.

## File names

- Lowercase, hyphen-separated: `reservation-sync-overview.md`.
- Name the file for the topic, not the ticket.
