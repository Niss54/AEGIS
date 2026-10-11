# PRD 2: AEGIS-CLIMATE Engineering Specification, Blockchain, Data Trust and Production Readiness

> **Repository:** https://github.com/Niss54/AEGIS  
> **Target event:** IEEE ClimateChain Global Hackathon 2026  
> **Created:** 14 October 2026  
> **Status:** Detailed implementation specification, not an assertion of completion  
> **Required client:** Existing React/Vite/TypeScript frontend  
> **Required backend baseline:** Existing FastAPI service and climate agent modules  

## 0. Engineering mandate
Implement a truthful, repeatable and independently verifiable climate evidence workflow on top of the existing AEGIS repository. Do not rewrite the product, introduce a new app, or add blockchain decoration. Work in small increments, keep old APIs backwards compatible where possible, and attach automated evidence to every completed P0 item.

## 1. Source-code baseline observed
The public repo tree includes `frontend/src/App.tsx`, Vite configuration and package lock; `backend/app/main.py`, `routes/analyze.py`, `agent1_ml.py`, `agent2_geo.py`, `agent3_financial.py`, schemas and websocket manager; `mcp_hub/hub.py` and registry; `backend/models/flood_classifier.pkl` with `model_metadata.json`; Dockerfiles and `docker-compose.yml`; and several agent/MCP/integration tests.

### Findings that must affect implementation decisions
- Frontend is React/Vite/TypeScript (current package) even though portions of existing README/PRD say Next.js. The new implementation should use actual stack and update the docs rather than migrating frameworks.
- The event history in `backend/app/routes/analyze.py` is process-local. Do not treat it as durable source-of-truth for evidence or blockchain status.
- `mcp_hub/hub.py` derives seven-day rainfall from 24-hour rainfall by a fixed multiplier. This is not an independent seven-day measurement.
- `backend/app/agent2_geo.py` contains formula-based exposure calculations and derives structure counts from a score. A genuine DEM/building inventory pipeline must be independently implemented before claiming those values are physically observed geospatial outputs.
- `backend/app/agent3_financial.py` embeds legal/policy text with very specific claims but no complete primary-source citation metadata in the visible seed records. Review and correct those before they appear as legal facts.
- `backend/app/main.py` permits wildcard CORS and returns raw exception strings to clients. Harden both.
- Metadata claims 95.14% accuracy and 0.9056 macro-F1. Re-run the documented training/evaluation path and inspect data splits before presenting them as evidence.
- MCP is described by the repo as a JSON-RPC 2.0 gateway. Conformance to the official protocol should be asserted only if the required protocol exchange and tool schemas are tested.

## 2. High-level architecture and trust boundaries
```text
Browser / React + TypeScript
  | REST calls / optional wallet signing / standalone verifier
  v
FastAPI public application
  |-- authentication and request validation
  |-- source adapters (live API / test fixtures, provenance attached)
  |-- current AEGIS analysis agents and versioned model tools
  |-- evidence schema + canonicalizer + Keccak-256 module
  |-- database persistence + outbox/transaction lifecycle
  |-- blockchain adapter (chain allowlist, contract interface, receipt parser)
  |-- independent verification API
  v
PostgreSQL / PostGIS (reports, provenance, evidence metadata, tx lifecycle)
Off-chain evidence object (canonical JSON, access policy, integrity recheck)
  | digest only + minimal public metadata
  v
EVM registry contract / event logs
  | third-party query by chain ID, address, digest, event and receipt
  v
Independent verification client recomputes digest and validates receipt
```

### Security boundaries
- Browser is untrusted; it can change JSON, request fields, and reported digests.
- Weather/provider responses are untrusted external input until schema, ranges, timestamps, and units are validated.
- Retrieved policy documents are untrusted data and cannot alter application policy or authorize chain transactions.
- Private signer material, API credentials and DB credentials remain server-side.
- A valid on-chain digest is only an integrity check for the committed content. Upstream source truth and model science need independent validation.

## 3. Recommended repository additions
```text
contracts/ClimateEvidenceRegistry.sol
contracts/test/ClimateEvidenceRegistry.test.ts
contracts/deploy/deploy-registry.ts
contracts/hardhat.config.ts (or Foundry configuration if selected)
backend/app/evidence/
  schema.py
  canonicalize.py
  digest.py
  service.py
backend/app/chain/
  config.py
  evm_client.py
  registry_adapter.py
  receipt_verifier.py
backend/app/db/
  models.py
  migrations/
backend/app/routes/evidence.py
frontend/src/components/EvidencePanel.tsx
frontend/src/components/AnchorStatus.tsx
frontend/src/pages/VerifyEvidence.tsx (or equivalent routing in current app)
schemas/climate-evidence.v1.schema.json
tests/test_evidence_canonicalization.py
tests/test_evidence_api.py
tests/test_chain_local_e2e.py
docs/THREAT_MODEL.md
docs/DATA_PROVENANCE.md
docs/CHAIN_DEPLOYMENT.md
docs/PRODUCTION_READINESS.md
```
These paths are suggested boundaries; follow current repo conventions where a clear equivalent already exists. Do not create multiple competing modules for the same responsibility.

## 4. Priority and merge gates
- **P0 - trust critical:** truthful input windows and labels, evidence schema, deterministic digest, contract/event, receipt validation, tamper failure, safe exception handling, secret safety, regression tests.
- **P1 - judge and deployment readiness:** durable database records, responsive verifier, chain failure states, data-source registry, model card/evaluation, policy corpus corrections, reproducible Docker/local test workflow.
- **P2 - after submission:** formal user accounts, multi-tenant permissions, hardware sensor ingestion, institutional attestations, multi-chain support, large-scale GIS data, production operations.
Do not drop P0 work to fit P2 features. A locally verified proof is better than a dashboard that visually claims a transaction but cannot prove the stored data.

## 5. Engineering requirements and acceptance evidence
Every requirement below should map to an implementation issue, code path, tests and evidence. Keep external service calls behind adapters so local development and judge review remain reproducible.

### 1. Repository baseline and implementation truth

