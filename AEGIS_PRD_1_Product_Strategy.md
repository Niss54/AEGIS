# PRD 1: AEGIS-CLIMATE Product Strategy, User Experience, Evidence and Hackathon Win Plan

> **Repository:** https://github.com/Niss54/AEGIS  
> **Target event:** IEEE ClimateChain Global Hackathon 2026  
> **Created:** 14 October 2026  
> **Document status:** Proposed product specification, pending implementation and factual source validation  
> **Chosen track:** Climate Data & Environmental Monitoring  

## 0. How to use this PRD
This document instructs an implementation agent and the AEGIS team. It is not a claim that the described features already exist. Treat the current GitHub repository as the baseline, implement incrementally, and verify acceptance evidence before updating the README or public demo. Requirements use P0 for blocking trust/demo work, P1 for high-value scope, and P2 for later expansion.

## 1. Executive recommendation
Keep AEGIS-CLIMATE and its existing React/Vite, FastAPI, ML, geospatial, RAG, and tool-hub foundations. Add a focused climate-evidence lifecycle that captures source lineage, computes a deterministic digest, anchors that digest in a small EVM-compatible registry, and allows a third party to detect tampering. Do not create a separate product, replace the current UI framework, or add tokens/NFTs/carbon-credit issuance just to make blockchain visible.

### One-sentence pitch
AEGIS-CLIMATE turns climate observations and explainable risk analysis into traceable evidence that another person can independently verify, including detection when a report changes after it was anchored.

### Product wedge
Climate data is fragmented, observations and forecasts get conflated, analysis reports often omit traceable lineage, and downstream users cannot easily prove that a shared report has not been modified. AEGIS reduces this verification gap; it does not pretend that a hash proves the weather observation itself was true.

### Must-win principle
A judge should be able to see the climate input, inspect its provenance, understand the analysis, anchor the exact report digest, and change one value to prove that independent verification fails. That end-to-end behaviour is more persuasive than an oversized architecture diagram or an unexplained blockchain logo.

## 2. Official hackathon requirements and fit
The official Devpost page names five judging criteria: climate impact, innovation and creativity, technical execution, practical usefulness, and presentation/communication. It requests explicit track alignment, a project description explaining problem/solution/users/scalability/adoption, a 3-5 minute demo video, public repository, and a working prototype or proof of concept. The listed deadline is 25 October 2026 at 5:00 PM MSK, equivalent to 7:30 PM IST. Recheck Devpost immediately before submission because organizers can update rules. Source: https://ieee-climatechain-hack.devpost.com/

### Track selection: Climate Data & Environmental Monitoring
AEGIS already analyses environmental inputs and produces climate risk reports. The most coherent fit is the track whose stated problem is fragmented, difficult-to-verify environmental data and whose build examples include climate-data verification platforms, IoT monitoring, climate data marketplaces, and research tools. The proposed evidence registry directly answers this track without forcing a carbon credit or energy trading product into the existing architecture.

### Mapping to judging criteria
| Official criterion | Product proof required | What the judge should see |
|---|---|---|
| Climate impact | A climate signal is transformed into a bounded, decision-relevant risk report with source context. | A real or clearly labelled fixture-backed analysis and its next-action guidance. |
| Innovation and creativity | AI risk analysis and content-addressed evidence verification are joined in one verifiable workflow. | One field is changed and the verification status fails. |
| Technical execution | Validated data pipeline, reproducible model metadata, canonicalization, contract tests, transaction receipt validation, persistence. | Logs, tests, actual receipt/event, verifier result. |
| Practical usefulness | Researcher/operator/auditor can share a report and check integrity without trusting the creator's UI. | Standalone verification URL or downloaded JSON verifier. |
| Presentation and communication | Plain-language story, reliable demo, clear limitations, no fake results. | Three-to-five-minute recording with an explicit problem, workflow, proof, and adoption path. |

### Eligibility and rules checkpoint
The public page says the event is for students above the legal age of majority and excludes companies/professional organizations and certain countries/territories. The full rules link was not accessible during this review, so eligibility for the full team, country restrictions, and team requirements must be checked in the participant account before investing further effort. No PRD can guarantee a win; these requirements aim to improve the quality and credibility of the submission.

## 3. Existing AEGIS baseline: preserve, correct, extend
The public repository contains a React/Vite/TypeScript frontend, FastAPI backend, three climate-risk agents, a JSON-RPC-style tool hub, a stored GradientBoostingClassifier, geospatial exposure calculations, a policy RAG engine, Docker Compose services, and test suites. The codebase is a useful starting point, not proof that all README claims are production-accurate.

### Existing assets to preserve
- Keep the AEGIS-CLIMATE brand and current repo: https://github.com/Niss54/AEGIS.
- Preserve `frontend/src/App.tsx` and the current Vite/React setup; do not migrate to Next.js merely because an old PRD says Next.js.
- Extend the current FastAPI `/api/v1/analyze` workflow and the Agent 1 -> Agent 2 -> Agent 3 cascade.
- Keep the existing weather adapter, risk classifier, geospatial view, policy search, bilingual summaries, and what-if sandbox where their outputs can be labelled honestly.
- Reuse the current test suite as regression coverage and expand tests around the new evidence lifecycle.

### Critical integrity gaps discovered in source inspection
1. In `mcp_hub/hub.py`, `precipitation_7d_mm` is derived by multiplying 24-hour precipitation by 2.8. It must be replaced with an independently fetched and correctly windowed seven-day series or omitted/labeled unavailable.
2. `backend/app/agent2_geo.py` estimates water depth and drainage overflow with formulas and estimates building counts from the risk score. These are not real DEM samples or verified building-footprint intersections. Label these as heuristics until genuine input data is wired and validated.
3. `backend/app/agent3_financial.py` seeds a small policy corpus with concrete regulatory claims that need primary-source verification, including purported fees, mandatory thresholds and section-specific rules. Remove or relabel anything not verifiable against an official source.
4. `backend/app/routes/analyze.py` stores events in a process-local dictionary. Evidence records and transaction lifecycle must move to durable persistence before being represented as reliably retrievable.
5. `backend/app/main.py` uses wildcard CORS and returns `str(exc)` to clients from the global exception handler. Harden deployed CORS and return safe, correlated errors.
6. Existing model accuracy/F1 metadata must be reproduced from the committed training data and evaluation script before repeating the values in the pitch.
7. The tool hub implements a custom JSON-RPC tool dispatcher. Do not claim standards-conformant MCP behaviour unless compatibility tests actually establish it.

These are P0 because a technically polished demo that overstates data truth can lose judge trust during simple questions. The blockchain cannot repair bad source data; it only makes the committed content easier to detect if it later changes.

## 4. Product architecture at a glance
```text
Climate data provider / curated fixture
          | source id + observed/forecast window + timestamp + units
          v
Data quality and provenance adapter
          | validated feature vector + missingness/fallback flags
          v
Existing AEGIS analysis orchestrator
   | Agent 1 flood risk model
   | Agent 2 exposure analysis (real GIS or visibly labelled heuristic)
   | Agent 3 policy/RAG and financial estimate (verified citations only)
          v
Versioned canonical evidence bundle (off-chain JSON, persisted DB record)
          | server recomputes Keccak-256 digest
          v
ClimateEvidenceRegistry contract (digest + minimal metadata + event)
          | chain id + registry address + tx hash + receipt/event
          v
Independent verifier: canonicalize -> recompute -> compare -> inspect receipt
          |
          +---- pass: content matches the anchored digest
          +---- fail: content differs / record unknown / receipt invalid
```

### The boundary of the claim
- The source provider is responsible for the upstream measurement and its quality controls.
- AEGIS is responsible for parsing, unit handling, transformations, model behaviour, labels, and disclosed limitations.
- Blockchain records a content commitment and traceable event. It does not prove that the original observation was truthful, that the model is accurate, or that a flood will occur.
- A qualified external authority still owns public emergency warnings, engineering certifications, and legal compliance decisions.

## 5. Target personas and user journeys
### Municipal disaster-response analyst
Goal: identify a high-risk location, confirm the input is fresh and credible, review the model's supporting factors, and share a traceable report. Success is a comprehensible risk review with known input limitations, not automatic public evacuation messaging.
### Climate-data researcher
Goal: reproduce the dataset lineage and model version behind an analysis and compare runs without confusing simulation with actual observations. Success is an exported evidence bundle and reproducible digest.
### Infrastructure operator
Goal: review a facility or region for potential exposure and prioritise validation work. Success is seeing the difference between measured assets, sourced geospatial calculations, and approximate exposure assumptions.
### Independent verifier or judge
Goal: validate a report created by someone else and check if the exact content matches a committed digest. Success is a standalone verifier that works from a bundle or public-safe report ID.

