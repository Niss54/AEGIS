"""
TERRA-SENTINEL Phase 21 Verification Test Suite
Google Cloud Build Automation (`cloudbuild.yaml`) & CI/CD Pipeline
Governance: Gravitas Reliability Runtime · Mathematical Invariant Verification
"""
import os
import time
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.cloud_ci import (
    CloudCIController,
    CloudBuildModel,
    CIBuildStepResult,
    evaluate_ci_pipeline_sequence,
    inspect_cloudbuild_yaml,
    simulate_ci_trigger
)
from mcp_hub.hub import execute_tool_logic


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_phase_21_execution_invariant():
    """
    Verification Target: PRD Phase 21 Invariant Gate.
    Asserts CloudBuildModel schema validation and GitPush(main) ==> Test ==> Build ==> Deploy(CloudRun).
    """
    controller = CloudCIController()
    sample_payload = {
        "event_id": "TEST-PHASE-21",
        "steps": ["run-pytest", "build-image", "push-image", "deploy-cloud-run"],
        "branch": "main"
    }
    result = await controller.execute_phase_pipeline(sample_payload)
    assert isinstance(result, CloudBuildModel)
    assert result.event_id == "TEST-PHASE-21"
    assert result.verified_flag is True
    assert result.metadata["status"] == "OPERATIONAL"
    assert result.metadata["phase_id"] == 21
    assert "pipeline_evaluation" in result.metadata
    eval_meta = result.metadata["pipeline_evaluation"]
    assert eval_meta["is_compliant"] is True
    assert eval_meta["verdict"] == "PASSED_STRICT_INVARIANT_GATE"


@pytest.mark.asyncio
async def test_phase_21_empty_payload_rejection():
    """Asserts that empty payload is rejected with ValueError."""
    controller = CloudCIController()
    with pytest.raises(ValueError) as excinfo:
        await controller.execute_phase_pipeline({})
    assert "Empty payload rejected" in str(excinfo.value)


def test_mathematical_governing_equation_pipeline_order():
    """
    Governing Equation Invariant:
        GitPush(main) ==> Test ==> Build ==> Deploy(CloudRun)
    """
    # Case 1: Standard compliant sequence
    res1 = evaluate_ci_pipeline_sequence(
        steps=["test", "build", "push", "deploy"],
        branch="main"
    )
    assert res1.is_compliant is True
    assert res1.order_valid is True
    assert res1.verdict == "PASSED_STRICT_INVARIANT_GATE"
    assert res1.status == "COMPLIANT"

    # Case 2: Zero-test deployment gate rejection
    res2 = evaluate_ci_pipeline_sequence(
        steps=["build", "push", "deploy"],
        branch="main"
    )
    assert res2.is_compliant is False
    assert res2.has_mandatory_test is False
    assert res2.verdict == "ZERO_TEST_DEPLOYMENT_REJECTED"

    # Case 3: Deploy before test violation
    res3 = evaluate_ci_pipeline_sequence(
        steps=["deploy", "test", "build"],
        branch="main"
    )
    assert res3.is_compliant is False
    assert res3.verdict == "DEPLOY_BEFORE_TEST_VIOLATION"

    # Case 4: Deploy before build violation
    res4 = evaluate_ci_pipeline_sequence(
        steps=["test", "deploy", "build"],
        branch="main"
    )
    assert res4.is_compliant is False
    assert res4.verdict == "DEPLOY_BEFORE_BUILD_VIOLATION"

    # Case 5: Direct deployment attempt from non-main branch
    res5 = evaluate_ci_pipeline_sequence(
        steps=["test", "build", "deploy"],
        branch="feature/risk-model"
    )
    assert res5.is_compliant is False
    assert res5.verdict == "DIRECT_DEPLOY_FROM_NON_MAIN_BRANCH_DISALLOWED"

    # Case 6: Non-main branch test-only validation pass
    res6 = evaluate_ci_pipeline_sequence(
        steps=["test"],
        branch="feature/risk-model"
    )
    assert res6.is_compliant is True
    assert res6.verdict == "BRANCH_TEST_VALIDATION_PASSED"


def test_cloudbuild_yaml_static_inspection():
    """
    Verifies that cloudbuild.yaml exists, parses correctly, and defines the mandatory 4-step pipeline:
    1. run-pytest
    2. build-image
    3. push-image
    4. deploy-cloud-run
    """
    inspection = inspect_cloudbuild_yaml()
    assert inspection["status"] == "VALIDATED"
    assert inspection["valid"] is True
    assert inspection["total_steps"] >= 4
    assert inspection["has_automated_tests"] is True
    assert inspection["has_container_build"] is True
    assert inspection["has_cloud_run_deploy"] is True
    assert inspection["region"] == "asia-south1"
    assert inspection["target_service"] == "terra-sentinel"


