"""
AEGIS-CLIMATE: Crisis Cleanup 4R Inter-Agency Collaborative Relief Engine
Phase 29.3: Collaborative Disaster Response & Work Order Lifecycle Core

Synthesizes architectural patterns from CrisisCleanup/crisiscleanup-4-web:
1. 4R Lifecycle: REPORT -> CLAIM -> WORK -> CLOSE
2. Work order taxonomy (Muck out, Tarping, Tree debris, Biohazard, Medical evac, Elderly rescue)
3. Vulnerability priority scoring:
   P_priority = 0.30*V_vulnerability + 0.30*min(1.0, D_water/150cm) + 0.25*I(SpecialNeeds) + 0.15*I(AccessCutoff)
4. Mutual-Aid Claim Lease Lock (24-hour timeout) preventing duplicate rescue deployment
5. Relief Agency roster (NDRF, Indian Red Cross, BMC Disaster Cell, Civil Defence, Khalsa Aid)
6. Equipment & vehicle capability auto-matching (Inflatable Boat vs Municipal High-Axle Truck)
"""

import math
import logging
from enum import Enum
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("aegis.crisis_cleanup")


class CaseStatus(str, Enum):
    OPEN = "OPEN"
    CLAIMED = "CLAIMED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"


class WorkType(str, Enum):
    MUCK_OUT = "MUCK_OUT"
    TARPING = "TARPING"
    TREE_DEBRIS = "TREE_DEBRIS"
    BIOHAZARD = "BIOHAZARD"
    MEDICAL_EVAC = "MEDICAL_EVAC"
    ELDERLY_RESCUE = "ELDERLY_RESCUE"
    FOOD_WATER_RELIEF = "FOOD_WATER_RELIEF"