## 6. MVP user journey (must work end to end)
1. Open AEGIS and choose a supported location or sample scenario.
2. Inspect source/provider, time window, update time, observed/forecast status, and data-quality warnings.
3. Run the existing AEGIS analysis and inspect only the agents that actually ran.
4. Read the result with model version and clearly labeled real, estimated, or synthetic fields.
5. Create a versioned evidence JSON bundle. Verify locally that its digest is stable.
6. Anchor the digest on the configured local chain or public EVM testnet, with chain state visibly labelled.
7. Open a separate verifier view, load the unchanged bundle, and confirm digest plus registry event/receipt.
8. Edit one input/output field in a copy and re-run verification. It must fail with a mismatch explanation.
9. Restore the original bundle and verify the pass state again.
10. Export a shareable report that retains provenance, limitations and on-chain transaction details.

## 7. Feature specification and acceptance criteria
The following requirements are detailed enough for an implementation agent to break into GitHub issues. Per-feature acceptance evidence is required. A checkbox in the PRD does not count as evidence that code exists.

### 1. Product identity and track fit
**Primary users:** Disaster manager, climate-data researcher, municipal planner.
**Product outcome:** Position AEGIS as a trustworthy climate evidence and decision platform, not another ungrounded flood dashboard.

#### P-001: Primary track declaration
- **Priority:** P0.
- **Persona / outcome:** Disaster manager, climate-data researcher, municipal planner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Primary track declaration**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The submission and landing page explicitly select Climate Data & Environmental Monitoring and map every major feature to climate-data verification, environmental monitoring, or research insight.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-002: Product name continuity
- **Priority:** P0.
- **Persona / outcome:** Disaster manager, climate-data researcher, municipal planner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Product name continuity**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The product remains AEGIS-CLIMATE and preserves the existing GitHub repository, domain story, React/Vite application, and three-agent model.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-003: One-sentence proposition
- **Priority:** P0.
- **Persona / outcome:** Disaster manager, climate-data researcher, municipal planner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **One-sentence proposition**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The home screen communicates in one sentence that AEGIS converts climate observations and model outputs into explainable risk reports with verifiable evidence commitments.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-004: Problem boundary
- **Priority:** P0.
- **Persona / outcome:** Disaster manager, climate-data researcher, municipal planner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Problem boundary**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The problem statement distinguishes missing trustworthy, contextualized evidence from the separate problem of flood prediction accuracy.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-005: Climate outcome
- **Priority:** P0.
- **Persona / outcome:** Disaster manager, climate-data researcher, municipal planner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Climate outcome**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Every major workflow links a risk result to a decision such as inspect, prepare, verify source, or share an evidence report, without claiming it prevents a disaster by itself.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-006: Blockchain necessity
- **Priority:** P0.
- **Persona / outcome:** Disaster manager, climate-data researcher, municipal planner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Blockchain necessity**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The product explains why a third party benefits from verifying the unchanged report digest without trusting the hosting database.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-007: AI necessity
- **Priority:** P0.
- **Persona / outcome:** Disaster manager, climate-data researcher, municipal planner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **AI necessity**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The product explains that ML classifies the current input vector while deterministic policy and safety rules control what actions follow.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-008: User-focused language
- **Priority:** P0.
- **Persona / outcome:** Disaster manager, climate-data researcher, municipal planner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **User-focused language**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Judges can understand the product without prior familiarity with LangGraph, MCP, EVM, embeddings, or GIS jargon.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-009: Track-to-feature matrix
- **Priority:** P0.
- **Persona / outcome:** Disaster manager, climate-data researcher, municipal planner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Track-to-feature matrix**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The submission includes a track-fit table linking environmental data verification to ingestion, provenance, risk analysis, evidence digest, on-chain anchor, and public verification.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-010: Claim discipline
- **Priority:** P0.
- **Persona / outcome:** Disaster manager, climate-data researcher, municipal planner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Claim discipline**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** All performance, impact, regulatory, and deployment claims are backed by reproducible evidence or labeled estimates.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-011: Competition positioning
- **Priority:** P0.
- **Persona / outcome:** Disaster manager, climate-data researcher, municipal planner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Competition positioning**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The product differentiates through a complete evidence lifecycle and tamper verification, not through the number of agents or animated UI elements.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-012: Scope guardrails
- **Priority:** P0.
- **Persona / outcome:** Disaster manager, climate-data researcher, municipal planner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Scope guardrails**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The roadmap explicitly defers tokens, NFT-based carbon credits, speculative offset issuance, and a carbon marketplace.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

### 2. Target users and jobs-to-be-done
**Primary users:** Municipal disaster-response analyst, climate researcher, infrastructure operator, auditor.
**Product outcome:** Make one urgent decision workflow easy to explain and verify.

#### P-013: Municipal analyst persona
- **Priority:** P0.
- **Persona / outcome:** Municipal disaster-response analyst, climate researcher, infrastructure operator, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Municipal analyst persona**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A municipal analyst can choose a hotspot, inspect weather-source freshness, evaluate risk, and export a signed-off evidence report in one workflow.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-014: Climate researcher persona
- **Priority:** P0.
- **Persona / outcome:** Municipal disaster-response analyst, climate researcher, infrastructure operator, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Climate researcher persona**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A researcher can inspect source names, timestamps, temporal resolution, transformations, model version, and evidence hash for a result.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-015: Infrastructure operator persona
- **Priority:** P0.
- **Persona / outcome:** Municipal disaster-response analyst, climate researcher, infrastructure operator, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Infrastructure operator persona**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** An operator can retrieve a risk assessment for an asset or region and understand which inputs are observed, forecast, simulated, or estimated.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-016: Independent verifier persona
- **Priority:** P0.
- **Persona / outcome:** Municipal disaster-response analyst, climate researcher, infrastructure operator, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Independent verifier persona**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A reviewer who did not create a report can retrieve the public proof and confirm whether supplied evidence matches the anchored digest.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-017: Auditor persona
- **Priority:** P0.
- **Persona / outcome:** Municipal disaster-response analyst, climate researcher, infrastructure operator, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Auditor persona**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** An auditor can trace a reported value to source metadata and transformations, and can distinguish an on-chain integrity proof from scientific validation.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-018: First-use path
- **Priority:** P0.
- **Persona / outcome:** Municipal disaster-response analyst, climate researcher, infrastructure operator, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **First-use path**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A first-time user can complete the primary flow without setting up a wallet if demo mode supports a clearly labeled demo identity or relayer.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-019: Expert path
- **Priority:** P0.
- **Persona / outcome:** Municipal disaster-response analyst, climate researcher, infrastructure operator, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Expert path**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Technical users can reveal underlying model features, prediction metadata, tool events, transaction receipt, and raw verification results.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-020: Accessibility path
- **Priority:** P0.
- **Persona / outcome:** Municipal disaster-response analyst, climate researcher, infrastructure operator, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Accessibility path**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Core labels, risk state, evidence status, and failure messages remain understandable with keyboard navigation and screen-reader semantics.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-021: Role assumptions
- **Priority:** P0.
- **Persona / outcome:** Municipal disaster-response analyst, climate researcher, infrastructure operator, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Role assumptions**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The application makes no claim that a public anonymous visitor is a verified government official or accredited auditor.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-022: User feedback capture
- **Priority:** P0.
- **Persona / outcome:** Municipal disaster-response analyst, climate researcher, infrastructure operator, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **User feedback capture**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A demo reviewer can flag an incorrect data source, confusing label, or failed workflow without inserting untrusted content into authoritative evidence.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-023: Language preference
- **Priority:** P0.
- **Persona / outcome:** Municipal disaster-response analyst, climate researcher, infrastructure operator, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Language preference**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Hindi and English summaries may be available, but both languages present the same numeric values, provenance, uncertainty, and alert priority.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-024: Job completion metric
- **Priority:** P0.
- **Persona / outcome:** Municipal disaster-response analyst, climate researcher, infrastructure operator, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Job completion metric**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The product records successful evidence verification, report retrieval, and completed analysis separately from vanity metrics such as screen views.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

### 3. Primary end-to-end climate evidence workflow
**Primary users:** All personas.
**Product outcome:** Make the complete working demo the centre of product design.