#### E-001: Framework documentation
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Documentation identifies the actual React 19 + Vite + TypeScript frontend and does not claim Next.js until code has actually migrated.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-002: Code inventory
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** An automated inventory maps existing routes, agents, model files, MCP hub, frontend panels, Docker services, and test modules.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-003: Implementation labels
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Every capability is classified as real API-backed, trained-model-backed, formula heuristic, synthetic fallback, placeholder, or not implemented.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-004: Branch protection
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Work proceeds on a named feature branch with a clean baseline commit and no destructive rewrite of the existing repository.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-005: Reproducible environment
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Python and Node versions, lockfiles, package installation commands, and environment preconditions are documented and tested.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-006: Build baseline
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Backend tests and frontend production build run before feature work, with failures triaged and captured as baseline evidence.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-007: Dependency graph
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The team documents which modules import ML/GIS/RAG engines and removes avoidable import-time side effects where practical.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-008: Configuration loading
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Settings have typed defaults, environment overrides, validation at startup, and no unsafe hard-coded production credentials.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-009: Error taxonomy
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The backend defines stable machine-readable errors for validation, source unavailable, model unavailable, database failure, chain failure, and verification mismatch.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-010: No false MCP claim
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Protocol behavior is tested against the declared MCP version or documentation calls it a custom JSON-RPC tool gateway.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-011: Change map
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Each PRD requirement maps to actual repository paths, tests, migration files, and acceptance evidence.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-012: Release identity
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Each build records release version and source revision, displayed by health/API and embedded in evidence metadata.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

### 2. Meteorological source adapter

#### E-013: Provider adapter
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Weather access is isolated behind an adapter with typed response schema, timeout, retry policy, and provider metadata.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-014: Correct rolling windows
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** 24-hour and 7-day precipitation are calculated from independent time-series windows with missing-hour checks and units retained.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-015: Observed and forecast split
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The adapter does not mix forecast values with observed values without explicit field-level provenance.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-016: Soil moisture semantics
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Soil moisture fractions are not relabeled as percent soil saturation without a documented and validated conversion model.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-017: Temperature and humidity validation
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Provider values are range-checked and nulls remain null or trigger a declared fallback path.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-018: Source observation time
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The parser preserves the timestamp of each observation rather than attaching only the time when the request was made.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-019: Geo query validation
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Latitude, longitude, timezone, temporal range, and query size are validated before creating the request.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-020: Cache key correctness
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Cached weather vectors are keyed by normalized coordinates, source, window, variables, and data version, with clear expiry.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-021: Timeout budget
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A slow source cannot hold the request indefinitely and timeout values are configurable for local/test/deployed environments.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-022: Rate-limit respect
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** HTTP 429 and provider quota errors use bounded backoff and never trigger rapid request loops.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-023: Synthetic fallback schema
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Fallback data includes `is_synthetic`, `fallback_reason`, and scenario ID; downstream UI and evidence retain the flags.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-024: Source adapter tests
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Fixture-based tests include normal response, absent hourly rows, missing field, invalid timestamp, timeout, HTTP error, and rate limit.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

### 3. ML evaluation and model artifact

#### E-025: Reproducible training command
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The repository documents a single reproducible command to train the model and generate metadata with a fixed seed.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-026: Dataset record
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The training data has a source, retrieval date, permitted use, target label definition, sample counts, and feature definitions.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-027: Train/test isolation
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Evaluation prevents duplicates and temporal/geospatial leakage and reports the chosen holdout method.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-028: Per-class metrics
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The evaluation artifact contains confusion matrix, precision, recall, F1 per class, macro/weighted F1, and support counts.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-029: Probability calibration
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The system evaluates calibration before interpreting classifier class probabilities as calibrated flood probabilities.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-030: Model checksum
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The model file has a SHA-256 digest captured at build/runtime and included in the model card and evidence bundle.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-031: Feature schema guard
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Inference checks exact feature names, order, numeric types, ranges, and missing-value behavior before calling the estimator.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-032: Deserialization risk
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The model artifact is loaded only from a trusted packaged path and never from a user-supplied pickle or URL.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-033: Model fallback
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** If the model artifact cannot load, the system reports degraded heuristic mode explicitly and does not retain the trained-model badge.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-034: Drift baseline
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Input feature ranges and alert counts can be inspected over time; drift monitoring does not claim retraining automatically.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-035: Model test fixture
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Golden input fixtures assert schema and broad expected behavior, while avoiding brittle tests on false precision.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-036: Metric claim gate
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** README, demo overlays, and submission text use only metrics reproduced by the committed training/evaluation pipeline.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

### 4. Geospatial engine remediation

#### E-037: DEM reader integration
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** If AEGIS claims DEM-derived elevation, the code opens a real identified raster and records tile/product/version and pixel lookup.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-038: Current heuristic isolation
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Formula-based values are moved behind explicit heuristic functions and exposed as estimates, not true measured geo results.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-039: Real footprint source
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A building exposure count can be called a count only when based on a cited footprint dataset and actual spatial joins.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-040: Spatial index
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Real polygon and asset intersections use an appropriate spatial index to bound runtime for a configurable radius.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-041: CRS discipline
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Geometries are transformed to a suitable projected CRS before area or distance calculations and converted back for display.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-042: Raster nodata behavior
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Missing raster pixels and edge-of-coverage cells yield unavailable values instead of default elevation.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-043: Flood-depth provenance
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The method for inundation depth is stated explicitly; rain-derived heuristics cannot be described as hydraulic simulation.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-044: Curve source metadata
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Asset damage curves and replacement cost values carry source/date/unit/region metadata or are labeled illustrative assumptions.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-045: Scenario model separation
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Long-horizon factors remain scenario assumptions unless a climate projection dataset and approved method are integrated.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-046: GeoJSON validity
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Output GeoJSON complies with geometry validity, coordinate order, and finite-number checks.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-047: Geo engine benchmarks
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Tests cover low/high rainfall, low/high elevation, zero/near-zero radius, missing raster, and geometry boundaries.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-048: Map provenance fields
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Every feature includes a stable layer type, provenance level, generated-at time, source ID, and limitations label.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

### 5. Regulatory RAG hardening

