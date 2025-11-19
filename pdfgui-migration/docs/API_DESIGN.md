# pdfGUI REST API Design

## API Overview

- **Base URL**: `/api/v1`
- **Authentication**: JWT Bearer tokens
- **Content-Type**: `application/json`
- **File Uploads**: `multipart/form-data`

## Authentication Endpoints

### POST `/auth/register`

Register new user account.

**Request:**

```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:** `201 Created`

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "created_at": "2025-01-15T10:30:00Z"
}
```

### POST `/auth/login`

Authenticate user and get JWT token.

**Request:**

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:** `200 OK`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### POST `/auth/refresh`

Refresh access token.

### POST `/auth/logout`

Invalidate current session.

### POST `/auth/forgot-password`

Request password reset email.

### POST `/auth/reset-password`

Reset password with token.

---

## Project Management

### GET `/projects`

List all projects for current user.

**Query Parameters:**

- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20)
- `archived`: Include archived (default: false)
- `search`: Search by name

**Response:** `200 OK`

```json
{
  "items": [
    {
      "id": "uuid",
      "name": "LaMnO3 Temperature Series",
      "description": "Temperature-dependent study",
      "fitting_count": 10,
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-16T14:20:00Z"
    }
  ],
  "total": 45,
  "page": 1,
  "per_page": 20
}
```

### POST `/projects`

Create new project.

**Request:**

```json
{
  "name": "Ni FCC Study",
  "description": "Room temperature Ni refinement"
}
```

### GET `/projects/{project_id}`

Get project details with fittings summary.

### PUT `/projects/{project_id}`

Update project metadata.

### DELETE `/projects/{project_id}`

Archive/delete project.

### POST `/projects/{project_id}/duplicate`

Duplicate entire project.

### POST `/projects/{project_id}/export`

Export project as .ddp file (original format).

### POST `/projects/import`

Import from .ddp file.

**Request:** `multipart/form-data`

- `file`: .ddp project file

---

## Fitting (Refinement) Management

### GET `/projects/{project_id}/fittings`

List all fittings in project.

**Response:** `200 OK`