def test_github_actions_workflows():
    """
    Verifies .github/workflows/deploy.yml and .github/workflows/ci.yml existence and properties.
    """
    root_dir = os.path.join(os.path.dirname(__file__), "..")
    deploy_path = os.path.join(root_dir, ".github", "workflows", "deploy.yml")
    ci_path = os.path.join(root_dir, ".github", "workflows", "ci.yml")

    assert os.path.exists(deploy_path), "deploy.yml must exist"
    assert os.path.exists(ci_path), "ci.yml must exist"

    with open(deploy_path, "r", encoding="utf-8") as f:
        deploy_content = f.read()
    assert "branches: [ main ]" in deploy_content or "branches: [main]" in deploy_content
    assert "cloud run deploy" in deploy_content.lower() or "deploy to google cloud run" in deploy_content.lower()

    with open(ci_path, "r", encoding="utf-8") as f:
        ci_content = f.read()
    assert "pytest" in ci_content
    assert "npm" in ci_content


def test_simulation_git_push_trigger():
    """
    Tests simulation of Git Push trigger on main vs feature branches.
    """
    # Main branch push triggers build and deploy
    main_plan = simulate_ci_trigger(branch="main", commit_sha="abc1234567")
    assert main_plan["action_taken"] == "BUILD_AND_DEPLOY"
    assert main_plan["pipeline_compliant"] is True
    assert main_plan["cloud_run_service"] == "terra-sentinel"

    # Feature branch push triggers test-only
    feat_plan = simulate_ci_trigger(branch="feature/bilingual", commit_sha="def7890123")
    assert feat_plan["action_taken"] == "TEST_ONLY"
    assert feat_plan["cloud_run_service"] == "NONE"


@pytest.mark.asyncio
async def test_circuit_breaker_transitions():
    """
    Verifies 3-tier circuit breaker:
    CLOSED -> (3 failures) -> OPEN -> (cooldown) -> HALF_OPEN -> (success) -> CLOSED.
    """
    controller = CloudCIController()
    controller.cooldown_period = 0.2  # 200ms
    assert controller.circuit_state == "CLOSED"

    # Simulate 3 consecutive failures
    controller._record_failure("Cloud Build quota exceeded 1")
    controller._record_failure("Cloud Build quota exceeded 2")
    assert controller.circuit_state == "CLOSED"
    controller._record_failure("Cloud Build quota exceeded 3")
    assert controller.circuit_state == "OPEN"

    # In OPEN state, pipeline routes to fallback
    res_open = await controller.execute_phase_pipeline({
        "event_id": "TEST-CI-FALLBACK",
        "branch": "main"
    })
    assert res_open.execution_tier == "LOCAL_FALLBACK"

    # Cooldown expires -> HALF_OPEN
    time.sleep(0.25)
    assert controller._evaluate_circuit_state() == "HALF_OPEN"

    # Successful request resets state to CLOSED
    controller._record_success()
    assert controller.circuit_state == "CLOSED"
    assert controller.failure_count == 0


def test_rest_ci_endpoints(client):
    """Verifies FastAPI REST endpoints under /ci and /api/v1/ci."""
    # 1. Health check
    resp_h = client.get("/ci/phase21/health")
    assert resp_h.status_code == 200
    data_h = resp_h.json()
    assert data_h["status"] == "healthy"
    assert data_h["phase"] == 21

    # 2. Pipeline execution
    resp_p = client.post("/ci/phase21/pipeline", json={
        "event_id": "TEST-REST-PHASE-21",
        "steps": ["test", "build", "push", "deploy"],
        "branch": "main"
    })
    assert resp_p.status_code == 200
    data_p = resp_p.json()
    assert data_p["event_id"] == "TEST-REST-PHASE-21"
    assert data_p["verified_flag"] is True

    # 3. Pipeline step validation
    resp_v = client.post("/ci/validate/pipeline", json={
        "steps": ["test", "build", "push", "deploy"],
        "branch": "main",
        "target_platform": "Google Cloud Run"
    })
    assert resp_v.status_code == 200
    data_v = resp_v.json()
    assert data_v["is_compliant"] is True
    assert data_v["verdict"] == "PASSED_STRICT_INVARIANT_GATE"

    # 4. Cloud Build config
    resp_c = client.get("/ci/cloudbuild/config")
    assert resp_c.status_code == 200
    assert resp_c.json()["valid"] is True
    assert resp_c.json()["total_steps"] >= 4

    # 5. Simulate trigger
    resp_t = client.post("/ci/simulate/trigger", json={
        "branch": "main",
        "commit_sha": "f1234567"
    })
    assert resp_t.status_code == 200
    assert resp_t.json()["action_taken"] == "BUILD_AND_DEPLOY"


def test_mcp_tools_execution():
    """Verifies Phase 21 MCP tools registered and dispatched correctly."""
    # 1. validate_ci_pipeline_step
    res1 = execute_tool_logic("validate_ci_pipeline_step", {
        "steps": ["test", "build", "push", "deploy"],
        "branch": "main"
    })
    assert res1["is_compliant"] is True
    assert res1["verdict"] == "PASSED_STRICT_INVARIANT_GATE"

    # 2. get_cloud_build_configuration
    res2 = execute_tool_logic("get_cloud_build_configuration", {})
    assert res2["valid"] is True
    assert res2["region"] == "asia-south1"

    # 3. simulate_git_push_ci_trigger
    res3 = execute_tool_logic("simulate_git_push_ci_trigger", {
        "branch": "main",
        "commit_sha": "abc1234"
    })
    assert res3["action_taken"] == "BUILD_AND_DEPLOY"
    assert res3["pipeline_compliant"] is True