#### E-049: Corpus audit
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Each existing seeded regulatory passage is checked against an official primary source; unsupported legal content is deleted or explicitly fictionalized for tests.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-050: Source manifest
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Every ingested document stores canonical URL, issuing body, title, version/effective date, retrieval timestamp, jurisdiction, and digest.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-051: PDF parsing pipeline
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Document ingestion preserves page/section locators and extracts text with robust error reporting and content size limits.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-052: Chunk boundaries
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Chunking respects section boundaries and attaches parent/source locator metadata to every chunk.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-053: Embedding/version manifest
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The corpus records embedding model ID, dimensions, version, chunker settings, and index rebuild ID.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-054: Retrieval metrics
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A curated evaluation suite measures recall@k, citation precision, no-answer behavior, and unsupported legal assertions.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-055: Citation output schema
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Responses return cited snippet, canonical URL, document version, locator, retrieval score, and explanation of uncertainty.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-056: Abstention threshold
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Low-relevance retrieval leads to a documented no-answer response rather than filling gaps with generated policy content.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-057: Prompt-injection handling
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Retrieved text is presented as data, sanitized, length-bounded, and unable to trigger wallet signing or contract calls.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-058: Index consistency
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Database and vector index entries can be rebuilt from the authoritative manifest without duplicate IDs or orphaned chunks.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-059: User-upload isolation
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Uploaded documents enter a quarantined user corpus and are never silently promoted to official regulatory corpus.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-060: Legal disclaimer
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Policy answer exports clarify that RAG outputs are research support, not legal advice or official compliance certification.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

### 6. Canonical evidence schema and digest

#### E-061: Schema definition
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Add a versioned JSON Schema file for climate evidence bundles with required properties, enums, ranges, and additional-property policy.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-062: Canonicalization spec
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Document canonical JSON rules including UTF-8, property ordering, number normalization, timestamp form, Unicode normalization, and null policy.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-063: Preimage function
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** One shared function builds the digest preimage by excluding hash, transaction, and verification fields that are not part of report content.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-064: Keccak choice
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The design explicitly chooses a Solidity-compatible keccak256 digest and avoids accidentally substituting SHA3-256.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-065: Cross-language fixtures
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A fixed canonical bundle has an expected digest that passes in Python, TypeScript, and Solidity tests.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-066: Deterministic arrays
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Arrays are sorted by documented stable keys only where semantic order is irrelevant; ordered time series remain chronological.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-067: Numeric representation
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Non-finite floats are rejected and values use documented precision/rounding rules before canonical serialization.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-068: Hash versioning
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The evidence metadata records hash algorithm and canonicalization version, and future versions preserve old verification support.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-069: Server ownership
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The backend validates and canonicalizes evidence itself; client-supplied digest claims are recomputed and rejected on mismatch.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-070: Sensitive-field filtering
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The bundle builder uses an allowlist and redacts secrets, user identifiers, and exact coordinates unless approved by configuration.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-071: Bundle schema evolution
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Required/optional changes create a new schema version with migration and backward-verification tests.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-072: Export/import round trip
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Exporting, downloading, uploading, parsing, and re-hashing a bundle yields the same digest without hidden mutable fields.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

### 7. Solidity registry contract

#### E-073: Minimal contract scope
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The contract anchors evidence digests and emits events; it does not claim that a registered climate estimate is true or certified.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-074: Registry record structure
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A record includes evidence digest, schema version, issuer, recorded timestamp/reference, and status needed for lookup.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-075: EvidenceAnchored event
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A typed event exposes indexed digest and report identifier plus schema version and issuer information.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-076: Duplicate digest defense
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A mapping prevents accidental duplicate records or emits a clearly defined already-registered outcome without double-count ambiguity.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-077: Issuer access control
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The contract uses a small auditable role model such as owner/authorized issuer and includes tests for unauthorized writes.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-078: Input constraints
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The contract rejects zero digest, invalid schema version, empty or oversized report identifiers, and invalid configuration.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-079: No raw climate data
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The storage layout contains no raw weather time series, API keys, exact coordinates, personal data, or long report text.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-080: Event/storage strategy
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The design compares event-only evidence anchoring versus minimal storage and documents gas/privacy/retrieval trade-offs.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-081: Reentrancy relevance
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The contract has no unnecessary external calls or token transfer logic; if future external calls exist, security controls are added and tested.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-082: Pause/emergency path
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** If a pause capability is included, it is limited, documented, tested, and does not pretend to erase immutable historical events.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-083: Contract tests
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Unit tests cover successful anchor, duplicate anchor, zero digest, unauthorized issuer, version constraints, and expected events.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-084: Static analysis
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Run Solidity compiler checks plus available static analysis or explain tool limitation; resolve all severe/high issues before deployment.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

### 8. Blockchain network adapter and transaction lifecycle

#### E-085: Provider abstraction
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** An adapter isolates EVM RPC client details from product routes and supports local test chain plus configured public testnet.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-086: Chain ID allowlist
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The app checks the configured chain ID before requesting a wallet signature or transaction broadcast.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-087: Contract address validation
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The configured registry address is checksummed/validated and contract bytecode or expected deployment metadata is checked at startup.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-088: Transaction idempotency
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A stable evidence digest prevents retrying an identical anchor blindly after a network timeout.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-089: Receipt polling
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Polling is bounded with exponential backoff and returns a pending state rather than hanging the API request indefinitely.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-090: Receipt event matching
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The backend decodes the receipt and checks the event signature, evidence digest, issuer, version, and registry address.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-091: Confirmation depth
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The UI and API distinguish transaction mined from application policy-confirmed using a configurable confirmation count.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-092: Revert reporting
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A reverted transaction returns safe chain error metadata and never updates evidence to anchored.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-093: RPC failure
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Rate limit, timeouts, invalid chain, and unreachable RPC return typed errors with recoverable status.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-094: Explorer links
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Explorer URLs derive from an allowlisted configured network mapping rather than a user-provided arbitrary URL.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-095: Local-chain labeling
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Transactions on Anvil/Hardhat/local chain display a persistent local simulation label and are not described as public proof.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-096: Wallet optionality
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The MVP documents whether signing uses a user wallet, backend-owned demo signer, or relayer; secret handling follows that choice.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

### 9. FastAPI routes and service orchestration

