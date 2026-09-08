# AquaSentinel Backend REST API Contract

Version: `1.0.0`  
Base URL: `/api`

---

## 1. Overview
This document defines the formal REST API contract for AquaSentinel's incident management, sensor telemetry analysis, and network observability services. It is intended for consume by frontend applications (e.g. Next.js).

---

## 2. Status & Severity Enums

### Incident Status Lifecycle
- `OPEN`: Newly detected leak or burst incident requiring operator attention.
- `ACKNOWLEDGED`: Operator has reviewed and acknowledged the incident.
- `RESOLVED`: Leak has been repaired or resolved.

**Allowed Status Transitions**:
- `OPEN` ➔ `ACKNOWLEDGED`
- `OPEN` ➔ `RESOLVED`
- `ACKNOWLEDGED` ➔ `RESOLVED`
- *Note: Reverse or illegal transitions (e.g., `RESOLVED` ➔ `OPEN`) return HTTP 400 Bad Request.*

### Incident Severity Levels
- `LOW`: Minor flow variance or localized anomaly.
- `MEDIUM`: Moderate flow loss ($\ge 10$ LPM).
- `HIGH`: Significant leak ($\ge 20$ LPM or $\ge 300$ Liters).
- `CRITICAL`: Severe burst/leak ($\ge 40$ LPM or $\ge 800$ Liters with high confidence).

---

## 3. API Endpoints

### 1. `POST /api/incidents/analyze`
Executes end-to-end incident analysis on a telemetry batch and persists the result idempotently.

- **HTTP Method**: `POST`
- **Path**: `/api/incidents/analyze`
- **Request Body**: Array of `SensorReadingSchema`
  ```json
  [
    {
      "timestamp": "2026-09-08T08:15:00Z",
      "sensor_id": "B3",
      "zone_id": "Zone_B",
      "pipeline_segment_id": "B2-B3",
      "pressure": 2.45,
      "flow_rate": 205.0,
      "temperature": 20.0,
      "sensor_health": "HEALTHY"
    }
  ]
  ```
- **Response**: `200 OK` — `IncidentResultSchema` (or `null` if no leak incident detected)
  ```json
  {
    "incident_id": "INC-001",
    "fingerprint": "a1b2c3d4e5f67890",
    "incident_type": "LEAK_SUSPECTED",
    "severity": "CRITICAL",
    "status": "OPEN",
    "affected_segment": "B2-B3",
    "affected_zone": "Zone_B",
    "detected_at": "2026-09-08T08:15:00Z",
    "created_at": "2026-09-08T08:15:01Z",
    "updated_at": "2026-09-08T08:15:01Z",
    "detection_delay_min": 15.0,
    "confidence": 0.879,
    "responsive_sensors": ["B1", "B2", "B3"],
    "estimated_flow_loss_lpm": 30.94,
    "estimated_volume_loss_liters": 1082.8,
    "candidate_segments": [
      {
        "segment_id": "B2-B3",
        "confidence": 0.87,
        "reason": "Segment connects responsive sensors B2 and B3"
      }
    ],
    "evidence": [
      "Localized to segment B2-B3 in Zone_B",
      "Estimated flow loss rate: 30.9 LPM"
    ],
    "observability_score": 0.897,
    "disclaimer": "Loss values are model-derived simulation estimates intended for demonstration and system evaluation."
  }
  ```

---

### 2. `GET /api/incidents`
Lists persisted pipeline incidents with optional status and severity filtering.

- **HTTP Method**: `GET`
- **Path**: `/api/incidents`
- **Query Parameters**:
  - `status` *(optional)*: `OPEN`, `ACKNOWLEDGED`, `RESOLVED`
  - `severity` *(optional)*: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
  - `limit` *(optional)*: Default 50 (max 200)
  - `offset` *(optional)*: Default 0
- **Response**: `200 OK` — Array of `IncidentResultSchema`

---

### 3. `GET /api/incidents/{incident_id}`
Retrieves a single incident by its unique ID.

- **HTTP Method**: `GET`
- **Path**: `/api/incidents/{incident_id}`
- **Response**:
  - `200 OK`: `IncidentResultSchema`
  - `404 Not Found`: `{"detail": "Incident 'INC-999' not found."}`

---

### 4. `PATCH /api/incidents/{incident_id}/status`
Updates the lifecycle status of an existing incident.

- **HTTP Method**: `PATCH`
- **Path**: `/api/incidents/{incident_id}/status`
- **Request Body**:
  ```json
  {
    "status": "ACKNOWLEDGED"
  }
  ```
- **Response**:
  - `200 OK`: Updated `IncidentResultSchema`
  - `400 Bad Request`: `{"detail": "Invalid status transition from 'RESOLVED' to 'OPEN'."}`
  - `404 Not Found`: `{"detail": "Incident 'INC-999' not found."}`

---

## 4. Government Data Context Endpoints

> [!NOTE]
> The endpoints below expose external regional surface water data (NWDP / Rajasthan telemetry datasets) for regional context and calibration only. They do NOT represent direct pipeline leak telemetry or trigger automated leak alerts.

### 1. `GET /api/data-sources`
Lists available government surface water telemetry datasets.

- **HTTP Method**: `GET`
- **Path**: `/api/data-sources`
- **Response**: `200 OK`
  ```json
  {
    "sources": [
      {
        "source_id": "rajasthan_rainfall_telemetry",
        "dataset_name": "Rajasthan Surface Water Telemetry Hourly Rainfall",
        "agency": "Rajasthan Surface Water Department",
        "source_organization": "National Water Data Portals / India WRIS",
        "geography": "Rajasthan, India",
        "data_frequency": "Hourly",
        "start_date": "2021-10-17 07:00",
        "end_date": "2030-01-01 08:00",
        "format": "CSV",
        "local_file": "rainfall_tel_hr_rajasthan_sw_rj_2021_2025.csv",
        "source_type": "GOVERNMENT_TELEMETRY",
        "description": "Hourly regional rainfall telemetry observations from rain stations across Rajasthan.",
        "unit": "mm",
        "zone": null
      }
    ],
    "total_count": 3
  }
  ```

### 2. `GET /api/data-sources/{source_id}`
Retrieves metadata for a specific government dataset.

- **HTTP Method**: `GET`
- **Path**: `/api/data-sources/{source_id}`
- **Response**: `200 OK` (Single `DataSourceResponse` object) or `404 Not Found`

### 3. `GET /api/data-sources/{source_id}/summary`
Retrieves statistical summary, coverage dates, and historical calibration metrics.

- **HTTP Method**: `GET`
- **Path**: `/api/data-sources/{source_id}/summary`
- **Response**: `200 OK`
  ```json
  {
    "source_id": "rajasthan_rainfall_telemetry",
    "latest_timestamp": "2026-01-01 08:00",
    "latest_value": 0.5,
    "unit": "mm",
    "min_value": 0.0,
    "max_value": 420.0,
    "mean_value": 2.451,
    "median_value": 0.5,
    "observation_count": 143464,
    "missing_value_count": 0,
    "coverage_start": "2021-10-17 07:00",
    "coverage_end": "2026-01-01 08:00",
    "historical_mean_deviation": -1.951
  }
  ```

### 4. `GET /api/data-sources/{source_id}/recent`
Retrieves a bounded list of recent observations for a dataset.

- **HTTP Method**: `GET`
- **Path**: `/api/data-sources/{source_id}/recent?limit=50`
- **Query Parameters**:
  - `limit` *(optional)*: Integer between 1 and 500 (default 50).
- **Response**: `200 OK` (`ObservationListResponse`)

