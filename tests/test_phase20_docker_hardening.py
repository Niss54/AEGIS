"""
AEGIS-CLIMATE Phase 20 Verification Test Suite
Multi-Stage Dockerfile Hardening & Google Cloud Run Serverless Packaging
Governance: Gravitas Reliability Runtime · Mathematical Invariant Verification
"""
import os
import time
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.docker_package import (
    DockerPackagingController,
    ContainerPackageModel,
    ContainerBudgetResult,
    evaluate_container_image_budget,
    inspect_dockerfile_security,
    get_cloud_run_spec,
    MAX_IMAGE_SIZE_MB,
    MAX_VULNERABILITIES
)
from mcp_hub.hub import execute_tool_logic


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_phase_20_execution_invariant():
    """
    Verification Target: PRD Phase 20 Invariant Gate.
    Asserts ContainerPackageModel schema validation, ImageSize <= 250MB, Vulnerabilities = 0.
    """
    controller = DockerPackagingController()
    sample_payload = {
        "event_id": "TEST-PHASE-20",
        "image_size_mb": 215.0,
        "vulnerability_count": 0,
        "non_root_user": True
    }
    result = await controller.execute_phase_pipeline(sample_payload)
    assert isinstance(result, ContainerPackageModel)
    assert result.event_id == "TEST-PHASE-20"
    assert result.verified_flag is True
    assert result.metadata["status"] == "OPERATIONAL"
    assert result.metadata["phase_id"] == 20
    assert "container_budget_evaluation" in result.metadata
    budget_eval = result.metadata["container_budget_evaluation"]
    assert budget_eval["size_compliant"] is True
    assert budget_eval["vulnerability_compliant"] is True
    assert budget_eval["security_verdict"] == "PASSED_HARDENED_PRODUCTION"


@pytest.mark.asyncio
async def test_phase_20_empty_payload_rejection():
    """Asserts that empty payload is rejected with ValueError."""
    controller = DockerPackagingController()
    with pytest.raises(ValueError) as excinfo:
        await controller.execute_phase_pipeline({})
    assert "Empty payload rejected" in str(excinfo.value)


def test_mathematical_governing_equation_container_budget():
    """
    Governing Equation Invariant:
        ImageSize <= 250MB, Vulnerabilities = 0
    """
    # Case 1: Standard compliant build (215MB, 0 CVEs)
    res1 = evaluate_container_image_budget(image_size_mb=215.0, vulnerability_count=0, non_root_user=True)
    assert res1.size_compliant is True
    assert res1.vulnerability_compliant is True
    assert res1.security_verdict == "PASSED_HARDENED_PRODUCTION"
    assert res1.compliance_status == "COMPLIANT"
    assert res1.budget_utilization_pct == 86.0

    # Case 2: Exact boundary limit (250.0MB)
    res2 = evaluate_container_image_budget(image_size_mb=250.0, vulnerability_count=0, non_root_user=True)
    assert res2.size_compliant is True
    assert res2.budget_utilization_pct == 100.0
    assert res2.security_verdict == "PASSED_HARDENED_PRODUCTION"

    # Case 3: Oversized image failure (280.0MB)
    res3 = evaluate_container_image_budget(image_size_mb=280.0, vulnerability_count=0, non_root_user=True)
    assert res3.size_compliant is False
    assert res3.security_verdict == "IMAGE_OVERSIZED_OPTIMIZATION_REQUIRED"
    assert res3.compliance_status == "NON_COMPLIANT_SIZE"

    # Case 4: Vulnerability gate failure (2 CVEs)
    res4 = evaluate_container_image_budget(image_size_mb=215.0, vulnerability_count=2, non_root_user=True)
    assert res4.vulnerability_compliant is False
    assert res4.security_verdict == "SECURITY_GATE_FAILED_CVE_FOUND"
    assert res4.compliance_status == "NON_COMPLIANT_VULNERABILITY"

    # Case 5: Root user security violation
    res5 = evaluate_container_image_budget(image_size_mb=215.0, vulnerability_count=0, non_root_user=False)
    assert res5.non_root_verified is False
    assert res5.security_verdict == "ROOT_USER_VIOLATION"


def test_dockerfile_static_security_inspection():
    """
    Verifies that the repository Dockerfile implements hardened multi-stage architecture:
    Stage 1: node:20-alpine
    Stage 2: python:3.12-slim
    Non-root user: UID 10001 (appuser:appgroup)
    Healthcheck: defined
    Pip flag: --no-cache-dir
    """
    inspection = inspect_dockerfile_security()
    assert inspection["status"] == "ANALYZED"
    assert inspection["is_hardened"] is True
    assert inspection["multi_stage_build"] is True
    assert inspection["stage_count"] >= 2
    assert inspection["non_root_user_enforced"] is True
    assert inspection["healthcheck_defined"] is True
    assert inspection["pip_no_cache_enforced"] is True
    assert inspection["dynamic_port_binding"] is True


