# AquaSentinel Backend

AquaSentinel is an intelligent water pipeline monitoring and leak detection platform built for hackathon demonstration. This package contains the complete Python/FastAPI backend, synthetic IoT network simulator, anomaly detection algorithms, topology-aware leak localization engine, water loss estimator, incident management pipeline, government data adapters, and AI reasoning integration.

---

## 🏗️ Backend Architecture Overview

```
backend/
├── app/
│   ├── main.py                   # FastAPI application entrypoint & lifecycle
│   ├── api/                      # REST API endpoints
│   │   └── routes/
│   │       ├── health.py         # /api/health endpoint
│   │       ├── network.py        # /api/network topology & status
│   │       └── incidents.py      # /api/incidents/analyze endpoint
│   ├── core/                     # Configuration and structured logging
│   │   ├── config.py
│   │   └── logging.py
│   ├── db/                       # Database engines and ORM models
│   │   ├── database.py           # SQLite fallback & PostgreSQL support
│   │   └── models.py             # SQLAlchemy ORM definitions
│   ├── models/                   # Water network & incident domain models
│   │   ├── zone.py
│   │   ├── pipeline.py
│   │   ├── sensor.py
│   │   ├── reading.py
│   │   ├── anomaly.py
│   │   ├── observability.py
│   │   ├── incident.py           # Incident domain model & enums
│   │   └── network.py
│   ├── schemas/                  # Pydantic API response/request schemas
│   │   ├── zone.py
│   │   ├── pipeline.py
│   │   ├── sensor.py
│   │   ├── reading.py
│   │   ├── anomaly.py
│   │   ├── observability.py
│   │   ├── incident.py           # Incident schemas
│   │   └── network.py
│   └── services/                 # Business logic & intelligence engines
│       ├── simulator.py          # Synthetic IoT Sensor Simulator service
│       ├── anomaly_detector.py   # Anomaly Detection service (Z-score + IsolationForest)
│       ├── observability.py      # Network Observability & Blind-spot engine
│       ├── localization.py       # Topology-aware Leak Localizer
│       ├── loss_estimator.py     # Model-derived Water Loss Estimator
│       └── incident_service.py   # End-to-End Incident Pipeline service
├── scripts/                      # Data generation & evaluation scripts
│   ├── generate_demo_data.py
│   ├── evaluate_anomaly_detection.py
│   ├── evaluate_incident_pipeline.py
│   └── observability_evaluation.py
├── tests/                        # Automated unit & API tests
│   ├── conftest.py
│   ├── test_network_models.py
│   ├── test_health_api.py
│   ├── test_simulator.py
│   ├── test_anomaly_detection.py
│   ├── test_observability.py
│   └── test_incident.py          # Incident pipeline unit tests
├── .env.example                  # Environment template
├── requirements.txt              # Backend dependencies
└── README.md                     # Backend documentation
```

---

## 🌊 Virtual Water Network Topology

AquaSentinel models a virtual water distribution network as a directed graph (`NetworkX`):

```
                       [ Reservoir ]
                            |
         +------------------+------------------+
         |                  |                  |
      [  A1  ]           [  B1  ]           [  C1  ]
         |                  |                  |
      [  A2  ]           [  B2  ]           [  C2  ]
         |                  |                  |
      [  A3  ]           [  B3  ]           [  C3  ]
                            |
                         [  B4  ]
```

- **Zone A**: Residential district (Nodes A1, A2, A3; Segments R-A1, A1-A2, A2-A3)
- **Zone B**: Industrial hub (Nodes B1, B2, B3, B4; Segments R-B1, B1-B2, B2-B3, B3-B4)
- **Zone C**: Commercial center (Nodes C1, C2, C3; Segments R-C1, C1-C2, C2-C3)

---

## 🚨 Incident Pipeline & Leak Localization

The AquaSentinel incident pipeline processes simulated sensor telemetry to identify, localize, and estimate the severity of pipeline leaks and burst events:

