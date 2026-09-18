# AquaSentinel

### AI-Powered Water Network Intelligence & Resilience (Hardware-Integrated Release)

> **AquaSentinel is not just a leak detector. It is a water-network intelligence and resilience platform that evaluates both incidents and the observability of the system detecting them — now featuring real ESP32 IoT hardware integration.**

> *"See the Network. Detect the Incident. Understand the Risk."*

---

## 🌐 Live Production Deployments

- 🖥️ **Live Vercel Frontend Control Room**: [`https://aquasentinel-rouge.vercel.app`](https://aquasentinel-rouge.vercel.app)
- ⚙️ **Live Render Backend API Service**: [`https://aquasentinel-api-r00y.onrender.com`](https://aquasentinel-api-r00y.onrender.com)
- 📚 **Interactive Swagger API Documentation**: [`https://aquasentinel-api-r00y.onrender.com/docs`](https://aquasentinel-api-r00y.onrender.com/docs)
- 📦 **Official GitHub Repository**: [`https://github.com/HackIndiaXYZ/hackindia-spark-12-jaipur-rajasthan-north-india-region-bankai`](https://github.com/HackIndiaXYZ/hackindia-spark-12-jaipur-rajasthan-north-india-region-bankai)

---

## ⚡ Executive Summary (Judge Quick View)

| What | Why | Differentiator | Live & Hardware Demo |
| :--- | :--- | :--- | :--- |
| **Full-Stack Water Network Intelligence Platform** with physical ESP32 IoT hardware telemetry, statistical anomaly detection, graph localization, loss estimation, government context, and Gemini AI. | Traditional SCADA alerts produce high false alarms and lack spatial network context to distinguish pipe leaks from sensor faults. | **"Monitor the Network. Monitor the Monitoring."** Combines real physical ESP32 sensor input with simulated network observability and candidate virtual sensor placement. | **Physical ESP32 + 5 Simulation Scenarios**: Hardware FSR force trigger, Normal, Gradual Leak (B2-B3), Sensor Fault (B3), Sudden Burst, Multi-Anomaly. |

AquaSentinel is an infrastructure intelligence platform designed to monitor water distribution networks, ingest live physical ESP32 force sensor telemetry, detect anomalous hydraulic behavior, evaluate network observability, identify monitoring blind spots, localize suspected pipeline incidents, estimate model-derived water loss, maintain persistent incident lifecycles, and provide server-side grounded AI explainability for utility operators.

*Note: AquaSentinel combines a physical ESP32 hardware prototype (using an FSR402 force-sensitive resistor as a prototype force input simulator) with a synthetic 10-node water distribution network, model-derived hydraulic loss estimation, offline regional government telemetry, and server-side grounded AI reasoning.*

---

## 🔌 Hardware Integration

AquaSentinel includes a fully working physical ESP32 prototype for live hardware telemetry and dual alarm demonstrations.

### Hardware Components
- **Microcontroller**: ESP32 Dev Module (38-pin / 30-pin compatible)
- **Primary Input**: FSR402 Force-Sensitive Resistor (prototype force input simulator)
- **Divider Resistor**: 10kΩ voltage-divider resistor (pull-down configuration)
- **Local Alarm Output**: 3-pin Active Buzzer Module

### Hardware Wiring & Pin Mapping

| Component Signal | ESP32 Pin | Function | Power / Ground |
| :--- | :--- | :--- | :--- |
| **FSR402 Signal** | **GPIO34** | Analog force reading (ADC 0–4095) | 3.3V power via 10kΩ divider |
| **Buzzer Signal** | **GPIO32** | Active alarm output (HIGH/LOW) | 3.3V power |
| **Ground** | **GND** | Common ground reference | GND |

> [!IMPORTANT]
> **FSR402 Sensor Terminology & Precision Disclaimer**:
> The FSR402 is used as a **prototype force input simulator** for interactive physical testing. It is **NOT** a calibrated hydraulic pressure transducer or PSI sensor.
> In telemetry processing and documentation, terms such as **"pressure-equivalent"**, **"prototype force input"**, and **"simulated/derived flow"** are used to reflect that raw ADC force values (0–4095) are scaled to prototype pressure units (bars/PSI) for network modeling.

---

## 🔄 Hardware Data Flow & Architecture

The AquaSentinel physical prototype operates across two decoupled alert loops: a zero-latency hardware alert loop and a full-stack telemetry & web control loop.

```text
               +-----------------------------------+
               | FSR402 Force Sensor (Prototype)  |
               +-----------------+-----------------+
                                 |
                                 v
                       +-------------------+
                       |    ESP32 GPIO34   |
                       +--------+----------+
                                |
        +-----------------------+-----------------------+
        |                                               |
        v                                               v
+---------------+---------------+             +-------------------+
| ESP32 Local Logic (GPIO32)    |             | USB Serial / COM  |
+---------------+---------------+             +---------+---------+
                |                                       |
                v                                       v
+---------------+---------------+             +-------------------+
| Physical 3-pin Buzzer         |             | esp32_bridge.py   |
| (Independent Local Alarm)     |             +---------+---------+
+-------------------------------+                       |
                                                        v
                                              +-------------------+
                                              | FastAPI Backend   |
                                              | (/api/hardware)   |
                                              +---------+---------+
                                                        |
                                                        v
                                              +-------------------+
                                              | AquaSentinel      |
                                              | Incident Pipeline |
                                              +---------+---------+
                                                        |
                                                        v
                                              +-------------------+
                                              | Next.js Dashboard |
                                              | & Web Audio API   |
                                              +-------------------+
```

### 1. Zero-Latency Local Buzzer Path
```text
FSR402 Force ➔ ESP32 GPIO34 ➔ Local Threshold Check (ADC >= 50) ➔ GPIO32 HIGH ➔ Physical Buzzer
```
*Note: The physical buzzer is driven directly by firmware code on the ESP32. It sounds instantly when force is applied and does NOT depend on USB serial connection, backend server health, or browser state.*

### 2. Full-Stack Web Telemetry & Laptop Alert Path
```text
FSR402 Force ➔ ESP32 GPIO34 ➔ USB Serial JSON ➔ esp32_bridge.py ➔ FastAPI Backend ➔ Incident Pipeline ➔ Dashboard WebSocket/Polling ➔ Web Audio Synth ➔ Laptop Audible Alarm
```

---

## ⚡ Live ESP32 Mode

AquaSentinel supports zero-internet local hardware operation tailored specifically for hackathon environments.

- **USB Serial Connection**: The ESP32 connects directly to the operator's laptop via standard micro-USB or USB-C cable.
- **No Wi-Fi Dependency**: The ESP32 does not require college/event Wi-Fi credentials or internet access to deliver telemetry.
- **Local Bridge**: `esp32_bridge.py` reads serial JSON packets from the USB COM port and forwards HTTP POST requests to the local FastAPI backend (`http://localhost:8000/api/hardware/telemetry`).
- **Flexible Port Configuration**: The default COM port can be customized via environment variable `ESP32_SERIAL_PORT`.

```text
ESP32 Dev Module ➔ USB Cable ➔ COM15 (Example) ➔ esp32_bridge.py ➔ http://localhost:8000 ➔ AquaSentinel Dashboard
```
*Note: `COM15` is an example Windows serial port designation from the local dev environment and is dynamically autodetected or overridden via `ESP32_SERIAL_PORT=COM15`.*

---

## 🚨 Hardware-Driven Incident Detection & Topology Mapping

Physical force applied to the FSR402 is injected directly into the canonical AquaSentinel 10-node water network model.

### Sensor Mapping & Threshold Parameters
- **Mapped Physical Sensor**: `FSR-P01`
- **Assigned Sub-Zone**: `Zone_B` (Residential Sub-Zone)
- **Canonical Network Node**: `B2`
- **Target Pipeline Segment**: `B2-B3`
- **Activation Threshold**: Raw ADC `raw_adc >= 50` (or `pressure_equivalent >= 2.8 bar`)

### Real-Time Incident Trigger Flow
```text
1. Physical pressure applied to FSR402
   ↓
2. Raw ADC crosses threshold (>= 50)
   ↓
3. ESP32 physical buzzer sounds instantly (GPIO32)
   ↓
4. Telemetry packet sent over USB serial (115200 baud)
   ↓
5. esp32_bridge.py posts to FastAPI endpoint
   ↓
6. Anomaly engine flags statistical deviation & triggers pipeline
   ↓
7. NetworkX localizer isolates target edge B2-B3
   ↓
8. Incident INC-HW-XXXXX created & stored in database
   ↓
9. Dashboard enters LIVE HARDWARE ALERT state
   ↓
10. Web Audio API plays laptop browser alarm
```

---

## 📜 Persistent Incident History & Lifecycle

AquaSentinel separates real-time transient sensor alerts from persistent audit history.

### Incident Lifecycle State Machine
```text
[ OPEN ] ➔ [ ACKNOWLEDGED ] ➔ [ RESOLVED ]
```

- **Transient State vs Persistent Incident**: When physical pressure on the FSR402 is released, the live hardware gauge and alert panel return to `NORMAL`. However, the recorded incident is **NOT deleted**.
- **Database Persistence**: Incidents remain permanently recorded in the local SQLite database (`aquasentinel.db`).
- **Operator Workflow**: Utility operators can inspect historical hardware incidents, review correlated network evidence, click **Acknowledge**, and transition status to **Resolved**.
- **Audit Trace**: Resolved incidents remain visible in the Incident History table with complete timestamp logs for compliance reporting.
- **Idempotent Incident Deduplication**: Telemetry packets arrive every 500 ms. The backend uses deterministic SHA-256 fingerprinting over continuous alert windows to prevent identical telemetry streams from spawning duplicate incident IDs for the same event.
- **Re-triggering**: Applying force to the FSR after a previous incident is resolved creates a brand-new distinct incident ID (`INC-HW-YYYYY`).

---

## 🔔 Dual Alarm System

AquaSentinel implements a two-tier redundant alarm architecture for local field operations and control room monitoring:

| Alarm Tier | Primary Mechanism | Dependencies | Mute Controls |
| :--- | :--- | :--- | :--- |
| **1. Physical ESP32 Buzzer** | Active 3-pin buzzer on GPIO32 | ESP32 Power only | Controlled via hardware reset / FSR release |
| **2. Laptop Control Room Alarm** | Web Audio API synthesizer synth | Browser tab & audio context | Mute button in UI top bar |

> [!NOTE]
> **Independent Mute Functionality**:
> Muting or silencing the laptop browser alarm via the UI top bar header does **NOT** turn off or affect the physical ESP32 buzzer. The hardware buzzer operates independently on the ESP32 microcontroller.

---

## 🤖 AI-Assisted Analysis & Grounded Gemini Integration

```text
Structured Incident Facts ➔ AI Analysis Service ➔ Gemini 2.5 Flash / Fallback ➔ Validated Schema ➔ Frontend UI
```

- **Server-Side Security**: `GEMINI_API_KEY` is managed strictly in `backend/.env` and is **never** exposed to browser JavaScript or client code.
- **Structured Pydantic Validation**: Uses `google-genai` Python SDK with `response_schema=AIAnalysisResult` to enforce strict JSON output structure.
- **Grounded Evidence Bounding**: Gemini receives pre-computed deterministic facts (sensor ID, localized segment, loss rate, observability score) and cannot invent fake telemetry.
- **Dual Engine Execution (Gemini vs Fallback)**:
  - When `GEMINI_API_KEY` is present and operational, analysis is generated by **Gemini 2.5 Flash** (marked with `provider: "gemini-2.5-flash"`).
  - If Gemini is unconfigured, rate-limited, or offline, AquaSentinel automatically falls back to an evidence-grounded rule-based analyzer (`provider: "deterministic_fallback"`).
  - The UI explicitly displays a provider badge (`Gemini 2.5 Flash` or `Deterministic Fallback`) so operators always know which engine produced the summary.
- **Performance Caching**: In-memory caching keyed by `incident_id` prevents redundant API calls during incident review.

---

## ⭐ System Features

- 🔌 **Real ESP32 Hardware Telemetry**: USB serial streaming from physical FSR402 force sensor.
- ⚡ **FSR402 Prototype Force Input**: Real-time force input scaling to pressure-equivalent metrics.
- 🌉 **USB Serial Telemetry Bridge**: High-frequency Python bridge connecting hardware COM ports to REST API.
- 🔔 **Physical Buzzer Alerts**: Instant hardware sound alarm driven directly by ESP32 GPIO32.
- 💻 **Laptop Audible Alarms**: Synthetic Web Audio browser alarm for control room notification.
- 🟢 **Live Hardware Dashboard Mode**: Automatic UI detection switching from synthetic replay to live hardware streaming.
- 🎯 **Hardware-Driven Anomaly Detection**: Statistical Z-score and rate-of-change detection over live physical inputs.
- 🗺️ **Pipeline Topology Localization**: Graph-based NetworkX edge mapping isolating incidents to target segment `B2-B3`.
- 📊 **Persistent Incident History**: Full SQLite persistence tracking historical events across system restarts.
- 🔄 **Incident Lifecycle Management**: Operator workflow supporting `OPEN` ➔ `ACKNOWLEDGED` ➔ `RESOLVED`.
- 🌐 **Network Observability & Blind-Spot Intelligence**: Quantitative simulated observability scoring across pipeline segments.
- 💧 **Model-Derived Water Loss Estimation**: Simulated flow loss rate (LPM) and accumulated loss calculation (Liters).
- 🛡️ **Sensor Fault Prevention**: Spatial neighbor consensus logic to prevent false alarms on isolated transducer faults.
- 🤖 **Gemini-Assisted Explainability**: Server-side AI analysis with grounded fallback mechanism.
- 📶 **Offline Hackathon Mode**: 100% operational locally without requiring external internet or Wi-Fi.

---

## 🎬 Hackathon Demo Flow (Step-by-Step)

Follow this 20-step demonstration flow to showcase both live ESP32 hardware and software capabilities to judges:

1. **Connect ESP32**: Plug the ESP32 Dev Module into the laptop via USB cable.
2. **Start Backend**: Launch FastAPI backend on port 8000 (`python -m uvicorn app.main:app --reload --port 8000`).
3. **Start ESP32 Bridge**: Run `python esp32_bridge.py` (verifying COM port detection, e.g. `COM15`).
4. **Start Frontend**: Launch Next.js dev server (`npm run dev`).
5. **Open Dashboard**: Navigate browser to `http://localhost:3000/dashboard`.
6. **Confirm Live Hardware Mode**: Verify the green **LIVE HARDWARE** status badge appears in the header.
7. **Show Normal State**: Keep the FSR402 released; show normal pressure/flow gauges and `NORMAL` status.
8. **Apply FSR Force**: Press down on the FSR402 force-sensitive resistor past the threshold (`raw_adc >= 50`).
9. **Observe Physical Buzzer**: Note that the ESP32 physical buzzer sounds immediately.
10. **Observe Laptop Alarm**: Listen to the Web Audio alarm sounding in the browser.
11. **Observe Dashboard Alert**: See the dashboard switch to `ALERT` mode with flashing red metrics.
12. **Observe Topology Localization**: Point out pipeline segment `B2-B3` highlighted in pulsing red on the SVG map.
13. **Open Incidents Console**: Navigate to `/incidents` to view the newly logged hardware incident.
14. **Inspect Incident Detail**: Click on incident `INC-HW-XXXXX` to review correlated evidence and localized segment `B2-B3`.
15. **Run AI Analysis**: Click **"Analyze"** to trigger server-side Gemini / fallback explainability.
16. **Acknowledge Incident**: Click **"Acknowledge"** to change status from `OPEN` to `ACKNOWLEDGED`.
17. **Release FSR Force**: Release the physical FSR sensor.
18. **Observe Live Recovery**: See live dashboard state return to `NORMAL` while the historical incident remains stored.
19. **Resolve Incident**: Click **"Resolve"** on the incident page to complete the lifecycle (`RESOLVED`).
20. **Demonstrate Re-Triggering**: Press the FSR again to prove that a distinct new incident (`INC-HW-YYYYY`) is spawned.

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

- **10 Sensors**: `A1`, `A2`, `A3`, `B1`, `B2`, `B3`, `B4`, `C1`, `C2`, `C3` (plus physical `FSR-P01` mapped to `B2`)
- **10 Pipeline Segments**: `R-A1`, `R-B1`, `R-C1`, `A1-A2`, `A2-A3`, `B1-B2`, `B2-B3`, `B3-B4`, `C1-C2`, `C2-C3`
- **3 Sub-Zones**: Zone A (Commercial), Zone B (Residential), Zone C (Industrial)

---

## 🏛️ Government Data Context Layer

AquaSentinel integrates local surface water telemetry datasets from Rajasthan, India (sourced from National Water Data Portals / India WRIS) as offline contextual and calibration sources:

1. **Rajasthan Surface Water Telemetry Hourly Rainfall** (`rainfall_telemetry`)
2. **Mahi Head Regulator Canal Telemetry Hourly Discharge** (`canal_telemetry`)
3. **Bisalpur Dam Reservoir Telemetry Hourly Discharge** (`reservoir_telemetry`)

> [!NOTE]
> **Contextual Dataset Purpose**:
> These datasets do not directly measure AquaSentinel pipeline leaks. They provide descriptive regional environmental context (e.g. ambient rainfall or reservoir levels) for baseline calibration.

---

## 🏗️ System Architecture & Data Flow

```text
 ┌──────────────────────────────────────────────────────────────────┐
 │                Physical ESP32 IoT Hardware                       │
 │      (ESP32 + FSR402 Force Sensor + Local Buzzer on GPIO32)      │
 └────────────────────────────────┬─────────────────────────────────┘
                                  │ (USB Serial / COM Port)
                                  ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │                     ESP32 Serial Bridge                          │
 │                    (esp32_bridge.py)                             │
 └────────────────────────────────┬─────────────────────────────────┘
                                  │ (HTTP POST /api/hardware/telemetry)
                                  ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │                FastAPI Backend Intelligence                      │
 │   • Anomaly Detection Engine (Rolling Z-Score & Rate of Change)   │
 │   • Observability Engine & Blind-Spot Analysis                   │
 │   • NetworkX Topology Localization (Maps FSR to B2-B3)           │
 │   • Model-Derived Loss Estimator (LPM & Volume)                  │
 │   • Persistent Incident Service (SQLite ORM Engine)              │
 └─────────────────┬──────────────────────────────┬─────────────────┘
                   │                              │
                   ▼                              ▼
 ┌──────────────────────────────────┐   ┌──────────────────────────┐
 │ SQLite Database (aquasentinel.db)│   │ Gemini 2.5 Flash /       │
 │ Permanent Incident Lifecycle     │   │ Grounded Fallback Engine │
 └─────────────────┬────────────────┘   └─────────┬────────────────┘
                   │                              │
                   └──────────────┬───────────────┘
                                  ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │                 Next.js 16 Control Room UI                       │
 │  • Real-Time Hardware Panel & Mode Switcher                      │
 │  • Interactive SVG Topology Map (Segment B2-B3 Pulse Alert)      │
 │  • Web Audio API Laptop Alarm Synth                              │
 │  • Persistent Incident Lifecycle Console                         │
 └──────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ Frontend Navigation & Routes

- `/` — **Landing Page**: Product introduction, platform differentiators, and system capabilities.
- `/dashboard` — **Operational Console**: Real-time gauges, live ESP32 status panel, interactive SVG map, active incident cards, and scenario switcher.
- `/network` — **Network Observability**: Topology view highlighting segment observability scores, blind spots, and virtual sensor placement recommendations.
- `/incidents` — **Incident Lifecycle**: Table of active and historical hardware/simulated incidents with status/severity filtering and lifecycle actions.
- `/incidents/[id]` — **Incident Detail View**: Candidate segment scoring, evidence list, model loss breakdown, and interactive **AI Analysis Panel**.
- `/sensors` & `/sensors/[id]` — **Sensors Console**: Individual telemetry charts, rolling Z-score metrics, and sensor health status (`HEALTHY`, `DEGRADED`, `FAULTY`).
- `/data-sources` — **Government Data Context**: Viewer for Rajasthan rainfall, reservoir, and canal telemetry datasets.

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Hardware** | ESP32 Dev Module, FSR402 Force Sensor, 10kΩ Resistor, 3-Pin Buzzer, C++ Arduino Firmware |
| **Bridge & Communication** | Python PySerial, HTTPX, USB CDC Serial Protocol (115200 baud), JSON Streaming |
| **Backend** | Python 3.11 / 3.14+, FastAPI, Pydantic v2, SQLAlchemy 2.0, NetworkX, NumPy, SciPy, scikit-learn, `google-genai` SDK, SQLite |
| **Frontend** | Next.js 16 (App Router, Turbopack), React 19, TypeScript, Tailwind CSS, Web Audio API, Lucide Icons, Recharts, SVG Network Visualization |
| **Testing & Quality** | Pytest, Pytest-Asyncio, HTTPX, ESLint, TypeScript Typechecker |

---

## ⚙️ Local Development Commands

Below are verified execution commands for running the complete hardware-integrated stack locally (Windows PowerShell syntax provided as reference):

### 1. Backend Server
```powershell
cd "A:\Amar\Projects\Project 8 (Hack India)\backend"
python -m uvicorn app.main:app --reload --port 8000
```
- **Backend API**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`

### 2. ESP32 Serial Bridge
```powershell
cd "A:\Amar\Projects\Project 8 (Hack India)\backend"
$env:ESP32_SERIAL_PORT="COM15"
python esp32_bridge.py
```

### 3. Frontend Control Room
```powershell
cd "A:\Amar\Projects\Project 8 (Hack India)\frontend"
npm run dev
```
- **Frontend Control Room**: `http://localhost:3000`

---

## 🔧 Troubleshooting

### 1. COM Port Access Denied (`PermissionError`)
- Close the Arduino IDE Serial Monitor or any other terminal accessing the serial port.
- Ensure only `esp32_bridge.py` is attempting to open the configured COM port.
- Confirm the correct COM port in Device Manager or use autodetect (`ESP32_SERIAL_PORT=""`).
- Reconnect the USB cable if the port remains locked.

### 2. Backend Server Unavailable
- Ensure the backend virtual environment is active.
- Verify uvicorn is running on port 8000:
  ```powershell
  python -m uvicorn app.main:app --reload --port 8000
  ```

### 3. Hardware Mode Appears as "Simulation Mode"
- Check that the USB cable is firmly connected to the ESP32.
- Verify `esp32_bridge.py` is actively printing telemetry output (`[Bridge] Telemetry sent: raw_adc=...`).
- Ensure `http://localhost:8000/api/hardware/telemetry` is receiving HTTP 200 responses.

### 4. Laptop Alarm Does Not Sound
- Click anywhere on the dashboard once after loading to allow browser audio context activation (browser autoplay policy restriction).
- Verify the system volume and browser tab audio are not muted.
- Ensure the mute toggle in the top navigation bar is set to unmuted.

---

## 🚀 Production Deployment vs Local Hardware Mode

AquaSentinel supports both cloud web deployment and local hackathon hardware operation:

- **Production Web Deployment**:
  - **Frontend**: Hosted on Vercel ([`aquasentinel-rouge.vercel.app`](https://aquasentinel-rouge.vercel.app))
  - **Backend API**: Hosted on Render ([`aquasentinel-api-r00y.onrender.com`](https://aquasentinel-api-r00y.onrender.com))
- **Local Hackathon Hardware Mode**:
  - The physical ESP32 connects via USB to the local hackathon laptop.
  - `esp32_bridge.py` streams serial telemetry directly to the local backend (`localhost:8000`).
  - *Note*: The physical USB port on a local laptop cannot be accessed directly by a remote Render cloud instance. For live physical hardware demonstrations, run the backend and bridge locally.

---

## 🧪 Verification & Test Results

The AquaSentinel release has been fully validated through backend unit/integration test suites, frontend TypeScript builds, and physical ESP32 runtime checks:

- **Backend Pytest Suite**: `69/69 passed` (100% pass rate covering anomaly detection, NetworkX localization, persistent incident SQLite lifecycle, government dataset parsers, hardware telemetry routes, and AI analysis grounding).
- **Frontend Build**: Successful Production Build (`npm run build`) with **0 TypeScript errors** and 0 ESLint warnings.
- **FastAPI API**: Verified operational on `http://127.0.0.1:8000`.
- **ESP32 Bridge**: Verified serial connection on `COM15` streaming 500 ms JSON telemetry packets.
- **Live Hardware Dashboard**: Verified live force telemetry ingestion with instant transition to `LIVE HARDWARE` state.
- **Dual Alarms**: Confirmed simultaneous activation of ESP32 physical buzzer (GPIO32) and Web Audio laptop alarm.
- **Topology Localization**: Confirmed physical force trigger correctly localizes target pipeline segment `B2-B3`.
- **Persistent Incident Lifecycle**: Verified incident creation, SQLite persistence, deduplication, operator acknowledgement, and resolution state machine.

---

## ⚠️ Limitations & Responsible Claims

- **Prototype Force Input**: The FSR402 is used as a prototype force input simulator for interactive physical demonstration. It is not a calibrated PSI pressure transducer.
- **Simulated Water Network Topology**: The canonical 10-node network is a synthetic representation built for intelligence, observability, and localization evaluation.
- **Model-Derived Loss Estimates**: Flow loss rates (LPM) and accumulated volume figures (Liters) are model-derived simulation estimates.
- **Topology-Aware Localization**: Localization uses NetworkX spatial graph reasoning and correlated sensor signals.
- **Government Context**: Rajasthan surface water telemetry provides regional environmental context; it does not directly measure underground pipeline leaks.
- **AI Explanations**: Gemini 2.5 Flash is an explainability and decision-support layer grounded strictly by pre-computed backend evidence.

---

## 🔒 Security

- All API keys (`GEMINI_API_KEY`) are managed strictly server-side in `backend/.env`.
- `.env` files are included in `.gitignore` and **never committed**.
- The frontend client never receives secret credentials or provider keys.

---

## 📅 Roadmap

### Implemented (Current Release)
- [x] Physical ESP32 hardware sensor integration (GPIO34 FSR402 force sensor + GPIO32 buzzer)
- [x] USB serial telemetry bridge (`esp32_bridge.py`)
- [x] Dual alarm system (ESP32 physical buzzer + browser Web Audio synth)
- [x] Hardware-driven anomaly detection & topology localization (Segment `B2-B3`)
- [x] Synthetic IoT telemetry simulator with diurnal demand curves
- [x] Statistical anomaly detection (Z-scores & Isolation Forest)
- [x] Network observability & blind-spot intelligence
- [x] Persistent incident management & lifecycle state machine (`OPEN` ➔ `ACK` ➔ `RESOLVED`)
- [x] Offline Rajasthan surface water government data context layer
- [x] Server-side grounded Gemini 2.5 Flash AI explainability with rule-based fallback
- [x] Production-quality Next.js 16 control room interface

### Future Roadmap
- [ ] Multi-node wireless ESP32 Mesh network with calibrated Modbus pressure transducers
- [ ] EPANET hydraulic model integration & field calibration
- [ ] Real-time WebSocket streaming telemetry
- [ ] GIS map overlays with geospatial shapefile support

---

## 🏆 Hackathon Highlights

- **End-to-End Hardware & Software Integration**: Real physical ESP32 prototype feeding a full-stack FastAPI + Next.js web application.
- **Zero-Latency Dual Alarms**: Hardware buzzer on GPIO32 operates independently of web server state.
- **10-Sensor Canonical Network**: Realistic directed graph topology with 3 distinct sub-zones.
- **Deterministic & Explainable**: Core leak detection and localization rely on explainable math and NetworkX graph algorithms.
- **Persistent Incident Lifecycle**: Full database tracking preventing duplicate incident creation while preserving audit history.
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
