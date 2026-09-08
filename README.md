# AquaSentinel

> **Water Pipeline Monitoring and Leak Detection Platform**
> Developed for HackIndia 2026 — Team Bankai (`hackindia-spark-12-jaipur-rajasthan-north-india-region-bankai`)

AquaSentinel is an infrastructure intelligence water pipeline monitoring system that integrates synthetic IoT sensor simulation, statistical anomaly detection, graph-based leak localization, water loss estimation, government water telemetry contextualization, persistent incident management, and server-side grounded Gemini AI explainability.

---

## 🛠 Project Structure

- **`backend/`**: Python 3.14/3.11+ FastAPI application containing domain models, NetworkX graph topology engine, SQLite database persistence, REST APIs, grounded Gemini AI analysis, and unit test suite.
- **`frontend/`**: Next.js 16 (React 19, TypeScript, Tailwind CSS) control room dashboard with topology visualization, real-time telemetry, incident lifecycle management, and government data context.
- **`docs/`**: [`docs/API_CONTRACT.md`](file:///a:/Amar/Projects/Project%208%20%28Hack%20India%29/docs/API_CONTRACT.md) defining canonical data models, endpoints, and architecture specs.

---

## 🚀 Quick Start

### 1. Backend Server
```bash
cd backend
pip install -r requirements.txt
python -m pytest
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Control Room
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` to view the control room dashboard.
Refer to [`backend/README.md`](file:///a:/Amar/Projects/Project%208%20%28Hack%20India%29/backend/README.md) for detailed architecture documentation.
