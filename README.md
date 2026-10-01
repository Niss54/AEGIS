<div align="center">

<img src="./public/logo.png" alt="AEGIS Logo" width="160" />

# 🛡️ AEGIS-CLIMATE
### *Autonomous Multi-Agent Environmental Intelligence Platform*
**Translating Environmental Threats into Actionable Business & Civic Intelligence**

Built for **BHARAT AGENTIC 2026** (Powered by **AIKart**)  
*12-Hour National Agentic AI Hackathon*

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/Niss54/AEGIS)
[![Domain](https://img.shields.io/badge/Domain-Energy%20%26%20ClimateTech-green)](#-domain--bharat-impact)
[![Architecture](https://img.shields.io/badge/Architecture-Hub--and--Spoke%20MCP-orange)](#-system-architecture)
[![Team](https://img.shields.io/badge/Team-Syntrix-purple)](#-team-syntrix)
[![Status](https://img.shields.io/badge/Hackathon-In%20Progress-brightgreen)](#-hackathon-details)

[📋 Hackathon Guidelines](./HACKATHON_GUIDELINES.md) · [🏗️ Architecture Specs](./docs/Architecture.md) · [🤖 Agent Specs](./docs/AGENTS.md) · [📊 Database](./docs/Database.md) · [🔌 API Reference](./docs/API.md)

---

</div>

## 📌 Project Overview

**AEGIS-CLIMATE** is an autonomous, multi-agent environmental intelligence system designed specifically for the unique vulnerabilities of **Bharat**. When extreme weather strikes — from sudden Mumbai cloudbursts to Assam flood basins — disaster response, infrastructure managers, and financial executives face fragmented, slow, and disconnected data.

AEGIS bridges this gap by deploying **3 Autonomous AI Agents** coordinated through an **MCP Hub (Model Context Protocol)** and **LangGraph**:
1. **Agent 1 (Acute Physical Risk Agent):** Real-time flood hazard classifier using Open-Meteo vectors & XGBoost ML.
2. **Agent 2 (Chronic Climate Vulnerability Agent):** Long-term (10–30yr) geospatial infrastructure degradation via DEM & drainage overlays.
3. **Agent 3 (Macro Transition & Financial Risk Agent):** Enterprise Value-at-Risk (VaR) & carbon compliance audit via RAG and LLM reasoning.

---

## 👥 Team Syntrix

| Name | Role in Team | Contact | Verification |
| :--- | :--- | :--- | :--- |
| **Nishant Maurya** | **Team Leader** (Full-Stack & Multi-Agent Architecture) | `+91 8840301998` | Verified ✅ |
| **Navya Chaudhary** | Core Member | `+91 9045659400` | Verified ✅ |
| **Om Tripathi** | Core Member | `+91 7905226392` | Verified ✅ |
| **Nikita Chopde** | Core Member | `+91 9343458471` | Verified ✅ |

---

## 🔄 Core Agentic Workflow

```
Understand ───► Reason ───► Plan ───► Use Tools ───► Act ───► Deliver
```

1. **Understand:** Ingests live telemetry (rainfall, soil moisture saturation, relative humidity, elevation DEM rasters, policy PDFs).
2. **Reason:** Multi-tier probabilistic evaluation deciding whether physical threats exceed acute safety thresholds.
3. **Plan:** LangGraph state graph dynamically schedules tool invocations across geospatial analysis and vector document search.
4. **Use Tools:** Open-Meteo APIs, GeoPandas spatial joins, HAZUS damage curves, ChromaDB cosine similarity search.
5. **Act:** Cascades from real-time operational alerts directly into structural degradation models and financial briefings.
6. **Deliver:** Streams real-time updates via WebSockets to a Next.js command center and generates C-suite VaR briefings.

---

## 🏛️ System Architecture

```
                  ┌──────────────────────────────────────────────┐
                  │          NEXT.JS 14 FRONTEND COCKPIT         │
                  │  (Interactive Leaflet GIS, Radial Gauges,    │
                  │   Real-time WebSockets, Recharts Analytics)  │
                  └──────────────────────┬───────────────────────┘
                                         │ REST / WS
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │              FASTAPI API BACKEND             │
                  │        (Auth, Validation, Orchestration)     │
                  └──────────────────────┬───────────────────────┘
                                         │ JSON-RPC 2.0
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │          MCP HUB (Context Gateway)           │
                  │  (Dynamic Tool Registry & State Dispatcher)  │
                  └──────┬────────────────┬───────────────┬──────┘
                         │                │               │
         ┌───────────────┘                │               └───────────────┐
         ▼                                ▼                               ▼
┌──────────────────┐            ┌──────────────────┐            ┌──────────────────┐
│     AGENT 1      │            │     AGENT 2      │            │     AGENT 3      │
│  ACUTE PHYSICAL  │            │ CHRONIC CLIMATE  │            │ MACRO TRANSITION │
│    RISK AGENT    │            │VULNERABILITY AGT │            │ & FINANCIAL RISK │
├──────────────────┤            ├──────────────────┤            ├──────────────────┤
│• Open-Meteo Live │ Score>0.65 │• GeoPandas + DEM │ High-Risk  │• Policy Corpus   │
│• XGBoost Model   │───────────>│• Drainage Matrix │───────────>│• ChromaDB RAG    │
│• 15-min Refresh  │            │• HAZUS Exposure  │            │• Value at Risk   │
└──────────────────┘            └──────────────────┘            └──────────────────┘
```

---

## 🛠️ Complete Tech Stack

- **Agentic Orchestration:** Model Context Protocol (MCP) Hub (JSON-RPC 2.0), LangGraph, LangChain
- **AI / ML & Reasoning:** Claude 3.5 / LLM, scikit-learn, XGBoost, sentence-transformers (`all-MiniLM-L6-v2`)
- **Geospatial & Vision:** GeoPandas, Shapely, Rasterio, SRTM 30m DEM, OpenStreetMap Overpass
- **Backend & APIs:** Python 3.11+, FastAPI, Uvicorn, Pydantic v2, WebSockets
- **Database & State:** PostgreSQL 16 with PostGIS 3.4, Redis 7.2 (context cache), ChromaDB (vector store)
- **Frontend Dashboard:** Next.js 14 (App Router), TypeScript, Tailwind CSS, Leaflet.js, Recharts
- **DevOps:** Docker, Docker Compose, GitHub Actions

---

## 🚀 Quick Start (Local Setup)

```bash
# 1. Clone repository
git clone https://github.com/Niss54/AEGIS.git
cd AEGIS

# 2. Environment Configuration
cp docs/.env .env.local

# 3. Spin up Infrastructure (PostGIS, Redis, ChromaDB, MCP Hub)
docker compose up -d

# 4. Backend Setup
cd backend
pip install -r requirements.txt
python scripts/train_model.py
uvicorn main:app --reload --port 8000

# 5. Frontend Setup
cd ../frontend
npm install
npm run dev
```

---

## 📄 Hackathon Guidelines & Evaluation Matrix

For full hackathon rules, submission requirements, 12-hour timeline, and judging criteria, see [HACKATHON_GUIDELINES.md](./HACKATHON_GUIDELINES.md).
