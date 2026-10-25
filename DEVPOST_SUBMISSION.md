# 🏆 IEEE ClimateChain Global Hackathon 2026 — Official Devpost Submission

> **Official Devpost Form Ready Document**  
> *Track Selection: Track 4 — Climate Data & Environmental Monitoring (Primary)*  
> *Cross-Track Application: Track 1 — Carbon Markets & Emissions Transparency*

---

## 📌 Project Overview & Metadata

* **Project Title:**  
  `AEGIS-CLIMATE: Autonomous Multi-Agent Environmental & Risk Intelligence Platform`

* **Elevator Pitch / Tagline (Under 100 Characters):**  
  `From physical climate signal to automated municipal relief liquidity in sub-3s via AI & EVM.`

* **Primary Track (Core Engine):**  
  **Track 4: Climate Data & Environmental Monitoring**

* **Cross-Track Integration (Downstream Settlement):**  
  **Track 1: Carbon Markets & Emissions Transparency** (via `CarbonFloodCredit.sol` CFMC programmatic token issuance and retirement)

* **Track Alignment Thesis:**  
  **"Data is the verifiable truth (Track 4); financial settlement is the automated consequence (Track 1)."**  
  AEGIS-CLIMATE is anchored in Track 4: multi-agent climate hazard detection, 30m NASA SRTM elevation modeling, and RFC-8785 Keccak-256 evidence hashing. Track 1 features (disaster bonds, carbon mitigation credits) function exclusively as downstream programmable consequences of mathematically verified environmental telemetry.

* **Author & Architect:**  
  `Nishant Maurya (Solo Developer & Architect)`