#### P-025: Location selection
- **Priority:** P0.
- **Persona / outcome:** All personas. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Location selection**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A user selects an allowlisted city/hotspot or enters bounded coordinates and sees the resolved location before analysis runs.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-026: Observation fetch
- **Priority:** P0.
- **Persona / outcome:** All personas. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Observation fetch**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The system fetches current or historical/forecast observations from named sources and shows exactly which time window was used.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-027: Input review
- **Priority:** P0.
- **Persona / outcome:** All personas. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Input review**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The user sees source timestamps, missing values, temporal type, units, and fallback indicators before relying on the result.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-028: Analysis start
- **Priority:** P0.
- **Persona / outcome:** All personas. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Analysis start**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** One explicit action creates an immutable analysis run ID and starts the existing AEGIS risk pipeline.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-029: Agent progression
- **Priority:** P0.
- **Persona / outcome:** All personas. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Agent progression**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The UI displays each real completed agent step and tool invocation; it never fabricates agent activity to create a cinematic demo.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-030: Risk explanation
- **Priority:** P0.
- **Persona / outcome:** All personas. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Risk explanation**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The final score displays risk tier, model/version, important input factors, calibration status if available, and an uncertainty caveat.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-031: Exposure explanation
- **Priority:** P0.
- **Persona / outcome:** All personas. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Exposure explanation**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The structural view distinguishes measured geospatial intersections from heuristic exposure proxies and labels both clearly.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-032: Evidence bundle creation
- **Priority:** P0.
- **Persona / outcome:** All personas. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Evidence bundle creation**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The system creates a deterministic, versioned evidence bundle from the chosen inputs, transformations, outputs, source references, and model digest.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-033: Anchor consent
- **Priority:** P0.
- **Persona / outcome:** All personas. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Anchor consent**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Before an on-chain transaction, the UI explains which digest and minimum metadata will be public and requests an explicit confirmation.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-034: Chain receipt
- **Priority:** P0.
- **Persona / outcome:** All personas. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Chain receipt**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The UI displays transaction submitted, pending, confirmed, reverted, or unavailable states without conflating them.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-035: Independent verification
- **Priority:** P0.
- **Persona / outcome:** All personas. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Independent verification**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A separate verifier route recomputes the digest from a provided report and reports match, mismatch, malformed bundle, or unavailable chain state.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-036: Shareable report
- **Priority:** P0.
- **Persona / outcome:** All personas. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Shareable report**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A user can share a report URL that loads stored off-chain evidence and independently displays its anchoring and verification state.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

### 4. Climate data provenance and quality
**Primary users:** Analyst, researcher, auditor.
**Product outcome:** Prevent proxy data from masquerading as measured environmental truth.

#### P-037: Source registry
- **Priority:** P0.
- **Persona / outcome:** Analyst, researcher, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Source registry**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Every ingestible source has a documented name, provider URL, licence note, source type, temporal resolution, geographic coverage, and freshness expectation.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-038: Observed-versus-forecast status
- **Priority:** P0.
- **Persona / outcome:** Analyst, researcher, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Observed-versus-forecast status**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Each meteorological value identifies observation, forecast, reanalysis, or simulation and propagates that label to the final report.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-039: Independent seven-day rainfall
- **Priority:** P0.
- **Persona / outcome:** Analyst, researcher, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Independent seven-day rainfall**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The seven-day precipitation field is calculated from a real, correctly bounded seven-day series or omitted; it is never generated by multiplying 24-hour rain by a constant.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-040: Timestamp normalisation
- **Priority:** P0.
- **Persona / outcome:** Analyst, researcher, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Timestamp normalisation**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Incoming source timestamps are normalized to UTC internally, with the display timezone and source timezone preserved in metadata.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-041: Unit normalisation
- **Priority:** P0.
- **Persona / outcome:** Analyst, researcher, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Unit normalisation**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Precipitation, temperature, humidity, elevation, and soil-moisture units are converted using documented transformations before modeling.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-042: Missing-data policy
- **Priority:** P0.
- **Persona / outcome:** Analyst, researcher, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Missing-data policy**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Every required field has an explicit reject, impute, omit, or fallback policy, with the selected branch visible in the evidence bundle.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-043: Synthetic fallback flag
- **Priority:** P0.
- **Persona / outcome:** Analyst, researcher, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Synthetic fallback flag**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Deterministic demo values set `data_mode=synthetic` and a prominent demo badge so no viewer mistakes them for live readings.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-044: Freshness badge
- **Priority:** P0.
- **Persona / outcome:** Analyst, researcher, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Freshness badge**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Each source shows fetch time, observation time, expected update interval, and a stale-data warning when limits are exceeded.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-045: Provider failure
- **Priority:** P0.
- **Persona / outcome:** Analyst, researcher, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Provider failure**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** If a provider times out or returns invalid data, the analysis either uses a labeled fallback or refuses to calculate a confidence claim.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-046: Input quality score
- **Priority:** P0.
- **Persona / outcome:** Analyst, researcher, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Input quality score**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A quality indicator reflects missingness, age, geographic specificity, and provider status and is not described as probability of flood.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-047: Data licence
- **Priority:** P0.
- **Persona / outcome:** Analyst, researcher, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Data licence**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The source registry records attribution or licence obligations and the output export preserves applicable attribution.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-048: Provenance completeness gate
- **Priority:** P0.
- **Persona / outcome:** Analyst, researcher, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Provenance completeness gate**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** An evidence anchor can be submitted only when mandatory provenance fields exist or the bundle is explicitly marked synthetic/incomplete.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

### 5. Hazard modelling and explainability
**Primary users:** Analyst, municipal planner, climate scientist.
**Product outcome:** Keep the existing risk model while reducing overclaiming and making its limits testable.

#### P-049: Model card
- **Priority:** P0.
- **Persona / outcome:** Analyst, municipal planner, climate scientist. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Model card**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The flood classifier has a model card with dataset origin, label definition, features, split method, geography, dates, limitations, and owner.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-050: Metric reproducibility
- **Priority:** P0.
- **Persona / outcome:** Analyst, municipal planner, climate scientist. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Metric reproducibility**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Displayed accuracy and macro-F1 match a reproducible training/evaluation command and committed evaluation artifact.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-051: Leakage check
- **Priority:** P0.
- **Persona / outcome:** Analyst, municipal planner, climate scientist. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Leakage check**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Validation prevents temporal, spatial, or duplicate-sample leakage and documents whether the test set is geographically independent.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-052: Risk score semantics
- **Priority:** P0.
- **Persona / outcome:** Analyst, municipal planner, climate scientist. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Risk score semantics**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The interface calls the value a model risk score unless calibrated probabilities have been validated against representative held-out outcomes.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-053: Risk tier thresholds
- **Priority:** P0.
- **Persona / outcome:** Analyst, municipal planner, climate scientist. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Risk tier thresholds**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** LOW, MODERATE, HIGH, and CRITICAL thresholds are centrally configured, versioned, and visible in the analysis metadata.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-054: Feature explanations
- **Priority:** P0.
- **Persona / outcome:** Analyst, municipal planner, climate scientist. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Feature explanations**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Displayed drivers derive from documented model feature importance or a real explanation algorithm and are not fabricated natural-language reasoning.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-055: Counterfactual sandbox
- **Priority:** P0.
- **Persona / outcome:** Analyst, municipal planner, climate scientist. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Counterfactual sandbox**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** What-if rainfall and saturation changes are tagged as simulations and cannot be confused with observed measurements.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-056: Model version pinning
- **Priority:** P0.
- **Persona / outcome:** Analyst, municipal planner, climate scientist. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Model version pinning**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Each completed run records the model artifact SHA-256, feature-schema version, code revision, and preprocessing version.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-057: Out-of-range input
- **Priority:** P0.
- **Persona / outcome:** Analyst, municipal planner, climate scientist. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Out-of-range input**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Coordinates, humidity, saturation, precipitation, and radius are validated and invalid values receive a clear error instead of a risk score.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-058: Uncertainty disclosure
- **Priority:** P0.
- **Persona / outcome:** Analyst, municipal planner, climate scientist. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Uncertainty disclosure**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The report communicates known uncertainty and missing evidence; it does not present one result as an official warning or a guaranteed forecast.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-059: Baseline comparison
- **Priority:** P0.
- **Persona / outcome:** Analyst, municipal planner, climate scientist. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Baseline comparison**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A documented baseline allows reviewers to compare the ML score with a transparent rule baseline on the same evaluation split.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-060: Human decision boundary
- **Priority:** P0.
- **Persona / outcome:** Analyst, municipal planner, climate scientist. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Human decision boundary**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** AEGIS recommends review actions but does not automatically order evacuation, dispatch responders, or make legally binding decisions.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

### 6. Geospatial exposure honesty
**Primary users:** Municipal planner, operator, auditor.
**Product outcome:** Preserve the current exposure agent while making the data/model boundary explicit.

