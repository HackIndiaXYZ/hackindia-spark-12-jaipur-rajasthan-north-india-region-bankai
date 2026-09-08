# AquaSentinel

### AI-Powered Water Network Intelligence & Resilience

> **"See the Network. Detect the Incident. Understand the Risk."**

AquaSentinel is an AI-powered water-network intelligence and resilience platform designed to monitor simulated network telemetry, detect anomalous hydraulic behavior, evaluate network observability, identify monitoring blind spots, localize suspected pipeline incidents, estimate model-derived water loss, manage incidents through their lifecycle, and provide AI-assisted explanations and operator guidance.

Water distribution networks are critical infrastructure, yet municipal operators often lack full visibility into spatial network behavior. Transient pressure drops, gradual flow leaks, sensor calibration drift, and severe pipe bursts present distinct operational signatures that traditional threshold alarms fail to differentiate. AquaSentinel addresses this challenge by combining statistical anomaly detection with topology-aware graph reasoning and network observability analysis.

*Note: The current implementation of AquaSentinel is a software-based prototype and intelligence platform utilizing a synthetic 10-node water distribution network, model-derived hydraulic loss estimation, offline regional government telemetry, and server-side grounded AI explainability.*

---

## 💡 Why AquaSentinel?

Water-network anomalies are not all the same. An abnormal sensor signal can represent a developing pipeline leak, a catastrophic pipe burst, an isolated sensor transducer fault, or simply inadequate monitoring coverage in a complex sub-zone.

AquaSentinel combines anomaly detection with topology-aware reasoning and observability analysis so the system can answer not only:

> **"Is something abnormal?"**

...but also:

- **"Where is it likely happening?"** (Graph-based spatial localization across pipeline segments)
- **"How observable is that part of the network?"** (Quantified simulated observability scoring)
- **"How much impact is estimated?"** (Model-derived flow loss rate in LPM and accumulated volume loss in Liters)
- **"Is this a network incident or an isolated sensor problem?"** (Spatial neighbor correlation to prevent false leak alarms)
- **"What evidence supports the conclusion?"** (Grounded multi-signal evidence and AI-assisted operator guidance)

---

## ⭐ What Makes AquaSentinel Different?

### Network Observability & Blind-Spot Intelligence

A water network may contain healthy sensors and still suffer from weak spatial observability. AquaSentinel goes beyond point anomaly detection by evaluating **simulated network observability** across pipeline segments, identifying sub-zones with weaker sensor coverage, and evaluating candidate virtual sensor placements for simulated coverage improvement.

AquaSentinel evaluates:
- **Simulated Observability Scores**: Segment-level observability calculated from topology distance, sensor responsiveness, and network redundancy.
- **Candidate Sensor Placements**: Algorithmic evaluation of potential virtual sensor locations to improve network coverage.
- **Monitoring Blind Spots**: Clear visual highlighting of sub-zones where detection delay or spatial coverage is sub-optimal.

> **"Monitor the Network. Monitor the Monitoring."**

---

## 🚀 Key Capabilities

| Capability | Description |
| :--- | :--- |
| **Synthetic Telemetry Simulation** | Generates realistic time-series pressure/flow behavior with diurnal demand curves, noise, drift, leaks, bursts, and faults. |
| **Statistical Anomaly Detection** | Detects unusual pressure drops, flow discrepancies, and transient spikes using rolling Z-scores and Isolation Forest models. |
| **Sensor Fault Distinction** | Distinguishes isolated single-sensor anomalies from correlated spatial network incidents, preventing false leak alarms. |
| **Network Observability** | Quantifies simulated detection and response coverage across all 10 canonical pipeline segments. |
| **Blind-Spot Intelligence** | Identifies lower-observability areas and evaluates candidate virtual sensor placements to boost network coverage. |
| **Topology-Aware Localization** | Uses NetworkX graph structure and spatial sensor correlation to localize suspected leaks to specific pipeline segments. |
| **Water-Loss Estimation** | Computes model-derived simulated flow loss rates (LPM) and accumulated volume loss (Liters). |
| **Incident Persistence Lifecycle** | Tracks and persists pipeline incidents through a strict lifecycle state machine (`OPEN` ➔ `ACKNOWLEDGED` ➔ `RESOLVED`). |
| **Government Data Context** | Integrates offline Rajasthan surface water telemetry (rainfall, reservoir, canal) as descriptive regional context and baseline calibration. |
| **Grounded Gemini AI Analysis** | Employs server-side Google Gemini 2.5 Flash to generate grounded incident summaries, evidence explanations, and operator action steps. |