#### E-097: Evidence creation endpoint
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A versioned endpoint creates evidence from an existing persisted analysis ID and returns bundle ID, schema version, digest, and provenance status.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-098: Anchor endpoint
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A separate endpoint requests an anchor for a stored evidence record and cannot accept arbitrary on-chain metadata without validation.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-099: Verify endpoint
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A public-safe verify endpoint accepts evidence ID or validated bundle upload and returns digest match plus chain/receipt verification.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-100: Status endpoint
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A transaction status route returns pending/confirmed/reverted/unavailable and is safe to poll.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-101: Request models
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** All new routes use Pydantic request/response models and explicit length/range constraints.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-102: Async RPC calls
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Chain I/O does not block event loop execution and uses explicit connection/request timeouts.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-103: Request idempotency
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Anchor writes use digest-level idempotency and optional idempotency keys, with documented replay behavior.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-104: Correlation IDs
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Every request and background job has a correlation ID propagated to logs and evidence error details.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-105: Safe errors
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Global exception responses omit raw exception strings and sensitive internals while server-side logs preserve redacted context.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-106: Route scopes
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Read-only verification endpoints are separated from chain write endpoints and write routes require authorization controls.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-107: OpenAPI clarity
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Generated API docs include sample payloads, error codes, and examples for synthetic versus real-data workflow.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-108: Backward compatibility
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Existing `/api/v1/analyze` and related event endpoints keep existing contracts or are versioned deliberately with tests.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

### 10. Persistence and migrations

#### E-109: Durable analysis records
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Replace process-local-only history with a database table keyed by stable analysis ID and source/model metadata.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-110: Evidence table
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Persist schema version, content digest, bundle location/reference, provenance status, and link to the source analysis.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-111: Chain transaction table
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Persist chain ID, registry address, tx hash, submit time, receipt state, block number, confirmations, and error code.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-112: Uniqueness constraints
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Database constraints prevent duplicate evidence IDs/digest records where the product contract requires uniqueness.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-113: Atomic state changes
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Evidence state and anchor lifecycle transitions commit atomically where practical and are recoverable after service restart.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-114: Migration scripts
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Versioned database migrations create and alter tables with a documented reset path for development only.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-115: Data retention
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The application documents which climate reports persist, whether they are public, and how user-supplied data is retained or deleted.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-116: JSON integrity
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Stored bundle content is re-hashed on read or background audit and mismatch is raised as a storage-integrity error.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-117: Restart recovery
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** On restart, pending transactions are reconciled using persisted hashes and receipt lookups rather than recreated.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-118: Storage fallback
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** If database is unavailable, write endpoints fail clearly or enter explicit demo-only mode; they do not imply durable save.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-119: Backup/export
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A reproducible database backup/export mechanism preserves evidence metadata and supports recovery tests.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-120: Retention and access
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Queries are scoped by public-safe IDs/permissions and pagination limits prevent accidental full-dataset extraction.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

### 11. Frontend dashboard integration

#### E-121: No framework rewrite
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** New features integrate into the existing Vite/React/TypeScript app unless a separate migration decision is justified by a measured blocker.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-122: Evidence panel
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The existing dashboard adds a provenance/evidence panel showing inputs, transformations, model identity, schema version, and digest.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-123: Anchor UX
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The user receives a clear pre-transaction explanation and confirms network, digest, visibility, and whether signing incurs any fee.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-124: Transaction states
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** UI state is derived from API status and receipt data rather than optimistic success messages.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-125: Verifier page
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A standalone route verifies a report ID or user-supplied JSON without needing access to a private workspace.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-126: Tamper sandbox
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A dedicated demo action changes a copy of the JSON bundle and shows mismatch while preserving the original anchored record.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-127: Wallet handling
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** If browser wallet integration is selected, chain mismatch, rejection, disconnected account, and pending user signature are handled.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-128: No-wallet demo
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** If a backend demo signer is used, the screen clearly labels it and restricts private signing keys to server environment secrets.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-129: Source label reuse
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Observed, forecast, synthetic, estimated, and heuristic labels appear consistently across card, map, report, and verification screen.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-130: Responsive proof view
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The digest, status, source list, and verification result remain usable at laptop and small-screen dimensions.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-131: Accessible status announcements
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Loading, chain pending, confirmation, and verification mismatch are announced accessibly and do not rely only on color.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-132: API error rendering
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Frontend handles non-2xx responses, network offline, timeout, schema mismatch, and unknown statuses without crashing.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

### 12. Security, privacy, and threat modelling

#### E-133: Threat model
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A focused threat model covers forged climate data, report tampering, fake tx receipts, malicious documents, wallet phishing, RPC compromise, and secret leakage.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-134: CORS hardening
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The permissive wildcard in the current FastAPI app is replaced with an environment-managed explicit origin allowlist for deployed environments.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-135: Exception redaction
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The current global handler no longer returns raw exception text and exposes only safe error codes plus correlation IDs.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-136: Secret scanning
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** CI and a local pre-commit path scan for API keys, RPC secrets, signing keys, tokens, and accidental `.env` commits.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-137: Signer isolation
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Any private key is stored only in deployment secret storage and never enters frontend environment bundles, logs, commits, or model prompts.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-138: Write permission checks
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Anchor endpoints authenticate/authorize requesters and contract roles independently constrain issuers.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-139: Abuse controls
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Analysis, file upload, report lookup, and RPC polling are rate-limited and protected against oversized payloads.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-140: SSRF protection
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Users cannot provide arbitrary provider URLs for backend fetch; only allowlisted sources/network endpoints are accepted.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-141: RAG prompt injection
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Untrusted source text cannot manipulate assistant role, disclose secrets, or initiate contract writes.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-142: Privacy minimization
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Coordinates and location labels are minimized on-chain and public data exposure is explained before writing.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-143: Dependency review
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Run Python/Node/Solidity dependency audits and record high-severity exceptions with owner and mitigation.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-144: Security event log
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Unauthorized anchors, hash mismatches, failed receipt checks, and validation rejections generate redacted audit events.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

### 13. Automated test strategy