#### P-061: DEM provenance
- **Priority:** P0.
- **Persona / outcome:** Municipal planner, operator, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **DEM provenance**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A claimed elevation or DEM-derived calculation includes the actual raster product, version, resolution, source date, and sampled cell metadata.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-062: No fictional footprint intersections
- **Priority:** P0.
- **Persona / outcome:** Municipal planner, operator, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **No fictional footprint intersections**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Building counts are labelled heuristic estimates until real footprint data and spatial intersections are implemented.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-063: Heuristic depth label
- **Priority:** P0.
- **Persona / outcome:** Municipal planner, operator, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Heuristic depth label**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Formula-derived water depth is shown as an illustrative heuristic, not a measured or hydraulically simulated inundation depth.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-064: GeoJSON provenance
- **Priority:** P0.
- **Persona / outcome:** Municipal planner, operator, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **GeoJSON provenance**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Each map layer identifies whether it is source geometry, derived geometry, or illustrative demonstration geometry.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-065: Coordinate reference system
- **Priority:** P0.
- **Persona / outcome:** Municipal planner, operator, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Coordinate reference system**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Spatial processing documents and validates CRS transformation before area, distance, buffering, or intersection operations.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-066: Radius semantics
- **Priority:** P0.
- **Persona / outcome:** Municipal planner, operator, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Radius semantics**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A selected radius affects the actual operation and visible footprint; no result implies parcel-level accuracy when only a radius heuristic was used.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-067: Exposure count uncertainty
- **Priority:** P0.
- **Persona / outcome:** Municipal planner, operator, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Exposure count uncertainty**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Estimated structure totals show method, assumptions, and confidence limitations rather than implying a verified asset inventory.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-068: Damage curve provenance
- **Priority:** P0.
- **Persona / outcome:** Municipal planner, operator, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Damage curve provenance**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Damage curves and asset values include source references, currency year, applicability, and whether adapted locally or illustrative.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-069: Long-horizon projections
- **Priority:** P0.
- **Persona / outcome:** Municipal planner, operator, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Long-horizon projections**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** 10-, 20-, and 30-year values are shown only if an explicit scenario methodology supports them; otherwise label as scenario heuristics or hide.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-070: Map legend
- **Priority:** P0.
- **Persona / outcome:** Municipal planner, operator, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Map legend**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The legend makes observed assets, sourced elevation, computed risk geometry, and demo-only overlays visually distinct.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-071: Spatial input validation
- **Priority:** P0.
- **Persona / outcome:** Municipal planner, operator, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Spatial input validation**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Latitude and longitude bounds, radius caps, and invalid geometry are rejected before expensive analysis.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-072: GIS limitations panel
- **Priority:** P0.
- **Persona / outcome:** Municipal planner, operator, auditor. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **GIS limitations panel**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The report lists the geographic/data limits that prevent using the result as an engineering or emergency certification.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

### 7. Evidence bundle and content addressing
**Primary users:** Researcher, auditor, third-party verifier.
**Product outcome:** Define a stable artefact that survives re-download, transfer, and independent hash recomputation.

#### P-073: Canonical evidence schema
- **Priority:** P0.
- **Persona / outcome:** Researcher, auditor, third-party verifier. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Canonical evidence schema**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A documented JSON schema versions all required inputs, units, source records, transformations, model metadata, output metrics, disclaimers, and timestamps.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-074: Deterministic JSON encoding
- **Priority:** P0.
- **Persona / outcome:** Researcher, auditor, third-party verifier. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Deterministic JSON encoding**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Canonical serialization fixes key order, UTF-8 encoding, number representation, null handling, and array ordering before hashing.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-075: Digest preimage
- **Priority:** P0.
- **Persona / outcome:** Researcher, auditor, third-party verifier. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Digest preimage**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The hash preimage excludes the digest and transaction fields themselves to avoid recursive or self-referential hashing.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-076: Schema version retention
- **Priority:** P0.
- **Persona / outcome:** Researcher, auditor, third-party verifier. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Schema version retention**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Older bundles remain verifiable after the schema advances and the verifier dispatches by declared schema version.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-077: Source records
- **Priority:** P0.
- **Persona / outcome:** Researcher, auditor, third-party verifier. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Source records**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The bundle stores provider name, request window, requested coordinates or privacy-safe region identifier, retrieval time, and source record digest.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-078: Transformation manifest
- **Priority:** P0.
- **Persona / outcome:** Researcher, auditor, third-party verifier. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Transformation manifest**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Every derived field lists formula/code version, source field names, and unit transformations sufficient for audit reproduction.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-079: Model manifest
- **Priority:** P0.
- **Persona / outcome:** Researcher, auditor, third-party verifier. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Model manifest**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The bundle lists model identifier, model artifact digest, feature schema, score semantics, and training-data documentation URL or ID.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-080: Report digest
- **Priority:** P0.
- **Persona / outcome:** Researcher, auditor, third-party verifier. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Report digest**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The displayed digest is computed server-side from validated canonical content and is not accepted as an arbitrary client-provided truth.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-081: Tamper edit test
- **Priority:** P0.
- **Persona / outcome:** Researcher, auditor, third-party verifier. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Tamper edit test**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A deliberate one-field change causes local digest recomputation to differ from the anchored digest and displays a clear failure.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-082: Bundle export
- **Priority:** P0.
- **Persona / outcome:** Researcher, auditor, third-party verifier. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Bundle export**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A user can download a JSON bundle that can be verified outside the logged-in application without requiring private API keys.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-083: Bundle minimisation
- **Priority:** P0.
- **Persona / outcome:** Researcher, auditor, third-party verifier. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Bundle minimisation**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The bundle excludes secrets, personal identifiers, and sensitive exact coordinates unless explicitly needed and consented to.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-084: Integrity language
- **Priority:** P0.
- **Persona / outcome:** Researcher, auditor, third-party verifier. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Integrity language**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The UI says the digest proves content integrity against the anchored commitment, not that the underlying climate data was true.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

### 8. Blockchain evidence registry
**Primary users:** Independent verifier, judge, report creator.
**Product outcome:** Use an auditable on-chain event for the exact climate report digest; do not invent token economics.

#### P-085: Registry use case
- **Priority:** P0.
- **Persona / outcome:** Independent verifier, judge, report creator. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Registry use case**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The contract anchors climate evidence digests and metadata needed to resolve the evidence, rather than tokenizing flood risk or creating carbon credits.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-086: Digest anchoring
- **Priority:** P0.
- **Persona / outcome:** Independent verifier, judge, report creator. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Digest anchoring**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A valid evidence digest can be written to the selected chain and emits a stable event that an independent client can query.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-087: Duplicate prevention
- **Priority:** P0.
- **Persona / outcome:** Independent verifier, judge, report creator. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Duplicate prevention**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The registry rejects or clearly identifies duplicate submissions of the same digest within the defined scope.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-088: Issuer authorization
- **Priority:** P0.
- **Persona / outcome:** Independent verifier, judge, report creator. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Issuer authorization**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Contract roles determine who may anchor reports and can be inspected through contract reads or deployment documentation.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-089: Event integrity
- **Priority:** P0.
- **Persona / outcome:** Independent verifier, judge, report creator. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Event integrity**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The emitted event contains the digest, schema version, issuer, timestamp reference, and report ID or privacy-safe reference needed for retrieval.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-090: Chain identity
- **Priority:** P0.
- **Persona / outcome:** Independent verifier, judge, report creator. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Chain identity**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The application pins chain ID, RPC endpoint, registry address, contract ABI/version, and deployment transaction in configuration/docs.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-091: Transaction lifecycle
- **Priority:** P0.
- **Persona / outcome:** Independent verifier, judge, report creator. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Transaction lifecycle**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The UI distinguishes local signing, wallet pending, RPC accepted, mined, confirmed, reverted, and receipt unavailable.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-092: Confirmation policy
- **Priority:** P0.
- **Persona / outcome:** Independent verifier, judge, report creator. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Confirmation policy**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Verification checks the transaction receipt and event arguments against the report digest instead of treating a submitted transaction hash as success.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-093: Contract versioning
- **Priority:** P0.
- **Persona / outcome:** Independent verifier, judge, report creator. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Contract versioning**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Registry deployments are versioned and the evidence bundle records the exact network and contract address used.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-094: No sensitive payload on-chain
- **Priority:** P0.
- **Persona / outcome:** Independent verifier, judge, report creator. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **No sensitive payload on-chain**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The contract stores no raw weather series, personal data, API tokens, or precise locations by default.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-095: Public-chain caveat
- **Priority:** P0.
- **Persona / outcome:** Independent verifier, judge, report creator. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Public-chain caveat**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The UI states that public chain activity and minimum metadata may be immutable and visible to everyone.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-096: Offline/degraded mode
- **Priority:** P0.
- **Persona / outcome:** Independent verifier, judge, report creator. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Offline/degraded mode**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** If chain RPC is unavailable, the report remains viewable with anchor status `not anchored` or `temporarily unavailable`, never a false success badge.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