---

## 🔄 How It Works

```text
               +----------------------------------+
               |  Synthetic / Replayed Telemetry  |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |    Anomaly Detection Engine      |
               | (Z-Score + Spatial Discrepancy)  |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               | Network Observability Evaluation |
               |   (Segment Coverage & Scoring)   |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |   Topology-Aware Localization    |
               | (Graph Reasoning & Neighbor Check)|
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |   Water Loss Estimation Engine   |
               | (Model-Derived Flow & Vol Loss)  |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |  Incident Classification & DB    |
               |   (Idempotent Fingerprinting)    |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |  Grounded Gemini 2.5 Flash AI    |
               |  (Server-Side Evidence Explainer)|
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |    Operator Control Console      |
               | (Lifecycle Action & Investigation)|
               +----------------------------------+
```

---

## 🏛️ System Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       NEXT.JS 16 FRONTEND CONTROL ROOM                       │
│  - App Shell & Scenario Controller                                          │
│  - Interactive SVG Topology Map (10 Sensors / 10 Segments)                  │
│  - Real-Time Telemetry Gauges & Historical Recharts Charts                  │
│  - Incident Management Table & Detail View                                  │
│  - AI Incident Analysis & Operator Guidance Panel                           │
│  - Rajasthan Government Data Context Viewer                                 │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │ REST API Calls (HTTP / JSON)
                                      v
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI BACKEND SERVICE                           │
│  - REST API Routes (/api/incidents, /api/network, /api/data-sources)       │
│  - Domain Models (Zone, Pipeline, Sensor, Reading, Anomaly, Incident)       │
│  - Anomaly Detector (Rolling Z-Score & Isolation Forest)                    │
│  - NetworkX Graph Topology Engine & Leak Localizer                          │
│  - Model-Derived Water Loss Estimator (LPM & Volume)                        │
│  - Observability & Virtual Sensor Placement Engine                          │
│  - SQLite Database & SQLAlchemy ORM Repository                              │
│  - Government Data CSV Loaders (Rajasthan Surface Water Datasets)          │
│  - Server-Side Gemini AI Service (google-genai SDK + Fallback)               │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │ Google GenAI API (Server-Side Only)
                                      v
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GOOGLE GEMINI 2.5 FLASH AI                          │
│  - Grounded Evidence Interpretation & Operator Decision Support             │
│  - Enforced Pydantic JSON Schema Validation (AIAnalysisResult)              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🧪 Interactive Demo Scenarios

AquaSentinel features 5 built-in, repeatable scenario presets for demonstration and verification:

1. **Scenario A: Normal Operation**
   - Baseline pressure (2.4–2.5 bar) and flow (200 LPM) across all 3 zones.
   - All 10 sensors report healthy status; network state is `HEALTHY`; zero active leaks.
2. **Scenario B: Gradual Leak (Segment B2-B3)**
   - Developing leak on segment `B2-B3` in Zone B.
   - Pipeline edge `B2-B3` pulses red on the topology map; flow loss rate ~32 LPM; incident classified as `LEAK_SUSPECTED`.
3. **Scenario C: Sudden Burst (Zone B)**
   - Catastrophic pressure drop (-1.45 bar in <2 min) across responsive sensors `B1`–`B4`.
   - Rapid detection delay; flow loss rate ~78 LPM; incident classified as `BURST_EVENT` with `CRITICAL` severity.
