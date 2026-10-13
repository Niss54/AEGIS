"""
Preloaded Global Climate Vulnerability Hotspots Route
Covers Türkiye, USA, Estonia, and India (with high-risk UP Lucknow Gomti Basin).
Conforms to Phase 1 Global Ingestion & Nested Jurisdictional Tagging (Yale OpenLab / dClimate).
"""
from typing import List
from fastapi import APIRouter
from backend.app.schemas import HotspotModel, JurisdictionHierarchy

router = APIRouter(tags=["Global Hotspots"])

GLOBAL_HOTSPOTS: List[HotspotModel] = [
    # --- 1. INDIA: Uttar Pradesh (User Region & Critical Gangetic Basin) ---
    HotspotModel(
        id="lucknow-gomti",
        name="Lucknow — Gomti River Basin & Lowland Drainage Corridor",
        state="Uttar Pradesh",
        country="India",
        lat=26.8467,
        lon=80.9462,
        risk_profile="HIGH",
        description="Gomti river embankment backflow and low-gradient drainage congestion during intense monsoon spells affecting residential and administrative clusters.",
        typical_annual_loss_inr="₹380 Crores",
        typical_annual_loss_usd="$45.6M",
        historical_baseline_24h_mm=42.0,
        jurisdiction=JurisdictionHierarchy(
            country_iso="IN",
            country_name="India",
            admin1_state="Uttar Pradesh",
            admin2_district="Lucknow",
            basin_name="Gomti River Basin"
        )
    ),
    # --- 2. TÜRKIYE: Host Country (Istanbul Bosphorus & Marmara Basin) ---
    HotspotModel(
        id="istanbul-marmara",
        name="Istanbul — Marmara & Golden Horn Estuary Basin",
        state="Istanbul",
        country="Türkiye",
        lat=41.0082,
        lon=28.9784,
        risk_profile="CRITICAL",
        description="Dense historical and financial metropolis exposed to severe Mediterranean cloudbursts, impermeable urban runoff, and Marmara coastal storm surges.",
        typical_annual_loss_inr="₹1,450 Crores",
        typical_annual_loss_usd="$174.2M",
        historical_baseline_24h_mm=28.0,
        jurisdiction=JurisdictionHierarchy(
            country_iso="TR",
            country_name="Türkiye",
            admin1_state="Istanbul",
            admin2_district="Fatih/Beyoglu",
            basin_name="Golden Horn & Bosphorus Basin"
        )
    ),
    # --- 3. TÜRKIYE: Host Country (Black Sea Mountainous River Surge) ---
    HotspotModel(
        id="kastamonu-bozkurt",
        name="Kastamonu — Bozkurt Ezine Stream Flash Basin",
        state="Black Sea Region",
        country="Türkiye",
        lat=41.9572,
        lon=34.0125,
        risk_profile="CRITICAL",
        description="Steep Pontic mountain cloudburst channeling flash flood debris flows through narrow valley riverbeds with extreme kinetic destruction.",
        typical_annual_loss_inr="₹920 Crores",
        typical_annual_loss_usd="$110.5M",
        historical_baseline_24h_mm=35.0,
        jurisdiction=JurisdictionHierarchy(
            country_iso="TR",
            country_name="Türkiye",
            admin1_state="Kastamonu",
            admin2_district="Bozkurt",
            basin_name="Ezine Stream Basin"
        )
    ),
    # --- 4. USA: Southern California / Orange County (IEEE Committee Leadership) ---
    HotspotModel(
        id="orange-county-santa-ana",
        name="Orange County — Santa Ana River & Newport Coastal Basin",
        state="California",
        country="United States",
        lat=33.7175,
        lon=-117.8311,
        risk_profile="HIGH",
        description="Pacific atmospheric river storm surges triggering high-velocity runoff from Prado Dam down the Santa Ana channel into low-elevation Pacific coastal zones.",
        typical_annual_loss_inr="₹2,100 Crores",
        typical_annual_loss_usd="$252.3M",
        historical_baseline_24h_mm=18.0,
        jurisdiction=JurisdictionHierarchy(
            country_iso="US",
            country_name="United States",
            admin1_state="California",
            admin2_district="Orange County",
            basin_name="Santa Ana River Basin"
        )
    ),
    # --- 5. ESTONIA: Baltic Sea Surge (IEEE Estonia Leadership) ---
    HotspotModel(
        id="parnu-baltic",
        name="Pärnu — Baltic Sea Surge & Lowland River Inundation",
        state="Pärnu County",
        country="Estonia",
        lat=58.3859,
        lon=24.4971,
        risk_profile="HIGH",
        description="Southwesterly Baltic gale surges causing severe sea-level rise and river backflow into low-elevation historic town centers and coastal hotels.",
        typical_annual_loss_inr="₹480 Crores",
        typical_annual_loss_usd="$57.6M",
        historical_baseline_24h_mm=22.0,
        jurisdiction=JurisdictionHierarchy(
            country_iso="EE",
            country_name="Estonia",
            admin1_state="Pärnu County",
            admin2_district="Pärnu",
            basin_name="Pärnu River & Baltic Coast"
        )
    ),
    # --- 6. INDIA: Maharashtra (Mumbai Arterial Catchment) ---
    HotspotModel(
        id="mumbai-mithi",
        name="Mumbai — Mithi River & Kurla Basin",
        state="Maharashtra",
        country="India",
        lat=19.0728,
        lon=72.8797,
        risk_profile="CRITICAL",
        description="High-density urban basin prone to severe monsoon cloudburst overflow, tidal lock, and suburban transit standstill.",
        typical_annual_loss_inr="₹1,200 Crores",
        typical_annual_loss_usd="$144.1M",
        historical_baseline_24h_mm=35.0,
        jurisdiction=JurisdictionHierarchy(
            country_iso="IN",
            country_name="India",
            admin1_state="Maharashtra",
            admin2_district="Mumbai Suburban",
            basin_name="Mithi River Catchment"
        )
    ),
    # --- 7. INDIA: Karnataka (Bengaluru Tech Corridor) ---
    HotspotModel(
        id="bengaluru-bellandur",
        name="Bengaluru — Bellandur & Outer Ring Road Tech Corridor",
        state="Karnataka",
        country="India",
        lat=12.9352,
        lon=77.6775,
        risk_profile="HIGH",
        description="Major tech corridor affected by lake interconnect encroachment, impervious surface runoff, and rapid road inundation.",
        typical_annual_loss_inr="₹450 Crores",
        typical_annual_loss_usd="$54.0M",
        historical_baseline_24h_mm=25.0,
        jurisdiction=JurisdictionHierarchy(
            country_iso="IN",
            country_name="India",
            admin1_state="Karnataka",
            admin2_district="Bengaluru Urban",
            basin_name="Bellandur-Varthur Lake Basin"
        )
    ),
    # --- 8. INDIA: Assam (Brahmaputra Valley) ---
    HotspotModel(
        id="assam-kaziranga",
        name="Assam — Brahmaputra Basin & Kaziranga Eco-Corridor",
        state="Assam",
        country="India",
        lat=26.5775,
        lon=93.1711,
        risk_profile="CRITICAL",
        description="Annual Brahmaputra riverine surge causing catastrophic agricultural submergence and habitat displacement.",
        typical_annual_loss_inr="₹850 Crores",
        typical_annual_loss_usd="$102.1M",
        historical_baseline_24h_mm=45.0,
        jurisdiction=JurisdictionHierarchy(
            country_iso="IN",
            country_name="India",
            admin1_state="Assam",
            admin2_district="Golaghat / Nagaon",
            basin_name="Middle Brahmaputra Basin"
        )
    ),
    # --- 9. INDIA: Tamil Nadu (Chennai Coastal Wetland) ---
    HotspotModel(
        id="chennai-velachery",
        name="Chennai — Velachery & Pallikaranai Wetland Basin",
        state="Tamil Nadu",
        country="India",
        lat=12.9759,
        lon=80.2212,
        risk_profile="HIGH",
        description="Coastal low-lying urban depression prone to northeast monsoon depressions and slow stormwater drainage.",
        typical_annual_loss_inr="₹680 Crores",
        typical_annual_loss_usd="$81.7M",
        historical_baseline_24h_mm=30.0,
        jurisdiction=JurisdictionHierarchy(
            country_iso="IN",
            country_name="India",
            admin1_state="Tamil Nadu",
            admin2_district="Chennai",
            basin_name="Pallikaranai Marshland Catchment"
        )
    ),
    # --- 10. INDIA: Gujarat (Mundra Industrial Coastal Hub) ---
    HotspotModel(
        id="mundra-industrial",
        name="Gujarat — Mundra Port & Industrial Corridor",
        state="Gujarat",
        country="India",
        lat=22.8395,
        lon=69.7042,
        risk_profile="MEDIUM",
        description="Heavy coastal logistics and thermal infrastructure exposed to Arabian Sea cyclones and carbon emission transition audits.",
        typical_annual_loss_inr="₹320 Crores",
        typical_annual_loss_usd="$38.4M",
        historical_baseline_24h_mm=20.0,
        jurisdiction=JurisdictionHierarchy(
            country_iso="IN",
            country_name="India",
            admin1_state="Gujarat",
            admin2_district="Kutch",
            basin_name="Gulf of Kutch Coastal Basin"
        )
    )
]

# Backward compatibility alias
BHARAT_HOTSPOTS = GLOBAL_HOTSPOTS


@router.get("/hotspots", response_model=List[HotspotModel])
async def list_global_hotspots():
    """Retrieve pre-configured multi-national climate vulnerability hotspots for instant one-click analysis."""
    return GLOBAL_HOTSPOTS
