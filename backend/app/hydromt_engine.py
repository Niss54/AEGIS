"""
TERRA-SENTINEL: Deltares HydroMT Computational Hydrography & TWI Catchment Engine
Phase 30.2: Automated Watershed Delineation, D8 Flow Direction & Topographic Wetness Index
Synthesized from Deltares/hydromt (wflow, pyflwdir, SFINCS)
"""

import math
import logging
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel, Field

logger = logging.getLogger("terra_sentinel.hydromt_engine")


class FlowDirectionD8(int, Enum):
    """
    Standard ESRI / Deltares D8 Flow Direction encoding:
    32  64  128
    16   x    1
     8   4    2
    """
    EAST = 1
    SOUTHEAST = 2
    SOUTH = 4
    SOUTHWEST = 8
    WEST = 16
    NORTHWEST = 32
    NORTH = 64
    NORTHEAST = 128


class LandCoverType(str, Enum):
    URBAN_IMPERVIOUS = "URBAN_IMPERVIOUS"
    WATER_CANAL = "WATER_CANAL"
    MANGROVE_WETLAND = "MANGROVE_WETLAND"
    CROPLAND_SOIL = "CROPLAND_SOIL"
    FOREST_CANOPY = "FOREST_CANOPY"


# Standard Manning's n roughness coefficients
MANNING_ROUGHNESS: Dict[LandCoverType, float] = {
    LandCoverType.URBAN_IMPERVIOUS: 0.015,
    LandCoverType.WATER_CANAL: 0.025,
    LandCoverType.CROPLAND_SOIL: 0.035,
    LandCoverType.FOREST_CANOPY: 0.060,
    LandCoverType.MANGROVE_WETLAND: 0.080
}


class DelineateRequest(BaseModel):
    basin_id: str = Field(default="mumbai_mithi", description="Target basin identifier")
    grid_size: int = Field(default=8, ge=4, le=32, description="Square DEM dimension (NxN)")
    cell_resolution_m: float = Field(default=30.0, ge=5.0, le=500.0, description="Spatial resolution delta_x in meters")
    inflow_precipitation_mm: float = Field(default=95.0, ge=0.0, description="Active precipitation event in mm")
    land_cover: LandCoverType = Field(default=LandCoverType.URBAN_IMPERVIOUS)


class TWICell(BaseModel):
    row: int
    col: int
    elevation_m: float
    slope_rad: float
    contributing_area_cells: int
    twi_score: float
    is_depression_sink: bool
    manning_velocity_ms: float


class DelineationResult(BaseModel):
    basin_id: str
    basin_name: str
    grid_dimension: str
    cell_resolution_m: float
    total_catchment_area_sqkm: float
    mean_twi: float
    max_twi: float
    critical_depression_cells_count: int
    manning_roughness_n: float
    peak_overland_velocity_ms: float
    time_of_concentration_min: float
    twi_matrix: List[List[float]]
    depression_sinks: List[TWICell]
    governing_invariant: str
    timestamp: str


class HydroMTBasinProfile(BaseModel):
    basin_id: str
    basin_name: str
    state: str
    center_lat: float
    center_lon: float
    outlet_elevation_m: float
    ridge_elevation_m: float
    dominant_land_cover: LandCoverType
    total_area_sqkm: float


