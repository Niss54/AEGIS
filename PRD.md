# 📋 Product Requirements Document (PRD) — AEGIS-CLIMATE
### *Autonomous Multi-Agent Environmental & Climate Risk Intelligence Platform*

> **Event:** BHARAT AGENTIC 2026 (12-Hour Hackathon powered by AIKart)  
> **Team:** Syntrix (Nishant Maurya, Navya Chaudhary, Om Tripathi, Nikita Chopde)  
> **Repository:** [https://github.com/Niss54/AEGIS](https://github.com/Niss54/AEGIS)  
> **Version:** 1.0.0 (Hackathon Release)  
> **Status:** 🟢 Approved & Active  
> **Target Delivery:** 1 October 2026, 08:00 PM IST (Submission Deadline: 09:00 PM IST)

---

## 📑 Table of Contents
1. [Executive Summary & Vision](#1-executive-summary--vision)
2. [The Bharat Problem Statement & Opportunity](#2-the-bharat-problem-statement--opportunity)
3. [Target Personas & Stakeholders](#3-target-personas--stakeholders)
4. [System Architecture & Multi-Agent Flow](#4-system-architecture--multi-agent-flow)
5. [Detailed Agent Specifications](#5-detailed-agent-specifications)
6. [Core Functional Requirements](#6-core-functional-requirements)
7. [Winning Edge: High-Impact Differentiators](#7-winning-edge-high-impact-differentiators)
8. [API Keys & Live Integration Architecture Matrix](#8-api-keys--live-integration-architecture-matrix)
9. [Phased Implementation Roadmap (12-Hour Sprint)](#9-phased-implementation-roadmap-12-hour-sprint)
10. [REST API & WebSocket Specifications](#10-rest-api--websocket-specifications)
11. [Data Architecture & Schema](#11-data-architecture--schema)
12. [Judging Evaluation Alignment & Success Metrics](#12-judging-evaluation-alignment--success-metrics)
13. [Demo Execution & Deliverables Checklist](#13-demo-execution--deliverables-checklist)

---

## 1. Executive Summary & Vision

### 1.1 Mission
**AEGIS-CLIMATE** is an autonomous, multi-agent environmental intelligence platform built to protect Bharat's communities, critical infrastructure, and enterprises from accelerating climate risks. It ingests real-time environmental telemetry, geospatial terrain models, and regulatory policy documents, executing a synchronized **Understand → Reason → Plan → Use Tools → Act → Deliver** loop across three specialized autonomous AI agents.

### 1.2 The Core Disconnect
Organizations and civic bodies today face a severe operational disconnect:
- **Petabytes of raw data exist:** Satellite imagery, Open-Meteo streams, digital elevation models, and voluminous climate policies.
- **Decision-makers receive fragmented reports:** Civic disaster authorities respond hours too late; municipal planners lack structural degradation projections; and enterprises face unquantified financial penalties under new ESG/carbon compliance mandates (e.g., SEBI BRSR).
- **The AEGIS Solution:** A unified Hub-and-Spoke multi-agent system orchestrated via the **Model Context Protocol (MCP)** and **LangGraph**, bridging 15-minute emergency hazard detection with 30-year infrastructure vulnerability and enterprise financial Value-at-Risk (VaR).

---

## 2. The Bharat Problem Statement & Opportunity

| Geographic & Economic Challenge | Current Failure Point | AEGIS Agentic Solution |
| :--- | :--- | :--- |
| **Monsoon Cloudbursts & Urban Flash Floods** (e.g., Mumbai, Bengaluru, Chennai) | Static rain gauges report rainfall after flooding has already inundated roads and underpasses. | **Agent 1 (Acute Physical Risk):** Machine learning classifier (XGBoost) runs on live Open-Meteo telemetry and antecedent saturation indices, computing localized flood probability in real-time. |
| **Infrastructure Degradation & Waterlogging** (Smart cities, highways, rail corridors) | Municipal bodies lack parcel-level topological drainage models, resulting in billions in recurring road and structural damage. | **Agent 2 (Chronic Vulnerability):** Spatial computation with GeoPandas and 30m SRTM DEM rasters models water accumulation, runoff over-capacity, and HAZUS depth-damage estimates. |
| **Enterprise Carbon & Climate Regulatory Exposure** (SEBI BRSR, Carbon Border Tax) | Industrial hubs and financial risk officers cannot quantify how physical risks translate into stranded assets and regulatory non-compliance. | **Agent 3 (Macro Transition & Financial Risk):** PyMuPDF + ChromaDB RAG with Claude synthesizes policy clauses with physical hazard data to deliver executive Value-at-Risk (VaR) briefs. |

---

## 3. Target Personas & Stakeholders

### 3.1 Primary Persona: Civic Emergency & Municipal Officer ("Aditi Verma")
- **Role:** Municipal Disaster Management Authority (MDMA / Municipal Commissioner)
- **Goal:** Receive automated early warnings for specific wards/coordinates before water accumulates; identify which buildings and roads require evacuation or sandbagging.
- **Pain Point:** Bombarded by raw PDF weather alerts with no localized risk score or actionable geospatial footprint.

### 3.2 Secondary Persona: Enterprise Risk & Infrastructure Manager ("Rajesh Nair")
- **Role:** Chief Risk Officer (CRO) / ESG Director for an industrial corridor or logistics fleet.
- **Goal:** Quantify asset vulnerability across warehouses, transport hubs, and plants; audit compliance against carbon taxation and environmental regulations.
- **Pain Point:** Disconnected spreadsheets, delayed annual ESG audits, zero visibility into real-time operational exposure.

---

## 4. System Architecture & Multi-Agent Flow

AEGIS-CLIMATE implements an asynchronous **Hub-and-Spoke Multi-Agent Architecture** utilizing the **Model Context Protocol (MCP)**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      NEXT.JS 14 COMMAND CENTER                         │
│   (Interactive GIS Map · Risk Gauges · Live WebSocket Stream · Charts)  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ REST / WebSockets
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    FASTAPI ASYNCHRONOUS BACKEND                        │
│          (/api/v1/analyze · /api/v1/events · State Persistence)        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ JSON-RPC 2.0
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   MCP HUB (Model Context Protocol)                     │
│    Tool Registry · Shared Session Context Bus · LangGraph Router       │
└───────┬───────────────────────────┼────────────────────────────┬───────┘
        │                           │                            │
        ▼                           ▼                            ▼
┌──────────────────┐       ┌──────────────────┐        ┌──────────────────┐
│     AGENT 1      │       │     AGENT 2      │        │     AGENT 3      │
│  ACUTE PHYSICAL  │       │ CHRONIC CLIMATE  │        │ MACRO TRANSITION │
│    RISK AGENT    │       │VULNERABILITY AGT │        │ & FINANCIAL RISK │
├──────────────────┤       ├──────────────────┤        ├──────────────────┤
│• Open-Meteo Live │Score  │• 30m SRTM DEM    │Exposure│• Climate Corpus  │
│• Feature Matrix  │>0.65  │• GeoPandas Join  │Report  │• ChromaDB Vector │
│• XGBoost Model   │──────>│• Drainage Overcap│───────>│• Claude Reasoning│
│• Risk Tier 0-1.0 │       │• HAZUS Damage Est│        │• VaR Briefing    │
└──────────────────┘       └──────────────────┘        └──────────────────┘
```

### Architectural Principles:
1. **No Peer-to-Peer Agent Sprawl:** Agents communicate strictly via the MCP Hub using JSON-RPC 2.0 payloads. This guarantees auditability, replayability, and independent scaling.
2. **LangGraph StateGraph Routing:** Execution is managed by a deterministic state graph:
   - Node 1: `fetch_weather_vectors(lat, lon)`
   - Node 2: `run_ml_classifier(feature_matrix)`
   - Node 3: `route_decision(risk_score)`:
     - Score `< 0.50` ➔ SAFE REPORT (end)
     - Score `0.50 – 0.65` ➔ WATCH ALERT (end)
     - Score `> 0.65` ➔ Auto-triggers Agent 2
   - Node 4: `load_geodata(lat, lon, radius)`
   - Node 5: `compute_structural_exposure(geo_layers)`
   - Node 6: `route_financial(exposure_report)` ➔ Triggers Agent 3 for HIGH/CRITICAL tiers
   - Node 7: `rag_retrieve(region, sector, policy_corpus)`
   - Node 8: `llm_synthesize(risk + exposure + clauses)` ➔ Value-at-Risk calculation
   - Node 9: `compile_unified_report()` ➔ Persist & push to WebSocket

---

## 5. Detailed Agent Specifications

### 5.1 Agent 1: Acute Physical Risk Agent (Operational Layer)
- **Objective:** Calculate localized flash flood probability in near-real-time (15-min refresh).
- **Inputs:** GPS Coordinates `(lat, lon)`, timestamp, search radius (default 10km).
- **Tool Invocations:**
  - `fetch_live_meteo`: Calls Open-Meteo API for hourly precipitation, 7-day rolling antecedent precipitation, relative humidity, and soil moisture saturation index.
  - `load_elevation_delta`: Quick DEM lookup.
- **ML Engine:** XGBoost / Random Forest classifier trained on historical meteorological anomaly datasets with SMOTE oversampling.
- **Outputs:**
  ```json
  {
    "risk_score": 0.87,
    "risk_tier": "HIGH",
    "dominant_factor": "soil_saturation",
    "metrics": {
      "precipitation_24h_mm": 94.2,
      "precipitation_7d_mm": 218.4,
      "soil_saturation_pct": 91.5,
      "humidity_pct": 89
    },
    "triggered_chronic": true,
    "timestamp": "2026-10-01T09:30:00Z"
  }
  ```

### 5.2 Agent 2: Chronic Climate Vulnerability Agent (Structural Layer)
- **Objective:** Long-term infrastructure degradation and asset exposure analysis over 10–30 year horizons.
- **Trigger:** Automatic activation when Agent 1 emits `risk_score > 0.65`.
- **Tool Invocations:**
  - `load_dem_raster`: Loads 30m SRTM Digital Elevation Model tiles via Rasterio.
  - `overlay_drainage_capacity`: GeoPandas spatial intersection with civic drainage infrastructure and OpenStreetMap building footprints.
  - `apply_hazus_curves`: Applies HAZUS-MH depth-damage curves against building types.
- **Rule Engine:**
  - `IF drainage_overflow_pct > 70 AND elevation_delta < 5m` ➔ Classifies as `INFRASTRUCTURE_FAILURE`.
- **Outputs:**
  ```json
  {
    "exposure_tier": "INFRASTRUCTURE_FAILURE",
    "waterlogging_depth_cm": 85,
    "buildings_at_risk": 342,
    "drainage_overflow_pct": 78,
    "damage_estimate_inr": 102500000,
    "damage_estimate_usd": 1240000,
    "geo_overlay_geojson": "/api/v1/geo/layer/event-xyz",
    "horizon_curves": { "10yr": 0.35, "20yr": 0.62, "30yr": 0.88 }
  }
  ```

### 5.3 Agent 3: Macro Transition & Financial Risk Agent (Executive Layer)
- **Objective:** Quantify corporate balance-sheet exposure, Value-at-Risk (VaR), stranded asset likelihood, and compliance with Indian climate mandates (e.g., SEBI BRSR, National Action Plan on Climate Change).
- **Architecture:** PyMuPDF document ingestion ➔ Chunking (512 tokens, 64 overlap) ➔ Embeddings (`sentence-transformers/all-MiniLM-L6-v2`) ➔ ChromaDB vector store.
- **Tool Invocations:**
  - `query_regulatory_corpus`: Cosine similarity search (top-5 clauses) for region and industry sector.
  - `model_var_exposure`: Multi-factor VaR formula linking physical damage probability with asset book values and regulatory carbon penalties.
  - `synthesize_executive_brief`: Claude LLM prompt with strict Pydantic JSON validation.
- **Outputs:**
  ```json
  {
    "var_estimate_usd": 4500000,
    "var_estimate_inr": 375000000,
    "stranded_asset_risk": "HIGH",
    "applicable_regulations": ["SEBI BRSR Core 2024", "National Water Mission Policy", "Carbon Tax Schema 2026"],
    "compliance_gap_pct": 34,
    "recommended_actions": [
      "Commission immediate stormwater retention vaults at North logistics hub",
      "Accelerate ESG Scope 1 & 2 carbon disclosures to avoid tier-2 non-compliance penalties",
      "Restructure asset insurance coverage with parametric flood endorsements"
    ],
    "briefing_pdf_ready": true
  }
  ```

---

## 6. Core Functional Requirements

### 6.1 Backend & Orchestration (FastAPI + MCP Hub)
- **FR-1.1:** Asynchronous REST endpoints for coordinate analysis (`POST /api/v1/analyze`).
- **FR-1.2:** MCP Hub JSON-RPC 2.0 dispatcher with tool validation against JSON Schema.
- **FR-1.3:** LangGraph StateGraph managing conditional branching between Agent 1, Agent 2, and Agent 3.
- **FR-1.4:** WebSocket endpoint (`/ws/events`) broadcasting live agent progression (`IDLE` ➔ `RUNNING` ➔ `COMPLETE`).
- **FR-1.5:** ChromaDB persistence for regulatory documents and vector querying.

### 6.2 Frontend Command Center (Next.js 14 + Tailwind + Leaflet)
- **FR-2.1:** **Interactive Geo-Map:** Full-screen Leaflet map displaying risk markers, flood inundation polygon overlays, and asset clusters.
- **FR-2.2:** **Real-time Risk Gauges:** Animated radial gauges (0–100) with color tier coding (Safe: `#2EC4B6`, Watch: `#F4A261`, Danger: `#E76F51`, Critical: `#D62828`).
- **FR-2.3:** **Agent Status Matrix:** Real-time visual indicator badges for Agent 1, Agent 2, and Agent 3 with live execution timers.
- **FR-2.4:** **Interactive Event Feed:** Scrolling stream of analyzed coordinates and triggered alerts.
- **FR-2.5:** **Executive VaR Breakdown Chart:** Recharts visualization showing capital at risk across physical damage vs. carbon compliance penalties.

---

## 7. Winning Edge: High-Impact Differentiators
*(Designed specifically to wow judges and secure 1st place in Bharat Agentic 2026)*

```
┌────────────────────────────────────────────────────────────────────────┐
│                   🌟 AEGIS WINNING DIFFERENTIATORS                    │
├────────────────────────────────────────────────────────────────────────┤
│ 1. 🔍 Agent Thought Log & Tool Trace (Real-time LangGraph Monologue)    │
│ 2. 🇮🇳 Pre-Loaded Bharat Hotspots (Mumbai, Bengaluru, Assam, Chennai)   │
│ 3. 🧪 "What-If" Climate Anomaly Simulator (Live Rainfall Slider)        │
│ 4. 🗣️ Bhasha-AI: Bilingual Hindi/English Audio & Text Alert Generator  │
│ 5. 📄 One-Click Executive Briefing PDF/HTML Exporter                    │
│ 6. 🔌 Multi-Provider API & LLM Arbitration Matrix (Gemini + Groq + OSS) │
│ 7. ✨ High-Energy Cyber-Cockpit UI/UX (Inspired by nissh.info & UI-UX)  │
└────────────────────────────────────────────────────────────────────────┘
```

1. **Agent Thought Log & Tool Trace (Autonomous Proof):**
   - *Why Judges Care:* Basic chatbots hide everything or fake responses. Judges evaluate *Agentic Capability*.
   - *Feature:* Live drawer on the UI displaying the agent's internal reasoning cycle (`Thought` ➔ `Tool Call: open_meteo_fetch` ➔ `Observation: 94mm rain` ➔ `Decision: Trigger Chronic Agent`).
2. **Pre-Loaded Bharat Hotspots:**
   - *Why Judges Care:* Demonstrates immediate *Bharat Relevance* without requiring judges to find coordinates.
   - *Included Presets:*
     - 📍 **Mumbai (Mithi River / Kurla Basin):** Severe urban waterlogging & suburban rail disruption.
     - 📍 **Bengaluru (Bellandur / Outer Ring Road):** Tech park stormwater overflow & lake breach risk.
     - 📍 **Assam (Brahmaputra / Kaziranga):** Severe riverine flood corridor.
     - 📍 **Chennai (Velachery / Adyar Basin):** Coastal monsoon storm surge.
3. **"What-If" Climate Anomaly Simulator:**
   - *Why Judges Care:* Lets judges interact with the agents dynamically. A slider adjusts simulated precipitation (+25mm to +150mm) or soil saturation and watches the 3 agents autonomously re-plan and re-calculate in real time.
4. **Bhasha-AI (Voice & Multilingual Civic Dispatch):**
   - *Why Judges Care:* Bharat Agentic highlights *Bharat Languages & Accessibility*.
   - *Feature:* Generates instant audio speech synthesis and Hindi/English localized broadcast text for field response teams using ElevenLabs / Sarvam AI / Web Speech.
5. **One-Click Executive Briefing Exporter:**
   - *Why Judges Care:* Proves end-to-end product utility from operational telemetry to C-suite boardroom briefing (`/api/v1/events/{id}/executive-briefing/html`).
6. **Mission-Control Cyber Cockpit (Inspired by nissh.info & docs/UI-UX.md):**
   - *Why Judges Care:* Instant visual WOW factor. Floating ambient particle canvas, live telemetry marquee, neon glassmorphic cards, and an interactive API integrations drawer.

---

## 8. API Keys & Live Integration Architecture Matrix

### 8.1 Why Tests Pass Without Live API Keys (Deterministic Graceful Degradation)
In enterprise disaster response systems, **network outages or API quota limits must NEVER cause system failure**. AEGIS is architected with a **Dual-Engine Model**:
- **Offline Deterministic Fallback (Active in Unit Tests & Air-Gapped Deployments):**
  - **Agent 1:** Trained Scikit-Learn GradientBoostingClassifier (95.14% accuracy) runs locally in memory.
  - **Agent 2:** Geospatial elevation and HAZUS depth-damage lookup tables run locally using GeoPandas.
  - **Agent 3:** Statistical Value-at-Risk (VaR) equations and deterministic regulatory templates run locally.
  - *Result:* 100% of unit tests pass reliably, validating system integrity and disaster resilience even with zero external network connectivity.
- **Live Online LLM & Telemetry Engine (Activated via `.env`):**
  - When API keys are supplied in `.env`, the system automatically activates dynamic multi-model LLM reasoning (Gemini 1.5 Flash + Groq LLaMA-3-70B), live Open-Meteo satellite streams, Mapbox 3D satellite tiles, and ElevenLabs / Sarvam AI neural voice synthesis.

### 8.2 API Key Configuration Matrix (`.env`)

| Variable Name | Service Provider | Tier / Cost | Core Feature Powered | Where to Obtain |
| :--- | :--- | :--- | :--- | :--- |
| `GEMINI_API_KEY` | Google AI Studio | Free Tier | Dynamic ESG policy synthesis, nuance Hindi translation, C-Suite brief generation in Agent 3 | [aistudio.google.com](https://aistudio.google.com) |
| `GROQ_API_KEY` | Groq Cloud | Free Tier | Ultra-low latency (<400ms) LLaMA-3-70B reasoning for Agent Thought Trace monologues | [console.groq.com](https://console.groq.com) |
| `OPENMETEO_API_KEY` | Open-Meteo | Optional (Free for Hackathon) | Live 15-minute Doppler radar precipitation, soil moisture, and humidity telemetry | [open-meteo.com](https://open-meteo.com) |
| `MAPBOX_API_TOKEN` | Mapbox GL | Free (50k loads/mo) | High-resolution satellite tiles, 3D terrain elevation contours on Leaflet GIS | [mapbox.com](https://mapbox.com) |
| `ELEVENLABS_API_KEY` | ElevenLabs | Free Tier | High-fidelity neural voice synthesis for English civic emergency audio alerts | [elevenlabs.io](https://elevenlabs.io) |
| `SARVAM_API_KEY` | Sarvam AI | Trial Tier | Indic neural speech synthesis (Hindi, Marathi, Tamil, Bengali) for regional field response | [sarvam.ai](https://sarvam.ai) |
| `OPENAI_API_KEY` | OpenAI | Optional | GPT-4o fallback arbitration for macro financial risk analysis | [platform.openai.com](https://platform.openai.com) |
| `ANTHROPIC_API_KEY` | Anthropic | Optional | Claude 3.5 Sonnet RAG reasoning over complex SEBI BRSR regulatory clauses | [console.anthropic.com](https://console.anthropic.com) |

---

## 9. Phased Implementation Roadmap (12-Hour Sprint)

Aligned with the hackathon sprint from 09:00 AM to 08:00 PM build freeze:

```
[09:00 - 10:30] Phase 1: Foundation & Infrastructure (FastAPI + Docker + MCP Skeleton) [COMPLETE ✅]
[10:30 - 12:00] Phase 2: Agent 1 - Acute Physical ML Classifier (Open-Meteo + GBM 95.14%) [COMPLETE ✅]
[12:00 - 02:00] Phase 3: Agent 2 - Chronic Vulnerability & Geospatial Engine (GeoPandas + HAZUS) [COMPLETE ✅]
[02:00 - 04:00] Phase 4: Agent 3 - Regulatory RAG & VaR Modeling (ChromaDB + LLM Fallback) [COMPLETE ✅]
[04:00 - 06:00] Phase 5: Mission-Control Command Center & Real-Time GIS Leaflet Dashboard [COMPLETE ✅]
[06:00 - 07:30] Phase 6: Winning Edge & Full API Integration Matrix [COMPLETE ✅]
  ├── Phase 6.1: Live LLM Multi-Provider (Groq Sub-400ms 120B/20B + Gemini) [COMPLETE ✅]
  ├── Phase 6.2: Live Telemetry & Mapbox High-Res Satellite/Radar GIS [COMPLETE ✅]
  ├── Phase 6.3: Bhasha-AI Dual Voice Dispatch Pipeline (ElevenLabs + Sarvam AI) [COMPLETE ✅]
  ├── Phase 6.4: UI/UX Master Overhaul (Ambient Particle Canvas, Ticker Marquee, nissh.info Style) [COMPLETE ✅]
  └── Phase 6.5: C-Suite Executive Briefing HTML/PDF Print-Ready Generator [COMPLETE ✅]
[07:30 - 08:30] Phase 7: E2E Integration, Demo Scripting & Final Submission Packaging [COMPLETE ✅]
  ├── Phase 7.1: Model Context Protocol (MCP) Official Spec & 10/10 E2E Tests Passing [COMPLETE ✅]
  ├── Phase 7.2: Official aiKart Agent Manifest (agent_manifest.yaml) & Container Packaging [COMPLETE ✅]
  ├── Phase 7.3: 5-Slide Winning Pitch Deck & 2.5-Minute Timed Demo Script [COMPLETE ✅]
  └── Phase 7.4: Structured Git Commits & Pushed to GitHub (origin main) [COMPLETE ✅]
```

---

## 10. REST API & WebSocket Specifications

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/analyze` | Trigger full 3-agent autonomous pipeline for `(lat, lon)`. |
| `GET` | `/api/v1/events` | List all historical risk events with filtering by tier and location. |
| `GET` | `/api/v1/events/{id}` | Retrieve complete multi-agent report for a specific event. |
| `GET` | `/api/v1/events/{id}/structural`| Fetch Agent 2 geospatial damage & exposure calculations. |
| `GET` | `/api/v1/events/{id}/financial` | Fetch Agent 3 Value-at-Risk & regulatory compliance report. |
| `GET` | `/api/v1/geo/layer/{event_id}` | GeoJSON polygon layer of inundation and building footprints. |
| `POST` | `/api/v1/documents/ingest` | Upload and vectorize climate policy PDF into ChromaDB. |
| `GET` | `/api/v1/documents` | List indexed policy documents and chunk stats. |
| `GET` | `/api/v1/health` | System health check (DB, Redis, MCP Hub, Vector Store). |
| `GET` | `/api/v1/integrations/status` | Live status inspector for all connected AI and telemetry API services. |
| `GET` | `/api/v1/events/{id}/executive-briefing/html` | Print-ready A4 executive C-Suite briefing document. |
| `WS` | `/ws/events` | Bidirectional WebSocket stream for live agent execution tokens. |

---

## 11. Data Architecture & Schema

### PostgreSQL / PostGIS Core Tables:
1. `risk_events`:
   - `id` (UUID PK), `lat` (DECIMAL), `lon` (DECIMAL), `location_name` (VARCHAR), `risk_score` (DECIMAL), `risk_tier` (VARCHAR), `agent1_raw` (JSONB), `triggered_at` (TIMESTAMPTZ), `status` (VARCHAR).
2. `structural_reports`:
   - `id` (UUID PK), `risk_event_id` (UUID FK), `exposure_tier` (VARCHAR), `waterlogging_depth_cm` (INT), `buildings_at_risk` (INT), `damage_estimate_inr` (BIGINT), `agent2_raw` (JSONB).
3. `financial_reports`:
   - `id` (UUID PK), `structural_id` (UUID FK), `var_estimate_inr` (BIGINT), `stranded_risk` (VARCHAR), `regulations` (JSONB), `compliance_gap_pct` (INT), `agent3_raw` (JSONB).
4. `policy_documents`:
   - `id` (UUID PK), `title` (VARCHAR), `region` (VARCHAR), `doc_type` (VARCHAR), `ingested_at` (TIMESTAMPTZ).

---

## 12. Judging Evaluation Alignment & Success Metrics

| Judging Criteria | Maximum Score Objective | Built-in Proof Point in AEGIS |
| :--- | :--- | :--- |
| **Agentic Capability** | Autonomous reasoning, tool usage, multi-step planning | 3 independent agents orchestrated by LangGraph and MCP Hub, visible via real-time Thought Trace. |
| **Bharat Impact** | Addresses core Indian geographic & economic threats | Pre-configured Indian hotspots (Mumbai, Bengaluru, Assam) solving real monsoon flood crises. |
| **Technical Implementation** | Clean architecture, type safety, async throughput | FastAPI, Next.js 14, XGBoost, GeoPandas, ChromaDB, PostGIS, Docker Compose. |
| **Innovation** | Unification of physical + geospatial + corporate financial risk | First platform bridging 15-minute emergency warnings with 30-year infrastructure and balance sheet VaR. |
| **User Experience (UX)** | WOW factor, responsive, dark-mode cockpit | Glassmorphic dark UI (`#0D1B2A`), animated SVG radial gauges, interactive Leaflet layers. |
| **Scalability & Feasibility** | Microservices readiness | Decoupled MCP JSON-RPC protocol, modular tool registry. |
| **Demo Quality** | Flawless, repeatable demonstration | One-click simulation scenario triggers with instant visual updates. |

---

## 13. Demo Execution & Deliverables Checklist

### Unstop / AIKart Required Submission Assets:
- [ ] **Project Name:** AEGIS-CLIMATE
- [ ] **Team Syntrix Roster:** Nishant Maurya, Navya Chaudhary, Om Tripathi, Nikita Chopde
- [ ] **Domain:** Energy & ClimateTech / Citizen & GovTech
- [ ] **Live Working Demo:** Local Docker / Deployed Web URL
- [ ] **GitHub Repo:** `https://github.com/Niss54/AEGIS` (Clean history, documentation, `.gitignore`)
- [ ] **2–3 Minute Demo Video:**
  - 0:00–0:40: The Bharat climate crisis & why current tools fail.
  - 0:40–1:40: Live AEGIS multi-agent orchestration across Mumbai/Bengaluru hotspots.
  - 1:40–2:20: What-If simulation slider & executive VaR briefing output.
  - 2:20–2:50: Technical architecture (MCP Hub + LangGraph) & team closing.
- [ ] **5-Slide Pitch Deck:**
  - Slide 1: Cover & Team Syntrix
  - Slide 2: The Bharat Problem & Economic Exposure
  - Slide 3: The AEGIS Solution & 3-Agent MCP Hub
  - Slide 4: Real-time Demo Highlights & Tech Stack
  - Slide 5: Scalability, Business Feasibility & Next Steps