class PriorityTier(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ReliefAgency(str, Enum):
    NDRF_BATTALION_5 = "NDRF_BATTALION_5"
    BMC_DISASTER_MANAGEMENT_CELL = "BMC_DISASTER_MANAGEMENT_CELL"
    INDIAN_RED_CROSS_SOCIETY = "INDIAN_RED_CROSS_SOCIETY"
    CIVIL_DEFENCE_CORPS = "CIVIL_DEFENCE_CORPS"
    KHALSA_AID_INDIA = "KHALSA_AID_INDIA"


class ReliefCaseCreate(BaseModel):
    incident_ref: Optional[str] = Field(default=None, example="INC-MUM-001")
    survivor_name: str = Field(..., example="Rameshwar Sharma")
    survivor_contact: str = Field(..., example="+91-9820112233")
    location_name: str = Field(..., example="Kurla West, Chawl #4, Mumbai")
    latitude: float = Field(..., ge=-90.0, le=90.0, example=19.0685)
    longitude: float = Field(..., ge=-180.0, le=180.0, example=72.8792)
    work_types: List[WorkType] = Field(default=[WorkType.ELDERLY_RESCUE, WorkType.MEDICAL_EVAC])
    water_depth_cm: float = Field(default=85.0, ge=0.0, le=500.0)
    has_elderly_or_infants: bool = Field(default=True)
    has_chronic_medical_needs: bool = Field(default=False)
    road_access_severed: bool = Field(default=True)
    resident_count: int = Field(default=4, ge=1, le=100)
    notes: Optional[str] = Field(default="Ground floor water entering living quarters, electricity severed.")


class ClaimCaseRequest(BaseModel):
    agency: ReliefAgency = Field(..., example=ReliefAgency.NDRF_BATTALION_5)
    lead_officer: str = Field(..., example="Inspector Vikram Singh")
    team_headcount: int = Field(default=6, ge=1, le=50)
    deployed_vehicle: str = Field(default="NDRF Inflatable Rescue Boat (IRB-04)")


class UpdateWorkRequest(BaseModel):
    status: CaseStatus = Field(default=CaseStatus.IN_PROGRESS)
    equipment_deployed: List[str] = Field(default=["High-pressure dewatering pump", "Stretcher kit"])
    volunteers_active: int = Field(default=6, ge=1, le=50)
    work_notes: str = Field(..., example="Evacuated 4 residents onto inflatable craft, pumping out basement.")


class CloseCaseRequest(BaseModel):
    resolution_summary: str = Field(..., example="All 4 residents safely transported to BKC relief center.")
    survivor_status: str = Field(default="SAFE_EVACUATED")
    signoff_officer: str = Field(..., example="Inspector Vikram Singh")


class ReliefCase(BaseModel):
    case_id: str
    incident_ref: Optional[str] = None
    survivor_name: str
    survivor_contact: str
    location_name: str
    latitude: float
    longitude: float
    work_types: List[WorkType]
    water_depth_cm: float
    priority_score: float
    priority_tier: PriorityTier
    status: CaseStatus
    claimed_by_agency: Optional[ReliefAgency] = None
    claimed_by_officer: Optional[str] = None
    claimed_at: Optional[str] = None
    claim_lease_expires_at: Optional[str] = None
    deployed_vehicle: Optional[str] = None
    equipment_deployed: List[str] = []
    volunteers_active: int = 0
    resident_count: int
    has_special_needs: bool
    road_access_severed: bool
    recommended_vehicle_type: str
    notes: str
    resolution_summary: Optional[str] = None
    created_at: str
    updated_at: str


class CrisisCleanupEngine:
    """
    Crisis Cleanup 4R Collaborative Relief Case Management Engine.
    Enforces mutual-aid claim lease locks, vulnerability priority scoring,
    and automatic vehicle capability matching.
    """

    def __init__(self):
        self._cases: Dict[str, ReliefCase] = {}
        self._lease_duration_seconds = 86400  # 24 hours
        self._seed_production_cases()

    def _calculate_priority(
        self,
        water_depth_cm: float,
        has_special_needs: bool,
        road_access_severed: bool,
        resident_count: int
    ) -> (float, PriorityTier):
        """
        Calculates vulnerability priority score:
        P = 0.30*V_vuln + 0.30*min(1.0, D_water/150) + 0.25*I(SpecialNeeds) + 0.15*I(AccessCutoff)
        """
        v_vuln = min(1.0, 0.40 + (0.10 * min(5, resident_count)))
        depth_factor = min(1.0, water_depth_cm / 150.0)
        special_factor = 1.0 if has_special_needs else 0.0
        access_factor = 1.0 if road_access_severed else 0.0

        p = round(
            0.30 * v_vuln +
            0.30 * depth_factor +
            0.25 * special_factor +
            0.15 * access_factor,
            3
        )

        if p >= 0.75:
            tier = PriorityTier.CRITICAL
        elif p >= 0.50:
            tier = PriorityTier.HIGH
        elif p >= 0.25:
            tier = PriorityTier.MEDIUM
        else:
            tier = PriorityTier.LOW

        return p, tier

    def _recommend_vehicle(self, water_depth_cm: float) -> str:
        """Auto-matches vehicle requirements based on physical draft tolerances."""
        if water_depth_cm >= 65.0:
            return "NDRF Inflatable Rescue Boat (Amphibious)"
        elif water_depth_cm >= 40.0:
            return "BMC High-Clearance Ashok Leyland Rescue Bus (65cm limit)"
        else:
            return "Emergency Ambulance (40cm limit)"

    def _seed_production_cases(self):
        """Pre-seeds realistic relief work orders matching verified disaster hotspots."""
        now = datetime.now(timezone.utc)
        now_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        lease_iso = (now + timedelta(seconds=self._lease_duration_seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")

        seeds = [
            ReliefCase(
                case_id="CC-MUM-101",
                incident_ref="INC-MUM-001",
                survivor_name="Savitri Bai Shinde",
                survivor_contact="+91-9820198765",
                location_name="Kurla West, Ward L, Chawl #14, Mumbai",
                latitude=19.0685,
                longitude=72.8792,
                work_types=[WorkType.ELDERLY_RESCUE, WorkType.MEDICAL_EVAC],
                water_depth_cm=115.0,
                priority_score=0.94,
                priority_tier=PriorityTier.CRITICAL,
                status=CaseStatus.CLAIMED,
                claimed_by_agency=ReliefAgency.NDRF_BATTALION_5,
                claimed_by_officer="Inspector Vikram Singh",
                claimed_at=now_iso,
                claim_lease_expires_at=lease_iso,
                deployed_vehicle="NDRF Inflatable Rescue Boat (IRB-04)",
                equipment_deployed=["Life jackets", "Stretcher hoist", "First-aid triage pack"],
                volunteers_active=6,
                resident_count=14,
                has_special_needs=True,
                road_access_severed=True,
                recommended_vehicle_type="NDRF Inflatable Rescue Boat (Amphibious)",
                notes="14 senior citizens stranded on elevated cots. Water entering 115cm.",
                created_at=now_iso,
                updated_at=now_iso
            ),
            ReliefCase(
                case_id="CC-MUM-102",
                incident_ref="INC-MUM-002",
                survivor_name="BKC Ward Officer",
                survivor_contact="+91-9820234567",
                location_name="MTNL Junction, CST Road, Mumbai",
                latitude=19.0728,
                longitude=72.8797,
                work_types=[WorkType.MUCK_OUT, WorkType.BIOHAZARD],
                water_depth_cm=80.0,
                priority_score=0.78,
                priority_tier=PriorityTier.CRITICAL,
                status=CaseStatus.OPEN,
                resident_count=45,
                has_special_needs=False,
                road_access_severed=True,
                recommended_vehicle_type="NDRF Inflatable Rescue Boat (Amphibious)",
                notes="Mithi overflow contaminated transit corridor. High capacity dewatering pump needed.",
                created_at=now_iso,
                updated_at=now_iso
            ),
            ReliefCase(
                case_id="CC-BLR-103",
                incident_ref="INC-BLR-003",
                survivor_name="Kiran Reddy",
                survivor_contact="+91-9980112233",
                location_name="Kadubeesanahalli Underpass, Bengaluru",
                latitude=12.9352,
                longitude=77.6772,
                work_types=[WorkType.TREE_DEBRIS, WorkType.FOOD_WATER_RELIEF],
                water_depth_cm=95.0,
                priority_score=0.82,
                priority_tier=PriorityTier.CRITICAL,
                status=CaseStatus.IN_PROGRESS,
                claimed_by_agency=ReliefAgency.CIVIL_DEFENCE_CORPS,
                claimed_by_officer="Captain Arun Kumar",
                claimed_at=now_iso,
                claim_lease_expires_at=lease_iso,
                deployed_vehicle="BMC High-Clearance Ashok Leyland Rescue Bus (65cm limit)",
                equipment_deployed=["Chain saws", "Drinking water tanks", "Tow winches"],
                volunteers_active=12,
                resident_count=30,
                has_special_needs=True,
                road_access_severed=True,
                recommended_vehicle_type="NDRF Inflatable Rescue Boat (Amphibious)",
                notes="Stranded private company bus. 30 commuters awaiting extraction.",
                created_at=now_iso,
                updated_at=now_iso
            )
        ]
        for c in seeds:
            self._cases[c.case_id] = c

    def create_case(self, data: ReliefCaseCreate) -> ReliefCase:
        """Creates a new relief case / work order with automated priority calculation."""
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        case_id = f"CC-{int(datetime.now().timestamp() * 1000) % 1000000:06d}"

        has_special = data.has_elderly_or_infants or data.has_chronic_medical_needs
        p_score, p_tier = self._calculate_priority(
            water_depth_cm=data.water_depth_cm,
            has_special_needs=has_special,
            road_access_severed=data.road_access_severed,
            resident_count=data.resident_count
        )
        rec_vehicle = self._recommend_vehicle(data.water_depth_cm)

        case = ReliefCase(
            case_id=case_id,
            incident_ref=data.incident_ref,
            survivor_name=data.survivor_name,
            survivor_contact=data.survivor_contact,
            location_name=data.location_name,
            latitude=data.latitude,
            longitude=data.longitude,
            work_types=data.work_types,
            water_depth_cm=data.water_depth_cm,
            priority_score=p_score,
            priority_tier=p_tier,
            status=CaseStatus.OPEN,
            resident_count=data.resident_count,
            has_special_needs=has_special,
            road_access_severed=data.road_access_severed,
            recommended_vehicle_type=rec_vehicle,
            notes=data.notes or "",
            created_at=now_iso,
            updated_at=now_iso
        )

        self._cases[case_id] = case
        logger.info(f"Created relief case {case_id} [{p_tier}] for {data.survivor_name}")
        return case

    def claim_case(self, case_id: str, req: ClaimCaseRequest) -> ReliefCase:
        """
        Enforces Mutual-Aid Claim Lease Lock (24 hours).
        Prevents multiple agencies from duplicating response on the same survivor.
        """
        if case_id not in self._cases:
            raise ValueError(f"Case {case_id} not found")

        case = self._cases[case_id]
        now = datetime.now(timezone.utc)

        # Check if already claimed and lease is still active
        if case.status in [CaseStatus.CLAIMED, CaseStatus.IN_PROGRESS]:
            if case.claim_lease_expires_at and case.claimed_by_agency != req.agency:
                lease_active = False
                try:
                    raw_lease = case.claim_lease_expires_at
                    if raw_lease.endswith("Z"):
                        raw_lease = raw_lease[:-1] + "+00:00"
                    exp_dt = datetime.fromisoformat(raw_lease)
                    lease_active = now < exp_dt
                except Exception as ex:
                    logger.warning(f"Error parsing lease expiry: {ex}")
                    lease_active = True

                if lease_active:
                    raise ValueError(
                        f"Case {case_id} is already claimed by {case.claimed_by_agency}. "
                        f"Mutual-aid lease active until {case.claim_lease_expires_at}"
                    )

        now_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        lease_iso = (now + timedelta(seconds=self._lease_duration_seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")

        case.status = CaseStatus.CLAIMED
        case.claimed_by_agency = req.agency
        case.claimed_by_officer = req.lead_officer
        case.claimed_at = now_iso
        case.claim_lease_expires_at = lease_iso
        case.deployed_vehicle = req.deployed_vehicle
        case.volunteers_active = req.team_headcount
        case.updated_at = now_iso

        self._cases[case_id] = case
        logger.info(f"Agency {req.agency} claimed case {case_id} with 24h lease")
        return case

    def update_work_progress(self, case_id: str, req: UpdateWorkRequest) -> ReliefCase:
        """Updates work status, volunteers deployed, and equipment on site."""
        if case_id not in self._cases:
            raise ValueError(f"Case {case_id} not found")
        case = self._cases[case_id]
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        case.status = req.status
        case.equipment_deployed = req.equipment_deployed
        case.volunteers_active = req.volunteers_active
        case.notes = f"{case.notes} | Progress: {req.work_notes}"
        case.updated_at = now_iso

        self._cases[case_id] = case
        return case

    def close_case(self, case_id: str, req: CloseCaseRequest) -> ReliefCase:
        """Closes completed relief case with signoff."""
        if case_id not in self._cases:
            raise ValueError(f"Case {case_id} not found")
        case = self._cases[case_id]
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        case.status = CaseStatus.CLOSED
        case.resolution_summary = req.resolution_summary
        case.updated_at = now_iso

        self._cases[case_id] = case
        logger.info(f"Case {case_id} successfully closed by {req.signoff_officer}")
        return case

    def list_cases(
        self,
        status: Optional[CaseStatus] = None,
        agency: Optional[ReliefAgency] = None,
        priority_tier: Optional[PriorityTier] = None,
        limit: int = 50
    ) -> List[ReliefCase]:
        """Lists relief cases with multi-attribute filtering."""
        results = list(self._cases.values())
        if status:
            results = [c for c in results if c.status == status]
        if agency:
            results = [c for c in results if c.claimed_by_agency == agency]
        if priority_tier:
            results = [c for c in results if c.priority_tier == priority_tier]
        results.sort(key=lambda x: x.priority_score, reverse=True)
        return results[:limit]

    def get_case(self, case_id: str) -> Optional[ReliefCase]:
        """Retrieves relief case by ID."""
        return self._cases.get(case_id)


# Singleton Instance
crisis_cleanup_engine = CrisisCleanupEngine()
