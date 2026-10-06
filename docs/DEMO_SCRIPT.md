# 🎬 AEGIS-CLIMATE — Hackathon Video Demo Script (2:30 Mins)
### *BHARAT AGENTIC 2026 — 12-Hour Sprint Submission*

> **Project Name:** AEGIS-CLIMATE  
> **Team Name:** Syntrix (Nishant Maurya, Navya Chaudhary, Om Tripathi, Nikita Chopde)  
> **Target Video Length:** 2 Minutes 30 Seconds  
> **Target Resolution:** 1080p 60fps / 4K  
> **Aspect Ratio:** 16:9  

---

## ⏱️ Video Structure Overview

| Timestamp | Section | Key Screen Action | Voiceover Focus |
| :--- | :--- | :--- | :--- |
| **0:00 – 0:25** | The Hook & The Problem | Headline slide ➔ Command center reveal | ₹8,000 Cr annual Indian urban flood loss; siloed data crisis. |
| **0:25 – 0:50** | Command Center & GIS Map | Pan & zoom Leaflet map across Mumbai/Bengaluru | CartoDB Dark Matter tiles, multi-tier hazard polygons, asset pins. |
| **0:50 – 1:30** | The Autonomous Multi-Agent Cascade | Move "What-If" slider (+110mm) ➔ Click Trigger | Agent 1 (ML) ➔ Agent 2 (DEM Geo) ➔ Agent 3 (VaR RAG) cascade. |
| **1:30 – 1:55** | Bhasha-AI & Executive PDF Briefing | Play audio readout ➔ Click "Export C-Suite Briefing" | Hindi/English voice dispatch & print-ready executive PDF report. |
| **1:55 – 2:20** | Under The Hood (MCP Hub & Code) | Terminal test pass ➔ MCP Hub code ➔ Manifest | 95.14% GBM accuracy, JSON-RPC 2.0 MCP Hub, Docker Compose. |
| **2:20 – 2:30** | Closing Call to Action | Return to live dashboard with Team Syntrix tag | "Built for Bharat Agentic 2026. Ready to protect Bharat today." |

---

## 🎙️ Detailed Scene-by-Scene Script

### SCENE 1: The Hook & The Problem (0:00 – 0:25)
- **Visual:** Full screen capture of the **AEGIS-CLIMATE Command Center** (`http://localhost:5173` or `3000`) in dark glassmorphic navy theme. Glowing status badges (MCP HUB PORT 8001, ML MODEL GBM F1: 0.90, TEAM SYNTRIX).
- **Audio / Voiceover (Energetic, Professional):**
  > *"Every monsoon, cities across Bharat come to a devastating standstill. From Mumbai's Mithi River basin to Bengaluru's Outer Ring Road, urban flooding inflicts over ₹8,000 Crores in direct physical and economic destruction each year.*  
  > *Meteorological data, satellite elevation models, and disaster policies exist—but they are completely trapped in disconnected silos. Decision-makers receive warnings hours after water has already entered critical infrastructure.*  
  > *We are Team Syntrix, and this is **AEGIS-CLIMATE**—the first autonomous, multi-agent environmental and financial intelligence platform engineered for Bharat."*

---

### SCENE 2: Command Center & Interactive GIS (0:25 – 0:50)
- **Visual:** Cursor selects **"Mumbai — Mithi River & Kurla Basin"** from the Bharat Climate Hotspots drawer. The Leaflet map smoothly flies to `19.0728°N, 72.8797°E`.
- **Action:** Mouse hovers over the red High-Velocity Inundation Basin polygon (`#D62828`), clicks a critical asset pin (Kurla Traction Substation), displaying the popup: *Water Depth: 95cm • Status: SEVERE*.
- **Voiceover:**
  > *"AEGIS operates through a high-performance mission-control cockpit. Here in our center pane, we see real-time GIS layers rendered on CartoDB Dark Matter tiles:*  
  > *Red marks the high-velocity inundation basin, orange highlights the secondary perimeter, and cyan traces municipal stormwater drainage conduits.*  
  > *When we inspect individual pins, AEGIS identifies critical substations and transit junctions exposed to catastrophic failure."*

---

### SCENE 3: The Autonomous 3-Agent Cascade in Action (0:50 – 1:30)
- **Visual:** Focus shifts to the left **What-If Climate Sandbox**.
- **Action:** Drag the **Rainfall Cloudburst** slider to **+110 mm** and **Soil Saturation** to **94%**. Click the glowing button: **"Trigger Multi-Agent Cascade"**.
- **Action:** The live **Agent Execution Monologue** terminal at the bottom-right begins streaming:
  - `[ACUTE] REASON & PREDICT: GradientBoostingClassifier evaluated risk: 0.92 (CRITICAL).`
  - `[ACUTE] DECISION: Risk > 0.65 threshold breached. Triggered autonomous cascade to Agent 2.`
  - `[CHRONIC] GEO_COMPUTATION: 30m DEM elevation pooling modeled depth: 88cm. Drainage overflow: 84.5%.`
  - `[FINANCIAL] VAR SIMULATION: Value at Risk: ₹1,180 Cr ($142.5M). ChromaDB retrieved SEBI BRSR & NDMA SOPs.`
