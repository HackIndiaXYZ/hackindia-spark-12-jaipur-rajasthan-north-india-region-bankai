# AquaSentinel

> **Water Pipeline Monitoring and Leak Detection Platform**
> Developed for HackIndia 2026.

AquaSentinel is a software-based water pipeline monitoring system that integrates synthetic IoT sensor simulation, algorithmic anomaly detection, graph-based leak localization, water loss estimation, government water data contextualization, and AI reasoning.

---

## 🛠 Project Structure

- **`backend/`**: Python 3.11+ FastAPI backend application containing domain models, graph topology engine, database setup, REST APIs, and automated test suite.

---

## 🚀 Quick Start (Backend)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run tests:
   ```bash
   pytest
   ```
4. Launch backend dev server:
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```

Refer to [`backend/README.md`](file:///a:/Amar/Projects/Project%208%20%28Hack%20India%29/backend/README.md) for full architecture details.
