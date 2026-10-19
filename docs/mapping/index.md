# RUMBO to OPERA Cloud mapping

!!! warning "DRAFT"
    Structure only. Building-block pages are added as the shell workbooks are processed. Items marked **TBC** need confirmation from the migration team.

**RUMBO** is the RIU legacy platform that Genesis and OPERA Cloud replace. This section documents how each RUMBO building block maps to OPERA Cloud: which object it becomes, how every field is carried across or transformed, and what has no equivalent.

Use it to answer three questions for any piece of RUMBO data:

1. Where does it end up in OPERA Cloud?
2. What happens to it on the way (direct copy, transformation, code lookup, default)?
3. If it doesn't make it across, who decided that and why?

## How this section is organized

| Page | Contents |
|---|---|
| One page per building block | Summary, relationship, field mapping, transformation rules, code lookups, identifiers, gaps. Written from `templates/mapping.md`. |
| [Decision and gap log](decision-log.md) | Every mapping decision and every gap, numbered, so building-block pages can link to them instead of repeating the reasoning. |

## Source workbooks

The field-level mappings come from the **shell workbooks**: Excel files that map RUMBO building blocks to OPERA Cloud. The first delivery is due on 2026-10-02.

| Item | Value |
|---|---|
| Delivered by | TBC |
| Location of the master copies | TBC |
| Versioning | TBC: how revised workbooks are identified (file name, date, version cell) |

Every building-block page names the workbook, sheet, and version it was written from. When a workbook is revised, update the pages that cite it.

Whether the workbooks or these pages are the source of truth for field-level rows is an open decision. See [D-001](decision-log.md#d-001).

## Building blocks

<!-- generated:start blocks (tooling/mapping_import.py; edit the workbook, not this block) -->

| RUMBO building block | OPERA Cloud target | Workbook / sheet | Status | Page |
|---|---|---|---|---|
| Perfil de huésped | Profile (Guest) | `RUMBO-OPERA_perfil-huesped_v0.3.xlsx` / Campos (v0.3) | In progress | [Perfil de huésped](perfil-de-huesped.md) |

<!-- generated:end blocks -->

Filled in when the shell workbooks arrive.

## Status values

**Page status** (one per building block):

| Status | Meaning |
|---|---|
| Not started | Listed in a workbook; no page yet |
| In progress | Page exists; field mapping incomplete or has `TBC` rows |
| In review | Complete; waiting for SME validation |
| Validated | SME has signed off; the `DRAFT` marker is removed |

**Field status** (one per row in a field mapping table):

| Status | Meaning |
|---|---|
| Mapped | Copied as is to a named OPERA Cloud field |
| Transform | Converted by a numbered transformation rule or code lookup |
| Gap | No OPERA Cloud equivalent yet; has a gap log entry |
| Not migrated | Deliberately left behind; has a decision log entry |
| TBC | Target or rule not yet known |

## Open questions

- [ ] Does migrated data load directly into OPERA Cloud, or does it flow through Genesis?
- [ ] Which system is the system of record for each business object during the transition, while RUMBO and OPERA Cloud run side by side?
- [ ] Is historical data (past stays, cancelled reservations) in scope, or only open and future records?
- [ ] Who is the SME who validates each building block?

## Related topics

- [Genesis and OPERA Cloud integration overview](../guides/genesis-opera-integration-overview.md)
- [Identifier glossary](../reference/identifier-glossary.md)
- [Decision and gap log](decision-log.md)