def test_dockerignore_configuration():
    """
    Verifies that .dockerignore exists and prevents bulky build context transfers.
    """
    root_dir = os.path.join(os.path.dirname(__file__), "..")
    dockerignore_path = os.path.join(root_dir, ".dockerignore")
    assert os.path.exists(dockerignore_path), ".dockerignore must exist in workspace root"

    with open(dockerignore_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert ".git" in content
    assert "node_modules" in content
    assert "venv" in content
    assert "docs" in content
    assert "blockchain/artifacts" in content


def test_docker_compose_hardening():
    """
    Verifies docker-compose.yml security directives (no-new-privileges).
    """
    root_dir = os.path.join(os.path.dirname(__file__), "..")
    compose_path = os.path.join(root_dir, "docker-compose.yml")
    assert os.path.exists(compose_path), "docker-compose.yml must exist"

    with open(compose_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "no-new-privileges:true" in content


def test_cloud_run_spec():
    """
    Verifies production Google Cloud Run serverless deployment spec.
    """
    spec = get_cloud_run_spec()
    assert spec["service_name"] in ["aegis-climate-api", "aegis-climate-api"]
    assert spec["platform"] == "managed"
    assert spec["network"]["port"] == 8080
    assert spec["security"]["non_root_uid"] == 10001
    assert "resources" in spec
    assert spec["resources"]["limits"]["memory"] == "2048Mi"


@pytest.mark.asyncio
async def test_circuit_breaker_transitions():
    """
    Verifies 3-tier circuit breaker:
    CLOSED -> (3 failures) -> OPEN -> (cooldown) -> HALF_OPEN -> (success) -> CLOSED.
    """
    controller = DockerPackagingController()
    controller.cooldown_period = 0.2  # 200ms
    assert controller.circuit_state == "CLOSED"

    # Simulate 3 consecutive failures
    controller._record_failure("Docker build timeout error 1")
    controller._record_failure("Docker build timeout error 2")
    assert controller.circuit_state == "CLOSED"
    controller._record_failure("Docker build timeout error 3")
    assert controller.circuit_state == "OPEN"

    # In OPEN state, pipeline routes to fallback
    res_open = await controller.execute_phase_pipeline({
        "event_id": "TEST-CONTAINER-FALLBACK",
        "image_size_mb": 210.0
    })
    assert res_open.execution_tier == "LOCAL_FALLBACK"

    # Cooldown expires -> HALF_OPEN
    time.sleep(0.25)
    assert controller._evaluate_circuit_state() == "HALF_OPEN"

    # Successful request resets state to CLOSED
    controller._record_success()
    assert controller.circuit_state == "CLOSED"
    assert controller.failure_count == 0


def test_rest_container_endpoints(client):
    """Verifies FastAPI REST endpoints under /container and /api/v1/container."""
    # 1. Health check
    resp_h = client.get("/container/phase20/health")
    assert resp_h.status_code == 200
    data_h = resp_h.json()
    assert data_h["status"] == "healthy"
    assert data_h["phase"] == 20

    # 2. Pipeline execution
    resp_p = client.post("/container/phase20/pipeline", json={
        "event_id": "TEST-REST-PHASE-20",
        "image_size_mb": 220.0,
        "vulnerability_count": 0,
        "non_root_user": True
    })
    assert resp_p.status_code == 200
    data_p = resp_p.json()
    assert data_p["event_id"] == "TEST-REST-PHASE-20"
    assert data_p["verified_flag"] is True

    # 3. Budget validation
    resp_v = client.post("/container/spec/validate", json={
        "image_size_mb": 215.0,
        "vulnerability_count": 0,
        "base_image": "python:3.12-slim",
        "non_root_user": True
    })
    assert resp_v.status_code == 200
    data_v = resp_v.json()
    assert data_v["size_compliant"] is True
    assert data_v["vulnerability_compliant"] is True
    assert data_v["security_verdict"] == "PASSED_HARDENED_PRODUCTION"

    # 4. Cloud Run Spec
    resp_spec = client.get("/container/cloudrun/spec")
    assert resp_spec.status_code == 200
    assert resp_spec.json()["service_name"] in ["aegis-climate-api", "aegis-climate-api"]

    # 5. Dockerfile Inspection
    resp_d = client.get("/container/dockerfile/inspect")
    assert resp_d.status_code == 200
    assert resp_d.json()["is_hardened"] is True


def test_mcp_tools_execution():
    """Verifies Phase 20 MCP tools registered and dispatched correctly."""
    # 1. evaluate_container_image_budget
    res1 = execute_tool_logic("evaluate_container_image_budget", {
        "image_size_mb": 220.0,
        "vulnerability_count": 0,
        "non_root_user": True
    })
    assert res1["size_compliant"] is True
    assert res1["vulnerability_compliant"] is True
    assert res1["security_verdict"] == "PASSED_HARDENED_PRODUCTION"

    # 2. get_cloud_run_deployment_spec
    res2 = execute_tool_logic("get_cloud_run_deployment_spec", {})
    assert res2["service_name"] in ["aegis-climate-api", "aegis-climate-api"]
    assert res2["platform"] == "managed"

    # 3. inspect_dockerfile_security_layers
    res3 = execute_tool_logic("inspect_dockerfile_security_layers", {})
    assert res3["is_hardened"] is True
    assert res3["stage_count"] >= 2
    assert res3["non_root_user_enforced"] is True
