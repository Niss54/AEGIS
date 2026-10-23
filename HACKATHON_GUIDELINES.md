# 🛡️ AEGIS-CLIMATE — System Architecture & Engineering Blueprint

> **Autonomous Multi-Agent Environmental & Climate Risk Intelligence Platform**  
> **Architecture: Hub-and-Spoke MCP (Model Context Protocol) JSON-RPC 2.0 & LangGraph**

---

## 👥 1. Team & Project Overview

| Field | Detail |
| :--- | :--- |
| **Team Name** | **Syntrix** |
| **Project Name** | **AEGIS-CLIMATE** (*Autonomous Multi-Agent Environmental Intelligence Platform*) |
| **GitHub Repository** | [https://github.com/Niss54/AEGIS](https://github.com/Niss54/AEGIS) |
| **Primary Domain** | **Energy & ClimateTech** / **Citizen & GovTech** |
| **Blockchain Network** | **Polygon Amoy Testnet (Chain ID 80002)** |
| **Decentralized Storage**| **IPFS / Filecoin Pinning** |

### Team Members

| Name | Role | Contact Number | Status |
| :--- | :--- | :--- | :--- |
| **Nishant Maurya** | **Solo Developer & Lead Architect** (Full-Stack / Agent Systems / Blockchain / GIS) | +91 8840301998 | Verified ✅ |

---

## 🛠️ 2. Deployment & Container Architecture Specifications

### Method 1 — Open Agent Manifest & Container Deployment
1. Standardized `Dockerfile` ensuring all services run containerized.
2. `agent_manifest.yaml` specifying agent metadata, inputs, outputs, runtime, and entrypoints.
3. Microservices packaged via `docker-compose.yml`.

### Method 2 — Hosted API Endpoint Architecture
1. Publicly accessible REST endpoints (`POST /api/v1/analyze`, `GET /api/v1/health`).
2. Interactive Swagger documentation at `/docs` with live request/response schemas.
3. Model Context Protocol Gateway at `/mcp/invoke` over JSON-RPC 2.0.

---

## 🎯 3. Core Mission & Philosophy

### Problem Statement
India faces frequent climate extremities (flash floods, urban waterlogging, monsoon anomalies, and infrastructure degradation). Raw satellite imagery, meteorological feeds, and policy documents exist, but decision-makers receive fragmented, delayed, and non-actionable reports.

### AEGIS Solution
**AEGIS-CLIMATE** bridges this gap by deploying an autonomous **Hub-and-Spoke Multi-Agent Architecture** powered by the **Model Context Protocol (MCP)** and **LangGraph**:
1. **Understands** environmental telemetry (live weather, soil moisture, precipitation, satellite rasters).
2. **Reasons** across temporal horizons (immediate 15-minute emergency vs. 10–30 year infrastructure degradation vs. corporate regulatory Value-at-Risk).
3. **Plans** multi-step tool invocations across ML models, GIS spatial overlays, and regulatory RAG.
4. **Uses Tools** (Open-Meteo API, GeoPandas/DEM rasters, ChromaDB vector store, HAZUS damage curves).
5. **Acts** autonomously triggering cascading agents and broadcasting WebSocket alerts.
6. **Delivers** actionable civic and financial intelligence via an interactive React 19 + Vite + TypeScript command center.

```
       CORE AGENTIC EXECUTION CYCLE:
┌──────────────┐     ┌──────────┐     ┌──────────┐
│  UNDERSTAND  │ ──> │  REASON  │ ──> │   PLAN   │
└──────────────┘     └──────────┘     └──────────┘
                                            │
                                            ▼
┌──────────────┐     ┌──────────┐     ┌──────────┐
│   DELIVER    │ <── │   ACT    │ <── │ USE TOOLS│
└──────────────┘     └──────────┘     └──────────┘
```

---

## 🧠 4. Autonomous Multi-Agent Architecture

```
                  ┌──────────────────────────────────────────────┐
                  │ REACT 19 / VITE EXECUTIVE COMMAND CENTER     │
                  │ (Live Geo-Map, Risk Gauges, VaR Breakdown)   │
                  └──────────────────────┬───────────────────────┘
                                         │ REST / WebSocket
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │          FASTAPI ORCHESTRATION BACKEND       │
                  └──────────────────────┬───────────────────────┘
                                         │ JSON-RPC 2.0
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │     MCP HUB (Model Context Protocol Gateway) │
                  │     Tool Registry · State Bus · Router       │
                  └──────┬────────────────┬───────────────┬──────┘
                         │                │               │
         ┌───────────────┘                │               └───────────────┐
         ▼                                ▼                               ▼
┌──────────────────┐            ┌──────────────────┐            ┌──────────────────┐
│     AGENT 1      │            │     AGENT 2      │            │     AGENT 3      │
│  ACUTE PHYSICAL  │            │ CHRONIC CLIMATE  │            │ MACRO TRANSITION │
│    RISK AGENT    │            │VULNERABILITY AGT │            │ & FINANCIAL RISK │
├──────────────────┤            ├──────────────────┤            ├──────────────────┤
│• Operational     │ Trigger if │• 10-30yr Horizon │ Trigger if │• Regulatory RAG  │
│• Open-Meteo API  │ Risk > 0.65│• GeoPandas + DEM │ High Tier  │• ChromaDB Vector │
│• XGBoost Model   │───────────>│• Drainage Overly │───────────>│• Claude / LLM    │
│• Flood Prob.     │            │• HAZUS Damage Est│            │• VaR & Carbon Tax│
└──────────────────┘            └──────────────────┘            └──────────────────┘
```

---

## ⚖️ 5. Judging Criteria & Scoring Strategy

The judging panel will score entries on the following core pillars:

| Criteria | What Judges Look For | How AEGIS Wins Maximum Points |
| :--- | :--- | :--- |
| **1. Agentic Capability** | Autonomous reasoning, planning, multi-step workflows, tool calling, action taking. (No simple chatbot wrappers). | 3 distinct autonomous agents orchestrated via LangGraph & MCP Hub with automated conditional triggers and JSON-RPC dispatching. |
| **2. Bharat Impact & Relevance** | Tackling critical Indian challenges (monsoon floods, urban infrastructure damage, civic planning). | Direct application to Indian urban and rural regions (Mumbai, Bengaluru, Assam flood corridors, coastal ports). |
| **3. Technical Implementation** | Code quality, architecture robustness, asynchronous processing, modern stack. | Clean separation of concerns: FastAPI backend, scikit-learn/XGBoost, GeoPandas spatial processing, ChromaDB RAG, React 19 + Vite + TypeScript frontend. |
| **4. Innovation** | Novel approach, unique synergy of physical ML + geospatial + regulatory risk. | Unifies operational response, civil engineering vulnerability, and corporate financial exposure under one pane of glass. |
| **5. User Experience (UX)** | Intuitive, interactive, modern aesthetics, data density without clutter. | Sleek dark-mode interface, animated radial gauges, interactive Leaflet geo-overlays, instant WebSocket event feeds. |
| **6. Scalability & Feasibility** | Microservices readiness, Dockerized containers, async message passing, real-world deployability. | Docker Compose multi-container setup (PostGIS, Redis, ChromaDB, MCP Hub, Backend, Frontend). |
| **7. Demo Quality** | Clear presentation, working live flow without crashes, concise 2–3 min pitch video. | Scripted test scenarios (safe, alert, critical hazard trigger) with immediate visible agent reactions. |

---

## 📦 6. Final Submission Checklist

Each team must submit before **09:00 PM, 1 October 2026**:

- [ ] **Project Name:** AEGIS-CLIMATE
- [ ] **Team Members:** Nishant Maurya (Solo Developer) (Team Syntrix)
- [ ] **Selected Domain:** Energy & ClimateTech / Citizen & GovTech / Open Bharat
- [ ] **Problem Statement:** Detailed problem & pain point articulation
- [ ] **Solution Overview:** End-to-end multi-agent environmental intelligence system
- [ ] **Agent Workflow & Architecture:** Diagram & step-by-step data flow explanation
- [ ] **Technology Stack:** React 19 + Vite + TypeScript, FastAPI, LangGraph, MCP, XGBoost, GeoPandas, ChromaDB, PostGIS
- [ ] **GitHub Repository:** [https://github.com/Niss54/AEGIS](https://github.com/Niss54/AEGIS) (Clean code, setup instructions, architecture docs)
- [ ] **Working Demo:** Live deployed link or reproducible local Docker run
- [ ] **2–3 Minute Demo Video:** Clear walkthrough of problem, live agent orchestration, and impact
- [ ] **5-Slide Pitch Deck:**
  - Slide 1: Title & Vision
  - Slide 2: The Bharat Problem & Impact
  - Slide 3: The AEGIS Multi-Agent Solution & MCP Architecture
  - Slide 4: Live Demo Highlights & Technical Depth
  - Slide 5: Business Feasibility, Scalability & Team Syntrix

---

## 📜 7. Rules, Integrity & Responsible AI

1. **Eligibility & Team:** Team Syntrix (Solo Developer) registered under Team Leader Nishant Maurya.
2. **Fresh Development:** Core hackathon project built during the 12-hour sprint window.
3. **Open-Source & Libraries:** Open-source tools (LangGraph, FastAPI, GeoPandas, scikit-learn, Leaflet, React 19/Vite) are encouraged; existing foundational architecture must be clearly explained.
4. **Originality:** Zero plagiarism, authentic technical implementation and real-time execution.
5. **Responsible AI:** Strictly compliant with safety guidelines, no hazardous data injection, sanitization of RAG inputs, and transparent probabilistic hazard modeling.
6. **No Late Submissions:** The submission portal closes strictly at 9:00 PM. Target internal freeze by 8:00 PM.
