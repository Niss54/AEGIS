"""
Preloaded Bharat Climate Hotspots Route
Exposes mission-critical Indian urban and rural hazard test corridors.
"""
from typing import List
from fastapi import APIRouter
from backend.app.schemas import HotspotModel

router = APIRouter(tags=["Bharat Hotspots"])

BHARAT_HOTSPOTS: List[HotspotModel] = [
    HotspotModel(
        id="mumbai-mithi",
        name="Mumbai — Mithi River & Kurla Basin",
        state="Maharashtra",
        lat=19.0728,
        lon=72.8797,
        risk_profile="CRITICAL",
        description="High-density urban basin prone to severe monsoon cloudburst overflow, tidal lock, and suburban transit standstill.",
        typical_annual_loss_inr="₹1,200 Crores"
    ),
    HotspotModel(
        id="bengaluru-bellandur",
        name="Bengaluru — Bellandur & Outer Ring Road Tech Corridor",
        state="Karnataka",
        lat=12.9352,
        lon=77.6775,
        risk_profile="HIGH",
        description="Major tech corridor affected by lake interconnect encroachment, impervious surface runoff, and rapid road inundation.",
        typical_annual_loss_inr="₹450 Crores"
    ),
    HotspotModel(
        id="assam-kaziranga",
        name="Assam — Brahmaputra Basin & Kaziranga Eco-Corridor",
        state="Assam",
        lat=26.5775,
        lon=93.1711,
        risk_profile="CRITICAL",
        description="Annual Brahmaputra riverine surge causing catastrophic agricultural submergence and habitat displacement.",
        typical_annual_loss_inr="₹850 Crores"
    ),
    HotspotModel(
        id="chennai-velachery",
        name="Chennai — Velachery & Pallikaranai Wetland Basin",
        state="Tamil Nadu",
        lat=12.9759,
        lon=80.2212,
        risk_profile="HIGH",
        description="Coastal low-lying urban depression prone to northeast monsoon depressions and slow stormwater drainage.",
        typical_annual_loss_inr="₹680 Crores"
    ),
    HotspotModel(
        id="mundra-industrial",
        name="Gujarat — Mundra Port & Industrial Corridor",
        state="Gujarat",
        lat=22.8395,
        lon=69.7042,
        risk_profile="MEDIUM",
        description="Heavy coastal logistics and thermal infrastructure exposed to Arabian Sea cyclones and carbon emission transition audits.",
        typical_annual_loss_inr="₹320 Crores"
    )
]


@router.get("/hotspots", response_model=List[HotspotModel])
async def list_bharat_hotspots():
    """Retrieve pre-configured Indian climate vulnerability hotspots for instant one-click analysis."""
    return BHARAT_HOTSPOTS