### 9. Independent verification experience
**Primary users:** Auditor, judge, anyone with report link.
**Product outcome:** Make tamper detection demonstrable in the product, not just described in documentation.

#### P-097: Verification by report ID
- **Priority:** P0.
- **Persona / outcome:** Auditor, judge, anyone with report link. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Verification by report ID**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** An independent visitor can open a public-safe verification route using an evidence/report ID.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-098: Verification by file upload
- **Priority:** P0.
- **Persona / outcome:** Auditor, judge, anyone with report link. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Verification by file upload**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A visitor can upload a downloaded evidence JSON file and the client/server recomputes the canonical digest.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-099: Digest comparison
- **Priority:** P0.
- **Persona / outcome:** Auditor, judge, anyone with report link. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Digest comparison**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The result displays expected anchored digest, recomputed digest, exact match state, and safe failure reason.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-100: On-chain lookup
- **Priority:** P1.
- **Persona / outcome:** Auditor, judge, anyone with report link. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **On-chain lookup**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The verifier resolves the registry event using chain ID, contract address, and digest or event index.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-101: Receipt validation
- **Priority:** P1.
- **Persona / outcome:** Auditor, judge, anyone with report link. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Receipt validation**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The verifier requires a successful receipt and an expected `EvidenceAnchored` event whose digest equals the report digest.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-102: Chain reorganization awareness
- **Priority:** P1.
- **Persona / outcome:** Auditor, judge, anyone with report link. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Chain reorganization awareness**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** For chains where confirmation depth matters, the app distinguishes mined from sufficiently confirmed and handles missing receipts.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-103: Unknown record behavior
- **Priority:** P1.
- **Persona / outcome:** Auditor, judge, anyone with report link. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Unknown record behavior**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Unknown digests return `not found`, not `valid`, and never fall back to a success-colored state.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-104: Malformed bundle behavior
- **Priority:** P1.
- **Persona / outcome:** Auditor, judge, anyone with report link. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Malformed bundle behavior**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Invalid JSON, unsupported schema, duplicate keys, NaN values, and unexpected types produce validation errors before digesting.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-105: Tamper scenario
- **Priority:** P0.
- **Persona / outcome:** Auditor, judge, anyone with report link. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Tamper scenario**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The demo includes a mutation to rainfall, timestamp, or model version and shows verification fail without changing the anchor.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-106: Browser-independent proof
- **Priority:** P1.
- **Persona / outcome:** Auditor, judge, anyone with report link. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Browser-independent proof**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A documented script reproduces the hash and checks the contract independently of the front end.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-107: Verification receipt
- **Priority:** P0.
- **Persona / outcome:** Auditor, judge, anyone with report link. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Verification receipt**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** An optional downloadable verification result includes verifier version, time, chain, contract, digest, and outcome.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-108: Truthful meaning
- **Priority:** P1.
- **Persona / outcome:** Auditor, judge, anyone with report link. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Truthful meaning**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Verification copy distinguishes an intact report, source provenance completeness, model validity, and external scientific confirmation.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

### 10. Existing multi-agent workflow
**Primary users:** Technical judge, analyst.
**Product outcome:** Retain the useful agent cascade without implying that blockchain itself validates AI output.

#### P-109: Agent 1 retention
- **Priority:** P1.
- **Persona / outcome:** Technical judge, analyst. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Agent 1 retention**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The existing acute physical risk pipeline remains the entry point for all new climate evidence runs.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-110: Agent 2 gate
- **Priority:** P1.
- **Persona / outcome:** Technical judge, analyst. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Agent 2 gate**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The existing threshold-triggered exposure agent is called only when configured risk rules require it, with trigger explanation logged.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-111: Agent 3 gate
- **Priority:** P1.
- **Persona / outcome:** Technical judge, analyst. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Agent 3 gate**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The financial and policy agent is conditional and its regulatory outputs are not allowed to overstate unverified legal claims.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-112: MCP/tool catalog
- **Priority:** P1.
- **Persona / outcome:** Technical judge, analyst. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **MCP/tool catalog**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Tool names, versions, parameters, descriptions, and actual implementation status are discoverable in the repository and API.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-113: Actual invocation trace
- **Priority:** P1.
- **Persona / outcome:** Technical judge, analyst. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Actual invocation trace**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Trace entries are created by real tool invocation and report the result/error; placeholder monologues are prohibited.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-114: Tool schema validation
- **Priority:** P1.
- **Persona / outcome:** Technical judge, analyst. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Tool schema validation**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Inputs and outputs have schema validation and invalid calls fail without silently substituting unrelated defaults.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-115: Agent failure isolation
- **Priority:** P1.
- **Persona / outcome:** Technical judge, analyst. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Agent failure isolation**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** One optional agent failure results in an incomplete analysis state with a reason, not invented agent results.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-116: Idempotent rerun
- **Priority:** P1.
- **Persona / outcome:** Technical judge, analyst. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Idempotent rerun**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A rerun gets a new run ID and does not overwrite the source evidence or blockchain status of a prior run.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-117: Agent provenance
- **Priority:** P1.
- **Persona / outcome:** Technical judge, analyst. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Agent provenance**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Each agent output records implementation version and whether it used real source data, heuristic calculation, or deterministic fallback.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-118: No secret leakage
- **Priority:** P1.
- **Persona / outcome:** Technical judge, analyst. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **No secret leakage**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Agent traces shown in the browser exclude credentials, request authorization headers, raw exception traces, and private endpoint data.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-119: Workflow graph
- **Priority:** P1.
- **Persona / outcome:** Technical judge, analyst. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Workflow graph**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Documentation defines the real state machine, transitions, thresholds, retries, and terminal states with references to code paths.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-120: Protocol claims
- **Priority:** P1.
- **Persona / outcome:** Technical judge, analyst. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Protocol claims**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Public docs describe the existing hub accurately and only claim official MCP conformance after protocol tests prove it.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

### 11. Impact reporting and actionability
**Primary users:** Public-interest user, municipal decision-maker, climate researcher.
**Product outcome:** Translate analysis into grounded next steps without manufacturing quantified climate impact.

#### P-121: Risk-to-action mapping
- **Priority:** P1.
- **Persona / outcome:** Public-interest user, municipal decision-maker, climate researcher. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Risk-to-action mapping**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Each risk tier maps to bounded suggested review actions and explicitly says it is decision support, not an official public warning.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-122: Impact metric definitions
- **Priority:** P1.
- **Persona / outcome:** Public-interest user, municipal decision-maker, climate researcher. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Impact metric definitions**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Each impact metric has a definition, baseline, denominator, time period, and source or estimation method.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-123: No invented lives-saved claims
- **Priority:** P1.
- **Persona / outcome:** Public-interest user, municipal decision-maker, climate researcher. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **No invented lives-saved claims**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The UI never predicts lives saved, disaster losses avoided, or emissions reduced without a defensible causal methodology.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-124: Operational priority
- **Priority:** P1.
- **Persona / outcome:** Public-interest user, municipal decision-maker, climate researcher. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Operational priority**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Risk summaries identify which fields drove the result and what evidence the operator should validate next.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-125: Evidence completeness
- **Priority:** P1.
- **Persona / outcome:** Public-interest user, municipal decision-maker, climate researcher. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Evidence completeness**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Reports identify missing measurements and data sources that would most improve reliability for the selected location.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-126: Mitigation suggestions
- **Priority:** P1.
- **Persona / outcome:** Public-interest user, municipal decision-maker, climate researcher. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Mitigation suggestions**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Recommendations are linked to the source/model facts supporting them and are phrased as optional actions for responsible personnel.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-127: Intervention logging
- **Priority:** P1.
- **Persona / outcome:** Public-interest user, municipal decision-maker, climate researcher. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Intervention logging**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Where users record an action, the system captures action type, author role if authenticated, time, and evidence reference.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-128: Before/after comparison
- **Priority:** P1.
- **Persona / outcome:** Public-interest user, municipal decision-maker, climate researcher. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Before/after comparison**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Comparisons use compatible time windows, source types, and model versions and warn when the comparison is not like-for-like.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-129: Area coverage
- **Priority:** P1.
- **Persona / outcome:** Public-interest user, municipal decision-maker, climate researcher. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Area coverage**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A dashboard never generalizes a sample hotspot result to a whole city or state without representative coverage evidence.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-130: Exportable executive brief
- **Priority:** P1.
- **Persona / outcome:** Public-interest user, municipal decision-maker, climate researcher. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Exportable executive brief**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The brief includes the risk summary, source freshness, assumptions, model version, exposure limitations, and verification status.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-131: Public communication safeguards
- **Priority:** P1.
- **Persona / outcome:** Public-interest user, municipal decision-maker, climate researcher. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Public communication safeguards**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Public-facing alerts have a draft/review state and are never dispatched automatically to the public in the hackathon prototype.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-132: Outcome evaluation plan
- **Priority:** P1.
- **Persona / outcome:** Public-interest user, municipal decision-maker, climate researcher. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Outcome evaluation plan**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The roadmap defines a pilot metric such as time-to-verify or provenance completeness before any later claims of environmental outcome.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