# Catalog of preloaded Indian hydrological basins
PRELOADED_BASINS: Dict[str, HydroMTBasinProfile] = {
    "mumbai_mithi": HydroMTBasinProfile(
        basin_id="mumbai_mithi",
        basin_name="Mithi River Catchment Basin",
        state="Maharashtra",
        center_lat=19.0760,
        center_lon=72.8770,
        outlet_elevation_m=4.5,
        ridge_elevation_m=128.0,
        dominant_land_cover=LandCoverType.URBAN_IMPERVIOUS,
        total_area_sqkm=115.0
    ),
    "bengaluru_vrishabhavathi": HydroMTBasinProfile(
        basin_id="bengaluru_vrishabhavathi",
        basin_name="Vrishabhavathi River Basin",
        state="Karnataka",
        center_lat=12.9250,
        center_lon=77.5250,
        outlet_elevation_m=680.0,
        ridge_elevation_m=920.0,
        dominant_land_cover=LandCoverType.URBAN_IMPERVIOUS,
        total_area_sqkm=385.0
    ),
    "delhi_yamuna": HydroMTBasinProfile(
        basin_id="delhi_yamuna",
        basin_name="Yamuna Delhi Floodplain Reach",
        state="Delhi NCT",
        center_lat=28.6472,
        center_lon=77.2512,
        outlet_elevation_m=198.0,
        ridge_elevation_m=240.0,
        dominant_land_cover=LandCoverType.CROPLAND_SOIL,
        total_area_sqkm=540.0
    ),
    "assam_brahmaputra": HydroMTBasinProfile(
        basin_id="assam_brahmaputra",
        basin_name="Brahmaputra Kamrup Highland Catchment",
        state="Assam",
        center_lat=26.1856,
        center_lon=91.7498,
        outlet_elevation_m=48.0,
        ridge_elevation_m=580.0,
        dominant_land_cover=LandCoverType.FOREST_CANOPY,
        total_area_sqkm=1850.0
    ),
    "chennai_adyar": HydroMTBasinProfile(
        basin_id="chennai_adyar",
        basin_name="Adyar River Estuary Basin",
        state="Tamil Nadu",
        center_lat=13.0067,
        center_lon=80.2570,
        outlet_elevation_m=2.0,
        ridge_elevation_m=65.0,
        dominant_land_cover=LandCoverType.MANGROVE_WETLAND,
        total_area_sqkm=860.0
    )
}


