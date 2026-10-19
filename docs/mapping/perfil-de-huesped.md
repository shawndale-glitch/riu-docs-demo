# Perfil de huésped to Profile (Guest)

!!! warning "DRAFT"
    Not yet validated. Remove this block when an SME has reviewed the page.

Generated tables come from the shell workbook ([D-001](decision-log.md#d-001)). Change a mapping row in the workbook and re-run `tooling/mapping_import.py`; edit the other sections here.

## Summary

<!-- generated:start summary (tooling/mapping_import.py; edit the workbook, not this block) -->

| | RUMBO | OPERA Cloud |
|---|---|---|
| Object | Perfil de huésped | Profile (Guest) |
| Module / API | CLIENTES | OHIP CRM: Profiles |
| Business-object scope | Huéspedes individuales; empresas y agencias en otro bloque | |
| System of record after migration | | OPERA Cloud |

| | |
|---|---|
| Source workbook | `RUMBO-OPERA_perfil-huesped_v0.3.xlsx`, sheet `Campos`, version `v0.3` (2026-10-09) |
| Workbook SHA-256 | `5b49ca2d407dee94…` |
| Page status | In progress |
| SME | Responsable de Front Office (ejemplo) |

<!-- generated:end summary -->

## Relationship

TBC: cardinality and ownership after migration.

## Field mapping

<!-- generated:start fields (tooling/mapping_import.py; edit the workbook, not this block) -->

10 fields: 1 Gap, 4 Mapped, 1 Not migrated, 1 TBC, 3 Transform.

| RUMBO field | OPERA Cloud field | Rule | Identifier type | Required in OPERA Cloud | Status | Notes |
|---|---|---|---|---|---|---|
| `CLI_ID` | `profileIdList[type=ExternalReference]` | Direct | External reference | No | Mapped | Fuente RUMBO; se conserva para trazabilidad |
| `CLI_NOMBRE` | `customer.personName.givenName` | Direct | — | Yes | Mapped |  |
| `CLI_APELLIDOS` | `customer.personName.surname` | [T1](#t1) | — | Yes | Transform |  |
| `CLI_TRATAMIENTO` | `customer.personName.namePrefix` | [L1](#l1) | — | No | Transform |  |
| `CLI_IDIOMA` | `customer.language` | Direct | — | No | Mapped | ISO 639-1 en ambos |
| `CLI_EMAIL` | `emails.emailInfo.email.emailAddress` | Direct | — | No | Mapped |  |
| `CLI_VIP` | `profile.vipStatus` | [L2](#l2) | — | No | Transform |  |
| `CLI_FEC_ALTA` | — | — | — | — | Not migrated | [D-002](decision-log.md#d-002) |
| `CLI_PREF_ALMOHADA` | `preferenceCollection` | — | — | No | TBC | ¿Grupo de preferencias en OPERA? |
| `CLI_CONSENT_MKT` | — | — | — | — | Gap | [G-001](decision-log.md#g-001); OPERA guarda un consentimiento, RUMBO uno por canal |

<!-- generated:end fields -->

<!-- generated:start rules (tooling/mapping_import.py; edit the workbook, not this block) -->

## Transformation rules

### T1

Dividir apellidos.

| RUMBO value | OPERA Cloud value | Notes |
|---|---|---|
| García López | surname = García López | Se guardan juntos; OPERA tiene un solo campo |
| Smith | surname = Smith |  |

## Code lookups

### L1

Tratamiento.

| RUMBO code | Meaning | OPERA Cloud code | Notes |
|---|---|---|---|
| `SR` | Señor | `MR` |  |
| `SRA` | Señora | `MRS` |  |
| `DR` | Doctor/a | `DR` |  |

### L2

Nivel VIP.

| RUMBO code | Meaning | OPERA Cloud code | Notes |
|---|---|---|---|
| `1` | Cliente habitual | `VIP1` |  |
| `2` | Dirección | `VIP2` |  |
| `9` | Lista interna | — | Sin equivalente; ver notas de privacidad (TBC) |

<!-- generated:end rules -->

## Identifiers

TBC: list every RUMBO identifier and where it's stored in OPERA Cloud. See the [identifier glossary](../reference/identifier-glossary.md).

## Gaps and decisions

- [D-002](decision-log.md#d-002)
- [G-001](decision-log.md#g-001)

## Open questions

- [ ] TBC

## Related topics

- [RUMBO to OPERA Cloud mapping](index.md)
- [Decision and gap log](decision-log.md)