### 12. Regulatory and climate knowledge
**Primary users:** Enterprise risk analyst, auditor, researcher.
**Product outcome:** Keep RAG useful while eliminating fictional legal assertions.

#### P-133: Primary-source policy corpus
- **Priority:** P0.
- **Persona / outcome:** Enterprise risk analyst, auditor, researcher. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Primary-source policy corpus**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Each policy document includes official publisher, canonical source URL, title, version/date, jurisdiction, and source retrieval time.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-134: Legal claim review
- **Priority:** P1.
- **Persona / outcome:** Enterprise risk analyst, auditor, researcher. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Legal claim review**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The current embedded regulatory seed text is audited clause-by-clause and unsupported claims are removed or relabeled as illustrative examples.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-135: Citation-first answer
- **Priority:** P1.
- **Persona / outcome:** Enterprise risk analyst, auditor, researcher. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Citation-first answer**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A policy answer cites the specific document and passage from which the claim was retrieved.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-136: Abstention policy
- **Priority:** P1.
- **Persona / outcome:** Enterprise risk analyst, auditor, researcher. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Abstention policy**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** If no authoritative passage supports a legal claim, the agent says the corpus does not establish it rather than inventing a fee or mandate.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-137: Document freshness
- **Priority:** P1.
- **Persona / outcome:** Enterprise risk analyst, auditor, researcher. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Document freshness**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Changed policies trigger re-ingestion metadata and clearly show which source version underlies the answer.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-138: Chunk metadata
- **Priority:** P1.
- **Persona / outcome:** Enterprise risk analyst, auditor, researcher. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Chunk metadata**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Every vector chunk retains parent document ID, section heading, page/paragraph locator, and canonical source URL.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-139: Prompt injection isolation
- **Priority:** P1.
- **Persona / outcome:** Enterprise risk analyst, auditor, researcher. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Prompt injection isolation**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Text in uploaded or retrieved documents is treated as untrusted data and cannot change system policy or trigger blockchain writes.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-140: RAG evaluation set
- **Priority:** P1.
- **Persona / outcome:** Enterprise risk analyst, auditor, researcher. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **RAG evaluation set**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A small curated test set measures citation correctness, retrieval quality, unsupported claims, and abstention behavior.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-141: Disclosure label
- **Priority:** P1.
- **Persona / outcome:** Enterprise risk analyst, auditor, researcher. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Disclosure label**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Financial risk outputs are estimates for planning and are not described as a legally compliant VaR calculation without validation.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-142: Citation export
- **Priority:** P1.
- **Persona / outcome:** Enterprise risk analyst, auditor, researcher. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Citation export**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Executive reports preserve citations and the policy snapshot ID used for each legal/regulatory statement.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-143: No faux section numbers
- **Priority:** P1.
- **Persona / outcome:** Enterprise risk analyst, auditor, researcher. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **No faux section numbers**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The application does not invent regulation sections, penalties, certification rights, or mandatory asset thresholds.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-144: Corpus update ownership
- **Priority:** P1.
- **Persona / outcome:** Enterprise risk analyst, auditor, researcher. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Corpus update ownership**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A named maintainer and review checklist control publication of new legal or standards documents.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

### 13. UX, dashboard, and accessibility
**Primary users:** All personas and judging panel.
**Product outcome:** Use polish to reduce review effort, not to conceal gaps in data or chain state.

#### P-145: First-screen priorities
- **Priority:** P1.
- **Persona / outcome:** All personas and judging panel. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **First-screen priorities**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The first screen makes location, current data status, risk result, evidence availability, and verification state visible without excessive scrolling.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-146: Risk color semantics
- **Priority:** P1.
- **Persona / outcome:** All personas and judging panel. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Risk color semantics**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Color is paired with text/icon/contrast and never serves as the sole indicator of status.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-147: Provenance drawer
- **Priority:** P1.
- **Persona / outcome:** All personas and judging panel. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Provenance drawer**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A dedicated panel explains source origin, timestamp, transformations, fallback state, and model metadata for every displayed run.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-148: Blockchain status card
- **Priority:** P0.
- **Persona / outcome:** All personas and judging panel. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Blockchain status card**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A focused card shows network, explorer link when available, transaction state, digest, and last verification result.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-149: Loading states
- **Priority:** P1.
- **Persona / outcome:** All personas and judging panel. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Loading states**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Each external fetch, model execution, database save, and transaction step has a specific loading state and cancellation/failure behavior.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-150: Error recovery
- **Priority:** P1.
- **Persona / outcome:** All personas and judging panel. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Error recovery**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The UI provides a useful next step when an API, model, RPC endpoint, or wallet provider fails.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-151: Responsive layout
- **Priority:** P1.
- **Persona / outcome:** All personas and judging panel. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Responsive layout**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Core analysis and verification flows work at laptop and mobile widths used by judges reviewing the demo link.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-152: Keyboard access
- **Priority:** P1.
- **Persona / outcome:** All personas and judging panel. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Keyboard access**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** All actions including file upload, location selection, verification, and report export are keyboard-operable.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-153: Readable maps
- **Priority:** P1.
- **Persona / outcome:** All personas and judging panel. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Readable maps**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Maps include accessible text summaries so core meaning is not trapped in a visual layer alone.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-154: Reduced motion
- **Priority:** P1.
- **Persona / outcome:** All personas and judging panel. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Reduced motion**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Decorative animations respect reduced-motion preference and do not slow the primary path.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-155: Report print view
- **Priority:** P1.
- **Persona / outcome:** All personas and judging panel. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Report print view**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Printed or downloaded reports retain data labels, citations, QR/share link where useful, and honest caveats.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-156: No fake live indicators
- **Priority:** P1.
- **Persona / outcome:** All personas and judging panel. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **No fake live indicators**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Live/online labels derive from actual successful health checks and source timestamps, not static decoration.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

### 14. Reliability, security, and privacy
**Primary users:** Operator, developer, report owner.
**Product outcome:** Make the prototype resilient enough to be independently tested in a live judging session.

#### P-157: CORS allowlist
- **Priority:** P1.
- **Persona / outcome:** Operator, developer, report owner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **CORS allowlist**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Production CORS permits only configured frontend origins and does not combine wildcard origins with sensitive credentials.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-158: Secret handling
- **Priority:** P1.
- **Persona / outcome:** Operator, developer, report owner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Secret handling**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Keys remain server-side, `.env` files stay untracked, and no key or seed phrase is stored in evidence bundles or UI logs.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-159: Safe exception messages
- **Priority:** P1.
- **Persona / outcome:** Operator, developer, report owner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Safe exception messages**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Client responses show a stable error code and correlation ID while server logs keep redacted diagnostics.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-160: Rate limiting
- **Priority:** P1.
- **Persona / outcome:** Operator, developer, report owner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Rate limiting**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Public analysis, report lookup, verification, and upload endpoints have documented limits and payload bounds.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-161: Authentication boundary
- **Priority:** P1.
- **Persona / outcome:** Operator, developer, report owner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Authentication boundary**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The product states which routes are public and protects write operations with signer authorization or backend authentication.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-162: Input validation
- **Priority:** P1.
- **Persona / outcome:** Operator, developer, report owner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Input validation**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Every external input has type, range, length, schema version, and content-size constraints.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-163: Persistence reliability
- **Priority:** P1.
- **Persona / outcome:** Operator, developer, report owner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Persistence reliability**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** An analysis and its evidence metadata survive process restart and redeployment with clear retention policy.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-164: Transaction safety
- **Priority:** P1.
- **Persona / outcome:** Operator, developer, report owner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Transaction safety**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Repeated requests, network retries, and browser refreshes do not create misleading duplicate status or corrupt evidence links.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-165: Privacy-safe reports
- **Priority:** P1.
- **Persona / outcome:** Operator, developer, report owner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Privacy-safe reports**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Public views minimize precise coordinate disclosure and offer redaction where location sensitivity matters.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-166: Dependency hygiene
- **Priority:** P1.
- **Persona / outcome:** Operator, developer, report owner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Dependency hygiene**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The team audits pinned dependencies and scans the repository for secrets and known high-severity vulnerabilities.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-167: Backup/recovery
- **Priority:** P1.
- **Persona / outcome:** Operator, developer, report owner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Backup/recovery**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Production-like deployment defines database backup or at minimum a documented export/recovery path for hackathon evidence records.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-168: Service health
- **Priority:** P1.
- **Persona / outcome:** Operator, developer, report owner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Service health**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Health endpoints expose safe service readiness and dependency state without revealing credentials or internal exception strings.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