#### E-145: Existing regression suite
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** All existing agent and MCP tests continue to pass or any expected change is accompanied by a documented adjusted contract.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-146: Source fixtures
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Weather adapter tests cover correct time windows, provider errors, stale observations, missing values, and synthetic fallback labels.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-147: Model evaluation test
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A test proves model metadata and evaluated metrics can be regenerated from the documented command.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-148: Evidence schema tests
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Positive and negative schema fixtures cover required fields, enums, unexpected fields, non-finite numbers, and old schema versions.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-149: Canonical digest tests
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Identical content across machines produces identical digest and one canonical-field mutation changes digest.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-150: Contract unit tests
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The local EVM suite validates role enforcement, event values, duplicates, invalid input, and version metadata.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-151: RPC integration tests
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A local-chain integration suite validates deploy, anchor, receipt decode, independent contract read, and transaction revert.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-152: Cross-language test vectors
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Python and TypeScript compute the same keccak256 value as Solidity for a canonical evidence fixture.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-153: Persistence tests
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Database integration tests verify restarts, uniqueness, pending recovery, storage corruption detection, and transaction-state updates.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-154: API contract tests
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** FastAPI tests assert status codes, response shapes, validation errors, authentication, idempotency, and safe exception output.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-155: End-to-end scenario
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** One test covers select sample input, create analysis, persist it, create bundle, anchor, verify match, mutate, and verify mismatch.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-156: Load and latency smoke test
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A bounded smoke test measures analysis, verification, and receipt polling with explicit limits rather than unfounded scalability claims.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

### 14. CI, packaging, deployment, and operations

#### E-157: CI pipeline
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Pull requests run frontend typecheck/build, backend tests, schema tests, Solidity compile/tests, secret scan, and available security checks.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-158: Docker compose
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Local development compose includes only required services and health checks, with safe non-production default credentials clearly marked.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-159: Environment sample
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** `.env.example` documents chain ID, RPC URL, contract address, explorer base, DB URL, allowed origins, and demo mode without secrets.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-160: Deployment topology
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Documentation separates frontend hosting, API/backend, database, vector store, and blockchain RPC dependencies.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-161: Startup validation
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Missing required production settings fail fast with actionable messages; optional services can be marked degraded only where supported.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-162: Readiness and liveness
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Health endpoints distinguish process liveness from readiness of database, model, source provider, and chain RPC.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-163: Migration release step
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Database migrations run as a controlled release step with backup and rollback notes instead of an uncontrolled app-start side effect.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-164: Runtime timeouts
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** External APIs, database queries, LLM calls, and blockchain requests each have explicit timeouts and bounded retries.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-165: Cost guardrails
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Public endpoints enforce request and token budgets and the demo has a deterministic offline path requiring no paid LLM.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-166: Structured logs
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Application logs are machine-readable and include request ID, analysis ID, evidence ID, and chain transaction ID without secrets.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-167: Deployment smoke test
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Post-deploy smoke script checks homepage, API readiness, sample analyze route, evidence bundle, and chain verification path.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-168: Rollback plan
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The release can restore the last known working frontend/backend versions and reconcile pending chain transactions safely.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

### 15. Demo engineering and judge proof

#### E-169: Golden sample fixture
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A public demo scenario includes a fixed coordinate/region, known source fixtures, expected output schema, and expected digest.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-170: Clear live/synthetic mode
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The demo can use live weather when available and fall back to deterministic fixtures with a persistent synthetic badge.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-171: No network dependency surprise
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The core verification demonstration is runnable locally even if a third-party weather or RPC endpoint is down.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-172: Real chain evidence
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A public-testnet demo displays verified chain ID, deployed contract address, transaction hash, block number, and decoded event.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-173: Local chain alternative
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A local EVM fallback is labelled as a local proof of function, with clear instructions that it is not public anchoring.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-174: Tampering proof
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The presenter mutates one value, demonstrates digest mismatch, then restores the untouched bundle and shows a match again.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-175: Judge quickstart
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A judge can find one quickstart path, one test command, one architecture diagram, and one demo entry point within two minutes.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-176: Video evidence
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** A 3-5 minute capture shows climate problem, source provenance, actual agent/model run, blockchain anchor, tamper detection, and user value.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-177: Fail-safe rehearsal
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Team rehearses provider outage, wallet rejection, pending transaction, RPC failure, and synthetic mode without pretending success.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-178: Judge questions
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Docs prepare concise answers to why blockchain is needed, what the hash proves, why no token is used, and what makes data reliable.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-179: Impact disclaimer
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The script clearly states that the prototype is not an official flood warning service or certified carbon accounting system.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-180: Submission parity
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Every claim, screenshot, deployed feature, and code path in the Devpost submission matches the final public repository state.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

### 16. Release acceptance and production boundary

#### E-181: P0 acceptance gate
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The release cannot be called hackathon-ready until source labels, evidence digest consistency, receipt verification, and tamper rejection pass.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-182: P1 acceptance gate
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Core demo path has tested fallback behavior, durable records, security fixes, reproducible docs, and responsive verification UI.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-183: Production claim gate
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The README says production-ready only after operational security, data validation, model validation, observability, backups, and incident handling are demonstrated.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-184: No unsupported regulatory certification
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The product does not claim legal compliance or environmental certification based solely on an AI summary or blockchain record.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-185: No unsupported scientific claims
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The product distinguishes integrity validation from external ground-truth validation and model performance generalization.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-186: Data stewardship owner
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Each data source and model artifact has an accountable maintainer, change process, and deprecation plan.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-187: Smart contract upgrade policy
- **Priority:** P0.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** The registry version and upgrade/migration policy are documented; immutable versions remain verifiable.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-188: Incident handling
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** An operational checklist covers compromised API keys, bad source values, corrupt evidence, unavailable RPC, and erroneous report withdrawal notices.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-189: Monitoring thresholds
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Service failure, stale data, model fallback, hash mismatch, tx revert, and DB failure metrics have defined alert thresholds.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-190: Accessibility release check
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Core workflows pass keyboard, contrast, semantic label, and reduced-motion review before release.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-191: Field validation plan
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Any claimed accuracy or municipal adoption is deferred until a real pilot with reference flood observations and expert review.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

