# AquaSentinel

### AI-Powered Water Network Intelligence & Resilience

> **AquaSentinel is not just a leak detector. It is a water-network intelligence and resilience platform that evaluates both incidents and the observability of the system detecting them.**

> *"See the Network. Detect the Incident. Understand the Risk."*

---

## 🌐 Live Production Deployments

- 🖥️ **Live Vercel Frontend Control Room**: [`https://aquasentinel-rouge.vercel.app`](https://aquasentinel-rouge.vercel.app)
- ⚙️ **Live Render Backend API Service**: [`https://aquasentinel-api-r00y.onrender.com`](https://aquasentinel-api-r00y.onrender.com)
- 📚 **Interactive Swagger API Documentation**: [`https://aquasentinel-api-r00y.onrender.com/docs`](https://aquasentinel-api-r00y.onrender.com/docs)
- 📦 **Official GitHub Repository**: [`https://github.com/HackIndiaXYZ/hackindia-spark-12-jaipur-rajasthan-north-india-region-bankai`](https://github.com/HackIndiaXYZ/hackindia-spark-12-jaipur-rajasthan-north-india-region-bankai)

---

## ⚡ Executive Summary (Judge Quick View)

| What | Why | Differentiator | Live Demo |
| :--- | :--- | :--- | :--- |
| **Full-Stack Water Network Intelligence Platform** combining synthetic IoT simulation, statistical anomaly detection, graph localization, loss estimation, government context, and Gemini AI. | Traditional SCADA alerts produce high false alarms and lack spatial network context to distinguish pipe leaks from sensor faults. | **"Monitor the Network. Monitor the Monitoring."** Evaluates simulated network observability, blind spots, and candidate virtual sensor placement. | **5 Repeatable Scenarios**: Normal, Gradual Leak (B2-B3), Sensor Fault (B3), Sudden Burst, Multi-Anomaly. |

AquaSentinel is an infrastructure intelligence platform designed to monitor simulated water distribution networks, detect anomalous hydraulic behavior, evaluate network observability, identify monitoring blind spots, localize suspected pipeline incidents, estimate model-derived water loss, track incident lifecycles, and provide server-side grounded AI explainability for utility operators.

*Note: AquaSentinel is a software prototype and intelligence platform utilizing a synthetic 10-node water distribution network, model-derived hydraulic loss estimation, offline regional government telemetry, and server-side grounded AI reasoning.*

---

## 💡 Why AquaSentinel?

Water-network anomalies are not all the same. An abnormal sensor reading can represent:
- a developing pipeline leak
- a catastrophic pipe burst
- an isolated sensor transducer fault
- inadequate monitoring coverage in a sub-zone

AquaSentinel combines statistical anomaly detection with topology-aware graph reasoning and observability analysis so the system asks not only:

> **"Is something abnormal?"**

...but also:

- **"Where is it likely happening?"** (Graph-based spatial localization across pipeline segments)
- **"How observable is that part of the network?"** (Quantified simulated observability index)
- **"How much impact is estimated?"** (Model-derived flow loss rate in LPM and accumulated volume loss in Liters)
- **"Is this a network incident or an isolated sensor problem?"** (Spatial neighbor agreement to prevent false leak alarms)
- **"What evidence supports the conclusion?"** (Grounded multi-signal evidence and AI-assisted operator guidance)

---

## ⭐ What Makes AquaSentinel Different?

### Network Observability & Blind-Spot Intelligence

A water network may contain healthy sensors and still suffer from weak spatial observability. AquaSentinel evaluates **simulated network observability** across pipeline segments, identifies sub-zones with lower sensor response coverage, and evaluates candidate virtual sensor placements for potential coverage improvement.

- **Simulated Observability Score**: Segment-level index calculated from topology distance, sensor responsiveness, and network redundancy.
- **Monitoring Blind Spots**: Clear visual highlighting of sub-zones where detection delay or spatial coverage is sub-optimal.
- **Candidate Sensor Placement**: Algorithmic evaluation of potential virtual sensor locations to improve simulated network coverage.

> **"Monitor the Network. Monitor the Monitoring."**

---

## ⚙️ Technical Pipeline Details

AquaSentinel processes simulated sensor telemetry through a multi-stage deterministic and explainable intelligence pipeline:

```text
Synthetic / Replayed Telemetry
            ↓
     Anomaly Detection  (Rolling Z-Score, Rate-of-Change, Isolation Forest)
            ↓
   Network Observability (Simulated Observability Score & Blind Spots)
            ↓
Topology-Aware Localization (NetworkX Spatial Graph Reasoning)
            ↓
      Loss Estimation   (Model-Derived Flow LPM & Accumulated Volume)
            ↓
   Incident Classification (LEAK_SUSPECTED, SENSOR_FAULT, BURST_EVENT)
            ↓
     Incident Persistence (Idempotent SHA-256 Fingerprinting & DB Lifecycle)
            ↓
     Gemini AI Analysis (Server-Side Grounded Evidence Interpretation)
            ↓
   Operator Console     (Lifecycle State Machine: OPEN ➔ ACK ➔ RESOLVED)
```

### 1. Anomaly Detection
- **Baseline Behavior**: Tracks expected diurnal pressure (2.4–2.5 bar) and flow (200 LPM) patterns.
- **Rolling Statistics & Z-Scores**: Evaluates short-term rolling mean and standard deviation to flag statistical deviations ($|Z| \ge 2.5$).
- **Rate-of-Change & Persistence**: Monitors rapid pressure drop rate ($\Delta P / \Delta t$) and temporal persistence over consecutive intervals.
- **Multivariate Signals & Neighbor Comparison**: Compares pressure drops and flow discrepancies against neighboring nodes across the network graph.
- *Implementation Note*: Uses rolling statistical Z-scores and scikit-learn Isolation Forest as an ensemble anomaly detector over simulated telemetry.

### 2. Network Observability
- **Observability Score**: Combines sensor response ratio, spatial graph distance, detection latency, and anomaly signal strength into a normalized index ($0.0$ to $1.0$).
- *State Clearly*: **Model-derived simulated index.**

### 3. Topology-Aware Localization
- Analyzes spatial relationships between responsive sensors using NetworkX graph traversal.
- Scores candidate pipeline segments based on direct connectivity, directional head loss, and path alignment.
- *Important*: Does **not** imply exact real-world physical hydraulic localization.

### 4. Water-Loss Estimation
- **Flow Loss Rate**: Derived from observed vs expected simulated flow ($\Delta Q = Q_{\text{observed}} - Q_{\text{expected}}$).
- **Accumulated Volume**: Calculated as flow loss rate $\times$ duration ($\text{Volume} = \text{Flow Loss LPM} \times \text{Elapsed Minutes}$).
- *Clearly Labeled*: **Model-derived simulation estimate.**

### 5. Incident Persistence & Management
- Enforces strict lifecycle state machine: `OPEN` ➔ `ACKNOWLEDGED` ➔ `RESOLVED`.
- **Idempotent Deduplication**: Uses deterministic SHA-256 fingerprinting over reading timestamps, segment IDs, and anomaly signatures to prevent duplicate database rows.

### 6. Grounded AI Analysis
- Google Gemini 2.5 Flash receives structured, pre-computed AquaSentinel incident facts and generates: `summary`, `why_detected`, `recommended_actions`, `confidence_note`, `limitations`.
- *Core Principle*: Gemini is an **explainability layer**; it does **not** replace core deterministic anomaly detection or localization algorithms.

---

## 🎯 Signature Hackathon Demonstrations

### Demo 1 — Gradual Leak (Segment B2-B3)
- **Flow**: Normal Network ➔ Gradual anomaly develops on segment `B2-B3` ➔ Pipeline edge `B2-B3` pulses red on SVG map ➔ Incident `INC-66964E0E` appears ➔ Operator opens detail view ➔ Multi-signal evidence displayed ➔ Model-derived loss estimated (**~30.94 LPM / 1082 L**, **87.9% confidence**) ➔ Operator requests Gemini AI explanation ➔ Operator clicks **Acknowledge** ➔ Operator clicks **Resolve**.

### Demo 2 — Sensor Fault / False Alarm Prevention (*Critical Test*)
- **Flow**: Sensor `B3` exhibits erratic pressure spikes (+2.8 bar), while neighboring sensors `B2` and `B4` remain normal.
- **UI Behavior**: Highlights sensor `B3` in yellow/amber ➔ Leaves nearby pipeline edges `B2-B3` and `B3-B4` **cyan/healthy** ➔ Classifies event as `SENSOR_FAULT` ➔ Zero estimated water loss.
- **Takeaway**: **"Not every anomaly is a leak."** Prevents expensive false alarm field dispatches.

### Demo 3 — Network Observability & Blind-Spot Intelligence
- **Flow**: Operator opens `/network` ➔ Views simulated segment observability scores ➔ Identifies weakest coverage areas ➔ Evaluates candidate virtual sensor placements for simulated coverage improvement.

---

## 🌐 Canonical Network Topology

AquaSentinel models a canonical 10-sensor, 10-segment water distribution network reflected identically in both FastAPI backend and Next.js SVG frontend:

```text
                        [ Reservoir R0 ]
                               |
         +---------------------+---------------------+
         |                     |                     |
      [  A1  ]              [  B1  ]              [  C1  ]
         |                     |                     |
      [  A2  ]              [  B2  ]              [  C2  ]
         |                     |                     |
      [  A3  ]              [  B3  ]              [  C3  ]
                               |
                            [  B4  ]
```

- **10 Sensors**: `A1`, `A2`, `A3`, `B1`, `B2`, `B3`, `B4`, `C1`, `C2`, `C3`
- **10 Pipeline Segments**: `R-A1`, `R-B1`, `R-C1`, `A1-A2`, `A2-A3`, `B1-B2`, `B2-B3`, `B3-B4`, `C1-C2`, `C2-C3`
- **3 Sub-Zones**: Zone A (Commercial), Zone B (Residential), Zone C (Industrial)

---

## 🏛️ Government Data Context Layer

AquaSentinel integrates local surface water telemetry datasets from Rajasthan, India (sourced from National Water Data Portals / India WRIS) as offline contextual and calibration sources:

1. **Rajasthan Surface Water Telemetry Hourly Rainfall** (`rainfall_telemetry`)
2. **Mahi Head Regulator Canal Telemetry Hourly Discharge** (`canal_telemetry`)
3. **Bisalpur Dam Reservoir Telemetry Hourly Discharge** (`reservoir_telemetry`)

### Key Principles:
- **Read-only & Offline-first**: Data is parsed locally from bundled CSV files without external HTTP/API runtime dependencies.
- **Provenance Preserved**: Retains dataset metadata, agency attribution (*Rajasthan Surface Water Department*), and historical observation ranges.
- **Zero-Value Integrity**: Zero-valued discharge/rainfall observations in raw source CSVs are preserved rather than fabricated.
- *CRITICAL STATEMENT*: **"These datasets do not directly measure AquaSentinel pipeline leaks."** They provide descriptive regional environmental context (e.g. ambient rainfall or reservoir levels) for baseline calibration.

---

## 🤖 AI-Assisted Analysis & Gemini Integration

```text
Structured Incident Facts ➔ AI Analysis Service ➔ Gemini 2.5 Flash ➔ Validated Output ➔ Frontend UI
```

- **Server-Side Security**: `GEMINI_API_KEY` is managed strictly in `backend/.env` and is **never** exposed to browser JavaScript or client code.
- **Structured Pydantic Validation**: Uses `google-genai` Python SDK with `response_schema=AIAnalysisResult` to enforce strict JSON structure.
- **Safe Deterministic Fallback**: If Gemini is unavailable or missing an API key, the system returns a grounded, evidence-based deterministic fallback (`provider: "deterministic_fallback"`). *The fallback is explicitly labeled and never claimed to be AI-generated.*
- **Performance Caching**: In-memory cache keyed by `incident_id` prevents duplicate API requests.
- **Explicit Triggering**: AI analysis is triggered explicitly when requested by an operator in incident detail view; **no continuous background Gemini polling**.

---

## 🏗️ System Architecture

```text
 ┌────────────────────────────────────────────────────────┐
 │                Government Data Context                 │
 │            Rajasthan Surface Water / NWDP             │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ┌───────────────────┐    ┌───────────────────────────────┐
 │     Telemetry     │───▶│   Anomaly Detection Engine    │
 │     Simulator     │    └──────────────┬────────────────┘
 └───────────────────┘                   │
                                         ▼
                          ┌───────────────────────────────┐
                          │   Observability Engine &      │
                          │   Blind-Spot Intelligence     │
                          └──────────────┬────────────────┘
                                         ▼
                          ┌───────────────────────────────┐
                          │ Topology-Aware Localization & │
                          │     Water Loss Estimator      │
                          └──────────────┬────────────────┘
                                         ▼
                          ┌───────────────────────────────┐
                          │  Incident Management Service  │
                          └──────────────┬────────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
      ┌────────────────────┐                          ┌────────────────────┐
      │  SQLite Database   │                          │  Gemini 2.5 Flash  │
      │  (SQLAlchemy ORM)  │                          │ (Server-Side GenAI)│
      └──────────┬─────────┘                          └──────────┬─────────┘
                 │                                               │
                 └───────────────────────┬───────────────────────┘
                                         ▼
                               FastAPI REST API Services
                                         │
                                         ▼
                            Next.js 16 Control Room UI
```

The system strictly enforces backend/frontend separation. The Next.js frontend communicates exclusively via standard JSON REST APIs over HTTP, with a seamless fallback to `DemoContext` fixtures if the backend server is offline.

---

## 🖥️ Frontend Navigation & Routes

- `/` — **Landing Page**: Product introduction, platform differentiators, and system capabilities.
- `/dashboard` — **Operational Console**: 4 primary KPI cards, interactive topology map overlay, real-time gauges, and scenario switcher.
- `/network` — **Network Observability**: Topology view highlighting segment observability scores, blind spots, and virtual sensor placement recommendations.
- `/incidents` — **Incident Lifecycle**: Table of active and historical incidents with status/severity filtering.
- `/incidents/[id]` — **Incident Detail View**: Candidate segment scoring, evidence list, model loss breakdown, and interactive **AI Analysis Panel**.
- `/sensors` & `/sensors/[id]` — **Sensors Console**: Individual telemetry charts, rolling Z-score metrics, and sensor health status (`HEALTHY`, `DEGRADED`, `FAULTY`).
- `/data-sources` — **Government Data Context**: Viewer for Rajasthan rainfall, reservoir, and canal telemetry datasets.

---

## 📁 Repository Structure

```text
hackindia-spark-12-jaipur-rajasthan-north-india-region-bankai/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # FastAPI endpoints (health, network, incidents, data-sources)
│   │   ├── core/                # Config & logging
│   │   ├── db/                  # SQLite engine, ORM models, repository pattern
│   │   ├── models/              # Domain dataclasses & enums
│   │   ├── schemas/             # Pydantic schemas (ai_analysis, incident, data_source)
│   │   └── services/            # Anomaly detector, localizer, loss estimator, observability, AI service
│   ├── data/                    # Offline Rajasthan NWDP government CSV datasets
│   ├── experiments/             # Evaluation scripts (ai_analysis_evaluation.py, incident_evaluation.py)
│   ├── tests/                   # 65 automated pytest unit & integration tests
│   ├── requirements.txt         # Pinned Python dependencies
│   └── README.md                # Backend architecture guide
│
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router pages
│   │   ├── components/          # AppShell, Topology Map, AIAnalysisPanel, Recharts gauges
│   │   ├── context/             # DemoContext & scenario switcher
│   │   ├── lib/api/             # REST API client (`client.ts`)
│   │   └── types/               # TypeScript data types
│   ├── package.json
│   └── tsconfig.json
│
├── docs/
│   └── API_CONTRACT.md          # OpenAPI REST contract specification
├── LICENSE
└── README.md                    # Root project documentation
```

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Backend** | Python 3.14 / 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, NetworkX, NumPy, SciPy, scikit-learn, `google-genai` SDK, SQLite |
| **Frontend** | Next.js 16 (App Router, Turbopack), React 19, TypeScript, Tailwind CSS, Lucide Icons, Recharts, SVG Network Visualization |
| **Testing & Quality** | Pytest, Pytest-Asyncio, HTTPX, ESLint, TypeScript Typechecker |

---

## 🔌 API Overview

Detailed request/response schemas and examples are specified in [`docs/API_CONTRACT.md`](file:///a:/Amar/Projects/Project%208%20%28Hack%20India%29/docs/API_CONTRACT.md).

- `GET /api/health` — System health check.
- `GET /api/network` — Network operational status summary.
- `GET /api/network/topology` — Full canonical 10-sensor / 10-segment graph topology.
- `POST /api/incidents/analyze` — Run incident pipeline on telemetry batch.
- `GET /api/incidents` — List persisted incidents.
- `GET /api/incidents/{incident_id}` — Retrieve single incident details.
- `PATCH /api/incidents/{incident_id}/status` — Update incident status (`OPEN` ➔ `ACKNOWLEDGED` ➔ `RESOLVED`).
- `POST /api/incidents/{incident_id}/ai-analysis` — Generate or fetch grounded Gemini AI analysis.
- `GET /api/data-sources` — List government context datasets.
- `GET /api/data-sources/{source_id}` — Retrieve dataset metadata.
- `GET /api/data-sources/{source_id}/summary` — Dataset statistical summary & historical calibration metrics.
- `GET /api/data-sources/{source_id}/recent` — Recent observations for dataset.

---

## ⚙️ Local Setup & Setup Instructions

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

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell): .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env for optional Gemini AI Key
echo GEMINI_API_KEY="your-api-key-here" > .env
echo GEMINI_MODEL="gemini-2.5-flash" >> .env
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
```

---

## 🏃 Running the Full System

### Terminal 1: Backend Server
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
- **Backend API**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`

### Terminal 2: Frontend Control Room
```bash
cd frontend
npm run dev
```
- **Frontend Control Room**: `http://localhost:3000`

---

## 🧪 Testing & Validation

### Backend Automated Test Suite (65 Passed Tests)
AquaSentinel includes a comprehensive test suite verifying anomaly detection, observability scoring, localization graph logic, loss estimation, database lifecycle persistence, government data parsing, and AI grounding checks:

```bash
cd backend
python -m pytest
```

### Frontend Build & Type Validation
```bash
cd frontend
npm run lint
npm run build
```

---

## ⏱️ 2-Minute Demo Guide for Judges

1. **Start at Landing Page (`http://localhost:3000`)**: View value proposition and click **"Launch Control Room"**.
2. **Dashboard (`/dashboard`)**: Show normal healthy network status.
3. **Trigger Scenario B (Gradual Leak)**: Select **Scenario B** in the left sidebar.
   - Observe pipeline edge `B2-B3` pulse red.
   - Click on incident `INC-66964E0E` in the table to open detail view.
   - Review correlated evidence, observability score (**89.7%**), and estimated flow loss (**30.94 LPM**).
   - Click **"Analyze"** in the **AI Analysis Panel** to view server-side Gemini 2.5 Flash explainability.
   - Click **"Acknowledge"** and **"Resolve"** to demonstrate incident state transitions.
4. **Trigger Scenario D (Sensor Fault Prevention)**: Select **Scenario D** in the sidebar.
   - Show sensor `B3` highlighted in yellow/amber while pipeline edges `B2-B3` and `B3-B4` remain **cyan/healthy**.
   - Point out that **0 false leak alarms** were declared.
5. **Inspect Network Observability (`/network`)**: Show simulated segment observability scores and virtual sensor placement recommendations.
6. **Browse Government Data (`/data-sources`)**: View regional Rajasthan surface water telemetry context.

---

## ⚠️ Limitations & Responsible Claims

- **Software Prototype**: AquaSentinel is a software demonstration prototype built for hackathon evaluation using a synthetic 10-node water distribution network topology.
- **Simulated Telemetry**: Telemetry is generated via synthetic diurnal simulation models rather than real-world physical IoT sensors.
- **Model-Derived Loss Estimates**: Flow loss rates (LPM) and accumulated volume figures (Liters) are model-derived simulation estimates intended for system evaluation.
- **Topology-Aware Localization**: Localization uses NetworkX graph reasoning and correlated sensor signals, not physically validated real-world hydraulic models.
- **Government Context**: Rajasthan surface water telemetry provides regional environmental context; it does not directly measure underground pipeline leaks.
- **Candidate Sensor Placement**: Virtual sensor placement recommendations are model-derived heuristics, not globally optimal mathematical guarantees.
- **AI Explanations**: Gemini 2.5 Flash is an explainability and operator decision support layer, not the primary incident detection engine.

---

## 🔒 Security

- All API keys (`GEMINI_API_KEY`) are managed strictly server-side in `backend/.env`.
- `.env` files are included in `.gitignore` and **never committed**.
- The frontend client never receives secret credentials or provider keys.

---

## 📅 Roadmap

### Implemented (Current MVP)
- [x] Synthetic IoT telemetry simulator with diurnal demand curves
- [x] Statistical anomaly detection (Z-scores & Isolation Forest)
- [x] Network observability & blind-spot intelligence
- [x] Topology-aware leak localization (NetworkX graph engine)
- [x] Model-derived water-loss estimation (LPM & Volume)
- [x] Persistent incident management & lifecycle state machine (`OPEN` ➔ `ACK` ➔ `RESOLVED`)
- [x] Offline Rajasthan surface water government data context layer
- [x] Server-side grounded Gemini 2.5 Flash AI explainability
- [x] Production-quality Next.js 16 control room interface

### Future Roadmap
- [ ] Physical IoT hardware sensor integration (ESP32 / Modbus pressure transducers)
- [ ] EPANET hydraulic model integration & field calibration
- [ ] Real-time WebSocket streaming telemetry
- [ ] GIS map overlays with geospatial shapefile support
- [ ] Production SMS/Webhook alerting for field crews

---

## 🏆 Hackathon Highlights

- **End-to-End Full-Stack Architecture**: Fully connected FastAPI backend and Next.js frontend with OpenAPI REST contract.
- **10-Sensor Canonical Network**: Realistic directed graph topology with 3 distinct sub-zones.
- **Deterministic & Explainable**: Core leak detection and localization rely on explainable math and graph algorithms.
- **Sensor Fault Distinction**: Successfully prevents false leak alarms when isolated sensor transducers fail.
- **Grounded AI Intelligence**: Gemini AI provides operator explanations bounded strictly by pre-computed backend evidence.

---

## 👥 Team & Project Metadata

- **Hackathon**: HackIndia Spark-12 Jaipur 2026
- **Team Name**: Bankai
- **Repository Tag**: `hackindia-spark-12-jaipur-rajasthan-north-india-region-bankai`
- **Official GitHub Repository**: [`https://github.com/HackIndiaXYZ/hackindia-spark-12-jaipur-rajasthan-north-india-region-bankai`](https://github.com/HackIndiaXYZ/hackindia-spark-12-jaipur-rajasthan-north-india-region-bankai)
- **Live Vercel Frontend**: [`https://aquasentinel-rouge.vercel.app`](https://aquasentinel-rouge.vercel.app)
- **Live Render Backend API**: [`https://aquasentinel-api-r00y.onrender.com`](https://aquasentinel-api-r00y.onrender.com)
- **License**: MIT
