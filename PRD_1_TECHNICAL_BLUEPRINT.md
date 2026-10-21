# 🛡️ AEGIS-CHAIN v2.0 — TECHNICAL PRODUCT REQUIREMENTS DOCUMENT
## IEEE ClimateChain Global Hackathon 2026 — Engineering Blueprint

**Document Version:** 2.0.0-FINAL  
**Team:** Syntrix (Nishant Maurya — Lead Architect)  
**Target Hackathon:** IEEE ClimateChain Global Hackathon 2026  
**Submission Deadline:** October 25, 2026 — 7:30 PM IST  
**Base Repo:** https://github.com/Niss54/AEGIS  
**Status:** PRD LOCKED — Implementation Ready

---

## TABLE OF CONTENTS

1. [Executive Technical Summary](#1-executive-technical-summary)
2. [Strategic Gap Analysis — Why We Must Add Blockchain](#2-strategic-gap-analysis)
3. [Full System Architecture v2.0](#3-full-system-architecture-v20)
4. [Blockchain Layer Design](#4-blockchain-layer-design)
5. [Smart Contract Specifications](#5-smart-contract-specifications)
6. [Updated MCP Hub v2.0 — New Blockchain Tools](#6-updated-mcp-hub-v20)
7. [Agent Upgrades — Blockchain Integration](#7-agent-upgrades)
8. [New API Endpoints](#8-new-api-endpoints)
9. [IPFS/Filecoin Storage Layer](#9-ipfsfilecoin-storage-layer)
10. [The Graph Subgraph Specification](#10-the-graph-subgraph-specification)
11. [Frontend Dashboard v2.0 — Blockchain UI](#11-frontend-dashboard-v20)
12. [Database Schema Updates](#12-database-schema-updates)
13. [Complete Tech Stack v2.0](#13-complete-tech-stack-v20)
14. [Testing Strategy](#14-testing-strategy)
15. [Implementation Timeline — 11 Days to Submission](#15-implementation-timeline)
16. [Deployment Guide](#16-deployment-guide)
17. [Security Threat Model](#17-security-threat-model)
18. [Performance Benchmarks & SLOs](#18-performance-benchmarks--slos)
19. [Environment Configuration v2.0](#19-environment-configuration-v20)
20. [Judging Criteria Technical Mapping](#20-judging-criteria-technical-mapping)

---

## 1. EXECUTIVE TECHNICAL SUMMARY

### 1.1 What AEGIS-CHAIN v2.0 Is

AEGIS-CHAIN v2.0 is the blockchain-augmented evolution of AEGIS-CLIMATE, transforming it from a pure AI multi-agent system into a **hybrid AI + Blockchain climate intelligence platform** — exactly what the IEEE ClimateChain hackathon demands.

**The Core Innovation:** We don't just add blockchain as a cosmetic layer. We make blockchain a **structural necessity** by solving a genuine data integrity problem: AI-generated climate risk assessments can be tampered with, disputed, or dismissed without provenance. By anchoring every Agent 1 risk score, every Agent 2 DEM analysis, and every Agent 3 VaR briefing onto Polygon Amoy testnet (and optionally Base Sepolia), we create **tamper-evident, auditable, immutable climate intelligence** that regulators, insurers, and financial institutions can trust.

### 1.2 Three Blockchain Pillars

| Pillar | Contract | Purpose |
|--------|----------|---------|
| **Immutable Risk Ledger** | `AEGISRiskLedger.sol` | Every Agent 1 flash-flood risk score > 0.0 is anchored on-chain |
| **Parametric Disaster Bond** | `DisasterBond.sol` | Smart contract auto-pays USDC when on-chain risk > threshold for N blocks |
| **Carbon Flood Credit** | `CarbonFloodCredit.sol` (ERC-20) | Cities earn CFMC tokens when Agent 2 predicts no damage despite high Agent 1 risk |

### 1.3 What We Retain from AEGIS v1.0

Everything. The 3-agent cascade, MCP Hub, LangGraph orchestration, XGBoost model, DEM analysis, ChromaDB RAG, Voice AI, WebSocket streaming, Dashboard — all retained. We **add** blockchain on top, not replace. This is a v2.0 EXTENSION, not a rewrite.

### 1.4 Competitive Differentiator vs All Competitors

```
Competitor          | Blockchain?  | AI Agents? | GIS? | VaR? | Voice? | Demo?
--------------------|--------------|------------|------|------|--------|-------
ClearCredit         | ✅ Base Sep. | ❌         | ✅   | ❌   | ❌     | ✅
CarbonLens          | 🟡 Scaffold  | ❌         | ❌   | ❌   | ❌     | ❌
ClimateLens         | ❌ SHA-256   | ❌         | ❌   | ❌   | ❌     | ✅
VERDANT-X           | 🟡 Sigs only | ❌         | ❌   | ❌   | ❌     | 🟡
AEGIS-CHAIN v2.0    | ✅ Polygon   | ✅ 3 Live  | ✅   | ✅   | ✅ Hi  | ✅
```

**AEGIS-CHAIN is the ONLY entry combining real AI agents + real blockchain + real GIS + real VaR + real voice.**

---

## 2. STRATEGIC GAP ANALYSIS

### 2.1 Current AEGIS v1.0 State (What We Have)

**Strengths:**
- 3 fully functional autonomous AI agents (tested, 10/10 MCP tests pass)
- Official MCP Hub over JSON-RPC 2.0
- LangGraph state graph orchestration
- XGBoost ML model at 95.14% cross-validation accuracy
- GeoPandas + 30m SRTM DEM geospatial analysis
- ChromaDB vector RAG for SEBI BRSR policy corpus
- Sarvam AI (Hindi) + ElevenLabs (English) voice dispatch
- Leaflet.js + Esri GIS interactive map
- FastAPI + PostgreSQL + Redis + Docker production stack
- What-If climate anomaly sandbox (rain slider +0mm to +200mm)

**Critical Gap:**
- **ZERO blockchain integration** — this is an IEEE Blockchain hackathon
- The hackathon judges are IEEE Blockchain Technical Committee members
- Without blockchain, we cannot win — however good our AI is

### 2.2 What the Hackathon Requires

From official DevPost judging criteria and tracks:

**Track 4 — Climate Data & Environmental Monitoring (Primary Architectural Core):**
> "Climate data verification platforms • tools for research and insights"
> KEY PHRASE: **VERIFICATION** — requires tamper-evidence = blockchain & RFC-8785 canonical hashes

**Track 1 — Carbon Markets & Emissions Transparency (Cross-Track Settlement):**  
> "Transparency, accountability" — programmatic carbon flood mitigation credits (CFMC) and parametric disaster bonds triggered by verified environmental data.
> Core Thesis: *"Data is the verifiable truth (Track 4); financial settlement is the automated consequence (Track 1)."*

**Judging Dimensions:**
1. Innovation & Creativity
2. Technical Complexity & Completeness
3. Real-World Impact
4. Alignment with ClimateChain tracks
5. Presentation & Demo Quality

### 2.3 The Gap → The Solution

```
GAP                                     →  SOLUTION
----------------------------------------------------------------------
AI outputs can be tampered with         →  Anchor every assessment on-chain
No carbon market integration            →  Carbon Flood Credit (CFMC) token
No financial product on blockchain      →  Parametric Disaster Bond contract
Climate data lacks provenance           →  IPFS CIDs anchored on-chain
No public audit trail                   →  The Graph indexer + public explorer
Judges don't believe the demo is real   →  Live Polygon Amoy txn explorer links
```

### 2.4 Gap Analysis by Hackathon Track Coverage

| Track | v1.0 Coverage | v2.0 Coverage |
|-------|--------------|--------------|
| Carbon Markets & Emissions Transparency | 20% (VaR mentions carbon penalties) | 85% (CFMC token, carbon bond) |
| Climate Data & Environmental Monitoring | 90% (AI agents, GIS) | 100% (on-chain verified data) |
| Climate Resilience & Adaptation | 80% (flood risk, VaR) | 95% (parametric bond, alerts) |
| Data Integrity & Accountability | 30% (RAG provenance) | 100% (on-chain immutable ledger) |
| AI & Blockchain Innovations | 60% (AI only) | 100% (AI + Blockchain fused) |
| Renewable Energy & Grid Solutions | 10% (mentions energy) | 35% (grid resilience module) |

---

## 3. FULL SYSTEM ARCHITECTURE v2.0

### 3.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AEGIS-CHAIN v2.0 SYSTEM ARCHITECTURE                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│              NEXT.JS 14 / VITE-REACT COCKPIT v2             │
│  (Leaflet GIS · Radial Gauges · Blockchain Explorer Panel)  │
│  (CFMC Token Balance · Bond Status · IPFS CID Viewer)       │
└──────────────────────────────┬───────────────────────────────┘
                               │ REST / WebSockets / ethers.js
                               ▼
┌──────────────────────────────────────────────────────────────┐
│               FASTAPI CORE ENGINE v2 (Port 8000)            │
│  (/api/v2/analyze · /api/v2/blockchain · /api/v2/ipfs)      │
│  (Auth, Validation, Orchestration, Tx Manager)              │
└──────────────────────────────┬───────────────────────────────┘
                               │ JSON-RPC 2.0
                               ▼
┌──────────────────────────────────────────────────────────────┐
│            MCP HUB GATEWAY v2 (Port 8001 & 8000)            │
│   (Climate Tools · Blockchain Tools · IPFS Tools)           │
└───────┬───────────────┬─────────────────┬────────────────────┘
        │               │                 │
        ▼               ▼                 ▼
┌──────────────┐ ┌──────────────┐ ┌─────────────────────────────┐
│   AGENT 1    │ │   AGENT 2    │ │          AGENT 3             │
│  ACUTE RISK  │ │  CHRONIC DEM │ │   MACRO VaR + CARBON         │
│  + CHAIN ⛓  │ │  + CHAIN ⛓  │ │   COMPLIANCE + CHAIN ⛓       │
└──────┬───────┘ └──────┬───────┘ └─────────────┬───────────────┘
       │                │                        │
       └────────────────┴────────────┬───────────┘
                                     │ web3.py / ethers
                                     ▼
┌──────────────────────────────────────────────────────────────┐
│              BLOCKCHAIN GATEWAY LAYER (NEW)                  │
│                                                              │
│  ┌────────────────────┐  ┌─────────────────────────────┐    │
│  │  Polygon Amoy      │  │  IPFS / Filecoin Layer       │    │
│  │  Testnet           │  │  (Climate Data Storage)      │    │
│  │                    │  │                              │    │
│  │ AEGISRiskLedger    │  │ • GeoJSON Polygons → CID    │    │
│  │ DisasterBond       │  │ • DEM Rasters → CID         │    │
│  │ CarbonFloodCredit  │  │ • VaR Briefings → CID       │    │
│  └────────────────────┘  └─────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  The Graph — Subgraph Indexer (Public Explorer)     │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│                    DATA LAYER (UNCHANGED)                    │
│  PostgreSQL 16 + PostGIS · Redis 7.2 · ChromaDB             │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 Data Flow with Blockchain Integration

```
sequenceDiagram
  actor Officer as Disaster Officer / CFO
  participant UI as Mission Cockpit v2
  participant API as FastAPI v2
  participant MCP as MCP Hub v2
  participant A1 as Agent 1 (Acute + Chain)
  participant A2 as Agent 2 (Chronic + Chain)
  participant A3 as Agent 3 (VaR + Carbon)
  participant BC as Polygon Amoy Blockchain
  participant IPFS as IPFS/Filecoin
  participant TG as The Graph

  Officer->>UI: Analyze(lat=19.07, lon=72.87, rain=50mm)
  UI->>API: POST /api/v2/analyze
  API->>MCP: fetch_weather_vectors(lat, lon)
  API->>MCP: run_flood_classifier(vectors)
  MCP-->>A1: Risk Score = 0.78 (CRITICAL)
  
  A1->>IPFS: store_climate_report(json_payload) → CID
  A1->>BC: AEGISRiskLedger.anchorAssessment(lat, lon, score, cid, timestamp)
  BC-->>A1: txHash = 0xabc123...
  
  Note over A1,A2: Score > 0.65 — cascade triggers
  
  API->>MCP: compute_dem_exposure(lat, lon, 0.78)
  MCP-->>A2: depth=68cm, structures=321
  A2->>IPFS: store_dem_analysis(geojson, metadata) → CID2
  A2->>BC: AEGISRiskLedger.anchorDEMAnalysis(lat, lon, depth, cid2)
  BC-->>A2: txHash2 = 0xdef456...
  
  Note over A2,A3: Infrastructure Failure tier — cascade triggers
  
  API->>MCP: query_policy_rag(query)
  MCP-->>A3: VaR=₹3450Cr, Carbon Penalty=₹240Cr
  A3->>BC: CarbonFloodCredit.assessMitigation(lat, lon, risk_score, dem_depth)
  BC-->>A3: No CFMC earned (active emergency)
  A3->>BC: DisasterBond.checkTrigger(lat, lon) 
  BC-->>A3: Bond triggered! Payout: USDC 50,000
  A3->>IPFS: store_var_briefing(pdf_bytes) → CID3
  A3->>BC: AEGISRiskLedger.anchorVaR(var_inr, var_usd, cid3)
  BC-->>A3: txHash3 = 0xghi789...

  API-->>UI: Complete Assessment (with txHashes + CIDs)
  UI-->>Officer: Dashboard + Chain Explorer Panel + IPFS Links
  TG-->>UI: Real-time on-chain event stream
```

---

## 4. BLOCKCHAIN LAYER DESIGN

### 4.1 Network Choice: Polygon Amoy Testnet

**Why Polygon Amoy (not Ethereum Sepolia or Base Sepolia):**
1. Low gas fees — critical for frequent agent calls (every 15 minutes)
2. EVM-compatible — Solidity, Hardhat, ethers.js all work unchanged
3. Free testnet MATIC from Polygon faucet
4. Polygon Mumbai → Polygon Amoy is the current official testnet (2024+)
5. Production Polygon PoS is used by major climate protocols (Toucan Protocol, KlimaDAO)

**Chain Configuration:**
```
Network Name: Polygon Amoy Testnet
Chain ID: 80002
RPC URL: https://rpc-amoy.polygon.technology
Block Explorer: https://amoy.polygonscan.com
Currency: MATIC (testnet)
Faucet: https://faucet.polygon.technology
```

### 4.2 Blockchain Directory Structure (New)

```
AEGIS/
├── blockchain/                    ← NEW: entire blockchain layer
│   ├── contracts/
│   │   ├── AEGISRiskLedger.sol   ← Core risk anchoring contract
│   │   ├── DisasterBond.sol      ← Parametric insurance contract
│   │   ├── CarbonFloodCredit.sol ← ERC-20 CFMC token
│   │   └── interfaces/
│   │       ├── IAEGISRiskLedger.sol
│   │       └── IDisasterBond.sol
│   ├── scripts/
│   │   ├── deploy.ts             ← Hardhat deploy script
│   │   ├── seed_demo.ts          ← Seed demo data for submission
│   │   └── verify.ts             ← Verify on PolygonScan
│   ├── test/
│   │   ├── AEGISRiskLedger.test.ts
│   │   ├── DisasterBond.test.ts
│   │   └── CarbonFloodCredit.test.ts
│   ├── deployments/
│   │   └── amoy.json             ← Deployed contract addresses
│   ├── hardhat.config.ts
│   ├── package.json
│   └── tsconfig.json
├── backend/
│   └── app/
│       ├── blockchain/            ← NEW: blockchain integration module
│       │   ├── __init__.py
│       │   ├── chain_client.py   ← web3.py client
│       │   ├── risk_anchor.py    ← AEGISRiskLedger interface
│       │   ├── bond_manager.py   ← DisasterBond interface
│       │   └── cfmc_manager.py   ← CarbonFloodCredit interface
│       └── ipfs/                  ← NEW: IPFS integration
│           ├── __init__.py
│           └── storage.py        ← Pinata/Web3.Storage client
└── subgraph/                      ← NEW: The Graph subgraph
    ├── schema.graphql
    ├── subgraph.yaml
    └── src/
        └── mapping.ts
```

### 4.3 Blockchain Integration Architecture Principles

**Principle 1: Non-Blocking Integration**
Blockchain transactions are fire-and-forget async. Agent assessments NEVER wait for block confirmation before returning results to the UI. The UI shows a "pending" blockchain indicator that updates via WebSocket when the tx confirms.

**Principle 2: IPFS-First, Chain-Second**
Large data (GeoJSON, PDFs, DEM rasters) goes to IPFS. Only the CID hash (32 bytes) is stored on-chain. This keeps gas costs minimal.

**Principle 3: Graceful Degradation**
If the blockchain is unavailable (RPC down, gas estimation fails), the system logs the failure and continues normally. The assessment is still delivered. A retry queue processes failed anchoring attempts.

**Principle 4: Idempotency**
Each assessment has a deterministic `assessmentId = keccak256(lat, lon, timestamp_bucket)`. If the same assessment is submitted twice, the contract ignores the duplicate. Zero duplicate transactions.

---

## 5. SMART CONTRACT SPECIFICATIONS

### 5.1 Contract 1: AEGISRiskLedger.sol

**Purpose:** Immutable on-chain ledger of all AI-generated climate risk assessments. Every Agent 1, Agent 2, and Agent 3 output gets anchored here with its IPFS CID.

**File:** `blockchain/contracts/AEGISRiskLedger.sol`

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";

/**
 * @title AEGISRiskLedger
 * @notice Immutable on-chain ledger for AEGIS-CLIMATE multi-agent risk assessments.
 * @dev Deployed on Polygon Amoy Testnet for IEEE ClimateChain Hackathon 2026.
 *      Each climate risk assessment from the 3 autonomous AI agents is anchored
 *      here with its IPFS CID, creating tamper-evident climate intelligence.
 */
contract AEGISRiskLedger is Ownable {

    // ─── STRUCTS ────────────────────────────────────────────────────────────

    struct RiskAssessment {
        bytes32  assessmentId;      // keccak256(lat_scaled, lon_scaled, timestamp_bucket)
        int256   latScaled;         // latitude × 1e6 (no floats on-chain)
        int256   lonScaled;         // longitude × 1e6
        uint256  riskScoreBps;      // risk score in basis points (0–10000) = 0.0–1.0
        uint8    riskTier;          // 0=LOW, 1=MEDIUM, 2=HIGH, 3=CRITICAL
        bytes32  ipfsCid;           // IPFS CID of the full assessment JSON (32-byte truncated)
        string   ipfsCidFull;       // Full IPFS CID string (CIDv1)
        uint256  timestamp;         // Block timestamp of anchoring
        address  anchoredBy;        // AEGIS backend wallet address
        bool     demTriggered;      // Did Agent 2 cascade trigger?
        bool     varTriggered;      // Did Agent 3 cascade trigger?
        uint256  demDepthCm;        // Agent 2: waterlogging depth in cm (0 if not triggered)
        uint256  varInrLakhs;       // Agent 3: VaR in Indian Rupees (lakhs)
        string   locationName;      // Human-readable location name
    }

    struct ChainEvent {
        bytes32  assessmentId;
        uint8    eventType;         // 1=ANCHOR, 2=DEM_CASCADE, 3=VAR_CASCADE, 4=BOND_TRIGGER
        uint256  timestamp;
        bytes    data;              // ABI-encoded event-specific data
    }

    // ─── STATE VARIABLES ────────────────────────────────────────────────────

    mapping(bytes32 => RiskAssessment) public assessments;
    mapping(bytes32 => bool) public assessmentExists;
    bytes32[] public assessmentIds;   // ordered list for pagination

    mapping(int256 => mapping(int256 => bytes32[])) public locationHistory;
    // lat_scaled => lon_scaled => assessmentId[]

    uint256 public constant PRECISION = 1e6;     // 6 decimal places for lat/lon
    uint256 public constant CRITICAL_THRESHOLD_BPS = 6500;  // 0.65 = 65%
    uint256 public constant HIGH_THRESHOLD_BPS = 4000;      // 0.40 = 40%
    uint256 public constant MEDIUM_THRESHOLD_BPS = 2000;    // 0.20 = 20%

    uint256 public totalAssessments;
    uint256 public criticalAlerts;
    address public aegisBackend;      // Authorized AEGIS backend wallet

    // ─── EVENTS ─────────────────────────────────────────────────────────────

    event RiskAssessmentAnchored(
        bytes32 indexed assessmentId,
        int256 indexed latScaled,
        int256 indexed lonScaled,
        uint256 riskScoreBps,
        uint8 riskTier,
        string ipfsCidFull,
        uint256 timestamp,
        string locationName
    );

    event DEMCascadeAnchored(
        bytes32 indexed assessmentId,
        uint256 demDepthCm,
        uint256 exposedStructures,
        string ipfsCidFull
    );

    event VaRCascadeAnchored(
        bytes32 indexed assessmentId,
        uint256 varInrLakhs,
        uint256 varUsdCents,
        uint256 carbonPenaltyInrLakhs,
        string ipfsCidFull
    );

    event CriticalAlertEmitted(
        bytes32 indexed assessmentId,
        string locationName,
        uint256 riskScoreBps,
        uint256 timestamp
    );

    event BackendUpdated(address indexed oldBackend, address indexed newBackend);

    // ─── MODIFIERS ───────────────────────────────────────────────────────────

    modifier onlyBackend() {
        require(
            msg.sender == aegisBackend || msg.sender == owner(),
            "AEGISRiskLedger: caller is not authorized AEGIS backend"
        );
        _;
    }

    modifier assessmentMustExist(bytes32 assessmentId) {
        require(assessmentExists[assessmentId], "AEGISRiskLedger: assessment not found");
        _;
    }

    // ─── CONSTRUCTOR ────────────────────────────────────────────────────────

    constructor(address _aegisBackend) Ownable(msg.sender) {
        require(_aegisBackend != address(0), "AEGISRiskLedger: zero address");
        aegisBackend = _aegisBackend;
        emit BackendUpdated(address(0), _aegisBackend);
    }

    // ─── CORE FUNCTIONS ──────────────────────────────────────────────────────

    /**
     * @notice Anchors an Agent 1 (Acute Risk) assessment on-chain.
     * @dev Called by AEGIS backend for every risk assessment, regardless of score.
     * @param latScaled  latitude × 1e6 (e.g., 19.0728 → 19072800)
     * @param lonScaled  longitude × 1e6 (e.g., 72.8797 → 72879700)
     * @param riskScoreBps  risk score in basis points (0–10000)
     * @param ipfsCidFull  Full CIDv1 IPFS content identifier
     * @param locationName  Human-readable location (e.g., "Mumbai — Mithi River Basin")
     * @return assessmentId  The deterministic ID for this assessment
     */
    function anchorRiskAssessment(
        int256 latScaled,
        int256 lonScaled,
        uint256 riskScoreBps,
        string calldata ipfsCidFull,
        string calldata locationName
    ) external onlyBackend returns (bytes32 assessmentId) {
        require(riskScoreBps <= 10000, "AEGISRiskLedger: score exceeds max BPS");
        require(bytes(ipfsCidFull).length > 0, "AEGISRiskLedger: empty IPFS CID");

        // Deterministic ID: keccak256(lat, lon, timestamp bucket of 15 minutes)
        uint256 timeBucket = (block.timestamp / 900) * 900;
        assessmentId = keccak256(abi.encodePacked(latScaled, lonScaled, timeBucket));

        if (assessmentExists[assessmentId]) {
            // Idempotency: same assessment in same 15-min window → ignore
            return assessmentId;
        }

        uint8 tier = _computeRiskTier(riskScoreBps);
        bytes32 cidBytes = _cidToBytes32(ipfsCidFull);

        RiskAssessment storage assessment = assessments[assessmentId];
        assessment.assessmentId = assessmentId;
        assessment.latScaled = latScaled;
        assessment.lonScaled = lonScaled;
        assessment.riskScoreBps = riskScoreBps;
        assessment.riskTier = tier;
        assessment.ipfsCid = cidBytes;
        assessment.ipfsCidFull = ipfsCidFull;
        assessment.timestamp = block.timestamp;
        assessment.anchoredBy = msg.sender;
        assessment.locationName = locationName;

        assessmentExists[assessmentId] = true;
        assessmentIds.push(assessmentId);
        locationHistory[latScaled][lonScaled].push(assessmentId);
        totalAssessments++;

        if (tier == 3) {
            criticalAlerts++;
            emit CriticalAlertEmitted(assessmentId, locationName, riskScoreBps, block.timestamp);
        }

        emit RiskAssessmentAnchored(
            assessmentId, latScaled, lonScaled, riskScoreBps, tier,
            ipfsCidFull, block.timestamp, locationName
        );

        return assessmentId;
    }

    /**
     * @notice Anchors Agent 2 (Chronic DEM) cascade result on-chain.
     * @dev Only callable if the parent assessment exists and score was above CRITICAL_THRESHOLD.
     */
    function anchorDEMCascade(
        bytes32 assessmentId,
        uint256 demDepthCm,
        uint256 exposedStructures,
        uint256 drainageChokePct,
        string calldata ipfsCidFull
    ) external onlyBackend assessmentMustExist(assessmentId) {
        RiskAssessment storage assessment = assessments[assessmentId];
        require(
            assessment.riskScoreBps >= CRITICAL_THRESHOLD_BPS,
            "AEGISRiskLedger: DEM cascade requires CRITICAL risk tier"
        );
        require(!assessment.demTriggered, "AEGISRiskLedger: DEM already anchored");

        assessment.demTriggered = true;
        assessment.demDepthCm = demDepthCm;

        emit DEMCascadeAnchored(assessmentId, demDepthCm, exposedStructures, ipfsCidFull);
    }

    /**
     * @notice Anchors Agent 3 (Macro VaR) cascade result on-chain.
     * @dev Only callable if Agent 2 cascade was already anchored.
     */
    function anchorVaRCascade(
        bytes32 assessmentId,
        uint256 varInrLakhs,
        uint256 varUsdCents,
        uint256 carbonPenaltyInrLakhs,
        uint256 strandedAssetRiskBps,
        string calldata ipfsCidFull
    ) external onlyBackend assessmentMustExist(assessmentId) {
        RiskAssessment storage assessment = assessments[assessmentId];
        require(assessment.demTriggered, "AEGISRiskLedger: DEM cascade must precede VaR");
        require(!assessment.varTriggered, "AEGISRiskLedger: VaR already anchored");

        assessment.varTriggered = true;
        assessment.varInrLakhs = varInrLakhs;

        emit VaRCascadeAnchored(assessmentId, varInrLakhs, varUsdCents, carbonPenaltyInrLakhs, ipfsCidFull);
    }

    // ─── VIEW FUNCTIONS ──────────────────────────────────────────────────────

    function getAssessment(bytes32 assessmentId)
        external view returns (RiskAssessment memory)
    {
        return assessments[assessmentId];
    }

    function getLocationHistory(int256 latScaled, int256 lonScaled)
        external view returns (bytes32[] memory)
    {
        return locationHistory[latScaled][lonScaled];
    }

    function getRecentAssessments(uint256 count)
        external view returns (bytes32[] memory ids)
    {
        uint256 total = assessmentIds.length;
        uint256 n = count > total ? total : count;
        ids = new bytes32[](n);
        for (uint256 i = 0; i < n; i++) {
            ids[i] = assessmentIds[total - 1 - i];
        }
    }

    function getStats() external view returns (
        uint256 _totalAssessments,
        uint256 _criticalAlerts
    ) {
        return (totalAssessments, criticalAlerts);
    }

    // ─── ADMIN FUNCTIONS ─────────────────────────────────────────────────────

    function setBackend(address newBackend) external onlyOwner {
        require(newBackend != address(0), "AEGISRiskLedger: zero address");
        emit BackendUpdated(aegisBackend, newBackend);
        aegisBackend = newBackend;
    }

    // ─── INTERNAL HELPERS ────────────────────────────────────────────────────

    function _computeRiskTier(uint256 scoreBps) internal pure returns (uint8) {
        if (scoreBps >= CRITICAL_THRESHOLD_BPS) return 3;  // CRITICAL
        if (scoreBps >= HIGH_THRESHOLD_BPS)     return 2;  // HIGH
        if (scoreBps >= MEDIUM_THRESHOLD_BPS)   return 1;  // MEDIUM
        return 0;                                           // LOW
    }

    function _cidToBytes32(string memory cid) internal pure returns (bytes32) {
        bytes memory cidBytes = bytes(cid);
        bytes32 result;
        assembly { result := mload(add(cidBytes, 32)) }
        return result;
    }
}
```

---

### 5.2 Contract 2: DisasterBond.sol

**Purpose:** Parametric climate insurance smart contract. Pre-funded with testnet USDC. Automatically pays beneficiaries when the AEGIS risk ledger shows CRITICAL alerts for a registered location for N consecutive assessments.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title DisasterBond
 * @notice Parametric disaster insurance smart contract.
 * @dev Pays out automatically when AEGISRiskLedger records CRITICAL
 *      tier for a covered location, triggered by the AEGIS backend.
 *      Uses testnet USDC for hackathon demo purposes.
 */
contract DisasterBond is Ownable {

    // ─── STRUCTS ────────────────────────────────────────────────────────────

    struct Bond {
        bytes32  bondId;
        int256   latScaled;
        int256   lonScaled;
        address  beneficiary;         // Who receives the payout
        uint256  payoutAmount;        // In USDC (6 decimals)
        uint256  triggerThresholdBps; // Risk score BPS that triggers payout
        uint256  consecutiveRequired; // Number of consecutive CRITICAL assessments needed
        uint256  consecutiveCount;    // Current count
        bool     active;
        bool     triggered;
        uint256  createdAt;
        uint256  triggeredAt;
        bytes32  triggeringAssessmentId;  // Which AEGIS assessment triggered the bond
        string   locationName;
    }

    // ─── STATE ───────────────────────────────────────────────────────────────

    IERC20 public immutable usdc;
    address public aegisLedger;
    address public aegisBackend;

    mapping(bytes32 => Bond) public bonds;
    mapping(int256 => mapping(int256 => bytes32[])) public locationBonds;
    bytes32[] public allBondIds;

    uint256 public totalPayouts;
    uint256 public activeBondsCount;

    // ─── EVENTS ─────────────────────────────────────────────────────────────

    event BondCreated(
        bytes32 indexed bondId,
        int256 latScaled,
        int256 lonScaled,
        address indexed beneficiary,
        uint256 payoutAmount,
        string locationName
    );

    event BondTriggered(
        bytes32 indexed bondId,
        address indexed beneficiary,
        uint256 payoutAmount,
        bytes32 indexed triggeringAssessmentId,
        uint256 timestamp
    );

    event ConsecutiveThresholdUpdated(
        bytes32 indexed bondId,
        uint256 consecutiveCount,
        uint256 consecutiveRequired
    );

    // ─── CONSTRUCTOR ────────────────────────────────────────────────────────

    constructor(
        address _usdc,
        address _aegisLedger,
        address _aegisBackend
    ) Ownable(msg.sender) {
        usdc = IERC20(_usdc);
        aegisLedger = _aegisLedger;
        aegisBackend = _aegisBackend;
    }

    // ─── BOND MANAGEMENT ─────────────────────────────────────────────────────

    /**
     * @notice Creates a new parametric disaster bond for a location.
     * @dev Owner (AEGIS platform) creates bonds for registered beneficiaries.
     *      Requires prior USDC approval for payoutAmount.
     */
    function createBond(
        int256 latScaled,
        int256 lonScaled,
        address beneficiary,
        uint256 payoutAmount,
        uint256 triggerThresholdBps,
        uint256 consecutiveRequired,
        string calldata locationName
    ) external onlyOwner returns (bytes32 bondId) {
        require(beneficiary != address(0), "DisasterBond: zero beneficiary");
        require(payoutAmount > 0, "DisasterBond: zero payout");
        require(triggerThresholdBps <= 10000, "DisasterBond: invalid threshold");
        require(consecutiveRequired >= 1, "DisasterBond: min 1 consecutive");

        bondId = keccak256(abi.encodePacked(
            latScaled, lonScaled, beneficiary, block.timestamp
        ));

        // Escrow the payout amount from owner
        require(
            usdc.transferFrom(msg.sender, address(this), payoutAmount),
            "DisasterBond: USDC transfer failed"
        );

        Bond storage bond = bonds[bondId];
        bond.bondId = bondId;
        bond.latScaled = latScaled;
        bond.lonScaled = lonScaled;
        bond.beneficiary = beneficiary;
        bond.payoutAmount = payoutAmount;
        bond.triggerThresholdBps = triggerThresholdBps;
        bond.consecutiveRequired = consecutiveRequired;
        bond.active = true;
        bond.createdAt = block.timestamp;
        bond.locationName = locationName;

        allBondIds.push(bondId);
        locationBonds[latScaled][lonScaled].push(bondId);
        activeBondsCount++;

        emit BondCreated(bondId, latScaled, lonScaled, beneficiary, payoutAmount, locationName);
        return bondId;
    }

    /**
     * @notice Called by AEGIS backend when a new critical assessment is anchored.
     * @dev Increments consecutive counter; pays out if threshold is met.
     * @param latScaled    latitude × 1e6 of the assessed location
     * @param lonScaled    longitude × 1e6 of the assessed location
     * @param riskScoreBps the agent's risk score in basis points
     * @param assessmentId the ID from AEGISRiskLedger
     */
    function notifyAssessment(
        int256 latScaled,
        int256 lonScaled,
        uint256 riskScoreBps,
        bytes32 assessmentId
    ) external {
        require(
            msg.sender == aegisBackend || msg.sender == owner(),
            "DisasterBond: unauthorized"
        );

        bytes32[] storage bondIds = locationBonds[latScaled][lonScaled];
        for (uint256 i = 0; i < bondIds.length; i++) {
            Bond storage bond = bonds[bondIds[i]];
            if (!bond.active || bond.triggered) continue;

            if (riskScoreBps >= bond.triggerThresholdBps) {
                bond.consecutiveCount++;
                emit ConsecutiveThresholdUpdated(
                    bond.bondId,
                    bond.consecutiveCount,
                    bond.consecutiveRequired
                );

                if (bond.consecutiveCount >= bond.consecutiveRequired) {
                    _executePayout(bond, assessmentId);
                }
            } else {
                // Risk dropped below threshold — reset consecutive counter
                bond.consecutiveCount = 0;
            }
        }
    }

    // ─── INTERNAL ────────────────────────────────────────────────────────────

    function _executePayout(Bond storage bond, bytes32 assessmentId) internal {
        bond.triggered = true;
        bond.active = false;
        bond.triggeredAt = block.timestamp;
        bond.triggeringAssessmentId = assessmentId;
        activeBondsCount--;
        totalPayouts += bond.payoutAmount;

        require(
            usdc.transfer(bond.beneficiary, bond.payoutAmount),
            "DisasterBond: payout transfer failed"
        );

        emit BondTriggered(
            bond.bondId,
            bond.beneficiary,
            bond.payoutAmount,
            assessmentId,
            block.timestamp
        );
    }

    // ─── VIEW FUNCTIONS ──────────────────────────────────────────────────────

    function getBond(bytes32 bondId) external view returns (Bond memory) {
        return bonds[bondId];
    }

    function getLocationBonds(int256 latScaled, int256 lonScaled)
        external view returns (bytes32[] memory)
    {
        return locationBonds[latScaled][lonScaled];
    }

    function getContractBalance() external view returns (uint256) {
        return usdc.balanceOf(address(this));
    }
}
```

---

### 5.3 Contract 3: CarbonFloodCredit.sol (ERC-20 CFMC Token)

**Purpose:** ERC-20 token representing Carbon Flood Mitigation Credits. Municipalities/infrastructure managers earn CFMC when their area demonstrates successful flood mitigation (Agent 2 DEM predicts low damage despite Agent 1 high risk score). These CFMC tokens can be traded or retired as climate offsets.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title CarbonFloodCredit
 * @notice ERC-20 token representing Carbon Flood Mitigation Credits (CFMC).
 * @dev Minted when AEGIS Agent 2 detects effective flood mitigation:
 *      - Agent 1 risk score >= 0.65 (CRITICAL) but
 *      - Agent 2 DEM depth < LOW_DAMAGE_THRESHOLD (e.g., <20cm)
 *      This indicates the infrastructure successfully mitigated a predicted flood.
 *
 *      1 CFMC = 1 tonne CO2-equivalent of flood-damage-avoidance credit
 */
contract CarbonFloodCredit is ERC20, Ownable {

    uint256 public constant MITIGATION_REWARD = 100 * 1e18;    // 100 CFMC per mitigation event
    uint256 public constant CRITICAL_RISK_BPS = 6500;          // 0.65
    uint256 public constant LOW_DAMAGE_DEPTH_CM = 20;          // <20cm = successful mitigation

    address public aegisBackend;
    uint256 public totalMitigationEvents;
    uint256 public totalCFMCMinted;

    mapping(address => uint256) public mitigationCount;         // beneficiary => count
    mapping(bytes32 => bool) public mitigationRecorded;         // assessmentId => recorded

    event MitigationCreditIssued(
        address indexed beneficiary,
        uint256 amount,
        bytes32 indexed assessmentId,
        int256 latScaled,
        int256 lonScaled,
        uint256 riskScoreBps,
        uint256 demDepthCm
    );

    event CFMCRetired(address indexed holder, uint256 amount, string reason);

    constructor(address _aegisBackend)
        ERC20("Carbon Flood Mitigation Credit", "CFMC")
        Ownable(msg.sender)
    {
        aegisBackend = _aegisBackend;
    }

    /**
     * @notice Mint CFMC to a beneficiary when flood mitigation is detected.
     * @dev Agent 2 reports successful mitigation when:
     *      - Agent 1 riskScoreBps >= CRITICAL_RISK_BPS (high risk detected)
     *      - Agent 2 demDepthCm < LOW_DAMAGE_DEPTH_CM (minimal actual damage)
     *      This demonstrates effective infrastructure prevented flood damage.
     */
    function issueMitigationCredit(
        address beneficiary,
        bytes32 assessmentId,
        int256 latScaled,
        int256 lonScaled,
        uint256 riskScoreBps,
        uint256 demDepthCm
    ) external returns (bool) {
        require(
            msg.sender == aegisBackend || msg.sender == owner(),
            "CarbonFloodCredit: unauthorized"
        );
        require(!mitigationRecorded[assessmentId], "CarbonFloodCredit: already recorded");
        require(beneficiary != address(0), "CarbonFloodCredit: zero beneficiary");
        require(riskScoreBps >= CRITICAL_RISK_BPS, "CarbonFloodCredit: risk not critical");
        require(demDepthCm < LOW_DAMAGE_DEPTH_CM, "CarbonFloodCredit: damage not low enough");

        mitigationRecorded[assessmentId] = true;
        mitigationCount[beneficiary]++;
        totalMitigationEvents++;
        totalCFMCMinted += MITIGATION_REWARD;

        _mint(beneficiary, MITIGATION_REWARD);

        emit MitigationCreditIssued(
            beneficiary, MITIGATION_REWARD, assessmentId,
            latScaled, lonScaled, riskScoreBps, demDepthCm
        );

        return true;
    }

    /**
     * @notice Burn CFMC tokens to retire them as climate offsets.
     */
    function retireCredits(uint256 amount, string calldata reason) external {
        require(amount > 0, "CarbonFloodCredit: zero amount");
        _burn(msg.sender, amount);
        emit CFMCRetired(msg.sender, amount, reason);
    }

    function setBackend(address newBackend) external onlyOwner {
        aegisBackend = newBackend;
    }
}
```

---

### 5.4 Hardhat Configuration

**File:** `blockchain/hardhat.config.ts`

```typescript
import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import "@openzeppelin/hardhat-upgrades";
import * as dotenv from "dotenv";

dotenv.config({ path: "../.env" });

const DEPLOYER_PRIVATE_KEY = process.env.BLOCKCHAIN_DEPLOYER_KEY || "";
const POLYGONSCAN_API_KEY = process.env.POLYGONSCAN_API_KEY || "";

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.24",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  networks: {
    hardhat: {
      chainId: 31337,
    },
    polygonAmoy: {
      url: "https://rpc-amoy.polygon.technology",
      chainId: 80002,
      accounts: [DEPLOYER_PRIVATE_KEY],
      gasPrice: "auto",
    },
  },
  etherscan: {
    apiKey: {
      polygonAmoy: POLYGONSCAN_API_KEY,
    },
    customChains: [
      {
        network: "polygonAmoy",
        chainId: 80002,
        urls: {
          apiURL: "https://api-amoy.polygonscan.com/api",
          browserURL: "https://amoy.polygonscan.com",
        },
      },
    ],
  },
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts",
  },
};

export default config;
```

---

### 5.5 Deployment Script

**File:** `blockchain/scripts/deploy.ts`

```typescript
import { ethers } from "hardhat";
import * as fs from "fs";

async function main() {
  const [deployer] = await ethers.getSigners();
  const network = await ethers.provider.getNetwork();

  console.log("┌─────────────────────────────────────────┐");
  console.log("│  AEGIS-CHAIN v2.0 — Contract Deployment  │");
  console.log("└─────────────────────────────────────────┘");
  console.log(`Network: ${network.name} (chainId: ${network.chainId})`);
  console.log(`Deployer: ${deployer.address}`);
  console.log(`Balance: ${ethers.formatEther(await ethers.provider.getBalance(deployer.address))} MATIC`);
  console.log("");

  // Deploy Mock USDC for testnet
  console.log("1. Deploying Mock USDC (testnet only)...");
  const MockUSDC = await ethers.getContractFactory("MockERC20");
  const usdc = await MockUSDC.deploy("USD Coin", "USDC", 6);
  await usdc.waitForDeployment();
  const usdcAddress = await usdc.getAddress();
  console.log(`   ✅ Mock USDC deployed at: ${usdcAddress}`);

  // Deploy AEGISRiskLedger
  console.log("2. Deploying AEGISRiskLedger...");
  const BACKEND_WALLET = process.env.AEGIS_BACKEND_WALLET || deployer.address;
  const AEGISRiskLedger = await ethers.getContractFactory("AEGISRiskLedger");
  const ledger = await AEGISRiskLedger.deploy(BACKEND_WALLET);
  await ledger.waitForDeployment();
  const ledgerAddress = await ledger.getAddress();
  console.log(`   ✅ AEGISRiskLedger deployed at: ${ledgerAddress}`);

  // Deploy DisasterBond
  console.log("3. Deploying DisasterBond...");
  const DisasterBond = await ethers.getContractFactory("DisasterBond");
  const bond = await DisasterBond.deploy(usdcAddress, ledgerAddress, BACKEND_WALLET);
  await bond.waitForDeployment();
  const bondAddress = await bond.getAddress();
  console.log(`   ✅ DisasterBond deployed at: ${bondAddress}`);

  // Deploy CarbonFloodCredit
  console.log("4. Deploying CarbonFloodCredit (CFMC Token)...");
  const CarbonFloodCredit = await ethers.getContractFactory("CarbonFloodCredit");
  const cfmc = await CarbonFloodCredit.deploy(BACKEND_WALLET);
  await cfmc.waitForDeployment();
  const cfmcAddress = await cfmc.getAddress();
  console.log(`   ✅ CarbonFloodCredit (CFMC) deployed at: ${cfmcAddress}`);

  // Seed Demo Data: Create bonds for Mumbai, Delhi, Chennai
  console.log("5. Seeding demo disaster bonds...");
  const DEMO_LOCATIONS = [
    { name: "Mumbai — Mithi River Basin", lat: 19072800, lon: 72879700 },
    { name: "Chennai — Adyar River Corridor", lat: 13082700, lon: 80270700 },
    { name: "Delhi — Yamuna Floodplain", lat: 28613900, lon: 77209100 },
  ];
  const DEMO_PAYOUT = ethers.parseUnits("50000", 6); // 50,000 USDC per bond
  const DEMO_BENEFICIARY = deployer.address; // Team wallet for demo

  await usdc.mint(deployer.address, DEMO_PAYOUT * BigInt(3)); // Mint USDC for 3 bonds
  await usdc.approve(bondAddress, DEMO_PAYOUT * BigInt(3));

  for (const loc of DEMO_LOCATIONS) {
    const tx = await bond.createBond(
      loc.lat, loc.lon, DEMO_BENEFICIARY,
      DEMO_PAYOUT,
      6500,   // trigger at 0.65 risk score
      2,      // 2 consecutive CRITICAL assessments
      loc.name
    );
    await tx.wait();
    console.log(`   ✅ Bond created for ${loc.name}`);
  }

  // Save deployments
  const deployments = {
    network: network.name,
    chainId: Number(network.chainId),
    deployer: deployer.address,
    timestamp: new Date().toISOString(),
    contracts: {
      MockUSDC: usdcAddress,
      AEGISRiskLedger: ledgerAddress,
      DisasterBond: bondAddress,
      CarbonFloodCredit: cfmcAddress,
    },
    explorer: `https://amoy.polygonscan.com/address/${ledgerAddress}`,
  };

  const outPath = `./deployments/${network.name}.json`;
  fs.writeFileSync(outPath, JSON.stringify(deployments, null, 2));
  console.log(`\n✅ Deployments saved to ${outPath}`);
  console.log("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log(`AEGISRiskLedger: ${ledgerAddress}`);
  console.log(`DisasterBond:    ${bondAddress}`);
  console.log(`CFMC Token:      ${cfmcAddress}`);
  console.log(`PolygonScan:     https://amoy.polygonscan.com/address/${ledgerAddress}`);
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```

---

## 6. UPDATED MCP HUB v2.0 — NEW BLOCKCHAIN TOOLS

### 6.1 New Blockchain MCP Tools

The MCP Hub registers 4 new tools in addition to the original 4 climate tools:

**File:** `mcp_hub/hub.py` — additions to existing tool registry

```python
# ─── BLOCKCHAIN MCP TOOLS (NEW in v2.0) ───────────────────────────────────────

BLOCKCHAIN_TOOL_SCHEMAS = {
    "anchor_risk_on_chain": {
        "name": "anchor_risk_on_chain",
        "description": (
            "Anchors an Agent 1 risk assessment on the Polygon Amoy blockchain "
            "via AEGISRiskLedger.sol. Creates an immutable, tamper-evident record "
            "of the AI's climate risk output. Returns the transaction hash and "
            "on-chain assessment ID."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "lat":           {"type": "number", "description": "Latitude"},
                "lon":           {"type": "number", "description": "Longitude"},
                "risk_score":    {"type": "number", "description": "Agent 1 score [0.0–1.0]"},
                "ipfs_cid":      {"type": "string", "description": "IPFS CIDv1 of full assessment"},
                "location_name": {"type": "string", "description": "Human-readable location"},
            },
            "required": ["lat", "lon", "risk_score", "ipfs_cid", "location_name"],
        },
        "target_agent": "blockchain-layer",
    },

    "store_on_ipfs": {
        "name": "store_on_ipfs",
        "description": (
            "Stores a climate assessment payload (JSON, GeoJSON, or PDF bytes) "
            "on IPFS via Pinata and returns the CIDv1 content identifier. "
            "This CID is then anchored on-chain for provenance."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "payload":       {"type": "object", "description": "JSON payload to store"},
                "content_type":  {"type": "string", "enum": ["json", "geojson", "pdf"], "default": "json"},
                "filename":      {"type": "string", "description": "Logical filename for the IPFS pin"},
            },
            "required": ["payload"],
        },
        "target_agent": "ipfs-layer",
    },

    "check_bond_trigger": {
        "name": "check_bond_trigger",
        "description": (
            "Checks DisasterBond.sol for active bonds at the given location and "
            "notifies the contract about the new risk assessment. If consecutive "
            "CRITICAL alerts meet the bond threshold, the contract auto-pays. "
            "Returns bond status and any triggered payouts."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "lat":           {"type": "number"},
                "lon":           {"type": "number"},
                "risk_score_bps": {"type": "integer", "description": "Score in BPS (0–10000)"},
                "assessment_id": {"type": "string",  "description": "On-chain assessment ID (bytes32)"},
            },
            "required": ["lat", "lon", "risk_score_bps", "assessment_id"],
        },
        "target_agent": "blockchain-layer",
    },

    "check_cfmc_eligibility": {
        "name": "check_cfmc_eligibility",
        "description": (
            "Checks whether a location is eligible for Carbon Flood Mitigation "
            "Credits (CFMC) based on Agent 1 (high risk detected) and Agent 2 "
            "(low DEM damage despite high risk). If eligible, mints CFMC tokens "
            "to the beneficiary address."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "lat":             {"type": "number"},
                "lon":             {"type": "number"},
                "risk_score":      {"type": "number", "description": "[0.0–1.0]"},
                "dem_depth_cm":    {"type": "number", "description": "Agent 2 DEM waterlogging depth"},
                "beneficiary":     {"type": "string", "description": "Ethereum address for CFMC reward"},
                "assessment_id":   {"type": "string"},
            },
            "required": ["lat", "lon", "risk_score", "dem_depth_cm", "beneficiary", "assessment_id"],
        },
        "target_agent": "blockchain-layer",
    },
}

# Total tool registry v2.0:
# Original: fetch_weather_vectors, run_flood_classifier, compute_dem_exposure, query_policy_rag
# New:      anchor_risk_on_chain, store_on_ipfs, check_bond_trigger, check_cfmc_eligibility
```

### 6.2 Updated tools/list Response

```json
{
  "jsonrpc": "2.0",
  "id": "list-1",
  "result": {
    "tools": [
      { "name": "fetch_weather_vectors",    "target_agent": "agent-1-acute"    },
      { "name": "run_flood_classifier",     "target_agent": "agent-1-acute"    },
      { "name": "compute_dem_exposure",     "target_agent": "agent-2-chronic"  },
      { "name": "query_policy_rag",         "target_agent": "agent-3-financial"},
      { "name": "anchor_risk_on_chain",     "target_agent": "blockchain-layer" },
      { "name": "store_on_ipfs",            "target_agent": "ipfs-layer"       },
      { "name": "check_bond_trigger",       "target_agent": "blockchain-layer" },
      { "name": "check_cfmc_eligibility",   "target_agent": "blockchain-layer" }
    ],
    "protocol_version": "2024-11-05",
    "server_version": "aegis-chain-v2.0.0"
  }
}
```

---

## 7. AGENT UPGRADES — BLOCKCHAIN INTEGRATION

### 7.1 Agent 1 (Acute Physical Risk) — Chain Anchoring Added

**New Step After Risk Classification:**

```python
# backend/app/agents/agent1_acute.py — ADDITIONS

async def execute_with_blockchain(
    self,
    lat: float,
    lon: float,
    risk_score: float,
    risk_tier: str,
    weather_vectors: dict,
    location_name: str,
) -> Agent1Result:
    """
    Extended Agent 1 execution with IPFS + blockchain anchoring.
    """
    # Step 1: Original risk assessment (unchanged)
    result = await self._run_flood_classifier(weather_vectors)

    # Step 2: Store assessment on IPFS (non-blocking)
    ipfs_payload = {
        "agent": "agent-1-acute",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "location": {"lat": lat, "lon": lon, "name": location_name},
        "risk_score": risk_score,
        "risk_tier": risk_tier,
        "weather_vectors": weather_vectors,
        "model": "GradientBoostingClassifier",
        "model_accuracy_cv": 0.9514,
        "trigger_threshold": 0.65,
        "dem_cascade_triggered": risk_score >= 0.65,
        "hackathon": "IEEE ClimateChain 2026",
        "track": "Climate Data & Environmental Monitoring",
    }

    # Fire-and-forget: do not await (non-blocking)
    asyncio.create_task(
        self._anchor_to_chain(lat, lon, risk_score, ipfs_payload, location_name)
    )

    return result

async def _anchor_to_chain(
    self,
    lat: float, lon: float,
    risk_score: float,
    ipfs_payload: dict,
    location_name: str,
):
    """Stores on IPFS then anchors CID on Polygon Amoy."""
    try:
        # 1. Store on IPFS via Pinata
        ipfs_result = await self.mcp_client.call_tool(
            "store_on_ipfs",
            payload=ipfs_payload,
            content_type="json",
            filename=f"aegis_agent1_{lat}_{lon}_{int(time.time())}.json"
        )
        cid = ipfs_result["cid"]

        # 2. Anchor CID on Polygon Amoy
        chain_result = await self.mcp_client.call_tool(
            "anchor_risk_on_chain",
            lat=lat, lon=lon,
            risk_score=risk_score,
            ipfs_cid=cid,
            location_name=location_name,
        )

        # 3. Emit WebSocket event with tx hash
        await self.ws_broadcaster.emit("chain_anchor", {
            "agent": "agent-1",
            "tx_hash": chain_result["tx_hash"],
            "assessment_id": chain_result["assessment_id"],
            "ipfs_cid": cid,
            "explorer_url": f"https://amoy.polygonscan.com/tx/{chain_result['tx_hash']}",
        })

        # 4. Check bond triggers
        if risk_score >= 0.65:
            await self.mcp_client.call_tool(
                "check_bond_trigger",
                lat=lat, lon=lon,
                risk_score_bps=int(risk_score * 10000),
                assessment_id=chain_result["assessment_id"],
            )

        logger.info(f"[Agent1] Anchored on chain: {chain_result['tx_hash']}")

    except Exception as e:
        logger.error(f"[Agent1] Blockchain anchoring failed (non-critical): {e}")
        # System continues normally — blockchain is augmentative, not blocking
```

### 7.2 Agent 3 (Macro VaR) — Carbon Credit Integration

```python
# backend/app/agents/agent3_financial.py — ADDITIONS

async def check_cfmc_eligibility(
    self,
    assessment_id: str,
    lat: float, lon: float,
    risk_score: float,
    dem_depth_cm: float,
):
    """
    After VaR calculation, check if CFMC tokens should be minted.
    Eligibility: High risk (>= 0.65) but low actual damage (<20cm).
    This rewards infrastructure that prevented the predicted damage.
    """
    if risk_score >= 0.65 and dem_depth_cm < 20:
        # Mitigation detected! Infrastructure performed better than predicted.
        cfmc_result = await self.mcp_client.call_tool(
            "check_cfmc_eligibility",
            lat=lat, lon=lon,
            risk_score=risk_score,
            dem_depth_cm=dem_depth_cm,
            beneficiary=self.config.DEMO_BENEFICIARY_ADDRESS,
            assessment_id=assessment_id,
        )
        logger.info(f"[Agent3] CFMC minted: {cfmc_result.get('tx_hash', 'N/A')}")
        return cfmc_result
    return None
```

---

## 8. NEW API ENDPOINTS

### 8.1 Blockchain Endpoints (v2.0)

```
POST   /api/v2/blockchain/anchor          Manually trigger on-chain anchoring
GET    /api/v2/blockchain/assessment/{id}  Get on-chain assessment data
GET    /api/v2/blockchain/location-history?lat=&lon=  Get history for a location
GET    /api/v2/blockchain/stats           Get chain stats (total assessments, alerts)
GET    /api/v2/blockchain/bonds?lat=&lon= Get disaster bonds for a location
GET    /api/v2/blockchain/cfmc/balance?address= Get CFMC token balance
POST   /api/v2/blockchain/cfmc/retire     Retire CFMC tokens
GET    /api/v2/blockchain/explorer-url/{tx_hash}  Get PolygonScan link
```

### 8.2 IPFS Endpoints (v2.0)

```
POST   /api/v2/ipfs/store                Store payload on IPFS, get CID
GET    /api/v2/ipfs/retrieve/{cid}       Retrieve content from IPFS by CID
GET    /api/v2/ipfs/verify/{cid}         Verify IPFS content hash integrity
```

### 8.3 Sample Blockchain API Response

```json
{
  "assessment_id": "0xa3f4b1c2d5e678901234567890abcdef1234567890abcdef1234567890abcdef12",
  "tx_hash": "0xabc123def456789012345678901234567890abcdef123456789012345678901234",
  "block_number": 12345678,
  "timestamp": 1729925400,
  "lat": 19.0728,
  "lon": 72.8797,
  "risk_score_bps": 7800,
  "risk_tier": "CRITICAL",
  "ipfs_cid": "bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi",
  "ipfs_url": "https://gateway.pinata.cloud/ipfs/bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi",
  "explorer_url": "https://amoy.polygonscan.com/tx/0xabc123...",
  "dem_triggered": true,
  "dem_depth_cm": 68,
  "var_triggered": true,
  "var_inr_lakhs": 345000,
  "bond_triggered": false,
  "cfmc_minted": false,
  "location_name": "Mumbai — Mithi River Basin"
}
```

---

## 9. IPFS/FILECOIN STORAGE LAYER

### 9.1 IPFS Integration Architecture

**Provider:** Pinata (free tier: 1GB pinned storage, 100GB bandwidth/month — sufficient for hackathon)

**What Gets Stored on IPFS:**

| Content | When Stored | Estimated Size |
|---------|-------------|----------------|
| Agent 1 Assessment JSON | Every analysis | ~3KB |
| Agent 2 GeoJSON Polygons | Every DEM cascade | ~50KB |
| Agent 2 DEM Raster (PNG) | Every DEM cascade | ~200KB |
| Agent 3 VaR Briefing HTML | Every VaR cascade | ~80KB |
| Full Analysis Dossier | Every complete run | ~350KB |

### 9.2 IPFS Client Implementation

**File:** `backend/app/ipfs/storage.py`

```python
"""IPFS storage layer via Pinata API for AEGIS-CHAIN v2.0."""
import asyncio
import json
import hashlib
from typing import Union
import aiohttp
from loguru import logger

PINATA_API_URL = "https://api.pinata.cloud"
IPFS_PUBLIC_GATEWAY = "https://gateway.pinata.cloud/ipfs"

class IPFSStorageClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.headers = {
            "pinata_api_key": api_key,
            "pinata_secret_api_key": api_secret,
        }

    async def pin_json(
        self,
        payload: dict,
        filename: str = "aegis_assessment.json"
    ) -> dict:
        """Pin a JSON payload to IPFS via Pinata."""
        async with aiohttp.ClientSession() as session:
            pin_body = {
                "pinataMetadata": {
                    "name": filename,
                    "keyvalues": {
                        "source": "AEGIS-CHAIN",
                        "version": "2.0.0",
                        "hackathon": "IEEE-ClimateChain-2026",
                    }
                },
                "pinataContent": payload,
            }
            async with session.post(
                f"{PINATA_API_URL}/pinning/pinJSONToIPFS",
                headers={**self.headers, "Content-Type": "application/json"},
                json=pin_body,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                cid = data["IpfsHash"]
                return {
                    "cid": cid,
                    "url": f"{IPFS_PUBLIC_GATEWAY}/{cid}",
                    "pin_size": data.get("PinSize", 0),
                }

    async def pin_file(self, file_bytes: bytes, filename: str) -> dict:
        """Pin raw bytes (PDF, PNG, GeoJSON) to IPFS."""
        import io
        import aiohttp
        form_data = aiohttp.FormData()
        form_data.add_field(
            "file", io.BytesIO(file_bytes),
            filename=filename, content_type="application/octet-stream"
        )
        form_data.add_field("pinataMetadata", json.dumps({
            "name": filename,
            "keyvalues": {"source": "AEGIS-CHAIN", "version": "2.0.0"},
        }))

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{PINATA_API_URL}/pinning/pinFileToIPFS",
                headers=self.headers,
                data=form_data,
                timeout=aiohttp.ClientTimeout(total=60),
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                cid = data["IpfsHash"]
                return {"cid": cid, "url": f"{IPFS_PUBLIC_GATEWAY}/{cid}"}

    def compute_local_hash(self, payload: dict) -> str:
        """Compute SHA-256 of the JSON payload for local verification."""
        serialized = json.dumps(payload, sort_keys=True).encode()
        return hashlib.sha256(serialized).hexdigest()
```

---

## 10. THE GRAPH SUBGRAPH SPECIFICATION

### 10.1 Schema

**File:** `subgraph/schema.graphql`

```graphql
type RiskAssessment @entity(immutable: true) {
  id: ID!                          # assessment ID (bytes32 hex)
  lat: BigInt!                     # latScaled (× 1e6)
  lon: BigInt!                     # lonScaled (× 1e6)
  riskScoreBps: BigInt!           # 0–10000
  riskTier: Int!                  # 0=LOW, 1=MED, 2=HIGH, 3=CRITICAL
  ipfsCidFull: String!            # Full CIDv1
  timestamp: BigInt!
  anchoredBy: Bytes!
  locationName: String!
  demTriggered: Boolean!
  varTriggered: Boolean!
  demDepthCm: BigInt
  varInrLakhs: BigInt
  blockNumber: BigInt!
  transactionHash: Bytes!
}

type DisasterBondEvent @entity(immutable: true) {
  id: ID!
  bondId: Bytes!
  eventType: String!             # CREATED | TRIGGERED | CONSECUTIVE_UPDATE
  beneficiary: Bytes
  payoutAmount: BigInt
  triggeringAssessmentId: Bytes
  timestamp: BigInt!
  transactionHash: Bytes!
}

type CFMCMintEvent @entity(immutable: true) {
  id: ID!
  beneficiary: Bytes!
  amount: BigInt!
  assessmentId: Bytes!
  riskScoreBps: BigInt!
  demDepthCm: BigInt!
  timestamp: BigInt!
  transactionHash: Bytes!
}

type LocationStats @entity {
  id: ID!                         # "{latScaled}_{lonScaled}"
  totalAssessments: BigInt!
  criticalCount: BigInt!
  lastRiskScore: BigInt!
  lastAssessmentTimestamp: BigInt!
}
```

---

## 11. FRONTEND DASHBOARD v2.0 — BLOCKCHAIN UI

### 11.1 New Frontend Components

**New Panel: Blockchain Activity Feed**

```typescript
// frontend/src/components/BlockchainPanel.tsx

interface BlockchainActivity {
  txHash: string;
  assessmentId: string;
  type: "ANCHOR" | "DEM_CASCADE" | "VAR_CASCADE" | "BOND_TRIGGER" | "CFMC_MINT";
  timestamp: number;
  ipfsCid: string;
  explorerUrl: string;
  bondPayout?: number;
  cfmcAmount?: number;
}

// Features:
// 1. Live transaction feed (WebSocket updates from backend)
// 2. Click-to-open PolygonScan explorer in new tab
// 3. IPFS content viewer (click CID → open in IPFS gateway)
// 4. Bond status indicator (ACTIVE / TRIGGERED / PAID)
// 5. CFMC token balance display
// 6. Assessment ID copy-to-clipboard
```

**New UI Sections in Dashboard:**

```
┌─────────────────────────────────────────────────────────────────────┐
│  EXISTING SECTIONS (UNCHANGED):                                     │
│  [1] GIS Map with Flood Polygons                                    │
│  [2] Agent Thought Trace Stream                                     │
│  [3] Risk Gauges (Radial)                                           │
│  [4] What-If Slider                                                 │
│  [5] VaR Financial Cards                                            │
│  [6] Voice Dispatch Player                                          │
├─────────────────────────────────────────────────────────────────────┤
│  NEW SECTIONS (v2.0):                                               │
│                                                                     │
│  [7] ⛓ BLOCKCHAIN LEDGER PANEL                                     │
│     ┌────────────────────────────────────────────────────────┐    │
│     │ Latest On-Chain Assessment                              │    │
│     │ Assessment ID: 0xa3f4b1...                             │    │
│     │ Tx Hash: 0xabc123... [Open in PolygonScan ↗]          │    │
│     │ Block: 12345678 | Time: 2 seconds ago                  │    │
│     │ IPFS CID: bafybei... [View on IPFS ↗]                  │    │
│     │ Status: ✅ CONFIRMED                                    │    │
│     └────────────────────────────────────────────────────────┘    │
│                                                                     │
│  [8] 💰 DISASTER BOND STATUS                                        │
│     Bond: Mumbai — Mithi River Basin                               │
│     Status: 🟡 ACTIVE | Trigger: 2/2 consecutive CRITICAL          │
│     Payout Amount: $50,000 USDC                                    │
│     Current Consecutive: [████████░░] 1/2                          │
│                                                                     │
│  [9] 🌱 CARBON FLOOD MITIGATION CREDITS                            │
│     Your CFMC Balance: 0 CFMC                                      │
│     Eligibility: ❌ (Active emergency — damage too high)            │
│     Earn by: Prevent flood damage despite high risk alerts         │
│                                                                     │
│  [10] 📊 CHAIN STATISTICS                                           │
│     Total Anchored: 127 assessments                                │
│     Critical Alerts: 12                                            │
│     Bonds Triggered: 1 ($50,000 paid out)                         │
│     CFMC Minted: 300 tokens                                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 12. DATABASE SCHEMA UPDATES

### 12.1 New PostgreSQL Tables

```sql
-- Blockchain transaction tracking
CREATE TABLE blockchain_transactions (
    id              SERIAL PRIMARY KEY,
    assessment_id   VARCHAR(66) NOT NULL,    -- bytes32 hex
    tx_hash         VARCHAR(66) NOT NULL,
    block_number    BIGINT,
    contract_name   VARCHAR(50) NOT NULL,    -- 'AEGISRiskLedger' | 'DisasterBond' | 'CarbonFloodCredit'
    method_name     VARCHAR(50) NOT NULL,
    status          VARCHAR(20) DEFAULT 'pending',  -- pending | confirmed | failed
    gas_used        BIGINT,
    created_at      TIMESTAMP DEFAULT NOW(),
    confirmed_at    TIMESTAMP,
    retry_count     INTEGER DEFAULT 0,
    error_message   TEXT,
    UNIQUE(tx_hash)
);

-- IPFS pin tracking
CREATE TABLE ipfs_pins (
    id              SERIAL PRIMARY KEY,
    cid             VARCHAR(100) NOT NULL UNIQUE,
    assessment_id   VARCHAR(66),
    content_type    VARCHAR(20) NOT NULL,   -- json | geojson | pdf | png
    pin_size_bytes  INTEGER,
    filename        VARCHAR(200),
    gateway_url     TEXT,
    pinned_at       TIMESTAMP DEFAULT NOW(),
    verified_at     TIMESTAMP
);

-- Disaster bond registry
CREATE TABLE disaster_bonds (
    id                  SERIAL PRIMARY KEY,
    bond_id_hex         VARCHAR(66) NOT NULL UNIQUE,
    lat                 DECIMAL(10, 6) NOT NULL,
    lon                 DECIMAL(10, 6) NOT NULL,
    location_name       VARCHAR(200),
    beneficiary_address VARCHAR(42),
    payout_usdc         BIGINT NOT NULL,        -- in USDC units (6 decimals)
    trigger_threshold   INTEGER NOT NULL,       -- BPS
    consecutive_req     INTEGER NOT NULL,
    consecutive_count   INTEGER DEFAULT 0,
    status              VARCHAR(20) DEFAULT 'active',  -- active | triggered | expired
    created_at          TIMESTAMP DEFAULT NOW(),
    triggered_at        TIMESTAMP,
    triggering_tx_hash  VARCHAR(66)
);

-- CFMC token events
CREATE TABLE cfmc_events (
    id              SERIAL PRIMARY KEY,
    event_type      VARCHAR(20) NOT NULL,  -- mint | retire
    beneficiary     VARCHAR(42) NOT NULL,
    amount_cfmc     BIGINT NOT NULL,
    assessment_id   VARCHAR(66),
    tx_hash         VARCHAR(66),
    timestamp       TIMESTAMP DEFAULT NOW()
);

-- Retry queue for failed blockchain txns
CREATE TABLE blockchain_retry_queue (
    id              SERIAL PRIMARY KEY,
    operation       JSONB NOT NULL,
    attempts        INTEGER DEFAULT 0,
    max_attempts    INTEGER DEFAULT 3,
    next_attempt_at TIMESTAMP DEFAULT NOW(),
    created_at      TIMESTAMP DEFAULT NOW(),
    error_log       TEXT
);
```

---

## 13. COMPLETE TECH STACK v2.0

| Layer | Technologies (v1.0) | Technologies Added (v2.0) |
|-------|---------------------|---------------------------|
| **Blockchain** | — | Solidity 0.8.24, Hardhat, OpenZeppelin 5.x, ethers.js 6.x, web3.py 7.x, Polygon Amoy Testnet |
| **Smart Contracts** | — | AEGISRiskLedger.sol, DisasterBond.sol, CarbonFloodCredit.sol (ERC-20) |
| **Storage** | PostgreSQL, Redis, ChromaDB | + IPFS/Filecoin via Pinata SDK |
| **Indexing** | — | The Graph Protocol (subgraph) |
| **Frontend** | React 18 + Vite, Leaflet, Recharts | + wagmi 2.x, ethers.js, RainbowKit (wallet connect) |
| **Agentic Core** | MCP Hub, LangGraph, LangChain | (unchanged — extended with 4 new tools) |
| **AI/ML** | Groq, Gemini, scikit-learn, XGBoost | (unchanged) |
| **Voice** | Sarvam AI, ElevenLabs | (unchanged) |
| **Backend** | FastAPI, Uvicorn, Pydantic v2 | + blockchain gateway module, IPFS module |
| **DevOps** | Docker, Docker Compose | + Hardhat CI, PolygonScan verification |

---

## 14. TESTING STRATEGY

### 14.1 Smart Contract Tests

**File:** `blockchain/test/AEGISRiskLedger.test.ts`

```typescript
import { expect } from "chai";
import { ethers } from "hardhat";

describe("AEGISRiskLedger", () => {
  let ledger: AEGISRiskLedger;
  let owner: HardhatEthersSigner;
  let backend: HardhatEthersSigner;
  let attacker: HardhatEthersSigner;

  before(async () => {
    [owner, backend, attacker] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory("AEGISRiskLedger");
    ledger = await Factory.deploy(backend.address);
  });

  describe("anchorRiskAssessment", () => {
    it("should anchor a valid risk assessment and emit event", async () => {
      const tx = await ledger.connect(backend).anchorRiskAssessment(
        19072800n,  // lat=19.0728
        72879700n,  // lon=72.8797
        7800n,       // 0.78 risk score
        "bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi",
        "Mumbai — Mithi River Basin"
      );
      const receipt = await tx.wait();
      const event = receipt?.logs.find(
        log => log.topics[0] === ledger.interface.getEvent("RiskAssessmentAnchored").topicHash
      );
      expect(event).to.not.be.undefined;
    });

    it("should assign CRITICAL tier when score >= 6500 BPS", async () => {
      // Get the assessment ID from the last anchor
      const ids = await ledger.getRecentAssessments(1);
      const assessment = await ledger.getAssessment(ids[0]);
      expect(assessment.riskTier).to.equal(3); // CRITICAL
    });

    it("should be idempotent within the same 15-minute window", async () => {
      const before = await ledger.totalAssessments();
      await ledger.connect(backend).anchorRiskAssessment(
        19072800n, 72879700n, 7800n,
        "bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi",
        "Mumbai — Mithi River Basin"
      );
      const after = await ledger.totalAssessments();
      expect(after).to.equal(before); // No new assessment — idempotent
    });

    it("should REJECT anchoring from unauthorized address", async () => {
      await expect(
        ledger.connect(attacker).anchorRiskAssessment(
          19072800n, 72879700n, 7800n, "bafybei...", "Mumbai"
        )
      ).to.be.revertedWith("AEGISRiskLedger: caller is not authorized");
    });

    it("should reject invalid risk score > 10000 BPS", async () => {
      await expect(
        ledger.connect(backend).anchorRiskAssessment(
          19072800n, 72879700n, 10001n, "bafybei...", "Mumbai"
        )
      ).to.be.revertedWith("AEGISRiskLedger: score exceeds max BPS");
    });

    it("should emit CriticalAlertEmitted for CRITICAL tier", async () => {
      await expect(
        ledger.connect(backend).anchorRiskAssessment(
          28613900n, 77209100n, 9500n, "bafybei...", "Delhi — Yamuna Floodplain"
        )
      ).to.emit(ledger, "CriticalAlertEmitted");
    });
  });

  describe("anchorDEMCascade", () => {
    it("should reject DEM cascade for non-critical assessment", async () => {
      // First anchor a LOW risk assessment
      await ledger.connect(backend).anchorRiskAssessment(
        13082700n, 80270700n, 1500n, "bafybei...", "Chennai — Low Risk Area"
      );
      const ids = await ledger.getRecentAssessments(1);
      await expect(
        ledger.connect(backend).anchorDEMCascade(
          ids[0], 30n, 100n, 45n, "bafybei..."
        )
      ).to.be.revertedWith("DEM cascade requires CRITICAL");
    });
  });

  describe("getLocationHistory", () => {
    it("should return assessment history for a coordinate", async () => {
      const history = await ledger.getLocationHistory(19072800n, 72879700n);
      expect(history.length).to.be.greaterThan(0);
    });
  });
});
```

### 14.2 Blockchain Integration Tests (Python)

**File:** `tests/test_blockchain_integration.py`

```python
"""Integration tests for AEGIS blockchain layer."""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from app.blockchain.chain_client import AEGISChainClient
from app.blockchain.risk_anchor import RiskAnchorService

class TestRiskAnchorService:
    @pytest.fixture
    def mock_chain_client(self):
        client = AsyncMock(spec=AEGISChainClient)
        client.anchor_assessment.return_value = {
            "tx_hash": "0xabc123...",
            "assessment_id": "0xdeadbeef...",
            "block_number": 12345678,
            "status": "pending"
        }
        return client

    @pytest.mark.asyncio
    async def test_anchor_does_not_block_analysis(self, mock_chain_client):
        """Blockchain anchoring must be non-blocking."""
        service = RiskAnchorService(chain_client=mock_chain_client)
        import time
        start = time.time()
        await service.anchor_non_blocking(
            lat=19.0728, lon=72.8797,
            risk_score=0.78,
            ipfs_cid="bafybei...",
            location_name="Mumbai"
        )
        elapsed = time.time() - start
        assert elapsed < 0.1, "Blockchain anchoring must not block the analysis"

    @pytest.mark.asyncio
    async def test_anchor_failure_does_not_crash_system(self, mock_chain_client):
        """System must continue if blockchain is unavailable."""
        mock_chain_client.anchor_assessment.side_effect = Exception("RPC unavailable")
        service = RiskAnchorService(chain_client=mock_chain_client)
        # Should not raise exception
        await service.anchor_non_blocking(
            lat=19.0728, lon=72.8797,
            risk_score=0.78,
            ipfs_cid="bafybei...",
            location_name="Mumbai"
        )
        # Verify retry queue was populated
        assert service.retry_queue.qsize() > 0

    @pytest.mark.asyncio
    async def test_bond_trigger_notification(self, mock_chain_client):
        """DisasterBond.notifyAssessment is called for CRITICAL assessments."""
        mock_chain_client.notify_bond.return_value = {"bonds_notified": 1}
        service = RiskAnchorService(chain_client=mock_chain_client)
        await service.process_critical_alert(
            lat=19.0728, lon=72.8797,
            risk_score_bps=7800,
            assessment_id="0xdeadbeef..."
        )
        mock_chain_client.notify_bond.assert_awaited_once()
```

---

## 15. IMPLEMENTATION TIMELINE — 11 DAYS TO SUBMISSION

**Deadline: October 25, 2026 at 7:30 PM IST**
**Today: October 14, 2026**
**Time Available: 11 days**

```
Day | Date    | Task                                             | Priority | Hours
----|---------|--------------------------------------------------|----------|------
1   | Oct 15  | Setup Hardhat + write AEGISRiskLedger.sol        | 🔴 CRIT  | 4h
1   | Oct 15  | Write DisasterBond.sol + CarbonFloodCredit.sol   | 🔴 CRIT  | 3h
2   | Oct 16  | Deploy contracts to Polygon Amoy Testnet         | 🔴 CRIT  | 2h
2   | Oct 16  | Verify contracts on PolygonScan                  | 🟡 HIGH  | 1h
2   | Oct 16  | Write Hardhat tests (aim: 100% coverage)          | 🔴 CRIT  | 4h
3   | Oct 17  | Implement blockchain/ Python module in backend   | 🔴 CRIT  | 5h
3   | Oct 17  | web3.py integration with AEGISRiskLedger         | 🔴 CRIT  | 3h
4   | Oct 18  | Implement IPFS/Pinata storage layer              | 🔴 CRIT  | 3h
4   | Oct 18  | Update MCP Hub with 4 new blockchain tools       | 🔴 CRIT  | 3h
4   | Oct 18  | Update Agent 1 to call blockchain post-analysis  | 🔴 CRIT  | 2h
5   | Oct 19  | Update Agent 3 to check CFMC eligibility         | 🟡 HIGH  | 2h
5   | Oct 19  | Add blockchain retry queue + error handling      | 🟡 HIGH  | 3h
5   | Oct 19  | Add new PostgreSQL tables + migrations           | 🟡 HIGH  | 2h
6   | Oct 20  | Frontend: BlockchainPanel.tsx component          | 🟡 HIGH  | 4h
6   | Oct 20  | Frontend: Bond Status Panel + CFMC Panel         | 🟡 HIGH  | 3h
6   | Oct 20  | Frontend: ethers.js integration for chain reads  | 🟡 HIGH  | 2h
7   | Oct 21  | Deploy The Graph subgraph (optional, if time)    | 🟢 MED   | 3h
7   | Oct 21  | Seed demo data: 3 bonds + 10 sample assessments  | 🟡 HIGH  | 2h
7   | Oct 21  | End-to-end integration tests                     | 🔴 CRIT  | 4h
8   | Oct 22  | Fix bugs from integration testing                | 🔴 CRIT  | 6h
8   | Oct 22  | Update Docker Compose to include blockchain env  | 🟡 HIGH  | 1h
9   | Oct 23  | Update README.md with blockchain docs            | 🟡 HIGH  | 3h
9   | Oct 23  | Record demo video (3-5 min walkthrough)          | 🔴 CRIT  | 3h
9   | Oct 23  | Polish dashboard + blockchain panel UI           | 🟡 HIGH  | 3h
10  | Oct 24  | Devpost submission draft                         | 🔴 CRIT  | 3h
10  | Oct 24  | Screenshots, diagrams for submission             | 🟡 HIGH  | 2h
10  | Oct 24  | Final testing + dry-run of demo                  | 🔴 CRIT  | 3h
11  | Oct 25  | Submit before 7:30 PM IST                        | 🔴 CRIT  | —
```

---

## 16. DEPLOYMENT GUIDE

### 16.1 Environment Setup

```bash
# 1. Install blockchain dependencies
cd blockchain
npm install

# 2. Set environment variables
cp ../.env.example ../.env
# Add to .env:
# BLOCKCHAIN_DEPLOYER_KEY=<your-polygon-amoy-private-key>
# AEGIS_BACKEND_WALLET=<your-backend-wallet-address>
# POLYGONSCAN_API_KEY=<from-polygonscan.com>
# PINATA_API_KEY=<from-pinata.cloud>
# PINATA_API_SECRET=<from-pinata.cloud>
# POLYGON_AMOY_RPC=https://rpc-amoy.polygon.technology

# 3. Get testnet MATIC
# Visit: https://faucet.polygon.technology
# Select: Polygon Amoy, enter your deployer wallet address

# 4. Run Hardhat tests locally first
npx hardhat test

# 5. Deploy to Polygon Amoy
npx hardhat run scripts/deploy.ts --network polygonAmoy

# 6. Verify on PolygonScan
npx hardhat verify --network polygonAmoy <CONTRACT_ADDRESS> <CONSTRUCTOR_ARGS>

# 7. Seed demo data
npx hardhat run scripts/seed_demo.ts --network polygonAmoy

# 8. Update backend .env with deployed contract addresses
# (auto-populated from deployments/polygonAmoy.json)

# 9. Run full stack
docker compose up -d  # starts PostgreSQL, Redis, ChromaDB
cd backend && uvicorn app.main:app --port 8000 --reload
cd mcp_hub && uvicorn hub:app --port 8001 --reload
cd frontend && npm run dev
```

### 16.2 Verifying Deployment

```bash
# Verify AEGISRiskLedger is responding
curl -X POST "http://127.0.0.1:8000/api/v2/blockchain/stats"
# Expected: {"total_assessments": 0, "critical_alerts": 0}

# Run a full analysis (triggers blockchain anchoring)
curl -X POST "http://127.0.0.1:8000/api/v2/analyze" \
  -H "Content-Type: application/json" \
  -d '{"lat": 19.0728, "lon": 72.8797, "location_name": "Mumbai", "simulated_additional_rain_mm": 50}'

# Check blockchain panel for live tx hash
# Visit: https://amoy.polygonscan.com/address/<AEGIS_RISK_LEDGER_ADDRESS>
```

---

## 17. SECURITY THREAT MODEL

### 17.1 On-Chain Security

| Threat | Mitigation |
|--------|-----------|
| Unauthorized risk anchoring | `onlyBackend` modifier on all write functions |
| Replay attacks | Idempotency via deterministic assessmentId (15-min buckets) |
| Integer overflow | Solidity 0.8.x checked math + basis points (no floats) |
| Score manipulation | Score capped at 10000 BPS; validation in modifier |
| Bond double-trigger | `require(!bond.triggered)` prevents double payout |
| CFMC double-mint | `require(!mitigationRecorded[assessmentId])` |
| Reentrancy in payout | Checks-Effects-Interactions pattern in DisasterBond |

### 17.2 API Security

| Threat | Mitigation |
|--------|-----------|
| Private key exposure | Backend wallet loaded from env var, never hardcoded |
| Gas estimation attack | Max gas limit set in web3.py client config |
| IPFS poisoning | CID verified client-side via content hash recomputation |
| RPC downtime | Fallback RPC URLs + retry queue in PostgreSQL |

---

## 18. PERFORMANCE BENCHMARKS & SLOs

### 18.1 Non-Negotiable Performance Targets

| Metric | SLO | Baseline (v1.0) | Target (v2.0) |
|--------|-----|----------------|---------------|
| Analysis API response time | < 3 seconds | 1.8s | < 2.5s (blockchain is async) |
| Blockchain anchoring (non-blocking) | < 50ms task spawn | N/A | < 10ms task spawn |
| IPFS pin time | < 5 seconds | N/A | < 4s (Pinata) |
| Transaction confirmation (Polygon Amoy) | < 30 seconds | N/A | ~5-15s typical |
| MCP tool call latency | < 500ms | 220ms | < 300ms |
| WebSocket event propagation | < 100ms | 80ms | < 100ms |

---

## 19. ENVIRONMENT CONFIGURATION v2.0

```bash
# ─── EXISTING (v1.0) ───────────────────────────────────────────────

GROQ_API_KEY=<your-groq-key>
SARVAM_API_KEY=<your-sarvam-key>
ELEVENLABS_API_KEY=<your-elevenlabs-key>
MAPBOX_API_TOKEN=<your-mapbox-token>
GEMINI_API_KEY=<your-gemini-key>
ACUTE_RISK_TRIGGER_THRESHOLD=0.65
CHRONIC_DAMAGE_THRESHOLD=0.70

# ─── NEW (v2.0 BLOCKCHAIN) ──────────────────────────────────────────

# Polygon Amoy Testnet
POLYGON_AMOY_RPC=https://rpc-amoy.polygon.technology
POLYGON_CHAIN_ID=80002
BLOCKCHAIN_DEPLOYER_KEY=<private-key-of-deployer-wallet>
AEGIS_BACKEND_WALLET=<address-of-backend-signing-wallet>

# Smart Contract Addresses (populated after deploy)
AEGIS_RISK_LEDGER_ADDRESS=<AEGISRiskLedger-deployed-address>
DISASTER_BOND_ADDRESS=<DisasterBond-deployed-address>
CARBON_FLOOD_CREDIT_ADDRESS=<CarbonFloodCredit-deployed-address>
MOCK_USDC_ADDRESS=<MockUSDC-deployed-address>

# Polygon Explorer
POLYGONSCAN_API_KEY=<from-polygonscan.com/apis>

# IPFS / Filecoin
PINATA_API_KEY=<from-pinata.cloud>
PINATA_API_SECRET=<from-pinata.cloud>
IPFS_GATEWAY=https://gateway.pinata.cloud/ipfs

# Demo Configuration
DEMO_BENEFICIARY_ADDRESS=<wallet-to-receive-demo-bond-payouts>
BLOCKCHAIN_ENABLED=true        # set false to disable blockchain (graceful degradation)
BLOCKCHAIN_ASYNC_ANCHOR=true   # always true for non-blocking operation

# The Graph (optional)
SUBGRAPH_URL=https://api.thegraph.com/subgraphs/name/<your-org>/aegis-chain
```

---

## 20. JUDGING CRITERIA TECHNICAL MAPPING

| IEEE ClimateChain Judging Criterion | AEGIS-CHAIN v2.0 Technical Evidence |
|------------------------------------|--------------------------------------|
| **Technical Complexity** | 3 Solidity contracts + 3 AI agents + MCP Hub + LangGraph + XGBoost + GIS + RAG + Voice AI — unmatched depth |
| **Blockchain Integration** | Polygon Amoy deployed AEGISRiskLedger, DisasterBond, CFMC ERC-20; verified on PolygonScan; live txns in demo |
| **AI Integration** | 3 autonomous agents (LangGraph state graph), XGBoost ML, ChromaDB RAG, Groq/Gemini LLM, 95.14% accuracy |
| **Innovation** | World's first blockchain-anchored multi-agent flood risk + parametric bond auto-payout system |
| **Real-World Impact** | Addresses $15B+ annual flood losses in India; SEBI BRSR compliance; financial VaR for enterprises |
| **Carbon Market Track** | CFMC ERC-20 token = novel carbon credit for flood mitigation; directly addresses carbon markets track |
| **Data Integrity Track** | IPFS CID + on-chain hash = tamper-evident climate AI outputs; cannot be altered post-anchor |
| **Climate Resilience Track** | Parametric bonds = automatic disaster payouts; removes human delay in insurance claims |
| **Working Prototype** | Full Docker deployment; live demo at http://127.0.0.1:5173; all 10 MCP tests pass |
| **Demo Quality** | What-If slider; voice dispatch; chain explorer panel; live PolygonScan links during demo |

---

## APPENDIX A — DEPENDENCIES (NEW)

### blockchain/package.json additions:

```json
{
  "devDependencies": {
    "@nomicfoundation/hardhat-toolbox": "^5.0.0",
    "@openzeppelin/hardhat-upgrades": "^3.0.0",
    "hardhat": "^2.22.0"
  },
  "dependencies": {
    "@openzeppelin/contracts": "^5.0.2",
    "ethers": "^6.13.0"
  }
}
```

### backend/requirements.txt additions:

```
web3==7.6.0
eth-account==0.13.0
aiohttp==3.10.5
```

### frontend package.json additions:

```json
{
  "dependencies": {
    "wagmi": "^2.12.0",
    "ethers": "^6.13.0",
    "@rainbow-me/rainbowkit": "^2.1.0",
    "@tanstack/react-query": "^5.55.0"
  }
}
```

---

## APPENDIX B — SMART CONTRACT ABI SUMMARIES

### AEGISRiskLedger ABI (Key Functions):
- `anchorRiskAssessment(lat, lon, scoreBps, ipfsCid, locationName) → bytes32`
- `anchorDEMCascade(assessmentId, depthCm, structures, drainagePct, ipfsCid)`
- `anchorVaRCascade(assessmentId, varLakhs, varUsdCents, carbonLakhs, strandedBps, ipfsCid)`
- `getAssessment(assessmentId) → RiskAssessment`
- `getLocationHistory(lat, lon) → bytes32[]`
- `getRecentAssessments(count) → bytes32[]`
- `getStats() → (totalAssessments, criticalAlerts)`

### DisasterBond ABI (Key Functions):
- `createBond(lat, lon, beneficiary, payout, threshold, consecutive, name) → bytes32`
- `notifyAssessment(lat, lon, scoreBps, assessmentId)`
- `getBond(bondId) → Bond`
- `getLocationBonds(lat, lon) → bytes32[]`

### CarbonFloodCredit ABI (Key Functions):
- `issueMitigationCredit(beneficiary, assessmentId, lat, lon, scoreBps, demDepthCm) → bool`
- `retireCredits(amount, reason)`
- `balanceOf(address) → uint256`
- `totalMitigationEvents() → uint256`

---

*End of PRD 1 — Technical Blueprint*  
*AEGIS-CHAIN v2.0 | IEEE ClimateChain Global Hackathon 2026*  
*Team Syntrix | Nishant Maurya (Lead) | github.com/Niss54/AEGIS*