#### E-192: Final sign-off
- **Priority:** P1.
- **Implementation target:** Apply the requirement within existing AEGIS modules when possible; isolate new functionality at explicit evidence, chain, persistence, or security boundaries.
- **Required behaviour:** Technical owner and product owner record which criteria pass, which are deferred, and what remains demo-only before release.
- **API/data contract:** Validate input and output schemas; preserve analysis/evidence identifiers, timestamps, source-state labels, model revision and safe error codes end to end.
- **State and idempotency:** Every write has a deliberate state transition; retries are safe, and repeated analysis/anchor requests cannot silently rewrite prior evidence.
- **Security properties:** Trust neither browser-supplied digests nor provider responses; keep secrets server-side; limit requests and reject invalid types/ranges before side effects.
- **Failure handling:** Distinguish missing input, provider outage, model fallback, DB failure, RPC outage, transaction revert, malformed receipt and digest mismatch.
- **Required tests:** Add one positive test, at least one invalid/negative test, and a dependency-failure or restart/retry case where relevant.
- **Required evidence:** Provide a test report, fixture, API response, decoded receipt/event, migration proof, CI run, or screen recording that demonstrates the behaviour.
- **Documentation:** Update the architecture/data-flow docs, configuration matrix, troubleshooting note and the list of actual limitations.
- **Definition of done:** Feature code, tests, security review, logs/metrics, documentation and a reproducible acceptance step are complete; no README claim outruns evidence.

## 6. Evidence bundle schema: normative definition
Create `climate-evidence.v1.schema.json` and implement a typed Python model with a single canonicalization function. Keep schema and code aligned through CI. Exact property names can evolve during implementation, but one version must be frozen before writing contract integration tests.

### Required top-level fields
```json
{
  "schema_version": "1.0.0",
  "evidence_id": "opaque-stable-id",
  "analysis": {
    "analysis_id": "analysis-id",
    "location": { "region_label": "Mumbai demo area", "coordinate_commitment": null },
    "created_at_utc": "2026-10-14T12:00:00Z",
    "data_mode": "live|fixture|synthetic",
    "inputs": [],
    "transformations": [],
    "risk_output": {},
    "exposure_output": {},
    "policy_output": {}
  },
  "model_manifest": { "model_id": "flood-model", "artifact_sha256": "...", "feature_schema_version": "1" },
  "code_revision": "git-sha-or-release-id",
  "limitations": [],
  "hash_algorithm": "keccak256",
  "canonicalization_version": "aegis-canonical-json-v1"
}
```
The example is a schema illustration, not a valid proof until every required nested type, range, provenance source, and digest rule is implemented. The computed digest, transaction hash, chain confirmation state and verifier result are metadata about the bundle and must not be inserted into the digest preimage itself.

### Canonicalization requirements
1. Validate the bundle against its versioned schema.
2. Normalize timestamps to ISO-8601 UTC with a trailing `Z`; keep the original source timestamp/timezone in provenance metadata.
3. Reject NaN, infinity, invalid floats, and unknown number representations.
4. Set explicit rules for Unicode normalization, UTF-8 encoding, property ordering, array ordering, null values, and decimal precision.
5. Preserve time-series order; sort only arrays whose meaning is set-like and whose sort key is defined by schema.
6. Construct the digest preimage by removing digest/transaction/verifier metadata and other mutable transport fields.
7. Canonicalize once on the server and compute Ethereum Keccak-256. Do not use Python `hashlib.sha3_256` as a drop-in replacement; Ethereum Keccak and FIPS SHA3-256 differ.
8. Store the schema version, canonicalization version and digest algorithm alongside the result so verifiers can reproduce legacy proofs.
9. Reject a digest supplied by a client when recomputation from validated bundle content does not match.
10. Maintain fixed golden fixture files and assert exact digest equality in Python, TypeScript, and Solidity/contract integration tests.

## 7. Contract interface and security scope
### Minimum contract behaviour
- `anchorEvidence(bytes32 digest, uint32 schemaVersion, bytes32 reportRef)` (interface names may change once finalized).
- Require non-zero digest and supported schema version.
- Restrict anchoring to owner/authorized issuer addresses, with deployment commands making issuer configuration reproducible.
- Prevent duplicates or return an unambiguous duplicate outcome. Define whether identical digest reuse across separate analysis IDs is allowed.
- Emit `EvidenceAnchored(bytes32 indexed digest, bytes32 indexed reportRef, uint32 schemaVersion, address indexed issuer, uint256 blockTimestamp)` or an equivalently documented event.
- Provide read/lookup behaviour appropriate to the selected event or storage strategy.
- Never store the raw weather data, narrative, private coordinates, personal data, API keys or entire report on-chain.
- Do not implement token minting, token transfers, carbon-credit issuing, financial settlement, or arbitrary external calls in the hackathon registry.

### Contract acceptance tests
- Authorized issuer anchors a valid digest; exact event args match.
- Unauthorized issuer is rejected.
- Zero digest, unsupported schema version, or malformed reference is rejected.
- Duplicate anchor returns the documented result and does not create ambiguous proof records.
- Event decoding in the backend returns same digest/address/version as the confirmed receipt.
- The frontend verifies a record from chain data without trusting a UI-supplied `anchored=true` flag.
- Static analysis/compiler warnings and test report are attached to release evidence.

## 8. Data and scientific validity requirements
### Weather inputs
- Use a genuine provider response or a committed test fixture; include source identifier, query coordinates/region, requested window, observed/forecast label, per-variable timestamp semantics, provider fetch time, units and licence/attribution metadata.
- Seven-day precipitation must be computed from its own valid seven-day series. The current fixed `24h * 2.8` estimate is not acceptable as actual rainfall.
- A soil moisture fraction is not automatically a percentage of saturated soil. Preserve raw unit and either implement a validated conversion or label any transformation as heuristic.
- If source values are unavailable, choose a labelled deterministic fixture or show an unavailable state. Never mix live values and hard-coded fallback values without per-field state metadata.

### Geospatial outputs
- If using real DEM, record product, version, raster cell/resolution, nodata behaviour and sampled values.
- If using actual buildings, record dataset source/date/licence and real spatial-intersection method.
- Existing formula-based depth, overflow, building count, damage and horizon values must be moved behind clearly named heuristic helpers and labelled in API, map, report and evidence bundle.
- A heuristic can still serve a compelling demo, but it is not presented as observed flood depth, building inventory, engineered hydraulic simulation or official infrastructure condition.

