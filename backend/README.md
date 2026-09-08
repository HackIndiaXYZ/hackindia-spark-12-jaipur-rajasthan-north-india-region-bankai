# AquaSentinel Backend

AquaSentinel is an intelligent water pipeline monitoring and leak detection platform built for hackathon demonstration. This package contains the complete Python/FastAPI backend, synthetic IoT network simulator, anomaly detection algorithms, leak probability and localization engine, government data adapters, and AI reasoning integration.

---

## 🏗️ Backend Architecture Overview

```
backend/
├── app/
│   ├── main.py                   # FastAPI application entrypoint & lifecycle
│   ├── api/                      # REST API endpoints
│   │   └── routes/
│   │       ├── health.py         # /api/health endpoint
│   │       └── network.py        # /api/network topology & status
│   ├── core/                     # Configuration and structured logging
│   │   ├── config.py
│   │   └── logging.py
│   ├── db/                       # Database engines and ORM models
│   │   ├── database.py           # SQLite fallback & PostgreSQL support
│   │   └── models.py             # SQLAlchemy ORM definitions
│   ├── models/                   # Water network domain models
│   │   ├── zone.py               # Water network zone model
│   │   ├── pipeline.py           # Pipeline segment model
│   │   ├── sensor.py             # IoT sensor domain model
│   │   ├── reading.py            # Sensor telemetry reading model
│   │   └── network.py            # Graph topology network model
│   ├── schemas/                  # Pydantic API response/request schemas
│   │   ├── zone.py
│   │   ├── pipeline.py
│   │   ├── sensor.py
│   │   ├── reading.py            # Sensor reading schemas
│   │   ├── simulation.py         # Simulation scenario request & status schemas
│   │   └── network.py
│   └── services/                 # Business logic & simulation services
│       └── simulator.py          # Synthetic IoT Sensor Simulator service
├── scripts/                      # Data generation & setup scripts
│   └── generate_demo_data.py     # Demo scenario dataset generator
├── tests/                        # Automated unit & API tests
│   ├── conftest.py
│   ├── test_network_models.py
│   ├── test_health_api.py
│   └── test_simulator.py        # Comprehensive simulator unit test suite
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

## 📡 Synthetic IoT Sensor Simulator

AquaSentinel includes a deterministic synthetic IoT telemetry simulator to simulate realistic pipeline conditions without physical hardware.

> **Note**: All sensor telemetry in the MVP is synthetically generated based on physical head-loss heuristics and network topology propagation.

### Simulator Features
- **Diurnal Time-of-Day Demand Curve**: Smooth multi-peak diurnal variation (morning peak ~08:00, evening peak ~19:00, night trough ~03:00).
- **Pressure-Flow Physics Correlation**: Increased demand/flow correlates with friction head loss (decreased pressure downstream).
- **Noise & Drift**: Configurable Gaussian measurement noise and linear sensor calibration drift.
- **Deterministic Random Seed**: Identical seed produces identical time series across runs.

### Supported Simulation Scenarios
1. `normal_operation`: Standard demand curve, nominal flow/pressure ranges, minor noise and drift.
2. `gradual_leak`: Pressure slowly drops while flow increases at the affected segment over time.
3. `sudden_burst`: Abrupt pressure drop and flow spike occurring instantly at a specified minute.
4. `sensor_fault`: Single sensor fault (e.g. `stuck`, `spike`, `drop`, `high_noise`) without network-wide hydraulic change.
5. `multiple_anomalies`: Simultaneous leak and sensor fault events.

---

## 🚀 Setup & Execution

### 1. Prerequisites
- Python 3.11+
- virtualenv (optional but recommended)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Automated Tests
```bash
pytest
```

### 4. Generate Demo Scenario Datasets
```bash
python scripts/generate_demo_data.py
```
This produces CSV datasets in `demo_datasets/` for `normal_operation`, `gradual_leak`, `sudden_burst`, and `sensor_fault`.

### 5. Launch Backend Server
```bash
python -m uvicorn app.main:app --reload --port 8000
```
- Interactive OpenAPI Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- API Health Endpoint: [http://localhost:8000/api/health](http://localhost:8000/api/health)
- Network Status: [http://localhost:8000/api/network](http://localhost:8000/api/network)
- Network Topology: [http://localhost:8000/api/network/topology](http://localhost:8000/api/network/topology)

---

## 📅 Roadmap & Milestones

- [x] **Milestone 1**: Project structure, domain models, graph network topology, Pydantic schemas, database configuration, initial test suite.
- [x] **Milestone 2**: Synthetic IoT Sensor Simulator (normal operation, demand curves, noise, drift, leak/burst/fault scenarios, deterministic seeds).
- [ ] **Milestone 3**: Anomaly Detection Engine (rolling statistics, z-score, Isolation Forest).
- [ ] **Milestone 4**: Leak Probability, Severity & Water Loss Estimator.
- [ ] **Milestone 5**: Graph-based Leak Localization Algorithm.
- [ ] **Milestone 6**: Incident Management & Lifecycle Persistence.
- [ ] **Milestone 7**: Complete REST API endpoints for readings, anomalies, leaks, and simulation control.
- [ ] **Milestone 8**: External Government Water Data Adapters (NWIC / Data.gov.in with caching & fallback).
- [ ] **Milestone 9**: AI Reasoning Layer (LLM integration for structured incident summaries).
- [ ] **Milestone 10**: End-to-End integration, demo scenario trigger API, and end-to-end test suite.
