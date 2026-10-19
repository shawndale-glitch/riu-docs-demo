# <RUMBO building block> to <OPERA Cloud object>

!!! warning "DRAFT"
    Not yet validated. Remove this block when an SME has reviewed the page.

<One sentence: what this RUMBO building block holds and what it becomes in OPERA Cloud.>

## Summary

| | RUMBO | OPERA Cloud |
|---|---|---|
| Object | <building block> | <object, for example reservation, profile, rate code, room type> |
| Module / API | <RUMBO module or table> | <OHIP API or configuration area> |
| Business-object scope | | |
| System of record after migration | | |

| | |
|---|---|
| Source workbook | `<file name>.xlsx`, sheet `<sheet>`, version `<version or date>` |
| Page status | Not started / In progress / In review / Validated |
| SME | <name, role> |

## Relationship

<Cardinality and ownership. For example: one RUMBO group maps to one OPERA Cloud business block and many reservations; OPERA Cloud owns the block after migration.>

## Field mapping

| RUMBO field | OPERA Cloud field | Rule | Identifier type | Required in OPERA Cloud | Status | Notes |
|---|---|---|---|---|---|---|
| `<field>` | `<field or API path>` | Direct / [T1](#t1) / [L1](#l1) / Default `<value>` / — | — or Internal ID / External reference / Locator | Yes / No | Mapped / Transform / Gap / Not migrated / TBC | |

Field status values are defined in [RUMBO to OPERA Cloud mapping](index.md#status-values). Every **Gap** row links a `G-nnn` entry and every **Not migrated** row links a `D-nnn` entry in the [decision and gap log](decision-log.md).

## Transformation rules

### T1: <rule name> {#t1}

<What the rule does, in one or two sentences.>

| RUMBO value | OPERA Cloud value |
|---|---|
| | |

## Code lookups

### L1: <RUMBO code set> to <OPERA Cloud code set> {#l1}

| RUMBO code | Meaning | OPERA Cloud code | Notes |
|---|---|---|---|
| | | | |

## Identifiers

<List every RUMBO identifier on this building block and what happens to it. A RUMBO ID carried into OPERA Cloud is an external reference with source system RUMBO; say exactly where it's stored. See the [identifier glossary](../reference/identifier-glossary.md).>

| RUMBO identifier | Type in RUMBO | Stored in OPERA Cloud as | Location |
|---|---|---|---|
| | Internal ID / Locator | External reference / Not stored | <external reference type/context, UDF, or field> |

## Gaps and decisions

- <[G-nnn](decision-log.md#g-nnn): short title>
- <[D-nnn](decision-log.md#d-nnn): short title>

## Open questions

- [ ] <Question> (owner: <name>)

## Related topics

- [RUMBO to OPERA Cloud mapping](index.md)
- <related building-block pages>