class HydroMTEngine:
    """
    Computational hydrography engine implementing Deltares algorithms:
    - D8 Flow Direction and recursive contributing area accumulation
    - Topographic Wetness Index: TWI = ln(alpha / (tan(beta) + 1e-4))
    - Manning's equation overland hydraulic velocity
    """

    def __init__(self):
        self._basins = PRELOADED_BASINS

    def list_basins(self) -> List[HydroMTBasinProfile]:
        return list(self._basins.values())

    def get_basin(self, basin_id: str) -> Optional[HydroMTBasinProfile]:
        return self._basins.get(basin_id)

    def generate_synthetic_dem(self, n: int, min_elev: float, max_elev: float) -> List[List[float]]:
        """
        Generates a realistic V-shaped parabolic drainage valley with slope converging toward (n-1, n//2).
        """
        dem: List[List[float]] = []
        center_col = n // 2
        for r in range(n):
            row_elevs: List[float] = []
            for c in range(n):
                # Distance from central valley stream
                valley_dist = abs(c - center_col)
                # Gradient sloping downhill from row 0 to row n-1
                longitudinal_drop = (n - 1 - r) / max(1, n - 1)
                lateral_rise = (valley_dist / max(1, center_col)) * 0.4
                elev = min_elev + (max_elev - min_elev) * (0.6 * longitudinal_drop + lateral_rise)
                row_elevs.append(round(elev, 2))
            dem.append(row_elevs)
        return dem

    def compute_d8_flow_accumulation(
        self, dem: List[List[float]], dx: float
    ) -> Tuple[List[List[int]], List[List[float]]]:
        """
        Calculates D8 flow direction and total upslope contributing area cells.
        Returns:
            (accumulation_matrix, slope_radians_matrix)
        """
        rows = len(dem)
        cols = len(dem[0])
        accum = [[1 for _ in range(cols)] for _ in range(rows)]
        slopes = [[0.01 for _ in range(cols)] for _ in range(rows)]

        # Find steepest downhill neighbor for each cell
        # 8 neighbors: (dr, dc, dist_factor)
        neighbors = [
            (0, 1, 1.0), (1, 1, math.sqrt(2)), (1, 0, 1.0), (1, -1, math.sqrt(2)),
            (0, -1, 1.0), (-1, -1, math.sqrt(2)), (-1, 0, 1.0), (-1, 1, math.sqrt(2))
        ]

        # Sort cells by elevation descending to route flow without cycles
        flat_cells = []
        for r in range(rows):
            for c in range(cols):
                flat_cells.append((dem[r][c], r, c))
        flat_cells.sort(key=lambda x: x[0], reverse=True)

        for _, r, c in flat_cells:
            elev = dem[r][c]
            max_drop = -1e9
            best_nr, best_nc = -1, -1
            best_slope = 0.005

            for dr, dc, dist_mult in neighbors:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    drop = (elev - dem[nr][nc]) / (dx * dist_mult)
                    if drop > max_drop:
                        max_drop = drop
                        best_nr, best_nc = nr, nc
                        best_slope = max(0.0001, drop)

            if max_drop > 0 and best_nr != -1:
                accum[best_nr][best_nc] += accum[r][c]
                slopes[r][c] = max(0.001, math.atan(best_slope))
            else:
                slopes[r][c] = 0.001  # Flat sink / depression

        return accum, slopes

    def calculate_twi(
        self,
        contributing_cells: int,
        slope_rad: float,
        cell_resolution_m: float
    ) -> float:
        """
        Governing Invariant:
        alpha = contributing_cells * cell_resolution_m
        TWI = ln( alpha / (tan(slope_rad) + 1e-4) )
        """
        alpha = max(cell_resolution_m, contributing_cells * cell_resolution_m)
        tan_beta = max(1e-4, math.tan(slope_rad))
        val = math.log(alpha / tan_beta)
        return round(max(0.0, val), 3)

    def compute_manning_velocity(
        self,
        hydraulic_radius_m: float,
        slope_rad: float,
        land_cover: LandCoverType
    ) -> float:
        """
        Manning's Equation:
        v = (1 / n) * R_h^(2/3) * S_0^(1/2)
        """
        n = MANNING_ROUGHNESS.get(land_cover, 0.035)
        s_0 = max(1e-4, math.sin(slope_rad))
        r_h = max(0.05, hydraulic_radius_m)
        v = (1.0 / n) * math.pow(r_h, 2.0 / 3.0) * math.sqrt(s_0)
        return round(min(15.0, v), 3)

    def delineate_catchment(self, req: DelineateRequest) -> DelineationResult:
        """
        Executes end-to-end Deltares catchment delineation and TWI mapping.
        """
        basin = self.get_basin(req.basin_id) or PRELOADED_BASINS["mumbai_mithi"]
        n = req.grid_size
        dx = req.cell_resolution_m

        dem = self.generate_synthetic_dem(
            n=n,
            min_elev=basin.outlet_elevation_m,
            max_elev=basin.ridge_elevation_m
        )

        accum_matrix, slope_matrix = self.compute_d8_flow_accumulation(dem, dx)

        twi_matrix: List[List[float]] = []
        depressions: List[TWICell] = []
        all_twis: List[float] = []
        all_velocities: List[float] = []

        hydraulic_r = 0.10 + (req.inflow_precipitation_mm / 1000.0)

        for r in range(n):
            row_twis: List[float] = []
            for c in range(n):
                c_cells = accum_matrix[r][c]
                s_rad = slope_matrix[r][c]
                twi = self.calculate_twi(c_cells, s_rad, dx)
                row_twis.append(twi)
                all_twis.append(twi)

                v = self.compute_manning_velocity(hydraulic_r, s_rad, req.land_cover)
                all_velocities.append(v)

                is_sink = twi >= 12.0
                if is_sink:
                    depressions.append(TWICell(
                        row=r,
                        col=c,
                        elevation_m=dem[r][c],
                        slope_rad=round(s_rad, 4),
                        contributing_area_cells=c_cells,
                        twi_score=twi,
                        is_depression_sink=True,
                        manning_velocity_ms=v
                    ))
            twi_matrix.append(row_twis)

        # Watershed summary statistics
        total_cells = n * n
        area_sqkm = round((total_cells * dx * dx) / 1e6, 3)
        mean_twi = round(sum(all_twis) / len(all_twis), 2)
        max_twi = round(max(all_twis), 2)
        peak_v = round(max(all_velocities), 2)

        # Time of concentration: Tc = L / v_mean
        longest_flow_path_m = n * dx * math.sqrt(2)
        mean_v = max(0.2, sum(all_velocities) / len(all_velocities))
        time_of_concentration_min = round((longest_flow_path_m / mean_v) / 60.0, 1)

        from datetime import datetime, timezone
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        return DelineationResult(
            basin_id=basin.basin_id,
            basin_name=basin.basin_name,
            grid_dimension=f"{n}x{n} ({total_cells} cells)",
            cell_resolution_m=dx,
            total_catchment_area_sqkm=area_sqkm,
            mean_twi=mean_twi,
            max_twi=max_twi,
            critical_depression_cells_count=len(depressions),
            manning_roughness_n=MANNING_ROUGHNESS.get(req.land_cover, 0.035),
            peak_overland_velocity_ms=peak_v,
            time_of_concentration_min=time_of_concentration_min,
            twi_matrix=twi_matrix,
            depression_sinks=depressions,
            governing_invariant="TWI = ln(alpha / (tan(beta) + 1e-4)) | Manning v = (1/n)*Rh^(2/3)*S0^(1/2)",
            timestamp=now_iso
        )


hydromt_engine = HydroMTEngine()