### 15. Submission quality and judging demonstration
**Primary users:** Judge, mentor, prospective adopter.
**Product outcome:** Prove the solution in three to five minutes using the official requirements.

#### P-169: Judging rubric coverage
- **Priority:** P1.
- **Persona / outcome:** Judge, mentor, prospective adopter. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Judging rubric coverage**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The demo gives explicit evidence for climate impact, innovation, technical execution, practical usefulness, and presentation quality.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-170: Three-to-five-minute video
- **Priority:** P1.
- **Persona / outcome:** Judge, mentor, prospective adopter. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Three-to-five-minute video**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A script and recorded demo stay within the official 3-5 minute video requirement and show actual functionality.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-171: Public repository readiness
- **Priority:** P1.
- **Persona / outcome:** Judge, mentor, prospective adopter. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Public repository readiness**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Repository documentation provides architecture, installation, data-source caveats, chain deployment, tests, and working demo links.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-172: Reproducible local start
- **Priority:** P1.
- **Persona / outcome:** Judge, mentor, prospective adopter. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Reproducible local start**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A judge can start core services using a documented command or a simpler supported mode without guessing environment variables.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-173: Live evidence anchor
- **Priority:** P1.
- **Persona / outcome:** Judge, mentor, prospective adopter. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Live evidence anchor**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The video shows a real transaction on the declared network or a visibly labeled local-chain demonstration if public-chain access fails.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-174: Tamper proof
- **Priority:** P0.
- **Persona / outcome:** Judge, mentor, prospective adopter. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Tamper proof**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The video changes one field in an exported bundle, recomputes the digest, and shows verification fail.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-175: Climate impact narrative
- **Priority:** P1.
- **Persona / outcome:** Judge, mentor, prospective adopter. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Climate impact narrative**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The demo connects an environmental signal to a responsible action or research use case rather than making only a blockchain transaction.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-176: Method transparency
- **Priority:** P1.
- **Persona / outcome:** Judge, mentor, prospective adopter. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Method transparency**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The presenter explains exactly which outputs are live source data, model predictions, formula-based estimates, and synthetic demo data.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-177: No unsubstantiated benchmarks
- **Priority:** P1.
- **Persona / outcome:** Judge, mentor, prospective adopter. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **No unsubstantiated benchmarks**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Any metric on a slide or screen is traceable to a reproducible artifact or clearly marked as a target.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-178: Adoption pathway
- **Priority:** P1.
- **Persona / outcome:** Judge, mentor, prospective adopter. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Adoption pathway**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The submission names an initial user, integration requirements, likely operational costs, and limitations to pilot deployment.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-179: Rules and eligibility
- **Priority:** P0.
- **Persona / outcome:** Judge, mentor, prospective adopter. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Rules and eligibility**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The team checks full event rules, student-only eligibility, country restrictions, permitted team composition, and required submission fields before finalizing.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-180: Deadline lock
- **Priority:** P0.
- **Persona / outcome:** Judge, mentor, prospective adopter. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Deadline lock**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The release checklist targets completion with a safety margin before the official deadline shown on Devpost.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

### 16. Delivery phases and decision gates
**Primary users:** Team lead and each workstream owner.
**Product outcome:** Prevent low-value features from displacing evidence integrity and the demo-critical path.

#### P-181: Phase A baseline audit
- **Priority:** P1.
- **Persona / outcome:** Team lead and each workstream owner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Phase A baseline audit**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The first phase establishes a factual current-state inventory and records each feature as implemented, partial, mocked, or absent.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-182: Phase B provenance repair
- **Priority:** P1.
- **Persona / outcome:** Team lead and each workstream owner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Phase B provenance repair**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** No blockchain work is considered demo-ready until source values and synthetic fallbacks have correct labels and independent time windows.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-183: Phase C evidence schema
- **Priority:** P1.
- **Persona / outcome:** Team lead and each workstream owner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Phase C evidence schema**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The team freezes canonical JSON schema and cross-language digest test vectors before contract integration.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-184: Phase D contract path
- **Priority:** P1.
- **Persona / outcome:** Team lead and each workstream owner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Phase D contract path**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A local test chain and contract unit tests pass before deployment to any shared testnet.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-185: Phase E integration
- **Priority:** P1.
- **Persona / outcome:** Team lead and each workstream owner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Phase E integration**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Backend and UI implement persistable bundle creation, actual transaction lifecycle, and independent verification end to end.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-186: Phase F safety pass
- **Priority:** P1.
- **Persona / outcome:** Team lead and each workstream owner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Phase F safety pass**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Security review checks CORS, error leakage, secrets, input bounds, policy hallucinations, and duplicate writes.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-187: Phase G demo freeze
- **Priority:** P1.
- **Persona / outcome:** Team lead and each workstream owner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Phase G demo freeze**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The demo flow is rehearsed from a clean browser/profile and all environment dependencies have a tested fallback.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-188: Cutline discipline
- **Priority:** P1.
- **Persona / outcome:** Team lead and each workstream owner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Cutline discipline**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** If time is short, defer secondary UX or optional RAG capabilities instead of weakening digest verification or provenance integrity.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-189: Owner per deliverable
- **Priority:** P1.
- **Persona / outcome:** Team lead and each workstream owner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Owner per deliverable**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Every P0 item has one directly responsible owner, reviewer, target date, and proof link in the tracker.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-190: Risk review cadence
- **Priority:** P1.
- **Persona / outcome:** Team lead and each workstream owner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Risk review cadence**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** Blockers and external provider risks are reviewed at each phase gate with a go/no-go decision.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-191: Release rollback
- **Priority:** P1.
- **Persona / outcome:** Team lead and each workstream owner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Release rollback**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** The team can revert to the last working build without losing committed evidence or representing a failed build as deployed.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

#### P-192: Post-submission plan
- **Priority:** P1.
- **Persona / outcome:** Team lead and each workstream owner. This requirement must improve a climate evidence decision, independent verification, user comprehension, or honest disclosure.
- **Requirement:** Extend the current AEGIS implementation for **Post-submission plan**. Prefer the existing module and API contracts over parallel systems; add a new abstraction only when it isolates a real source, persistence, verification, or security boundary.
- **Acceptance criteria:** A follow-up roadmap distinguishes hackathon-ready proof of concept from genuine production readiness and field validation.
- **Failure behaviour:** Missing, stale, invalid, synthetic, or unavailable data must lead to a clear degraded/incomplete state or a documented fallback. It must never silently convert missing evidence into a confident live-data claim.
- **Evidence artefact:** Capture a test, API response, UI state, contract event, source record, or reproducible run that demonstrates this requirement. Link that artefact from the issue or release checklist.
- **Integrity / privacy:** Preserve source lineage and model version where relevant. Exclude API secrets, personal identifiers, and sensitive coordinates from public chain data by default.
- **Observability:** Emit structured events with correlation ID, analysis/evidence ID when available, result state, latency, and safe error category; never log secret values.
- **Verification method:** Cover a normal case, a negative case, and a dependency-unavailable case in automated tests or documented manual acceptance evidence.
- **Dependencies:** Link to the closest existing agent, adapter, database model, frontend route, contract, or public-source review rather than creating a duplicate module.
- **Definition of done:** Implementation, tests, documentation, safe UX copy, and the evidence artefact are merged; README and public demo claims match actual behaviour.

## 8. Product-level non-functional requirements
- **Honesty:** Each metric has a provenance level and uncertainty boundary. No fake live status, invented regulatory sections, synthetic building counts presented as observed inventory, or implied model probability without calibration.
- **Reproducibility:** A given canonical bundle and schema version always produces the same digest in supported implementations.
- **Verifiability:** A stranger can recompute report integrity without trusting the dashboard's success badge.
- **Reliability:** Source timeouts, wallet rejection, RPC outage, DB error, invalid bundle and model-load failure each have distinct and recoverable states.
- **Security:** CORS is restrictive in deployment, errors are redacted, write paths are controlled, request sizes are bounded, and secrets never reach the browser.
- **Accessibility:** Keyboard navigation, visible focus, meaningful status labels, sufficient contrast and reduced-motion support are maintained.
- **Cost:** Core MVP is testable locally and does not depend on a paid LLM call to complete the proof-of-integrity workflow.
- **Scalability language:** Do not claim production scalability from Docker Compose or one manual demo. State measured concurrency/latency only when benchmark evidence exists.