4. **Scenario D: Sensor Fault (Sensor B3) — *Critical Acceptance Test***
   - Sensor `B3` exhibits erratic pressure spikes (+2.8 bar), while neighboring sensors `B2` and `B4` remain normal.
   - Spatial correlation identifies zero network leak propagation; pipeline segments `B2-B3` and `B3-B4` remain **NORMAL** (cyan).
   - **False alarm prevented**: No false leak incident is declared on the pipeline network.
5. **Scenario E: Multiple Anomalies**
   - Concurrent anomalies across Zone A and Zone B evaluating multi-branch spatial isolation stability.

---

## 💻 Technology Stack

### Backend
- **Core Framework**: Python 3.14 / 3.11+, FastAPI, Pydantic v2, Pydantic-Settings
- **Graph Topology & Analytics**: NetworkX, NumPy, SciPy, scikit-learn
- **Database & Persistence**: SQLAlchemy 2.0, SQLite
- **AI / LLM Integration**: Official `google-genai` Python SDK (`gemini-2.5-flash`)
- **Testing & Quality**: Pytest, Pytest-Asyncio, HTTPX

### Frontend
- **Framework**: Next.js 16 (App Router, Turbopack), React 19, TypeScript
- **Styling & UI**: Tailwind CSS, Lucide Icons, Glassmorphic Modern Dark Mode Design System
- **Data Visualization**: Recharts, SVG Network Graph Visualization

---

## 📁 Repository Structure

```text
hackindia-spark-12-jaipur-rajasthan-north-india-region-bankai/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # FastAPI REST endpoints (health, network, incidents, data-sources)
│   │   ├── core/                # Configuration settings & structured logging
│   │   ├── db/                  # SQLite database engine, ORM models, and repositories
│   │   ├── models/              # Domain models (zone, pipeline, sensor, reading, anomaly, incident, network)
│   │   ├── schemas/             # Pydantic request/response schemas (AI analysis, incident, data sources)
│   │   └── services/            # Anomaly detector, localizer, loss estimator, observability, AI service
│   ├── experiments/             # Evaluation scripts (ai_analysis_evaluation.py, incident_evaluation.py)
│   ├── tests/                   # 65 automated unit, API, integration, and grounding tests
│   ├── data/                    # Offline Rajasthan NWDP government CSV datasets
│   ├── requirements.txt         # Pinned backend Python dependencies
│   └── README.md                # Detailed backend documentation
│
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router pages (dashboard, network, incidents, sensors, data-sources)
│   │   ├── components/          # Interactive Control Room UI, SVG Topology Map, AI Analysis Panel
│   │   ├── context/             # DemoContext & Scenario Controller
│   │   ├── lib/api/             # Centralized REST API client
│   │   ├── lib/demo/            # Demo data fixtures & telemetry generator
│   │   └── types/               # TypeScript data models and enums
│   ├── package.json
│   └── tsconfig.json
│
├── docs/
│   └── API_CONTRACT.md          # OpenAPI REST contract specification
├── LICENSE                      # Open-source license
└── README.md                    # Root project documentation
```

---

## 🤖 AI Engine & Gemini Integration

AquaSentinel incorporates a server-side **Google Gemini AI** explainability service (`google-genai` SDK):

1. **Server-Side Security**: All Gemini interactions occur 100% server-side in FastAPI. `GEMINI_API_KEY` is managed via `backend/.env` and is **never** exposed to browser JavaScript or client code.
2. **Grounded Explainability**: Gemini is **not** the primary leak detection engine; deterministic backend algorithms compute facts upstream. Gemini explains pre-computed evidence and generates operator action steps.
3. **Pydantic Schema Validation**: Enforces JSON schema constraints (`AIAnalysisResult`) on all generated outputs to guarantee structured responses (`summary`, `why_detected`, `recommended_actions`, `confidence_note`, `limitations`).
4. **Safe Deterministic Fallback**: If `GEMINI_API_KEY` is not configured or the API is unavailable, `AIAnalysisService` seamlessly falls back to a grounded deterministic analysis (`provider: "deterministic_fallback"`), ensuring zero system downtime.

---

## 🏛️ Government Data Context Layer

AquaSentinel includes an offline **Government Data Context & Calibration Layer** utilizing actual surface water datasets from Rajasthan, India (sourced from National Water Data Portals / India WRIS):

