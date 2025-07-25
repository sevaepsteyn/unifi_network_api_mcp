# UniFi Network API Documentation (based on 9.2.87)

## Authentication

- **Method**: X-API-Key header
- **Header Format**: `x-api-key: YOUR_API_KEY`

## API Versions

- **Production**: `/proxy/network/integration/v1/*`

## Base URL

```
https://{controller}/proxy/network/integration/v1
```

Where `{controller}` is your cloud-hosted UniFi controller hostname, for example:
- `1d82c190-8f4a-4bc8-8c87-687afca97309.unifi-hosting.ui.com`

## Common Response Format

### Paginated Response
```json
{
  "offset": 0,
  "limit": 25,
  "count": 10,
  "totalCount": 1000,
  "data": [...]
}
```

### Error Response
```json
{
  "statusCode": 400,
  "statusName": "UNAUTHORIZED",
  "message": "Missing credentials",
  "timestamp": "2024-11-27T08:13:46.966Z",
  "requestPath": "/integration/v1/sites/123",
  "requestId": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

**Note**: In case of Internal Server Error (statusCode = 500), the request ID can be used to track down the error in the server log.

## Filtering

The API supports advanced filtering using the `filter` query parameter.

### Filter Syntax
- **Property expressions**: `<property>.<function>(<arguments>)`
- **Compound expressions**: `<logical-operator>(<expressions>)`
- **Not expressions**: `not(<expression>)`

### Property Expression Examples
- `id.eq(123)` - checks if id equals 123
- `name.isNotNull()` - checks if name is not null
- `createdAt.in(2025-01-01, 2025-01-05)` - checks if createdAt is either date

### Compound Expression Examples
- `and(name.isNull(), createdAt.gt(2025-01-01))` - checks if name is null AND createdAt is greater than date
- `or(name.isNull(), expired.isNull(), expiresAt.isNull())` - checks if ANY of the properties is null

### Not Expression Example
- `not(name.like('guest*'))` - checks if name does NOT start with 'guest'

### Supported Data Types
| Type | Examples | Syntax |
|------|----------|--------|
| STRING | 'Hello, ''World''!' | Wrapped in single quotes. Escape single quote with another single quote |
| NUMBER | 123, 123.321 | Starts with digit, optional decimal part |
| TIMESTAMP | 2025-01-29, 2025-01-29T12:39:11Z | ISO 8601 format |
| BOOLEAN | true, false | Either true or false |
| UUID | 550e8400-e29b-41d4-a716-446655440000 | String without quotes, 8-4-4-4-12 format |

### Filtering Functions
| Function | Arguments | Semantics | Supported Types |
|----------|-----------|-----------|-----------------|
| isNull | 0 | is null | all types |
| isNotNull | 0 | is not null | all types |
| eq | 1 | equals | all types |
| ne | 1 | not equals | all types |
| gt | 1 | greater than | STRING, NUMBER, TIMESTAMP, UUID |
| ge | 1 | greater than or equals | STRING, NUMBER, TIMESTAMP, UUID |
| lt | 1 | less than | STRING, NUMBER, TIMESTAMP, UUID |
| le | 1 | less than or equals | STRING, NUMBER, TIMESTAMP, UUID |
| like | 1 | matches pattern | STRING |
| in | 1+ | one of | STRING, NUMBER, TIMESTAMP, UUID |
| notIn | 1+ | not one of | STRING, NUMBER, TIMESTAMP, UUID |

### Pattern Matching (like function)
- `.` matches any single character
- `*` matches any number of characters
- `\` escapes `.` and `*`

Examples:
- `type.like('type.')` matches `type1` but not `type100`
- `name.like('guest*')` matches `guest1` and `guest100`

## Available Endpoints

### About Application

#### GET /v1/info

Retrieve general information about the UniFi Network application.

**Request:**
```bash
curl -X GET "https://{controller}/proxy/network/integration/v1/info" \
  -H "x-api-key: YOUR_API_KEY"
```

**Response:**
```json
{
  "applicationVersion": "9.1.0"
}
```

### Sites

#### GET /v1/sites

Retrieve a paginated list of local sites managed by this Network application. Site ID is required for other UniFi Network API calls.

**Filterable Properties:**
| Name | Type | Allowed Functions |
|------|------|-------------------|
| id | UUID | eq, ne, in, notIn |
| internalReference | STRING | eq, ne, in, notIn |
| name | STRING | eq, ne, in, notIn |

**Query Parameters:**
- `offset` (number): >= 0, default: 0
- `limit` (number): 0-200, default: 25
- `filter` (string): Filter expression

**Request:**
```bash
curl -X GET "https://{controller}/proxy/network/integration/v1/sites" \
  -H "x-api-key: YOUR_API_KEY"