## 9. Recommended blockchain design decision
Use a minimal EVM-compatible smart contract called `ClimateEvidenceRegistry`. It should record a content digest and emit an `EvidenceAnchored` event. The report, time series and explanatory text remain off-chain. A content digest is not a climate attestation from an independent scientist; it is a verifiable commitment to a specific bundle.

### Required on-chain fields (keep lean)
- Evidence digest (`bytes32`).
- Schema version or small version code.
- Issuer address, governed by a simple authorized-issuer model.
- Stable non-sensitive report reference or opaque identifier where necessary.
- Timestamp and/or block timestamp semantics, documented so they are not confused with weather observation time.
- `EvidenceAnchored` event sufficient for a third-party verifier to match the digest and issuer.

### Keep off-chain
- Complete environmental time series and large source responses.
- API tokens, credentials, seed phrases, user identifiers, and exact sensitive coordinates.
- Full LLM prompts, full policy source text, and any personal or confidential report data.
- Raw images/rasters. Store references and cryptographic digests where licences and privacy allow.

### Chain strategy
Develop and test first on a local EVM test chain. Then deploy to a public testnet only after cross-language hash fixtures and contract tests pass. The selected network should be chosen for reliable faucet availability, a usable explorer, low-friction judging, and familiar EVM tooling. If the public network is down during the recording, demonstrate local-chain flow and mark it prominently as local simulation. Do not fake a public transaction.

### What not to build
- No new token, speculative crypto asset, NFT for each weather result, carbon credit, carbon offset issuance, or emissions marketplace.
- No on-chain raw climate data or private information.
- No claim that a block timestamp is the same as source observation time.
- No frontend-only hash or arbitrary client-supplied digest that the server does not recompute.

## 10. Past climate/blockchain project analysis and lessons
The projects below come from the 2024 DLT Climate Hackathon, not the current IEEE ClimateChain event. The descriptions are useful prior examples, not proof of the current event's winning formula. Public-facing project writeups show these submissions and awards; they do not publish the judges' detailed scoring sheets, so lessons below are inferred from disclosed design choices.

### Agrify (Grand Prize)
Project description: combines satellite imagery and AI to estimate carbon sequestration in regenerative agriculture and uses Hedera Guardian for traceability in carbon markets. The writeup also mentions accuracy, regulatory and integration challenges and pilot/collaboration work. Source: https://devpost.com/software/agrify-generating-vcus-through-regenerative-agriculture
**Lesson for AEGIS:** The blockchain is attached to a clearly described climate evidence workflow. Do not copy carbon credit issuance; replicate the discipline of connecting source data, modelled output, methodology and verifiability.

### Puro.earth Enhanced Rock Weathering Methodology (Silver Medal)
Its writeup describes digitizing a defined policy methodology with defined roles, required documents, structured workflow and an audit trail for certificates. Source: https://devpost.com/software/enhance-rock-weathering-erw-methodology
**Lesson for AEGIS:** Explicit schema, roles, evidence lifecycle and auditability can be more convincing than vague claims about decentralization. Build a precise evidence schema and verifier.

### DLT Deforestation Fire Fighters (Bronze Medal)
Its writeup names the VM0015 avoided-unplanned-deforestation methodology and a workflow involving a registrant and validation/verification body using Hedera Guardian. Source: https://devpost.com/software/dlt-deforestation-fire-fighters
**Lesson for AEGIS:** Use domain vocabulary carefully, describe actors and workflow, and tie claims to a known source methodology. For AEGIS, climate-risk evidence and integrity validation are the scope; do not imply a formal standard certification without the authority/process to support it.

### Regen (Bronze Medal)
The project combines farmer lending and crowdfunding for carbon-offset projects with smart contracts and policy workflows. Source: https://devpost.com/software/regen-w861mb
**Lesson for AEGIS:** Blockchain should make a concrete user workflow more trustworthy. Adding transaction buttons without solving a report-sharing and tamper-detection problem would be weak.

### Cross-winner pattern to apply, without overclaiming
1. Start with a named climate problem and a well-defined primary user.
2. Define the evidence or methodology artefact that is being processed.
3. Show the roles and lifecycle from input to result, approval or verification.
4. Make the blockchain/ledger's job specific and testable.
5. Show a working end-to-end demonstration and disclose what is prototype-only.
6. Ground emissions/carbon claims in established methods instead of generating market claims from model output.

## 11. Demo storyboard (3-5 minutes)
| Time | Screen / action | Message | Proof |
|---|---|---|---|
| 0:00-0:25 | Problem and selected track | Climate data is fragmented and shared risk reports are hard to independently verify. | One sentence problem, one target persona. |
| 0:25-0:55 | Choose a location; open provenance | AEGIS distinguishes observed, forecast, heuristic and synthetic fields. | Provider name, source time, temporal window, data-quality warnings. |
| 0:55-1:40 | Run AEGIS analysis | Existing agents turn data into a risk explanation. | Real model/tool results, thresholds, model ID and uncertainty label. |
| 1:40-2:15 | Inspect evidence bundle | The result has reproducible provenance and version metadata. | Canonical JSON preview and computed digest. |
| 2:15-3:00 | Anchor digest and verify transaction | The chain records a compact evidence commitment, not the raw weather data. | Network, contract, tx hash, receipt and decoded event. |
| 3:00-3:35 | Tamper with one field | The changed report no longer matches its earlier commitment. | Digest mismatch and verifier fail state. |
| 3:35-4:10 | Restore bundle and summarize value | Independent verification makes report sharing more trustworthy. | Pass state, use case, adoption path and limitations. |
| 4:10-4:40 | Architecture and next step (optional) | A realistic roadmap separates demo proof from field-grade deployment. | Public repo, test command, limitation note. |

### Presenter should say explicitly
- What data is live and what is a labelled fixture.
- What AEGIS's ML score means and whether it is calibrated.
- Which exposure values are estimates until verified GIS inputs are added.
- What the chain proves: integrity of the anchored content. What it does not prove: source truth, model accuracy, or official warning status.
- Why there is no token: it is not needed to solve this user's problem.

## 12. Release checklist
- [ ] Current implementation inventory updated; undocumented Next.js claims removed.
- [ ] Observed/forecast/synthetic labels flow through backend, frontend, export, and bundle.
- [ ] Seven-day rainfall uses an independent temporal window or returns unavailable.
- [ ] Heuristic geospatial outputs are labelled; any claim of real DEM/building spatial analysis is backed by source data.
- [ ] Regulatory seed corpus audited against official sources; unsupported claims removed.
- [ ] Model metrics reproduced and model card committed or metrics removed from claims.
- [ ] Evidence canonicalization and digest test vectors match in Python, TypeScript and Solidity.
- [ ] Contract role, duplicate, invalid input and event tests pass.
- [ ] Persisted evidence and transaction records survive backend restart.
- [ ] Tampered bundle fails verification; original bundle verifies through the registry event/receipt.
- [ ] Production CORS and error redaction are tested.
- [ ] Public repository quickstart and demo video reflect the actual code.
- [ ] Team rechecks current Devpost rules, eligibility, team constraints, deadline and submission fields.

## 13. Official and reference sources
- IEEE ClimateChain Global Hackathon 2026, official Devpost page, requirements, tracks, judging criteria and deadline: https://ieee-climatechain-hack.devpost.com/
- Agrify project description (DLT Climate Hackathon): https://devpost.com/software/agrify-generating-vcus-through-regenerative-agriculture
- Puro.earth Enhanced Rock Weathering Methodology submission: https://devpost.com/software/enhance-rock-weathering-erw-methodology
- DLT Deforestation Fire Fighters submission: https://devpost.com/software/dlt-deforestation-fire-fighters
- Regen project submission: https://devpost.com/software/regen-w861mb
- Existing AEGIS repository: https://github.com/Niss54/AEGIS

## 14. Final product decision
The strongest coherent version is an evidence-first AEGIS: climate input provenance, a transparent and appropriately caveated risk result, a deterministic report digest, a small registry contract, and independent tamper verification. Improve the truthfulness of the data before adding complexity. A production-ready claim comes only after the operational, scientific and security gates in PRD 2 are actually satisfied.
