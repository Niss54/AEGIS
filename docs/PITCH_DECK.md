# 🏆 AEGIS-CLIMATE — Pitch Deck (5 Slides)
### *BHARAT AGENTIC 2026 — Autonomous Multi-Agent Environmental & Financial Intelligence Platform*

> **Team Name:** Syntrix  
> **Team Members:** Nishant Maurya (Team Leader), Navya Chaudhary, Om Tripathi, Nikita Chopde  
> **Repository:** [https://github.com/Niss54/AEGIS](https://github.com/Niss54/AEGIS)  
> **Track:** Energy & ClimateTech / Citizen & GovTech / Open Bharat  

---

## 📽️ SLIDE 1: Title & Vision
### **AEGIS-CLIMATE: Autonomous Multi-Agent Environmental & Financial Intelligence for Bharat**
> *"Translating environmental hazards into actionable civic defense and enterprise Value-at-Risk intelligence in real time."*

- **The Vision:** Move Bharat from passive disaster observation to **autonomous, anticipatory, multi-horizon intelligence**.
- **The Core Breakthrough:** A unified **Hub-and-Spoke Multi-Agent Architecture** powered by the **Model Context Protocol (MCP)** and **LangGraph**, executing across three temporal horizons:
  1. *Immediate Operational Horizon (15-min):* Real-time meteorological flood hazard prediction.
  2. *Chronic Geospatial Horizon (10–30 years):* 30m DEM topographical inundation and structural asset degradation.
  3. *Macro Corporate Horizon:* Enterprise Value at Risk (VaR), SEBI BRSR Principle 6 compliance, and localized bilingual citizen alerts.
- **Team Syntrix:** Engineered end-to-end in 12 hours for BHARAT AGENTIC 2026.

---

## 📽️ SLIDE 2: The Problem — Bharat's ₹8,000+ Crore Climate Blindspot
### **Fragmented Data, Silent Inundation, Stranded Balance Sheets**

1. **Catastrophic Economic & Civic Toll:**
   - Indian urban hubs lose over **₹8,000 Crores annually** due to flash floods, drainage overflows, and monsoon anomalies (e.g. Mumbai 2005/2023, Bengaluru Bellandur 2022, Chennai Michaung 2023).
2. **The "Data Silo" Failure:**
   - Raw weather feeds (IMD/Open-Meteo), satellite rasters (ISRO/SRTM), and municipal GIS maps exist in isolation.
   - Disaster management authorities receive reports **hours after inundation begins**.
3. **The Corporate Regulatory Vacuum:**
   - Top 1,000 listed entities face mandatory **SEBI BRSR Principle 6** and Ministry of Finance carbon surcharges, yet have **zero quantitative tools** to model physical-to-financial asset stranding risk.
4. **The Vernacular Communication Divide:**
   - Alerts issued in technical jargon fail to reach grassroots emergency responders across Bharat's diverse languages.

---

## 📽️ SLIDE 3: The Architecture — Autonomous Multi-Agent Cascade
### **Understand ➔ Reason ➔ Plan ➔ Use Tools ➔ Act ➔ Deliver**

```
                   ┌──────────────────────────────────────────────┐
                   │    MISSION-CONTROL EXECUTIVE COMMAND CENTER  │
                   │ (Leaflet GIS, SVG Gauges, What-If Simulator) │
                   └──────────────────────┬───────────────────────┘
                                          │ REST / WebSocket
                                          ▼
                   ┌──────────────────────────────────────────────┐
                   │         FASTAPI ORCHESTRATION GATEWAY        │
                   └──────────────────────┬───────────────────────┘
                                          │ JSON-RPC 2.0
                                          ▼
                   ┌──────────────────────────────────────────────┐
                   │       MODEL CONTEXT PROTOCOL (MCP) HUB       │
                   │       Tool Registry · State Bus · Router     │
                   └──────┬────────────────┬───────────────┬──────┘
                          │                │               │
          ┌───────────────┘                │               └───────────────┐
          ▼                                ▼                               ▼
┌──────────────────┐            ┌──────────────────┐            ┌──────────────────┐
│     AGENT 1      │            │     AGENT 2      │            │     AGENT 3      │
│  ACUTE PHYSICAL  │            │ CHRONIC CLIMATE  │            │ MACRO TRANSITION │
│    RISK AGENT    │            │VULNERABILITY AGT │            │ & FINANCIAL RISK │
├──────────────────┤            ├──────────────────┤            ├──────────────────┤
│• 15m Telemetry   │ Threshold  │• 30m DEM Raster  │ Severity   │• ChromaDB RAG    │
│• Open-Meteo API  │ Trigger    │• Rational Runoff │ Trigger    │• SEBI BRSR Mand. │
│• GBM ML Model    │── P > 0.65 ┼─>• HAZUS Curves  │── Inf Fail ┼─>• 4-Factor VaR  │
│• 95.14% Accuracy │            │• GeoJSON Engine  │            │• Bhasha-AI Voice │
└──────────────────┘            └──────────────────┘            └──────────────────┘
```

- **True Agentic Behavior (Not a Chatbot):**
  - **Autonomous Condition Evaluation:** Agent 1 evaluates meteorological metrics; if risk exceeds 0.65, it autonomously awakens Agent 2 without human intervention.
  - **Tool Use & MCP Interoperability:** Tools are formally registered and invoked over standard JSON-RPC 2.0.
  - **Execution Monologue:** Every step (`THOUGHT`, `TOOL_CALL`, `OBSERVATION`, `DECISION`) is broadcast live over WebSockets.

---

## 📽️ SLIDE 4: Technical Depth & Verification Metrics
### **Production-Grade Deep Tech Built for Scale**

| Capability | Technical Mechanism | Verified Metric / Standard |
| :--- | :--- | :--- |
| **Operational ML Engine** | GradientBoostingClassifier (scikit-learn) trained on 3,500 Bharat monsoon samples | **95.14% Accuracy**, **0.9056 Macro F1**, **< 20ms inference latency** |
| **Chronic Geospatial Engine** | 30m DEM elevation pooling + Rational Runoff Method ($Q = C \cdot I \cdot A$) | Multi-tier GeoJSON contours: Core basin, secondary perimeter, conduit line-strings |
| **Structural Damage Modeling**| FEMA HAZUS-MH depth-damage non-linear vulnerability curves | 4 asset typologies (Power Substation, Transit Terminal, Commercial Hub, Sluice Gates) |
| **Regulatory Policy RAG** | Persistent ChromaDB vector store + sentence embeddings | Indexed **SEBI BRSR Core**, **MoF Carbon Surcharge 2026**, **NDMA Urban Flood SOP**, **RBI Guidelines** |
| **Financial VaR Engine** | 4-Factor Model: Direct Physical Damage + Business Interruption + Regulatory Fines + Insurance Surge | Quantitative capital at risk in **₹ Crores** and **$M USD** with 10/20/30-year projections |
| **Bhasha-AI Civic Voice** | Localized Hindi (देवनागरी) & English alert generation | In-browser Web Speech API audio synthesis with 1-click clipboard dispatch |
| **Testing & Stability** | 5 Test Suites (`test_phase1` to `test_phase5_e2e`) | **100% Pass Rate** across all unit, integration, and build suites |

---

## 📽️ SLIDE 5: Market Opportunity, Scalability & Team Syntrix
### **Enterprise SaaS + GovTech Deployment Roadmap**

1. **Target Market & Stakeholders:**
   - **Municipal Corporations (Smart Cities):** BMC Mumbai, BBMP Bengaluru, GCC Chennai for early floodgate actuation and traffic diversion.
   - **Critical Infrastructure & Port Authorities:** Adani Ports (Mundra), Indian Railways, Power Grid Corporation of India (PGCIL).
   - **Corporate Treasuries & Banks:** Top 1,000 NSE/BSE listed companies complying with mandatory SEBI BRSR Principle 6 climate audits.
2. **Business & Monetization Model:**
   - **B2G (GovTech Tier):** Annual municipal licensing for city hazard command centers.
   - **B2B (Enterprise ESG Tier):** Asset-level VaR modeling and BRSR reporting SaaS (₹25L – ₹1 Cr / year per enterprise).
3. **aiKart & Production Readiness:**
   - Packaged with **Method 1 (`agent_manifest.yaml`)** and containerized with multi-service **Docker Compose** (PostGIS, Redis, ChromaDB, MCP Hub, Backend, Frontend).
4. **Team Syntrix:**
   - **Nishant Maurya** (Team Leader — Architecture, Full-Stack & Multi-Agent Orchestration)
   - **Navya Chaudhary** (Core Member — ML & Meteorological Data Engineering)
   - **Om Tripathi** (Core Member — Geospatial Systems & HAZUS Modeling)
   - **Nikita Chopde** (Core Member — Financial VaR & Regulatory Policy RAG)

> **"Built for BHARAT AGENTIC 2026 — Ready to deploy across India today."**