- **Voiceover:**
  > *"Watch what happens when an extreme climate anomaly strikes. We stress-test the system by simulating a cloudburst of plus 110 millimeters and 94% soil saturation.*  
  > *Notice that this is NOT a passive chatbot. This is a fully autonomous cascade:*  
  > *First, **Agent 1** ingests live telemetry and executes our operational Gradient Boosting ML model in under 20 milliseconds, detecting a 92% critical flood probability.*  
  > *Because risk exceeds the 0.65 threshold, Agent 1 autonomously awakens **Agent 2** without human intervention.*  
  > *Agent 2 executes 30-meter DEM elevation pooling, computes municipal drainage overcapacity, and applies HAZUS depth-damage curves.*  
  > *Detecting infrastructure failure, Agent 2 triggers **Agent 3**, which queries our ChromaDB regulatory vector store and models a 4-factor Value-at-Risk of ₹1,180 Crores."*

---

### SCENE 4: Bhasha-AI Voice Dispatch & Executive C-Suite Briefing (1:30 – 1:55)
- **Visual:** Cursor moves to the **Bhasha-AI Civic Broadcast** card. Click the **"Audio Readout"** button. The browser synthesizes Hindi speech clearly.
- **Audio / Voiceover:**
  > *(Audio playback heard: "ऐजिस-भारत चेतावनी | स्तर: अति-गंभीर... मीठी नदी और कुर्ला बेसिन में...")*  
  > *"Through our proprietary **Bhasha-AI engine**, alerts are instantly synthesized in vernacular Indian languages like Hindi and English for emergency field teams.*  
  > *Next, for corporate leadership and NDMA officials, we click **'Export C-Suite Briefing'**.*  
- **Action:** Modal opens with the official confidential risk matrix. Click **"Print / Save as PDF"** or **"Standalone Print View"** showing the clean, formatted A4 PDF briefing ready for boardroom decision-makers.  
  > *"In a single click, executives receive an audit-ready PDF briefing detailing direct asset damage, SEBI BRSR compliance gaps, and actionable parametric hedging directives."*

---

### SCENE 5: Architecture & Production Readiness (1:55 – 2:20)
- **Visual:** Brief screen-share transition to the terminal showing all 5 test suites passing (`ALL 5 TEST SUITES PASSED 100%!`), followed by `agent_manifest.yaml` and `mcp_hub/hub.py`.
- **Voiceover:**
  > *"Under the hood, AEGIS-CLIMATE is built with rigorous engineering standards:*  
  > *All agent tool calls are coordinated through an asynchronous **Model Context Protocol (MCP) Hub** over JSON-RPC 2.0.*  
  > *Our ML flood classifier is trained on 3,500 samples achieving **95.14% accuracy** and a **0.90 Macro F1 score**.*  
  > *The entire platform is fully compliant with aiKart Method 1 specifications, complete with an official `agent_manifest.yaml` and multi-service Docker Compose architecture.*  
  > *Every single unit, integration, and end-to-end test suite passes at 100%."*

---

### SCENE 6: Conclusion & Closing Vision (2:20 – 2:30)
- **Visual:** Return to full-screen view of the glowing AEGIS-CLIMATE cockpit with all agents in `COMPLETE` state and live map pulsing.
- **Voiceover (Inspiring, Confident):**
  > *"AEGIS-CLIMATE transforms unpredictable climate volatility into transparent, anticipatory intelligence.*  
  > *Built by Team Syntrix for BHARAT AGENTIC 2026. Ready to protect Bharat's citizens and economy today. Thank you!"*

---

## 📋 Pre-Recording Checklist for the Presenter
- [ ] Run backend: `py -3.12 -m uvicorn backend.app.main:app --port 8000`
- [ ] Run MCP hub: `py -3.12 mcp_hub/hub.py`
- [ ] Run frontend: `cd frontend && npm run dev`
- [ ] Open browser at `http://localhost:5173` or `http://localhost:3000` in full-screen (`F11`).
- [ ] Ensure browser audio output is enabled so the Bhasha-AI voice synthesis is captured clearly.
- [ ] Have the terminal with `py -3.12 -c "..."` ready in a side window for the 15-second code snippet.