- **Integrated Datasets**:
  1. *Rajasthan Surface Water Telemetry Hourly Rainfall* (`rainfall_telemetry`)
  2. *Rajasthan Surface Water Telemetry Reservoir Level & Storage* (`reservoir_telemetry`)
  3. *Rajasthan Surface Water Telemetry Canal Discharge* (`canal_telemetry`)
- **Role & Boundaries**: Government data provides regional environmental context (e.g. ambient rainfall or regional reservoir levels) and baseline calibration data. It does **not** represent direct urban pipeline leak telemetry and does **not** trigger automated leak alerts.

---

## 🔌 API Overview

The backend exposes a clean REST API documented in [`docs/API_CONTRACT.md`](file:///a:/Amar/Projects/Project%208%20%28Hack%20India%29/docs/API_CONTRACT.md):

- `GET /api/health` — Backend health status.
- `GET /api/network` — Current network health summary and active anomaly counts.
- `GET /api/network/topology` — Full canonical 10-sensor / 10-segment topology graph.
- `POST /api/incidents/analyze` — End-to-end incident detection, localization, and loss estimation pipeline execution.
- `GET /api/incidents` — List persisted incidents with optional status/severity filters.
- `GET /api/incidents/{id}` — Retrieve single incident by ID.
- `PATCH /api/incidents/{id}/status` — Update incident status (`OPEN` ➔ `ACKNOWLEDGED` ➔ `RESOLVED`).
- `POST /api/incidents/{id}/ai-analysis` — Generate or fetch grounded Gemini AI analysis.
- `GET /api/data-sources` — List available government water datasets.
- `GET /api/data-sources/{id}/summary` — Statistical summary and coverage metrics for a dataset.
- `GET /api/data-sources/{id}/recent` — Bounded list of recent observations.

---

## ⚙️ Installation & Local Setup

### Prerequisites
- **Python**: `3.11` or `3.14+`
- **Node.js**: `18.x` or `20.x+` (with `npm`)

### 1. Clone Repository
```bash
git clone https://github.com/HackIndiaXYZ/hackindia-spark-12-jaipur-rajasthan-north-india-region-bankai.git
cd hackindia-spark-12-jaipur-rajasthan-north-india-region-bankai
```

### 2. Backend Setup
```bash
cd backend

# Create & activate virtual environment (optional)
python -m venv venv
# On Windows: venv\Scripts\activate
# On Linux/macOS: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file for Gemini API Key (optional)
echo GEMINI_API_KEY="your-gemini-api-key" > .env
echo GEMINI_MODEL="gemini-2.5-flash" >> .env
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
```

---

## 🏃 Running the Full Project

### Step 1: Start Backend API Server
In terminal 1:
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
*Backend API will run at `http://127.0.0.1:8000` (OpenAPI docs at `http://127.0.0.1:8000/docs`).*

### Step 2: Start Frontend Control Room
In terminal 2:
```bash
cd frontend
npm run dev
```
*Frontend Control Room will run at `http://localhost:3000`.*

---

## 🧪 Testing

### Backend Unit & Integration Test Suite
AquaSentinel includes a 65-test suite covering simulator logic, anomaly detection, topology graph traversal, loss estimation, incident persistence lifecycle, API routes, and AI grounding checks.

```bash
cd backend
python -m pytest
```
*Expected output: `65 passed`.*

### AI Evaluation Script
Evaluate Gemini AI structured generation across scenarios:
```bash
cd backend
python experiments/ai_analysis_evaluation.py
```

### Frontend Build & Lint Checks
```bash
cd frontend
npm run lint
npm run build
```

---

## 🎮 Demo Walkthrough for Judges

1. **Landing Page (`/`)**: Overview of AquaSentinel, platform architecture, and entry to Control Room.
2. **Dashboard (`/dashboard`)**:
   - Observe 4 high-level KPI cards (Network Status, Active Incidents, Total Water Loss Rate, Observability Index).
   - Use the **Scenario Control** dropdown in the left sidebar to toggle between scenarios.
   - Select **Scenario B: Gradual Leak (B2-B3)** and watch segment `B2-B3` pulse red on the SVG map.
3. **Network Topology (`/network`)**:
   - Inspect the interactive SVG graph displaying all 10 canonical nodes and 10 pipeline segments.
   - Hover over nodes to inspect sensor telemetry readings and segment health scores.
4. **Incidents (`/incidents` & `/incidents/[id]`)**:
   - View active incidents in the control table.
   - Click on an incident to view detail metrics, candidate segment confidence breakdown, and spatial evidence.
   - Click **"Analyze"** in the **AI Incident Analysis Panel** to trigger Gemini AI explainability.
   - Click **"Acknowledge"** and **"Resolve"** buttons to test the lifecycle state machine.
5. **Sensor Fault Demonstration (Scenario D)**:
   - Select **Scenario D: Sensor Fault (B3)**.
   - Observe that Sensor `B3` is highlighted yellow/amber, while pipeline segments `B2-B3` and `B3-B4` remain **cyan/healthy**.
   - Verify that **0 false leak alarms** are created on the pipeline network.
6. **Government Context (`/data-sources`)**:
   - Browse regional Rajasthan surface water datasets (Rainfall, Reservoir Storage, Canal Discharge) and view statistical summaries and recent observations.

---

## ⚠️ Limitations & Responsible Claims

- **Software Prototype**: AquaSentinel is a software demonstration prototype built for hackathon evaluation using a simplified synthetic water distribution network topology.
- **Model-Derived Loss Estimates**: Flow loss rates (LPM) and volume loss figures (Liters) are model-derived simulation estimates intended for system evaluation and do not represent physically calibrated hydraulic field measurements.
- **Government Data Role**: Offline Rajasthan surface water telemetry provides descriptive regional context and baseline calibration; it is not a live runtime dependency for pipeline leak alerts.
- **AI Boundaries**: Gemini AI provides server-side grounded explainability over computed backend facts; it does not replace core deterministic anomaly detection algorithms.

---

## 📅 Completed Milestones & Roadmap

- [x] **Milestone 1**: Project foundation, domain models, NetworkX graph topology engine, database setup, Pytest test suite.
- [x] **Milestone 2**: Synthetic IoT Sensor Simulator (diurnal curves, noise, drift, leak/burst/fault scenarios, deterministic seeds).
- [x] **Milestone 3**: Anomaly Detection Engine (rolling Z-scores, spatial graph neighbor comparison, Isolation Forest).
- [x] **Milestone 4**: Network Observability & Blind-Spot Intelligence (simulated observability scores, virtual sensor placement engine).
- [x] **Milestone 5**: Leak Detection, Topology-Aware Localization & Water Loss Estimator (spatial candidate scoring, flow/volume loss estimation).
- [x] **Milestone 6**: Incident Persistence Lifecycle & Database ORM (SQLAlchemy, status transitions, idempotent fingerprinting).
- [x] **Milestone 7**: Government Data Context & Calibration Layer (Offline Rajasthan NWDP loaders, summary statistics, provenance metadata).
- [x] **Frontend**: Production-quality Next.js 16 Control Room UI with interactive SVG topology map, Recharts telemetry charts, and incident management console.
- [x] **Milestone 9**: Grounded Gemini AI Analysis & Response Intelligence (Server-side Gemini 2.5 Flash SDK, Pydantic schema validation, safe deterministic fallback).
- [x] **System QA**: 100% automated test pass rate (65/65 pytest tests) and clean production build.

---

## 👥 Team & Project Metadata

- **Event**: HackIndia 2026
- **Team**: Bankai
- **Repository Tag**: `hackindia-spark-12-jaipur-rajasthan-north-india-region-bankai`
- **GitHub Repository**: [`https://github.com/HackIndiaXYZ/hackindia-spark-12-jaipur-rajasthan-north-india-region-bankai`](https://github.com/HackIndiaXYZ/hackindia-spark-12-jaipur-rajasthan-north-india-region-bankai)
- **License**: Open Source / MIT