### 1. Topology-Aware Localization (`LeakLocalizer`)
- Analyzes spatial relationships between responsive sensors using `NetworkX` graph traversal.
- Scores candidate pipeline segments based on direct connectivity between responsive sensors, directional flow/pressure head loss, and path alignment.
- **Sensor Fault Distinction**: Isolated single-sensor anomalies (e.g. noise spikes or faulty health status without neighboring sensor support) are correctly identified as sensor faults rather than false pipeline leaks.

### 2. Model-Derived Loss Estimator (`WaterLossEstimator`)
- Calculates instantaneous flow loss rate in Liters Per Minute (LPM) and accumulated volume loss in Liters.
- Uses explainable baseline flow comparison ($\Delta Q = Q_{\text{observed}} - Q_{\text{expected}}$) and pressure head loss heuristics.
- > **Disclaimer**: *Loss values are model-derived simulation estimates intended for demonstration and system evaluation.*

### 3. Incident Confidence & Severity Classification (`IncidentService`)
- **Normalized Confidence**: Weighted combination of localization confidence (45%), average anomaly score (30%), zone sensor response ratio (15%), and segment observability score (10%).
- **Severity Thresholds**:
  - `CRITICAL`: Confidence $\ge 0.70$ AND (Flow loss $\ge 40$ LPM OR Volume loss $\ge 800$ Liters)
  - `HIGH`: Confidence $\ge 0.60$ AND (Flow loss $\ge 20$ LPM OR Volume loss $\ge 300$ Liters)
  - `MEDIUM`: Confidence $\ge 0.50$ AND Flow loss $\ge 10$ LPM
  - `LOW`: Baseline leak detection.

---

## 🚀 Setup & Execution

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Automated Test Suite
```bash
pytest
```

### 3. Run Incident Pipeline Evaluation
```bash
python experiments/incident_evaluation.py
```

### 4. Launch Backend API Server
```bash
python -m uvicorn app.main:app --reload --port 8000
```
- Interactive OpenAPI Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- POST Incident Analysis Endpoint: `http://localhost:8000/api/incidents/analyze`
- GET Government Data Context Endpoints: `http://localhost:8000/api/data-sources`
- POST AI Analysis Endpoint: `http://localhost:8000/api/incidents/{id}/ai-analysis`

---

## 🤖 Grounded Gemini AI Analysis & Response Intelligence

AquaSentinel incorporates a server-side **Google Gemini AI** explainability service (`google-genai` SDK):

- **Grounded Explainability**: Gemini provides AI-assisted explanation and response guidance over pre-computed, structured AquaSentinel evidence. It is **not** the primary incident detection or localization engine.
- **Server-Side Security**: API keys (`GEMINI_API_KEY`) are managed 100% server-side and never exposed to browser code.
- **Structured JSON Validation**: Enforces Pydantic schema validation (`AIAnalysisResult`) on all generated outputs.
- **Safe Fallback**: Automatically switches to a deterministic grounded fallback (`provider: "deterministic_fallback"`) if API key is missing or network/quota errors occur.

---

## 📅 Roadmap & Milestones

- [x] **Milestone 1**: Project structure, domain models, graph network topology, Pydantic schemas, database configuration, initial test suite.
- [x] **Milestone 2**: Synthetic IoT Sensor Simulator (normal operation, demand curves, noise, drift, leak/burst/fault scenarios, deterministic seeds).
- [x] **Milestone 3**: Anomaly Detection Engine (rolling statistics, z-score, Isolation Forest).
- [x] **Milestone 4**: Network Observability & Blind-Spot Intelligence (observability scores, virtual sensor placement engine).
- [x] **Milestone 5**: Leak Detection, Localization & Loss Estimator (topology-aware localization, flow/volume loss estimation, confidence & severity scoring).
- [x] **Milestone 6**: Incident Management & Persistence Lifecycle (Database ORM persistence, idempotency fingerprinting, status transitions).
- [x] **Milestone 7**: Government Data Context & Calibration Layer (Offline Rajasthan NWDP loader, statistical summaries, provenance metadata, read-only API).
- [x] **Milestone 9**: Grounded Gemini AI Analysis & Response Intelligence (Server-side Gemini 2.5 Flash SDK, JSON schema validation, safe deterministic fallback).
- [ ] **Milestone 10**: End-to-End integration, demo scenario trigger API, and end-to-end test suite.


