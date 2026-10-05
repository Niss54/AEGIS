# ⏱️ AEGIS-CLIMATE — Hackathon Build Sprint Task Tracker
### *BHARAT AGENTIC 2026 (12-Hour Sprint)*

> **Team:** Syntrix  
> **Repository:** [https://github.com/Niss54/AEGIS](https://github.com/Niss54/AEGIS)  
> **Start Time:** 09:00 AM IST | **Submission Opens:** 08:00 PM IST | **Hard Deadline:** 09:00 PM IST

---

## 📊 Live Progress Tracker

```
Phase 1: Foundation & Infrastructure ██████████ 100% ✅
Phase 2: Agent 1 - ML Core           ░░░░░░░░░░   0% ⏳
Phase 3: MCP Hub & Agent 2 (Geo)     ░░░░░░░░░░   0% ⏳
Phase 4: Agent 3 - Regulatory RAG    ░░░░░░░░░░   0% ⏳
Phase 5: Next.js Command Center      ░░░░░░░░░░   0% ⏳
Phase 6: Winning Edge & Polish       ░░░░░░░░░░   0% ⏳
Phase 7: Submission & Video Demo     ░░░░░░░░░░   0% ⏳
```

---

## 🟢 Phase 1: Foundation Setup & Infrastructure (09:00 – 10:30) — COMPLETE ✅
- [x] Git repository initialization (`git init`)
- [x] Remote tracking set to `https://github.com/Niss54/AEGIS` (`origin/main`)
- [x] Configure `.gitignore` for secrets, Python cache, and Next.js artifacts
- [x] Draft and finalize production PRD (`PRD.md`, `docs/Prd.md`)
- [x] Document Hackathon guidelines, team roster, and judging rubrics (`HACKATHON_GUIDELINES.md`)
- [x] Initialize `backend/` FastAPI application skeleton with health check (`/api/v1/health`)
- [x] Implement WebSocket stream manager (`/ws/events`) for live agent thought tokens
- [x] Build preloaded Bharat Hotspots catalog (`/api/v1/hotspots`)
- [x] Implement GeoJSON polygon generation endpoint (`/api/v1/geo/layer/{id}`)
- [x] Initialize `mcp_hub/` Model Context Protocol JSON-RPC 2.0 dispatcher & tool registry
- [x] Generate official aiKart `agent_manifest.yaml` (Method 1) and container Dockerfiles
- [x] Setup `docker-compose.yml` for PostgreSQL/PostGIS, Redis, ChromaDB, MCP Hub, Backend
- [x] Implement & run integration test suite (`tests/test_phase1.py` - 100% passing)
- [x] Commit & push Phase 1 foundation to GitHub

---

## 🔵 Phase 2: Agent 1 — Acute Physical Risk Agent (ML Core) (10:30 – 12:00)
- [ ] Open-Meteo API live weather integration (hourly precipitation, soil moisture, humidity)
- [ ] Historical flood dataset feature engineering (SMOTE oversampling logic)
- [ ] Train & serialize XGBoost / Random Forest flood classifier model (`models/flood_classifier.pkl`)
- [ ] Expose `/api/v1/tools/predict` endpoint returning risk score [0.0–1.0] and tier (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`)
- [ ] Unit tests for Agent 1 risk inference
- [ ] Commit & push Phase 2 to GitHub

---

## 🟣 Phase 3: MCP Hub & Agent 2 — Chronic Geospatial Vulnerability (12:00 – 02:00)
- [ ] Implement MCP Hub JSON-RPC 2.0 gateway with tool registry
- [ ] LangGraph StateGraph pipeline (Node 1: fetch meteo ➔ Node 2: predict ➔ Node 3: route decision)
- [ ] Condition routing: auto-trigger Agent 2 if `risk_score > 0.65`
- [ ] Agent 2 Geospatial engine: 30m SRTM DEM elevation delta computation
- [ ] Drainage overflow & building exposure calculation via HAZUS damage curves
- [ ] Output GeoJSON polygon layer (`/api/v1/geo/layer/{id}`)
- [ ] Commit & push Phase 3 to GitHub

---

## 🟡 Phase 4: Agent 3 — Macro Transition & Financial VaR RAG (02:00 – 04:00)
- [ ] Climate policy document corpus setup (SEBI BRSR, Carbon Tax, National Water Policy)
- [ ] Document ingestion & chunking using PyMuPDF / LangChain
- [ ] Vector database setup with ChromaDB & `sentence-transformers (all-MiniLM-L6-v2)`
- [ ] LLM synthesis chain for Value-at-Risk (VaR), stranded asset risk, and regulatory gap analysis
- [ ] Output structured executive briefing JSON & summary
- [ ] Commit & push Phase 4 to GitHub

---

## 🔴 Phase 5: Next.js 14 Frontend Command Center (04:00 – 06:00)
- [ ] Initialize Next.js 14 App Router project with Tailwind CSS & Lucide icons
- [ ] Design System implementation (Dark Navy `#0D1B2A`, Teal `#0E9AA7`, Risk Tier Colors)
- [ ] Interactive Leaflet Geo-Risk Map with animated flood inundation polygons
- [ ] Animated Radial SVG Risk Score Gauges & Agent Status Badges (`IDLE`, `RUNNING`, `COMPLETE`)
- [ ] Real-time Event Feed panel with WebSocket streaming
- [ ] Recharts Executive VaR breakdown and 10/20/30-year exposure matrix
- [ ] Commit & push Phase 5 to GitHub

---

## 🌟 Phase 6: Winning Edge Differentiators & Hackathon Polish (06:00 – 07:30)
- [ ] **Agent Thought Log & Tool Trace:** Live visible drawer of agent internal reasoning (`Thought ➔ Action ➔ Observation`)
- [ ] **Pre-loaded Bharat Hotspots:** Instant one-click triggers for Mumbai, Bengaluru, Assam, Chennai
- [ ] **What-If Climate Anomaly Simulator:** Live interactive rainfall/saturation slider
- [ ] **Bhasha-AI:** Bilingual Hindi & English localized alert generation with audio synthesis
- [ ] **One-Click Executive PDF Exporter:** Downloadable C-suite briefing card
- [ ] Commit & push Phase 6 to GitHub

---

## 🚀 Phase 7: Demo Rehearsal, Video & Submission Freeze (07:30 – 08:30)
- [ ] Final End-to-End pipeline verification (Safe vs Watch vs High vs Critical trigger test)
- [ ] 2–3 Minute high-impact screen recording demo video
- [ ] 5-Slide winning pitch deck PDF
- [ ] Unstop / AIKart final submission entry completion before 09:00 PM
- [ ] Final Git commit & push with tag `v1.0.0-bharat-agentic`