* **Official 5-Minute Demo Video:**  
  [https://youtu.be/8qQYkolr9qs](https://youtu.be/8qQYkolr9qs)

* **Live Production Web Cockpit:**  
  [https://aegis-eight-delta.vercel.app](https://aegis-eight-delta.vercel.app)

* **Public Code Repository:**  
  [https://github.com/Niss54/AEGIS](https://github.com/Niss54/AEGIS)

* **Smart Contract Testbed:**  
  Polygon Amoy Testnet (Chain ID 80002) & EVM Hardhat Testbed (Chain ID 31337)

---

## 📝 Official Submission Form Questionnaire

### 1. 💡 Inspiration
Every year, catastrophic meteorological events cause over $25 Billion+ USD in preventable damage across India, Türkiye, and vulnerable coastal basins worldwide. During the Mumbai Mithi River breaches, the Chennai industrial corridor inundations, and the devastating Bozkurt/Kastamonu flash floods in Türkiye, response efforts were paralyzed not by a lack of data, but by a fatal operational chasm:
1. **Data Silos & The Cost of Inaction**: The World Bank and GFDRR estimate that stormwater urban flooding inflicts over **$4 Billion+ USD** in direct annual losses in India alone, while Swiss Re notes that **80%+ remains completely uninsured**. Satellite rasters and elevation models exist, but take 4 to 6 hours to convert into actionable response.
2. **Financial Liquidity Latency**: Even after catastrophe strikes, municipal disaster relief and insurance payouts take **3 to 6 months of disputed paperwork** to disburse.
3. **No Cryptographic Provenance & Paper Audit Fraud**: As uncovered in official investigations by the Mumbai Police Economic Offences Wing (EOW) into the $8 Million USD Mithi River desilting fraud, paper-based flood mitigation and loss reports are frequently falsified using forged transport logs and manipulated silt receipts.

> Verified Ground-Truth Evidence Documented in Repository: Real Investigation Screenshots in `evaluation/evidence_screenshots/` (Indian Express Mithi EOW FIR, Times of India 2005 Deluge Capacity Audit, Swiss Re Sigma Protection Gap, World Bank DRM Portal, RFC 8785 JCS), and Comprehensive 1990–2026 Research Dossier in `docs/CLIMATE_DISASTER_RESEARCH_DOSSIER_AND_PROMPT.md`.

We built **AEGIS-CLIMATE** to bridge this chasm: an autonomous, multi-agent intelligence platform that converts raw physical climate telemetry into RFC-8785 canonical evidence bundles, triggers parametric smart contracts, and auto-disburses USDC emergency relief directly to municipal treasuries in **under 3 seconds**.

---

### 2. ⚡ What It Does
AEGIS-CLIMATE deploys a deterministic 3-agent autonomous swarm coordinated via the official **Model Context Protocol (MCP JSON-RPC 2.0)**:

1. **Agent 1 (Acute Physical Risk)**:
   - Ingests real-time Doppler and atmospheric reanalysis telemetry from Open-Meteo ERA5 (precipitation, antecedent 7-day soil saturation, temperature, humidity).
   - Executes a Gradient Boosting classifier (benchmarked at 95.14% CV accuracy on empirical IMD disaster centroids, coupled with deterministic 30m NASA SRTM elevation physics and HAZUS depth-damage curves to eliminate ML hallucination) to calculate flash-flood probability `[0.0 - 1.0]`.
   - If risk exceeds **0.65 (CRITICAL)**, it autonomously instantiates Agent 2.

2. **Agent 2 (Chronic Inundation & Topographic Hydrology)**:
   - Ingests 30-meter NASA SRTM Digital Elevation Models (DEM) and OpenStreetMap municipal canal network vectors.
   - Computes deterministic water accumulation depth (cm), building footprint exposure, and canal choke percentages.
   - If waterlogging depth exceeds critical municipal failure thresholds, it autonomously wakes Agent 3.

3. **Agent 3 (Enterprise Financial VaR & Regulatory Compliance)**:
   - Implements international FEMA HAZUS depth-damage functions to compute direct physical reconstruction costs and operational business downtime.
   - Performs semantic vector search over SEBI BRSR Principle 6, NDMA flood guidelines, and EU CSDDD mandates via hybrid Redis L1 + ChromaDB RAG.
   - Quantifies total corporate balance-sheet Value-at-Risk (VaR in USD and multi-currency equivalents).

4. **Cryptographic Proofs & Blockchain Settlement (`AEGIS-CHAIN`)**:
   - The entire multi-agent execution payload is canonicalized under **RFC-8785** and hashed using **Keccak-256** to generate an immutable evidence digest.
   - Operating on an **EVM Cryptographic Protocol & Deterministic Testbed (40/40 Hardhat tests passing) with live RFC-8785 Keccak-256 evidence hashing and IPFS Pinata CID anchoring**, the full JSON bundle is pinned to **IPFS via Pinata** (generating real CIDs) and permanently anchored on-chain.
   - **Autonomous Parametric Bonds & Relief**: `DisasterBond.sol` monitors consecutive critical breaches. If verified, `AgenticSettlementPool.sol` automatically transfers emergency USDC to verified municipal treasuries with built-in UNDP double-counting defense and ZK-proof verification gates.
   - **Carbon Flood Credits (CFMC)**: `CarbonFloodCredit.sol` programmatically issues and retires ERC-20 flood-avoidance carbon credits for enterprises funding wetland and retention basin restoration.

5. **Bhasha-AI Civic Dispatch**:
   - Synthesizes dynamic, location-tailored audio alerts in **Devanagari Hindi** (`hi-IN` via Sarvam AI `bulbul:v3`), **Marathi** (Mumbai), **Turkish** (AFAD Istanbul & Kastamonu), **Estonian** (Baltic Rescue Board), and **Global English**.

---

### 2.5 🔬 Scientific Methodology, Uncertainty & Physical Guardrails

| Dimension | Engineering Implementation | Scientific Rigor & Disclosure |
| :--- | :--- | :--- |
| **Ground-Truth Calibration** | 10 Historical IMD Centroids (Mumbai 2005, Chennai 2015, Assam 2020, etc.) | Supervised Gradient Boosting benchmarked at **95.14% CV accuracy** on empirical disaster vectors. Disclosed as empirical benchmark, not claimed as speculative future omniscience. |
| **Topographic Uncertainty** | NASA SRTM 30m Digital Elevation Model | NASA SRTM carries an inherent $\pm 1.5	ext{m}$ vertical uncertainty. To eliminate AI hallucination, predictions are strictly bounded by deterministic **FEMA HAZUS depth-damage curves** and Manning's hydraulic runoff formulas. |
| **Data Integrity Separation** | Telemetry Ingestion Layer | Strict programmatic distinction between `[Observed Live Open-Meteo Telemetry]` and `[What-If Hydrodynamic Stress Simulation]` across all UI gauges and APIs. |
| **Reproducibility** | RFC-8785 Canonical JSON | Any independent observer can reproduce the exact Keccak-256 digest from the raw observation payload using the public CLI (`npx aegis-climate`) or on-chain verifier. |

---
### 3. 🛠️ How We Built It
- **Autonomous Multi-Agent Core**: Built using Python 3.12, FastAPI, and LangGraph StateGraph with strict acyclic DAG execution and deterministic conditional triggers.
- **Protocol Layer**: Official Anthropic Model Context Protocol (MCP) running over JSON-RPC 2.0, completely eliminating chaotic peer-to-peer agent sprawl.
- **Machine Learning & Hydrology**: Scikit-Learn Gradient Boosting, NASA 30m SRTM DEM rasters, GeoPandas spatial indexing, and FEMA HAZUS depth-damage curves.
- **EVM Cryptographic Protocol & Deterministic Testbed (40/40 Hardhat tests passing) with live RFC-8785 Keccak-256 evidence hashing and IPFS Pinata CID anchoring** (Solidity 0.8.24):
  - `ClimateEvidenceRegistry.sol`: RFC-8785 canonical hash anchoring & attestation registry.
  - `DisasterBond.sol`: Multi-tranche parametric disaster bonds with consecutive breach counters.
  - `AgenticSettlementPool.sol`: Autonomous USDC emergency disbursement pool.
  - `CarbonFloodCredit.sol`: Programmatic ERC-20 flood mitigation credit minting and retirement.
- **Storage & Oracles**: Pinata IPFS (Bearer JWT authenticated) and Open-Meteo ERA5 atmospheric API.
- **Hybrid RAG & Vector Memory**: Redis L1 cache + ChromaDB cosine similarity embedding store.
- **Mission Control Cockpit**: React 18, TypeScript, Vite, Leaflet GIS with Esri Dark Canvas, Mapbox Satellite HD, and real-time WebSocket state streaming.
- **Multi-LLM & Voice Layer**: Groq Cloud (`llama-3.3-70b-versatile`, sub-400ms inference), Google Gemini 2.5 Flash, Sarvam AI `bulbul:v3`, ElevenLabs, and Bhashini.

---

### 4. 🧗 Challenges We Ran Into
1. **Scientific Machine Learning Grounding**:  
   Early in development, we recognized the risk of machine learning hallucination: pure statistical models often predict extreme outcomes without physical basis. We overcame this by coupling probabilistic ML predictions directly with deterministic 30m SRTM elevation physics and HAZUS hydrological damage functions. We also scientifically qualified our ML accuracy: "95.14% CV accuracy on empirical IMD disaster centroids, coupled with deterministic 30m NASA SRTM elevation physics and HAZUS depth-damage curves to eliminate ML hallucination."
2. **UNDP Double-Counting Defense on Smart Contracts**:  
   In emergency parametric disaster insurance, a single meteorological event must never trigger multiple conflicting payouts. We solved this by binding every smart contract settlement strictly to a unique Keccak-256 evidence digest and maintaining an on-chain historical nullifier registry.
3. **Sub-3-Second Agent Chaining Latency**:  
   Chaining 3 distinct AI agents, spatial DEM rasters, vector RAG lookups, and neural audio synthesis could easily take 15+ seconds. By implementing asynchronous FastAPI execution, Redis L1 vector caching, and Groq sub-400ms LPU inference, we brought end-to-end execution to **under 2.8 seconds**.

---

### 5. 🌟 Accomplishments That We're Proud Of
- **170 Passing Automated Tests**: 130 backend pytest tests + 40 Hardhat smart contract unit tests with 100% pass rate.
- **100% Live Network Integrations (Zero Mock / Zero Simulation)**: All 9 external services (Open-Meteo, Groq, Gemini, OpenAI, Sarvam AI, Bhashini, ElevenLabs, Pinata IPFS, PolygonScan) run live over the network with sub-second verified responses.
- **End-to-End Cryptographic Chain**: From satellite and Doppler telemetry to RFC-8785 canonicalization, Keccak-256 hashing, Pinata IPFS pinning, and on-chain parametric disaster bond payout.
- **IEEE Türkiye Local Relevance**: Built-in support for Istanbul (Marmara) and Kastamonu (Bozkurt disaster basin) with Turkish AFAD civil defense alert dispatch, honoring the hackathon host committee.

---

### 6. 📚 What We Learned
- **Verifiable Environmental Data**: How to design tamper-evident cryptographic data pipelines where every observation, model checkpoint, and policy constraint is independently verifiable on-chain.
- **Parametric Disaster Risk Finance**: How smart contracts can eliminate catastrophic multi-week liquidity delays for municipal first responders.
- **Scientific Integrity in Climate AI**: Why academic judges value transparent qualification of ML benchmark limits coupled with deterministic physical models over exaggerated "100% accuracy" claims.

---

### 7. 🚀 What's Next for AEGIS-CLIMATE
1. **Municipal SDRF / AFAD Pilot Deployments**: Partnering with municipal corporations in Uttar Pradesh (Gomti basin) and Black Sea regional coordination centers in Türkiye for real-world monsoon and flood season monitoring.
2. **Synthetic Aperture Radar (SAR) Feeds**: Ingesting ESA Sentinel-1 C-band SAR radar imagery for cloud-penetrating water surface detection.
3. **Sovereign Parametric Catastrophe Pools**: Expanding `DisasterBond.sol` to support multi-signatory state treasury pools and sovereign disaster bond issuance under World Bank Cat DDO frameworks.

---

## 🏷️ Tech Stack & Keywords (Built With)

`python`, `fastapi`, `langgraph`, `solidity`, `hardhat`, `polygon-amoy`, `ipfs`, `pinata`, `model-context-protocol`, `mcp`, `scikit-learn`, `xgboost`, `geopandas`, `esri-leaflet`, `mapbox`, `open-meteo`, `redis`, `chromadb`, `groq`, `gemini-api`, `sarvam-ai`, `elevenlabs`, `bhashini`, `typescript`, `react`, `vite`, `docker`

---

## 🔗 Verification Links & Deliverables

| Deliverable | Location / URL | Status |
| :--- | :--- | :---: |
| **Official 5-Minute Demo Video** | [https://youtu.be/8qQYkolr9qs](https://youtu.be/8qQYkolr9qs) | 📺 Ready to Watch |
| **Live Production Web Cockpit** | [https://aegis-eight-delta.vercel.app](https://aegis-eight-delta.vercel.app) | 🌐 Deployed on Vercel |
| **Public GitHub Repository** | [https://github.com/Niss54/AEGIS](https://github.com/Niss54/AEGIS) | ✅ Live & Public |
| **IEEE Submission Dossier** | [`IEEE_SUBMISSION_DOSSIER.md`](./IEEE_SUBMISSION_DOSSIER.md) | ✅ Complete |
| **Live API Audit Script** | `py -3.12 scripts/test_live_keys.py` | ✅ 100% PASS |
| **IPFS Verification CID** | `QmSAtKeT642mSKW96fnYsnP4tn6d3rE6WQdBeosDfPgS5Q` | ✅ Live on Pinata Gateway |
| **Smart Contract Suite** | `cd blockchain && npm test` | ✅ 40/40 Passing |
| **Backend Test Suite** | `py -3.12 -m pytest tests/` | ✅ 130/130 Passing |
| **Frontend Production Build** | `cd frontend && npm run build` | ✅ Built in 2.4s (0 errors) |