```json
{
  "items": [
    {
      "id": "uuid",
      "name": "fit-d300",
      "status": "COMPLETED",
      "rw_value": 0.1823,
      "chi_squared": 1.456,
      "phase_count": 1,
      "dataset_count": 1,
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

### POST `/projects/{project_id}/fittings`

Create new fitting.

**Request:**

```json
{
  "name": "fit-d300",
  "copy_from": "uuid" // Optional: copy from existing fitting
}
```

### GET `/fittings/{fitting_id}`

Get complete fitting details.

**Response:** `200 OK`

```json
{
  "id": "uuid",
  "name": "fit-d300",
  "status": "COMPLETED",
  "phases": [...],
  "datasets": [...],
  "calculations": [...],
  "parameters": [...],
  "constraints": [...],
  "results": {
    "rw": 0.1823,
    "chi_squared": 1.456,
    "iterations": 45
  },
  "created_at": "2025-01-15T10:30:00Z",
  "completed_at": "2025-01-15T10:35:00Z"
}
```

### PUT `/fittings/{fitting_id}`

Update fitting configuration.

### DELETE `/fittings/{fitting_id}`

Delete fitting.

### POST `/fittings/{fitting_id}/duplicate`

Duplicate fitting within same project.

---

## Refinement Execution

### POST `/fittings/{fitting_id}/run`

Start refinement job.

**Request:**

```json
{
  "max_iterations": 100,
  "tolerance": 1e-8
}
```

**Response:** `202 Accepted`

```json
{
  "job_id": "uuid",
  "status": "QUEUED",
  "queue_position": 3
}
```

### GET `/fittings/{fitting_id}/status`

Get current refinement status.

**Response:** `200 OK`

```json
{
  "status": "RUNNING",
  "iteration": 23,
  "current_rw": 0.2156,
  "elapsed_time": 12.5
}
```

### POST `/fittings/{fitting_id}/stop`

Stop running refinement.

### WebSocket `/ws/fittings/{fitting_id}`

Real-time updates during refinement.

**Messages:**

```json
{
  "type": "iteration",
  "data": {
    "iteration": 23,
    "rw": 0.2156,
    "parameters": {...}
  }
}
```

---

## Phase (Structure) Management

### GET `/fittings/{fitting_id}/phases`

List all phases in fitting.

### POST `/fittings/{fitting_id}/phases`

Add phase to fitting.

**Request:**

```json
{
  "name": "LaMnO3",
  "file_id": "uuid" // Reference to uploaded structure file
}
```

### GET `/phases/{phase_id}`

Get phase details with atoms.

**Response:** `200 OK`

```json
{
  "id": "uuid",
  "name": "LaMnO3",
  "space_group": "Pnma",
  "lattice": {
    "a": 5.53884,
    "b": 7.7042,
    "c": 5.4835,
    "alpha": 90.0,
    "beta": 90.0,
    "gamma": 90.0
  },
  "atoms": [
    {
      "index": 1,
      "element": "La",
      "x": 0.0493,
      "y": 0.25,
      "z": -0.0086,
      "occupancy": 1.0,
      "uiso": 0.00126
    }
  ],
  "pdf_parameters": {
    "scale": 1.0,
    "delta1": 0.0,
    "delta2": 0.0,
    "sratio": 1.0,
    "spdiameter": 0.0
  },
  "constraints": {...}
}
```

### PUT `/phases/{phase_id}`

Update phase configuration.

### DELETE `/phases/{phase_id}`

Remove phase from fitting.

### PUT `/phases/{phase_id}/lattice`

Update lattice parameters.

**Request:**

```json
{
  "a": 5.54,
  "b": 7.71,
  "c": 5.49,
  "alpha": 90.0,
  "beta": 90.0,
  "gamma": 90.0
}
```

### PUT `/phases/{phase_id}/pdf-parameters`

Update PDF-specific parameters.

### GET `/phases/{phase_id}/atoms`

List atoms in phase.

### POST `/phases/{phase_id}/atoms`

Add atom(s) to phase.

### PUT `/phases/{phase_id}/atoms/{atom_index}`

Update atom properties.

### DELETE `/phases/{phase_id}/atoms/{atom_index}`

Delete atom from phase.

### POST `/phases/{phase_id}/atoms/bulk`

Bulk insert atoms.

### PUT `/phases/{phase_id}/selected-pairs`

Set pair selection for PDF calculation.

**Request:**

```json
{
  "selections": ["all-all", "!La-La", "Mn-O"]
}
```

---

## Dataset Management

### GET `/fittings/{fitting_id}/datasets`

List datasets in fitting.

### POST `/fittings/{fitting_id}/datasets`

Add dataset to fitting.

**Request:**

```json
{
  "name": "300K",
  "file_id": "uuid" // Reference to uploaded data file
}
```

### GET `/datasets/{dataset_id}`

Get dataset details with data arrays.

**Response:** `200 OK`

```json
{
  "id": "uuid",
  "name": "300K",
  "source_type": "N",
  "qmax": 32.0,
  "qdamp": 0.01,
  "qbroad": 0.02,
  "dscale": 1.0,
  "fit_range": {
    "rmin": 1.0,
    "rmax": 30.0,
    "rstep": 0.01
  },
  "point_count": 2000,
  "metadata": {
    "temperature": 300,
    "instrument": "NPDF"
  }
}
```

### PUT `/datasets/{dataset_id}`

Update dataset configuration.

### DELETE `/datasets/{dataset_id}`

Remove dataset from fitting.

### GET `/datasets/{dataset_id}/data`

Get raw data arrays.

**Query Parameters:**

- `rmin`: Minimum r value
- `rmax`: Maximum r value
- `include_calc`: Include calculated PDF
- `include_diff`: Include difference

**Response:** `200 OK`

```json
{
  "observed": {
    "r": [1.0, 1.01, 1.02, ...],
    "G": [-0.5, -0.3, -0.1, ...],
    "dG": [0.01, 0.01, 0.01, ...]
  },
  "calculated": {
    "r": [1.0, 1.01, 1.02, ...],
    "G": [-0.48, -0.31, -0.09, ...]
  },
  "difference": {
    "r": [1.0, 1.01, 1.02, ...],
    "G": [-0.02, 0.01, -0.01, ...]
  }
}
```

### PUT `/datasets/{dataset_id}/instrument`

Update instrument parameters.

**Request:**

```json
{
  "qmax": 32.0,
  "qdamp": 0.01,
  "qbroad": 0.02,
  "dscale": 1.0
}
```

### PUT `/datasets/{dataset_id}/fit-range`

Update fitting range.

**Request:**

```json
{
  "rmin": 1.5,
  "rmax": 25.0,
  "rstep": 0.01
}
```

---

## Calculation Management

### GET `/fittings/{fitting_id}/calculations`

List calculations in fitting.

### POST `/fittings/{fitting_id}/calculations`

Create new calculation.

**Request:**

```json
{
  "name": "calc-theory",
  "rmin": 0.01,
  "rmax": 50.0,
  "rstep": 0.01
}
```

### GET `/calculations/{calculation_id}`

Get calculation details and results.

### PUT `/calculations/{calculation_id}`

Update calculation parameters.

### DELETE `/calculations/{calculation_id}`

Delete calculation.

### POST `/calculations/{calculation_id}/run`

Execute calculation.

### GET `/calculations/{calculation_id}/data`

Get calculated PDF data.

---

## Parameter Management

### GET `/fittings/{fitting_id}/parameters`

Get all parameters for fitting.

**Response:** `200 OK`

```json
{
  "parameters": [
    {
      "index": 1,
      "name": "lat_a",
      "initial_value": 5.53,
      "refined_value": 5.53884,
      "uncertainty": 0.00012,
      "is_fixed": false,
      "bounds": { "lower": 5.0, "upper": 6.0 }
    }
  ]
}
```

### PUT `/fittings/{fitting_id}/parameters`

Update multiple parameters.

**Request:**

```json
{
  "parameters": [
    {
      "index": 1,
      "initial_value": 5.54,
      "is_fixed": false,
      "bounds": { "lower": 5.0, "upper": 6.0 }
    }
  ]
}
```

### PUT `/fittings/{fitting_id}/parameters/{index}/fix`

Fix/unfix parameter.

### PUT `/fittings/{fitting_id}/parameters/{index}/bounds`

Set parameter bounds.

---

## Constraint Management

### GET `/fittings/{fitting_id}/constraints`

List all constraints.

**Response:** `200 OK`

```json
{
  "constraints": [
    {
      "id": "uuid",
      "target": "lat(4)",
      "formula": "@1",
      "phase_id": "uuid"
    },
    {
      "id": "uuid",
      "target": "u11(3)",
      "formula": "@7 * 3.0",
      "phase_id": "uuid"
    }
  ]
}
```

### POST `/fittings/{fitting_id}/constraints`

Add constraint.

**Request:**

```json
{
  "target": "y(2)",
  "formula": "@3 + 0.4",
  "phase_id": "uuid"
}
```

### PUT `/constraints/{constraint_id}`

Update constraint formula.

### DELETE `/constraints/{constraint_id}`

Remove constraint.

### POST `/fittings/{fitting_id}/constraints/validate`

Validate constraint formula.

**Request:**

```json
{
  "formula": "@1 * sin(@2)"
}
```

**Response:** `200 OK`

```json
{
  "valid": true,
  "parameters_used": [1, 2],
  "parsed_ast": {...}
}
```

---

## File Upload & Management

### POST `/files/upload`

Upload structure or data file.

**Request:** `multipart/form-data`

- `file`: The file to upload
- `file_type`: 'stru', 'pdb', 'cif', 'xyz', 'gr', 'dat', 'chi'

**Response:** `201 Created`

```json
{
  "id": "uuid",
  "filename": "Ni.stru",
  "file_type": "stru",
  "file_size": 1234,
  "checksum": "sha256:...",
  "preview": {
    "format": "pdffit",
    "atom_count": 4,
    "space_group": "Fm-3m"
  },
  "created_at": "2025-01-15T10:30:00Z"
}
```

### GET `/files/{file_id}`

Get file metadata.

### GET `/files/{file_id}/download`

Download original file.

### GET `/files/{file_id}/preview`

Get parsed file preview.

### DELETE `/files/{file_id}`

Delete uploaded file.

### GET `/files`

List user's uploaded files.

**Query Parameters:**

- `file_type`: Filter by type
- `project_id`: Filter by project

---

## Plotting & Visualization

### GET `/fittings/{fitting_id}/plots/pdf`

Get PDF plot data.

**Query Parameters:**

- `datasets`: Dataset IDs (comma-separated)
- `show_calculated`: Include calculated (default: true)
- `show_difference`: Include difference (default: true)
- `offset`: Vertical offset between datasets

**Response:** `200 OK`

```json
{
  "plot_type": "pdf",
  "datasets": [
    {
      "id": "uuid",
      "name": "300K",
      "observed": {"r": [...], "G": [...]},
      "calculated": {"r": [...], "G": [...]},
      "difference": {"r": [...], "G": [...]}
    }
  ],
  "config": {
    "x_label": "r (Å)",
    "y_label": "G (Å⁻²)",
    "x_range": [0, 30],
    "y_range": [-5, 10]
  }
}
```

### GET `/fittings/{fitting_id}/plots/structure`

Get 3D structure visualization data.

### GET `/fittings/{fitting_id}/plots/parameters`

Get parameter evolution plot.

### GET `/projects/{project_id}/plots/series`

Get temperature/doping series plot.

**Query Parameters:**

- `parameter`: Parameter to plot (e.g., 'lat_a', 'rw')
- `series_type`: 'temperature' or 'doping'

### POST `/plots/config`

Save plot configuration.

### GET `/plots/config/{config_id}`

Load saved plot configuration.

---

## Series Analysis

### GET `/projects/{project_id}/series`

Get series analysis data.

**Response:** `200 OK`

```json
{
  "series_type": "temperature",
  "values": [300, 350, 400, 450, 500],
  "fittings": ["uuid1", "uuid2", "uuid3", "uuid4", "uuid5"],
  "parameters": {
    "lat_a": [5.53, 5.54, 5.55, 5.56, 5.57],
    "lat_b": [7.7, 7.71, 7.72, 7.73, 7.74],
    "rw": [0.18, 0.19, 0.17, 0.18, 0.19]
  }
}
```

### POST `/projects/{project_id}/series/extract`

Extract series from multiple fittings.

**Request:**

```json
{
  "series_type": "temperature",
  "fitting_ids": ["uuid1", "uuid2", ...],
  "temperature_regex": "fit-d(\\d+)"
}
```

---

## Run History & Session Management

### GET `/history`

Get user's run history.

**Query Parameters:**

- `page`, `per_page`: Pagination
- `fitting_id`: Filter by fitting
- `action_type`: Filter by action
- `date_from`, `date_to`: Date range

**Response:** `200 OK`

```json
{
  "items": [
    {
      "id": "uuid",
      "action_type": "RUN_REFINEMENT",
      "fitting_id": "uuid",
      "fitting_name": "fit-d300",
      "input_params": {...},
      "output_results": {...},
      "execution_time": 12.5,
      "status": "COMPLETED",
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

### GET `/history/{history_id}`

Get detailed history entry with wizard state.

### POST `/history/{history_id}/replay`

Replay a previous session.

**Response:** `201 Created`

```json
{
  "fitting_id": "uuid",
  "message": "Session replayed successfully"
}
```

---

## User Settings

### GET `/settings`

Get user settings.

### PUT `/settings`

Update user settings.

**Request:**

```json
{
  "plot_preferences": {
    "default_colors": ["#1f77b4", "#ff7f0e"],
    "line_width": 1.5,
    "marker_size": 4
  },
  "default_parameters": {
    "qmax": 32.0,
    "fit_rmax": 30.0
  },
  "ui_preferences": {
    "theme": "dark",
    "auto_save": true
  }
}
```

---

## Export & Import

### POST `/fittings/{fitting_id}/export/results`

Export fitting results.

**Request:**

```json
{
  "format": "json", // 'json', 'csv', 'txt'
  "include": ["parameters", "data", "plots"]
}
```

### POST `/fittings/{fitting_id}/export/structure`

Export refined structure.

**Request:**

```json
{
  "phase_id": "uuid",
  "format": "stru" // 'stru', 'cif', 'xyz', 'pdb'
}
```

### POST `/fittings/{fitting_id}/export/data`

Export PDF data.

**Request:**

```json
{
  "dataset_id": "uuid",
  "format": "gr", // 'gr', 'dat', 'csv'
  "include_calculated": true
}
```

---

## Health & Status

### GET `/health`

API health check.

### GET `/status`

System status including queue.

**Response:** `200 OK`

```json
{
  "status": "healthy",
  "queue": {
    "pending": 5,
    "running": 2
  },
  "version": "1.0.0"
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid parameter value",
    "details": {
      "field": "qmax",
      "reason": "must be positive"
    }
  }
}
```

### Error Codes

- `400` - Bad Request (validation errors)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `409` - Conflict (duplicate resource)
- `422` - Unprocessable Entity (business logic error)
- `500` - Internal Server Error
- `503` - Service Unavailable (queue full)

---

## Rate Limiting

- **Authenticated users**: 1000 requests/hour
- **File uploads**: 100/hour, 50MB max file size
- **Refinement jobs**: 20 concurrent per user
- **WebSocket connections**: 10 per user

Headers:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1642248000
```

---

## Pagination

All list endpoints use cursor-based or offset pagination:

```json
{
  "items": [...],
  "total": 150,
  "page": 2,
  "per_page": 20,
  "has_next": true,
  "has_prev": true
}
```

---

## WebSocket Events

### Connection

```
ws://api.example.com/ws/fittings/{fitting_id}?token=<jwt>
```

### Event Types

- `status_change`: Fitting status changed
- `iteration`: Refinement iteration completed
- `parameter_update`: Parameters updated
- `error`: Error occurred
- `complete`: Refinement finished

### Example Messages

```json
{"type": "iteration", "data": {"iteration": 23, "rw": 0.2156}}
{"type": "complete", "data": {"rw": 0.1823, "iterations": 45}}
{"type": "error", "data": {"message": "Convergence failed"}}
```