### Model evaluation
- Store the training dataset provenance and label-generation process.
- Recreate accuracy, macro-F1 and per-class metrics from the same versioned artifact.
- Validate spatial and temporal leakage; maintain a held-out set appropriate to intended geography/use.
- Check probability calibration before calling a score a flood probability. Otherwise use terms such as model risk score.
- Pin model artifact SHA-256, preprocessing revision, feature order and model-card version into every evidence bundle.

### Regulatory corpus
- Remove unsupported legal claims and any plausible-looking but unverified penalties/thresholds/section references.
- Prefer official regulator/government/standard-owner sources; maintain publication/effective dates and immutable source snapshot digest.
- Every retrieved legal statement must retain document, section/page/paragraph, canonical URL and source version.
- If no official source supports a claim, the answer abstains or labels the wording as a fictional test fixture that is not used for user-facing legal guidance.

## 9. API contract proposal
Implement new routes under `/api/v1/evidence` to keep existing analysis routes stable.

### Create bundle
`POST /api/v1/evidence` takes `{analysis_id, include_optional_policy_context, privacy_profile}` and creates a validated, persisted versioned bundle. The server fetches the stored analysis record and recomputes provenance metadata rather than trusting a full arbitrary client-authored report.
Response includes `evidence_id`, `schema_version`, `digest`, `data_mode`, `provenance_status`, `created_at_utc`, and `anchor_status=NOT_ANCHORED`.

### Request anchor
`POST /api/v1/evidence/{evidence_id}/anchor` checks authorization, configuration and status; resolves the digest from persisted content; submits the registry call; and returns `SUBMITTED` or `PENDING` with transaction ID. It must not return `CONFIRMED` until a receipt and matching event are independently validated.

### Evidence status
`GET /api/v1/evidence/{evidence_id}` returns the safe evidence summary, current anchoring lifecycle, source labels and privacy-safe metadata. Full bundle retrieval may be public or scoped according to a clear policy.

### Verify evidence
`POST /api/v1/evidence/verify` accepts a validated upload or reference. The verifier loads the proper schema version, recomputes the digest, looks up the declared chain/registry, checks receipt/event and returns separate booleans for `content_digest_matches`, `chain_record_found`, `receipt_success`, `issuer_authorized`, and `bundle_provenance_complete`.

### Transaction status
`GET /api/v1/evidence/{evidence_id}/anchor-status` returns pending/confirmed/reverted/unavailable, chain ID, registry, transaction hash, block number, confirmations, decoded digest and safe error code.

## 10. Persistence model proposal
Use PostgreSQL or existing durable database deployment. PostGIS is appropriate if real spatial queries are added. Do not assume the current Docker service means the application already persists event records there.

### `analysis_runs`
- `analysis_id` primary key.
- `created_at_utc`, location privacy policy, source mode, state and code revision.
- Serialized typed analysis output, source-manifest reference and model-manifest reference.
- Stable content checksum and soft-delete/retention metadata if reports can be deleted.

### `evidence_bundles`
- `evidence_id` primary key and foreign key to `analysis_runs`.
- `schema_version`, `canonicalization_version`, `hash_algorithm`, `digest`, bundle location or JSONB payload, provenance status, visibility, created time.
- Unique constraint on the combination required by idempotency policy.
- Re-hash-on-read or scheduled integrity check for stored bundle bytes.

### `anchor_transactions`
- Evidence reference, chain ID, registry address, signer/issuer, transaction hash, submit time and latest checked time.
- State enum: `CREATED`, `SUBMITTED`, `PENDING`, `CONFIRMED`, `REVERTED`, `UNAVAILABLE`, `FAILED_VALIDATION`.
- Block number/hash, confirmations, event digest, receipt status, safe error code and retry metadata.
- No private key storage in these application tables.

### Migration and restart behaviour
- Add versioned migrations and test upgrade from a clean database.
- On restart, reconcile submitted/pending transactions by their persisted hashes. Do not resubmit blindly.
- Use unique constraints plus an idempotent state machine so a timeout retry does not create duplicate misleading anchors.
- Document backup/export and a practical restore test for the evidence metadata required by the demo.

## 11. Test plan and acceptance gates
### P0 gates before the feature is called demo-ready
- [ ] Seven-day rainfall is independently queried or explicitly unavailable.
- [ ] Every input and derived value carries a trustworthy observed/forecast/estimated/synthetic label.
- [ ] Canonicalization golden vector matches in Python, TypeScript and Solidity test paths.
- [ ] Contract authorizes only expected issuers and emits validated digest event.
- [ ] Backend verifies receipt status, correct contract and matching event values.
- [ ] Original bundle passes; one-field mutation fails; restoring original passes again.
- [ ] A submitted tx is not displayed as confirmed before receipt validation.
- [ ] Wildcard CORS and raw client exception text are removed for deployment.
- [ ] No secrets appear in repo, public bundle, frontend output, transaction calldata beyond expected digest metadata, or logs.
- [ ] Existing agent/MCP regression tests and frontend build pass.

### P1 gates before a public judge link is shared
- [ ] Analysis/evidence/transaction states persist after backend restart.
- [ ] Local-chain end-to-end script deploys contract, anchors fixture and verifies receipt.
- [ ] Public-testnet path has tested network/contract details or the demo is clearly labelled local-chain only.
- [ ] Regulatory corpus has source citations and unsupported claims removed.
- [ ] Model card and geospatial limitation labels agree with implementation.
- [ ] Public-safe verifier works from a downloaded evidence JSON.
- [ ] Mobile/responsive view and keyboard operation pass manual acceptance checks.
- [ ] Docker/local quickstart and troubleshooting docs work from a clean checkout.

## 12. CI and local developer workflow
### Pull request checks
1. Python lint/import check and existing unit/integration tests.
2. JSON Schema validation and canonicalization fixture digest test.
3. TypeScript lint/typecheck and Vite production build.
4. Solidity compilation, unit tests and static analysis where tool availability permits.
5. Contract/backend integration test on local EVM.
6. Secret scan and dependency vulnerability checks.
7. Documentation assertions or checklist confirming no unsupported `production-ready`, live-data, accuracy, or MCP claims remain.

