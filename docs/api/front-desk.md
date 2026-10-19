# Front Desk API (sample)

Fictional sample spec for the documentation demo. It shows how an OpenAPI file becomes the API reference page and the target that process bindings are checked against. Not a real Genesis API.

<!-- generated:start api (tooling/api_render.py; edit the spec, not this block) -->

| | |
|---|---|
| Spec | [`front-desk.openapi.yaml`](../api/specs/front-desk.openapi.yaml) (OpenAPI 3.0.3) |
| API version | `0.3.0` |
| Base URL | `https://api.example.test/front-desk/v0` |
| Spec SHA-256 | `317b7c12a173…` |

## Operations

| Operation ID | Method and path | Summary |
|---|---|---|
| [`getRoomStatus`](#getroomstatus) | `GET /rooms/{roomId}/status` | Get the housekeeping status of a room |
| [`recordRoomInspection`](#recordroominspection) | `POST /rooms/{roomId}/inspections` | Record a room inspection |
| [`requestPriorityCleaning`](#requestprioritycleaning) | `POST /housekeeping/tasks` | Ask housekeeping to clean a room first |
| [`assignRoom`](#assignroom) | `PUT /reservations/{reservationId}/room-assignment` | Assign a room to a reservation |
| [`checkInReservation`](#checkinreservation) | `POST /reservations/{reservationId}/check-in` | Check in the guest on a reservation |

### getRoomStatus

`GET /rooms/{roomId}/status`

Returns whether the room is dirty, clean, or clean and inspected. Front desk calls it before assigning a room early.

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `roomId` | path | string | Yes | Room number as configured for the hotel (internal ID). |
| `X-Correlation-ID` | header | string (uuid) | No | Correlation ID carried across systems for tracing and conformance replay. |

| Response | Description |
|---|---|
| `200` | Current status |
| `404` | No such resource |

### recordRoomInspection

`POST /rooms/{roomId}/inspections`

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `roomId` | path | string | Yes | Room number as configured for the hotel (internal ID). |
| `X-Correlation-ID` | header | string (uuid) | No | Correlation ID carried across systems for tracing and conformance replay. |

Request body:

| Field | Type | Required | Description |
|---|---|---|---|
| `result` | `PASSED` \| `FAILED` | Yes |  |
| `notes` | string | No |  |

| Response | Description |
|---|---|
| `201` | Inspection recorded; room status becomes INSPECTED when the result is PASSED |

### requestPriorityCleaning

`POST /housekeeping/tasks`

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `X-Correlation-ID` | header | string (uuid) | No | Correlation ID carried across systems for tracing and conformance replay. |

Request body:

| Field | Type | Required | Description |
|---|---|---|---|
| `roomId` | string | Yes |  |
| `priority` | `NORMAL` \| `HIGH` | Yes |  |

| Response | Description |
|---|---|
| `202` | Task queued |

### assignRoom

`PUT /reservations/{reservationId}/room-assignment`

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `reservationId` | path | string | Yes | Reservation internal ID (not the confirmation number). |
| `X-Correlation-ID` | header | string (uuid) | No | Correlation ID carried across systems for tracing and conformance replay. |

Request body:

| Field | Type | Required | Description |
|---|---|---|---|
| `roomId` | string | Yes |  |

| Response | Description |
|---|---|
| `200` | Room assigned |
| `409` | Room isn't available for this stay |

### checkInReservation

`POST /reservations/{reservationId}/check-in`

Renamed from `checkInGuest` in 0.3.0.

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `reservationId` | path | string | Yes | Reservation internal ID (not the confirmation number). |
| `X-Correlation-ID` | header | string (uuid) | No | Correlation ID carried across systems for tracing and conformance replay. |

| Response | Description |
|---|---|
| `200` | Guest checked in; emits `reservation.checked-in` |
| `409` | Reservation has no room assigned |

## Schemas

### RoomStatus

| Field | Type | Required | Description |
|---|---|---|---|
| `roomId` | string | Yes |  |
| `status` | `DIRTY` \| `CLEAN` \| `INSPECTED` \| `OUT_OF_ORDER` | Yes |  |
| `updatedAt` | string (date-time) | No |  |

## Events

From [`front-desk.asyncapi.yaml`](../api/specs/front-desk.asyncapi.yaml) (AsyncAPI 2.6.0, version `0.3.0`).

| Channel | Message | Description |
|---|---|---|
| `reservation.early-check-in.requested` | `EarlyCheckInRequested` | A guest asked to check in before the standard time. |
| `reservation.checked-in` | `ReservationCheckedIn` | A reservation moved to checked-in. |

<!-- generated:end api -->

## Related topics

- [API reference](index.md)
- [Identifier glossary](../reference/identifier-glossary.md)
