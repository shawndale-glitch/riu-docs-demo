# Identifier glossary

!!! warning "DRAFT"
    Definitions are final in intent. Examples marked **TBC** need confirmation against Genesis data and the OHIP specifications.

Integrations break when two different kinds of identifier get treated as the same thing. Use these four terms, and only these, when you document an identifier.

## Identifier types

| Type | Definition | Issued by | Stable? | Unique within | Use it to |
|---|---|---|---|---|---|
| **Internal ID** | The primary key a system assigns to its own record. | The owning system | Yes, for the life of the record | That system (sometimes per property) | Address the record in that system's APIs |
| **External reference** | Another system's identifier, stored on this record to link the two. | The *other* system; stored here | As stable as the other system's ID | The pair (value + source system) | Find the counterpart record in the other system |
| **Locator** | A human-facing lookup value, such as a confirmation number. | Usually the owning system | Not guaranteed; may be reissued or change on cancel/reinstate (TBC) | Often per property or per chain | Let guests and staff find a record |
| **Correlation ID** | A value attached to a request or event to trace one business operation across systems. | The originator of the operation | Per operation, not per record | The operation | Trace, debug, and deduplicate |

### Rules

- An external reference is meaningless without its **source system** (and in OPERA Cloud, its context/type). Always store and document both.
- A locator is **not** a key. Don't join or upsert on it.
- A correlation ID identifies an **operation**, not a business object. Don't store it as the record's identity.
- Always state the **business-object scope** of an ID: a reservation ID is not a profile ID, and a block ID is not a reservation ID.
- A RUMBO identifier carried into OPERA Cloud or Genesis is an **external reference** with source system RUMBO, whatever it was in RUMBO. Document exactly where it's stored: an external reference type/context, a UDF, or a named field.

## Examples by business object

| Business object | Internal ID | External reference | Locator | Legacy RUMBO identifier |
|---|---|---|---|---|
| OPERA Cloud reservation | Reservation ID (TBC: exact field) | Genesis reference stored on the reservation (TBC: external reference type/context) | Confirmation number; cancellation number when cancelled | RUMBO reservation ID (TBC: kept, and where) |
| OPERA Cloud profile | Profile ID (TBC) | Genesis guest ID (TBC) | Membership number (TBC: locator or external reference?) | RUMBO client ID (TBC) |
| OPERA Cloud business block | Block ID (TBC) | Genesis group reference (TBC) | Block code | RUMBO group ID (TBC) |
| Genesis stay | Genesis stay ID (TBC) | OPERA reservation ID(s) | TBC | TBC |

The legacy RUMBO identifier names are placeholders until the shell workbooks confirm them. See [RUMBO to OPERA Cloud mapping](../mapping/index.md).

## Related terms

| Term | Meaning here |
|---|---|
| **Building block** | A unit of RUMBO data or configuration that is mapped to OPERA Cloud as a whole, such as a code set or a record type. |
| **Business-object scope** | The kind of record an ID belongs to (reservation, profile, stay, membership, block). |
| **RUMBO** | The RIU legacy platform that Genesis and OPERA Cloud replace. |
| **System of record** | The system whose value wins when two systems disagree. |
| **UDF** | User-defined field in OPERA Cloud. Document the semantics of any UDF that carries an identifier; don't assume a UDF value is stable or unique. |

## Related topics

- [Genesis and OPERA Cloud integration overview](../guides/genesis-opera-integration-overview.md)
- [Style guide: identifiers and relationships](../contributing/style-guide.md#identifiers-and-relationships)
- [RUMBO to OPERA Cloud mapping](../mapping/index.md)