### Local quickstart quality bar
A clean clone must include commands for installing frontend/backend dependencies, configuring `.env`, starting required services, running tests, deploying the registry locally, creating one sample evidence bundle, anchoring it, and verifying a modified bundle fails. Optional paid APIs must not block the core digest/contract proof.

## 13. Deployment and security requirements
- Set an explicit frontend origin allowlist for deployed environments; local development origins can be added only in development configuration.
- Keep chain signer key, weather provider keys, LLM keys, database URL and JWT credentials in secret configuration. Never prefix secret frontend variables so Vite exposes them to browser code.
- Return stable error payloads such as `{error_code, message, correlation_id}`; log redacted trace details only on the server.
- Validate all coordinates, radii, time windows, uploaded JSON length, number formats, source URLs and schema versions.
- Use hard allowlists for backend source providers and blockchain network definitions to prevent SSRF and explorer-link abuse.
- Add bounded retries and timeouts for provider, database, LLM and chain RPC requests.
- Use a contract and backend state machine that survives wallet rejection, RPC lag, failed receipt lookup, backend restart and duplicate request.
- Expose distinct liveness and readiness health endpoints. Never return key material or private exception data from health checks.
- Before claiming production readiness, complete an independent contract/security review, test backup restoration, verify the source/model licence and validate hazard outputs with domain experts and reference outcomes.

## 14. Observability and operational signals
Track analysis request count/latency, provider fetch age/errors, synthetic fallback rate, model-load mode, agent execution time/error, provenance completeness, bundle digest mismatch, evidence persistence failure, transaction pending age, tx revert rate, receipt mismatch, and verification outcomes. Each metric requires a name, definition, dimensions, and action threshold. Do not log exact sensitive coordinates unless operationally required and permitted.

## 15. Suggested implementation sequence
### Phase 1: Correctness before chain
- Audit baseline APIs and claim inventory.
- Fix weather temporal semantics and propagate data-mode/provenance flags.
- Relabel current exposure formulas and audit unsupported policy text.
- Reproduce model evaluation claims and pin the model manifest.
- Harden CORS, safe errors, validation, and secret hygiene.

### Phase 2: Evidence core
- Define the JSON schema and canonicalization rule.
- Add server-side digest calculation and golden fixtures across languages.
- Persist analysis and evidence metadata.
- Build report export and local tamper-verification before adding a chain dependency.

### Phase 3: Blockchain adapter
- Implement and test the minimal registry contract.
- Deploy to local EVM, test valid/invalid roles and events.
- Integrate FastAPI chain adapter, transaction persistence and receipt verifier.
- Add public-testnet configuration and publish exact deployment metadata only after a real deployment succeeds.

### Phase 4: UX and evidence
- Add evidence panel and transaction lifecycle state.
- Add standalone verify view and mutation scenario.
- Wire report export to source citations and limitation labels.
- Complete regression, e2e, restart and failure-mode tests.

### Phase 5: Release rehearsal
- Record demo from a clean browser profile.
- Rehearse network/DB/wallet failure behaviours.
- Run local quickstart from clean clone.
- Freeze feature work; repair blockers only.
- Validate public Devpost submission and eligibility before deadline.

## 16. Open engineering decisions (must be resolved in repo docs)
1. Which EVM testnet is selected, and why is it reliably accessible for judges?
2. Is transaction signing performed by an explicit user wallet, a backend demo signer, or a relayer? What risks/costs does that choice create?
3. Is full evidence JSON publicly retrievable or must some fields remain private/redacted?
4. Which exact canonicalization library and Keccak implementation are used across Python and TypeScript?
5. How many confirmations are required before AEGIS marks a record confirmed?
6. Which actual geospatial source(s) are available under acceptable licenses within MVP scope?
7. Which authoritative policy documents replace any unsupported seed text?
8. What is the reproducible training dataset and split behind current model metrics?
9. Which features must be disabled in demo mode to avoid presenting synthetic values as live?
10. Who approves final production-readiness wording in the README and submission?

## 17. Runbook and troubleshooting checklist
- **Weather API timeout:** show provider unavailable; use only a fixture marked synthetic or report incomplete inputs.
- **Seven-day rainfall absent:** set unavailable and reduce provenance completeness; never estimate by scaling one-day rain.
- **Model not loaded:** identify degraded heuristic mode and do not show trained model identifier as active.
- **Exposure source missing:** show heuristic exposure with assumptions or suppress the metric; do not label it DEM/building inventory output.
- **RAG evidence weak:** abstain from legal claim and provide source-gap indicator.
- **Database down:** refuse durable-write success and preserve correlation ID for diagnosis.
- **Wallet rejected:** retain unanchored bundle and provide retry instructions; do not mark it anchored.
- **Wrong chain:** stop before broadcast, show expected chain ID and configured chain name.
- **RPC timeout after submit:** look up transaction hash before retrying; status remains unknown/pending until reconciled.
- **Receipt event mismatch:** mark integrity verification failed and preserve the transaction for debugging.
- **Modified evidence JSON:** show expected and computed digests, identify mismatch, and avoid revealing sensitive original fields.
- **Local test chain:** persistent label communicates that proof is local and not publicly discoverable.

## 18. Final acceptance statement
AEGIS is ready to submit as a credible hackathon prototype when a clean environment can create a transparent climate analysis, produce a deterministic evidence bundle, anchor its digest on a clearly identified chain, independently confirm the transaction event, and reject a tampered copy. It is production-ready only after source validity, model generalization, geospatial accuracy, regulatory source integrity, security, operations and domain-expert validation have separately passed. Do not collapse these two standards into one.

## 19. Reference links
- IEEE ClimateChain official page (tracks, rubric, requirements, deadline): https://ieee-climatechain-hack.devpost.com/
- Existing code: https://github.com/Niss54/AEGIS
- Prior DLT climate projects studied for workflow patterns: https://devpost.com/software/agrify-generating-vcus-through-regenerative-agriculture
- https://devpost.com/software/enhance-rock-weathering-erw-methodology
- https://devpost.com/software/dlt-deforestation-fire-fighters
- https://devpost.com/software/regen-w861mb
