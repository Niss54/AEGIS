"""
Unit & Integration Test Suite for Phase 29.3:
Crisis Cleanup 4R Inter-Agency Collaborative Disaster Relief Engine
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.crisis_cleanup import (
    crisis_cleanup_engine,
    ReliefCaseCreate,
    ClaimCaseRequest,
    UpdateWorkRequest,
    CloseCaseRequest,
    CaseStatus,
    PriorityTier,
    ReliefAgency,
    WorkType
)

client = TestClient(app)


def test_crisis_cleanup_seeded_cases_presence():
    """Validates that initial pre-seeded disaster relief work orders are present and structured correctly."""
    cases = crisis_cleanup_engine.list_cases()
    assert len(cases) >= 3

    case_ids = [c.case_id for c in cases]
    assert "CC-MUM-101" in case_ids
    assert "CC-MUM-102" in case_ids
    assert "CC-BLR-103" in case_ids

    # CC-MUM-101 Kurla Chawl must be CRITICAL priority
    c_kurla = crisis_cleanup_engine.get_case("CC-MUM-101")
    assert c_kurla is not None
    assert c_kurla.priority_tier == PriorityTier.CRITICAL
    assert c_kurla.priority_score >= 0.90
    assert c_kurla.claimed_by_agency == ReliefAgency.NDRF_BATTALION_5
    assert c_kurla.claim_lease_expires_at is not None


def test_crisis_cleanup_create_case_priority_scoring():
    """
    Validates vulnerability priority scoring:
    P = 0.30*V_vuln + 0.30*min(1.0, D_water/150cm) + 0.25*I(SpecialNeeds) + 0.15*I(AccessCutoff)
    """
    payload = ReliefCaseCreate(
        survivor_name="Pooja Kulkarni",
        survivor_contact="+91-9876543211",
        location_name="Bandra East, Bharat Nagar, Mumbai",
        latitude=19.0600,
        longitude=72.8550,
        work_types=[WorkType.ELDERLY_RESCUE, WorkType.FOOD_WATER_RELIEF],
        water_depth_cm=125.0,
        has_elderly_or_infants=True,
        has_chronic_medical_needs=True,
        road_access_severed=True,
        resident_count=6,
        notes="Bedridden senior citizen with infant grandchild. 125cm floodwater."
    )

    case = crisis_cleanup_engine.create_case(payload)
    assert case.case_id.startswith("CC-")
    assert case.status == CaseStatus.OPEN
    assert case.priority_score >= 0.85
    assert case.priority_tier == PriorityTier.CRITICAL
    assert "Boat" in case.recommended_vehicle_type


def test_crisis_cleanup_vehicle_recommendation():
    """Verifies automated vehicle recommendation based on physical flood depth tolerances."""
    # Depth >= 65cm -> Inflatable Boat
    assert "Boat" in crisis_cleanup_engine._recommend_vehicle(75.0)
    # Depth 40-64cm -> High-Clearance Bus
    assert "Bus" in crisis_cleanup_engine._recommend_vehicle(50.0)
    # Depth < 40cm -> Ambulance
    assert "Ambulance" in crisis_cleanup_engine._recommend_vehicle(25.0)


def test_crisis_cleanup_mutual_aid_claim_and_lease_lock():
    """
    Validates the 24-hour mutual-aid claim lease lock.
    Once claimed, another agency cannot overwrite the claim until the lease expires.
    """
    # Create an open case
    payload = ReliefCaseCreate(
        survivor_name="Vikram Joshi",
        survivor_contact="+91-9811223344",
        location_name="Kurla Pipe Road, Mumbai",
        latitude=19.0690,
        longitude=72.8800,
        work_types=[WorkType.MUCK_OUT],
        water_depth_cm=45.0,
        has_elderly_or_infants=False,
        has_chronic_medical_needs=False,
        road_access_severed=False,
        resident_count=2
    )
    case = crisis_cleanup_engine.create_case(payload)
    assert case.status == CaseStatus.OPEN

    # Agency A (BMC Disaster Cell) claims the case
    claim_req_a = ClaimCaseRequest(
        agency=ReliefAgency.BMC_DISASTER_MANAGEMENT_CELL,
        lead_officer="Officer Rajesh Gupta",
        team_headcount=8,
        deployed_vehicle="Municipal High-Clearance Truck"
    )
    claimed_case = crisis_cleanup_engine.claim_case(case.case_id, claim_req_a)
    assert claimed_case.status == CaseStatus.CLAIMED
    assert claimed_case.claimed_by_agency == ReliefAgency.BMC_DISASTER_MANAGEMENT_CELL
    assert claimed_case.claim_lease_expires_at is not None

    # Agency B (Indian Red Cross) attempts to claim the same active case -> Must raise ValueError
    claim_req_b = ClaimCaseRequest(
        agency=ReliefAgency.INDIAN_RED_CROSS_SOCIETY,
        lead_officer="Volunteer Coordinator Mary",
        team_headcount=4,
        deployed_vehicle="Red Cross Van"
    )
    with pytest.raises(ValueError) as excinfo:
        crisis_cleanup_engine.claim_case(case.case_id, claim_req_b)
    assert "already claimed" in str(excinfo.value)


def test_crisis_cleanup_work_progress_and_close():
    """Validates updating on-site work progress and closing the case with official signoff."""
    # Use CC-MUM-102
    case = crisis_cleanup_engine.get_case("CC-MUM-102")
    assert case is not None

    # Claim it first
    claim_req = ClaimCaseRequest(
        agency=ReliefAgency.CIVIL_DEFENCE_CORPS,
        lead_officer="Commander Deepak Sen",
        team_headcount=10,
        deployed_vehicle="Civil Defence Truck"
    )
    crisis_cleanup_engine.claim_case("CC-MUM-102", claim_req)

    # Update work progress
    work_req = UpdateWorkRequest(
        status=CaseStatus.IN_PROGRESS,
        equipment_deployed=["High-capacity submersible pump 500GPM", "Discharge hoses"],
        volunteers_active=10,
        work_notes="Pumping out CST road junction, water depth reduced from 80cm to 30cm."
    )
    updated = crisis_cleanup_engine.update_work_progress("CC-MUM-102", work_req)
    assert updated.status == CaseStatus.IN_PROGRESS
    assert len(updated.equipment_deployed) == 2
    assert "reduced from 80cm" in updated.notes

    # Close case
    close_req = CloseCaseRequest(
        resolution_summary="Road dewatered completely. Silt cleared, traffic restored.",
        survivor_status="RESOLVED_RESTORED",
        signoff_officer="Commander Deepak Sen"
    )
    closed = crisis_cleanup_engine.close_case("CC-MUM-102", close_req)
    assert closed.status == CaseStatus.CLOSED
    assert closed.resolution_summary is not None


def test_crisis_cleanup_rest_api_endpoints():
    """Tests all FastAPI REST endpoints for Phase 29.3."""
    # 1. POST /api/v1/relief/cases
    create_payload = {
        "survivor_name": "Ananya Sharma",
        "survivor_contact": "+91-9877001122",
        "location_name": "Assam Kaziranga Relief Camp #2",
        "latitude": 26.5800,
        "longitude": 93.1750,
        "work_types": ["FOOD_WATER_RELIEF", "MEDICAL_EVAC"],
        "water_depth_cm": 110.0,
        "has_elderly_or_infants": True,
        "has_chronic_medical_needs": False,
        "road_access_severed": True,
        "resident_count": 8,
        "notes": "Relief ration delivery needed."
    }
    r_create = client.post("/api/v1/relief/cases", json=create_payload)
    assert r_create.status_code == 200
    data_c = r_create.json()
    new_id = data_c["case_id"]
    assert new_id.startswith("CC-")

    # 2. GET /api/v1/relief/cases
    r_list = client.get("/api/v1/relief/cases?limit=10")
    assert r_list.status_code == 200
    c_list = r_list.json()
    assert isinstance(c_list, list)
    assert len(c_list) >= 3

    # 3. GET /api/v1/relief/cases/{case_id}
    r_get = client.get(f"/api/v1/relief/cases/{new_id}")
    assert r_get.status_code == 200
    assert r_get.json()["case_id"] == new_id

    # 4. POST /api/v1/relief/claim/{case_id}
    claim_payload = {
        "agency": "KHALSA_AID_INDIA",
        "lead_officer": "Sevadar Harpreet Singh",
        "team_headcount": 15,
        "deployed_vehicle": "Khalsa Aid All-Terrain Food Truck"
    }
    r_claim = client.post(f"/api/v1/relief/claim/{new_id}", json=claim_payload)
    assert r_claim.status_code == 200
    assert r_claim.json()["claimed_by_agency"] == "KHALSA_AID_INDIA"

    # Duplicate claim by another agency returns 409
    dup_claim = {
        "agency": "INDIAN_RED_CROSS_SOCIETY",
        "lead_officer": "Volunteer Officer",
        "team_headcount": 5,
        "deployed_vehicle": "Van"
    }
    r_dup = client.post(f"/api/v1/relief/claim/{new_id}", json=dup_claim)
    assert r_dup.status_code == 409

    # 5. POST /api/v1/relief/work/{case_id}
    work_payload = {
        "status": "IN_PROGRESS",
        "equipment_deployed": ["Langar food kits", "Potable water filters"],
        "volunteers_active": 15,
        "work_notes": "Distributed 200 food packets and clean drinking water."
    }
    r_work = client.post(f"/api/v1/relief/work/{new_id}", json=work_payload)
    assert r_work.status_code == 200
    assert r_work.json()["status"] == "IN_PROGRESS"

    # 6. POST /api/v1/relief/close/{case_id}
    close_payload = {
        "resolution_summary": "Rations delivered for 3 days. Clean water established.",
        "survivor_status": "RESTORED",
        "signoff_officer": "Sevadar Harpreet Singh"
    }
    r_close = client.post(f"/api/v1/relief/close/{new_id}", json=close_payload)
    assert r_close.status_code == 200
    assert r_close.json()["status"] == "CLOSED"

    # 7. GET /api/v1/relief/spec
    r_spec = client.get("/api/v1/relief/spec")
    assert r_spec.status_code == 200
    assert "priority_formula" in r_spec.json()
    assert "participating_agencies" in r_spec.json()


def test_crisis_cleanup_not_found_handling():
    """Tests 404 response on non-existent case queries."""
    r = client.get("/api/v1/relief/cases/CC-NON-EXISTENT-999")
    assert r.status_code == 404