```

**Response:**
```json
{
  "offset": 0,
  "limit": 25,
  "count": 10,
  "totalCount": 1000,
  "data": [
    {
      "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "internalReference": "string",
      "name": "string"
    }
  ]
}
```

### UniFi Devices

#### GET /v1/sites/{siteId}/devices

Retrieve a paginated list of all adopted devices on a site, including basic device information.

**Path Parameters:**
- `siteId` (required): string (UUID)

**Query Parameters:**
- `offset` (number): >= 0, default: 0
- `limit` (number): 0-200, default: 25

**Response:**
```json
{
  "offset": 0,
  "limit": 25,
  "count": 10,
  "totalCount": 1000,
  "data": [
    {
      "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "name": "IW HD",
      "model": "UHDIW",
      "macAddress": "94:2a:6f:26:c6:ca",
      "ipAddress": "192.168.1.55",
      "state": "ONLINE",
      "features": ["switching"],
      "interfaces": ["ports"]
    }
  ]
}
```

#### GET /v1/sites/{siteId}/devices/{deviceId}

Retrieve detailed information about a specific adopted device.

**Path Parameters:**
- `siteId` (required): string (UUID)
- `deviceId` (required): string (UUID)

**Response:**
```json
{
  "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
  "name": "IW HD",
  "model": "UHDIW",
  "supported": true,
  "macAddress": "94:2a:6f:26:c6:ca",
  "ipAddress": "192.168.1.55",
  "state": "ONLINE",
  "firmwareVersion": "6.6.55",
  "firmwareUpdatable": true,
  "adoptedAt": "2019-08-24T14:15:22Z",
  "provisionedAt": "2019-08-24T14:15:22Z",
  "configurationId": "7596498d2f367dc2",
  "uplink": {
    "deviceId": "4de4adb9-21ee-47e3-aeb4-8cf8ed6c109a"
  },
  "features": {
    "switching": null,
    "accessPoint": null
  },
  "interfaces": {
    "ports": [
      {
        "idx": 1,
        "state": "UP",
        "connector": "RJ45",
        "maxSpeedMbps": 10000,
        "speedMbps": 1000,
        "poe": {
          "standard": "802.3bt",
          "type": 3,
          "enabled": true,
          "state": "UP"
        }
      }
    ],
    "radios": [
      {
        "wlanStandard": "802.11a",
        "frequencyGHz": "2.4",
        "channelWidthMHz": 40,
        "channel": 36
      }
    ]
  }
}
```

#### GET /v1/sites/{siteId}/devices/{deviceId}/statistics/latest

Retrieve the latest real-time statistics of a specific adopted device.

**Path Parameters:**
- `siteId` (required): string (UUID)
- `deviceId` (required): string (UUID)

**Response:**
```json
{
  "uptimeSec": 0,
  "lastHeartbeatAt": "2019-08-24T14:15:22Z",
  "nextHeartbeatAt": "2019-08-24T14:15:22Z",
  "loadAverage1Min": 0.1,
  "loadAverage5Min": 0.1,
  "loadAverage15Min": 0.1,
  "cpuUtilizationPct": 0.1,
  "memoryUtilizationPct": 0.1,
  "uplink": {
    "txRateBps": 0,
    "rxRateBps": 0
  },
  "interfaces": {
    "radios": [
      {
        "frequencyGHz": "2.4",
        "txRetriesPct": 0.1
      }
    ]
  }
}
```

#### POST /v1/sites/{siteId}/devices/{deviceId}/actions

Perform an action on a specific adopted device.

**Path Parameters:**
- `siteId` (required): string (UUID)
- `deviceId` (required): string (UUID)

**Request Body:**
```json
{
  "action": "RESTART"
}
```

**Supported Actions:**
- `RESTART` - Restart the device

#### POST /v1/sites/{siteId}/devices/{deviceId}/interfaces/ports/{portIdx}/actions

Perform an action on a specific device port.

**Path Parameters:**
- `siteId` (required): string (UUID)
- `deviceId` (required): string (UUID)
- `portIdx` (required): integer

**Request Body:**
```json
{
  "action": "POWER_CYCLE"
}
```

**Supported Actions:**
- `POWER_CYCLE` - Power cycle the port

### Clients

#### GET /v1/sites/{siteId}/clients

Retrieve a paginated list of all connected clients on a site.

**Filterable Properties:**
| Name | Type | Allowed Functions |
|------|------|-------------------|
| id | UUID | eq, ne, in, notIn |
| type | STRING | eq, ne, in, notIn |
| macAddress | STRING | isNull, isNotNull, eq, ne, in, notIn |
| ipAddress | STRING | isNull, isNotNull, eq, ne, in, notIn |
| connectedAt | TIMESTAMP | isNull, isNotNull, eq, ne, gt, ge, lt, le |
| access.type | STRING | eq, ne, in, notIn |
| access.authorized | BOOLEAN | isNull, isNotNull, eq, ne |

**Query Parameters:**
- `offset` (number): >= 0, default: 0
- `limit` (number): 0-200, default: 25
- `filter` (string): Filter expression

**Response:**
```json
{
  "offset": 0,
  "limit": 25,
  "count": 10,
  "totalCount": 1000,
  "data": [
    {
      "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "name": "string",
      "connectedAt": "2019-08-24T14:15:22Z",
      "ipAddress": "string",
      "access": {
        "type": "DEFAULT"
      },
      "type": "string"
    }
  ]
}
```

#### GET /v1/sites/{siteId}/clients/{clientId}

Retrieve detailed information about a specific connected client.

**Path Parameters:**
- `siteId` (required): string (UUID)
- `clientId` (required): string (UUID)

**Response (Example for WIRED client):**
```json
{
  "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
  "name": "string",
  "connectedAt": "2019-08-24T14:15:22Z",
  "ipAddress": "string",
  "access": {
    "type": "string"
  },
  "type": "WIRED",
  "macAddress": "string",
  "uplinkDeviceId": "c2692e57-1e51-4519-bb90-c2bdad5882ca"
}
```

**Client Types:**
- `WIRED`
- `WIRELESS`
- `VPN`
- `TELEPORT`

#### POST /v1/sites/{siteId}/clients/{clientId}/actions

Perform an action on a specific connected client.

**Path Parameters:**
- `siteId` (required): string (UUID)
- `clientId` (required): string (UUID)

**Request Body:**
```json
{
  "action": "AUTHORIZE_GUEST_ACCESS",
  "timeLimitMinutes": 1440,
  "dataUsageLimitMBytes": 1024,
  "rxRateLimitKbps": 1000,
  "txRateLimitKbps": 1000
}
```

**Supported Actions:**
- `AUTHORIZE_GUEST_ACCESS` - Authorize guest access
- `UNAUTHORIZE_GUEST_ACCESS` - Revoke guest access

**Optional Parameters for AUTHORIZE_GUEST_ACCESS:**
- `timeLimitMinutes` (integer): 1-1000000, time limit in minutes
- `dataUsageLimitMBytes` (integer): 1-1048576, data usage limit
- `rxRateLimitKbps` (integer): 2-100000, download rate limit
- `txRateLimitKbps` (integer): 2-100000, upload rate limit

### Hotspot Vouchers

#### GET /v1/sites/{siteId}/hotspot/vouchers

Retrieve a paginated list of Hotspot vouchers.

**Filterable Properties:**
| Name | Type | Allowed Functions |
|------|------|-------------------|
| id | UUID | eq, ne, in, notIn |
| createdAt | TIMESTAMP | eq, ne, gt, ge, lt, le |
| name | STRING | eq, ne, in, notIn, like |
| code | STRING | eq, ne, in, notIn |
| authorizedGuestLimit | NUMBER | isNull, isNotNull, eq, ne, gt, ge, lt, le |
| authorizedGuestCount | NUMBER | eq, ne, gt, ge, lt, le |
| activatedAt | TIMESTAMP | eq, ne, gt, ge, lt, le |
| expiresAt | TIMESTAMP | eq, ne, gt, ge, lt, le |
| expired | BOOLEAN | eq, ne |
| timeLimitMinutes | NUMBER | eq, ne, gt, ge, lt, le |
| dataUsageLimitMBytes | NUMBER | isNull, isNotNull, eq, ne, gt, ge, lt, le |
| rxRateLimitKbps | NUMBER | isNull, isNotNull, eq, ne, gt, ge, lt, le |
| txRateLimitKbps | NUMBER | isNull, isNotNull, eq, ne, gt, ge, lt, le |

**Query Parameters:**
- `offset` (number): >= 0, default: 0
- `limit` (number): 0-1000, default: 100
- `filter` (string): Filter expression

**Response:**
```json
{
  "offset": 0,
  "limit": 25,
  "count": 10,
  "totalCount": 1000,
  "data": [
    {
      "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "createdAt": "2019-08-24T14:15:22Z",
      "name": "hotel-guest",
      "code": 4861409510,
      "authorizedGuestLimit": 1,
      "authorizedGuestCount": 0,
      "activatedAt": "2019-08-24T14:15:22Z",
      "expiresAt": "2019-08-24T14:15:22Z",
      "expired": true,
      "timeLimitMinutes": 1440,
      "dataUsageLimitMBytes": 1024,
      "rxRateLimitKbps": 1000,
      "txRateLimitKbps": 1000
    }
  ]
}
```

#### POST /v1/sites/{siteId}/hotspot/vouchers

Create one or more Hotspot vouchers.

**Path Parameters:**
- `siteId` (required): string (UUID)

**Request Body:**
```json
{
  "count": 1,
  "name": "hotel-guest",
  "authorizedGuestLimit": 1,
  "timeLimitMinutes": 1440,
  "dataUsageLimitMBytes": 1024,
  "rxRateLimitKbps": 1000,
  "txRateLimitKbps": 1000
}
```

**Required Fields:**
- `name` (string): Voucher note
- `timeLimitMinutes` (integer): 1-1000000

**Optional Fields:**
- `count` (integer): 1-1000, default: 1
- `authorizedGuestLimit` (integer): >= 1
- `dataUsageLimitMBytes` (integer): 1-1048576
- `rxRateLimitKbps` (integer): 2-100000
- `txRateLimitKbps` (integer): 2-100000

**Response (201 Created):**
```json
{
  "vouchers": [
    {
      "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "createdAt": "2019-08-24T14:15:22Z",
      "name": "hotel-guest",
      "code": 4861409510,
      "authorizedGuestLimit": 1,
      "authorizedGuestCount": 0,
      "activatedAt": "2019-08-24T14:15:22Z",
      "expiresAt": "2019-08-24T14:15:22Z",
      "expired": true,
      "timeLimitMinutes": 1440,
      "dataUsageLimitMBytes": 1024,
      "rxRateLimitKbps": 1000,
      "txRateLimitKbps": 1000
    }
  ]
}
```

#### GET /v1/sites/{siteId}/hotspot/vouchers/{voucherId}

Retrieve details of a specific Hotspot voucher.

**Path Parameters:**
- `siteId` (required): string (UUID)
- `voucherId` (required): string (UUID)

#### DELETE /v1/sites/{siteId}/hotspot/vouchers/{voucherId}

Remove a specific Hotspot voucher.

**Path Parameters:**
- `siteId` (required): string (UUID)
- `voucherId` (required): string (UUID)

**Response:**
```json
{
  "vouchersDeleted": 0
}
```

#### DELETE /v1/sites/{siteId}/hotspot/vouchers

Remove Hotspot vouchers based on filter criteria.

**Path Parameters:**
- `siteId` (required): string (UUID)

**Query Parameters:**
- `filter` (required): Filter expression

**Response:**
```json
{
  "vouchersDeleted": 0
}
```

## Error Handling

Common error responses:

### Missing Credentials
```json
{
  "statusCode": 401,
  "statusName": "UNAUTHORIZED",
  "message": "Missing credentials",
  "timestamp": "2024-11-27T08:13:46.966Z",
  "requestPath": "/integration/v1/sites/123",
  "requestId": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

### Bad Request
```json
{
  "statusCode": 400,
  "statusName": "BAD_REQUEST",
  "message": "Invalid request format",
  "timestamp": "2024-11-27T08:13:46.966Z",
  "requestPath": "/integration/v1/sites/123",
  "requestId": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

### Not Found
```json
{
  "statusCode": 404,
  "statusName": "NOT_FOUND",
  "message": "Resource not found",
  "timestamp": "2024-11-27T08:13:46.966Z",
  "requestPath": "/integration/v1/sites/123",
  "requestId": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

### Internal Server Error
```json
{
  "statusCode": 500,
  "statusName": "INTERNAL_SERVER_ERROR",
  "message": "An unexpected error occurred",
  "timestamp": "2024-11-27T08:13:46.966Z",
  "requestPath": "/integration/v1/sites/123",
  "requestId": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```
