"""
AEGIS-CLIMATE: NASA VEDA STAC & Raster Tiling REST API Endpoints
Derived from NASA-IMPACT/veda-backend (TiTiler + STAC FastAPI Architecture)
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Response
from backend.app.veda_raster import (
    veda_engine,
    StacCollection,
    StacSearchRequest,
    StacSearchResponse,
    ZonalStatsRequest,
    ZonalStatsResponse
)

logger = logging.getLogger("aegis.routes.veda")

router = APIRouter(tags=["NASA VEDA STAC & Raster Service"])


@router.get("/stac/collections", response_model=List[StacCollection])
async def get_stac_collections():
    """
    Returns the list of all available SpatioTemporal Asset Catalog (STAC v1.0.0) collections.
    """
    return veda_engine.get_collections()


@router.get("/stac/collections/{collection_id}", response_model=StacCollection)
async def get_stac_collection_by_id(collection_id: str):
    """
    Retrieves metadata, extents, and asset links for a specific STAC collection.
    """
    coll = veda_engine.get_collection(collection_id)
    if not coll:
        raise HTTPException(status_code=404, detail=f"STAC Collection '{collection_id}' not found.")
    return coll


@router.post("/stac/search", response_model=StacSearchResponse)
async def search_stac_post(req: StacSearchRequest):
    """
    Executes a SpatioTemporal Asset Catalog (STAC) search query using POST body.
    Filters by bounding box, collection IDs, and temporal range.
    """
    return veda_engine.search_stac(req)


@router.get("/stac/search", response_model=StacSearchResponse)
async def search_stac_get(
    bbox: Optional[str] = Query(None, description="Comma-separated: min_lon,min_lat,max_lon,max_lat"),
    collections: Optional[str] = Query(None, description="Comma-separated collection IDs"),
    datetime: Optional[str] = Query(None, description="ISO datetime or range"),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Executes a STAC search query using GET URL query parameters.
    """
    parsed_bbox = None
    if bbox:
        try:
            parsed_bbox = [float(v.strip()) for v in bbox.split(",")]
            if len(parsed_bbox) != 4:
                parsed_bbox = None
        except Exception:
            parsed_bbox = None

    parsed_colls = [c.strip() for c in collections.split(",")] if collections else None

    req = StacSearchRequest(
        collections=parsed_colls,
        bbox=parsed_bbox,
        datetime=datetime,
        limit=limit
    )
    return veda_engine.search_stac(req)


@router.get("/raster/tile/{z}/{x}/{y}")
async def get_dynamic_raster_tile(
    z: int,
    x: int,
    y: int,
    collection_id: str = Query("veda-flood-inundation", description="STAC collection ID"),
    colormap_name: str = Query("blues", description="Colormap: blues, magma, sar_radar, viridis"),
    tile_size: int = Query(256, ge=128, le=512)
):
    """
    Dynamically generates Slippy Map Web Mercator (EPSG:3857) RGBA PNG tiles on-the-fly.
    Directly compatible with Leaflet, MapLibre GL, and OpenLayers tile layers.
    """
    tile_bytes = veda_engine.generate_raster_tile(
        z=z,
        x=x,
        y=y,
        collection_id=collection_id,
        colormap_name=colormap_name,
        tile_size=tile_size
    )

    return Response(
        content=tile_bytes,
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=3600, stale-while-revalidate=86400",
            "X-NASA-VEDA-Engine": "TiTiler-Dynamic-COG",
            "X-Tile-Coords": f"{z}/{x}/{y}"
        }
    )


@router.post("/raster/statistics", response_model=ZonalStatsResponse)
async def compute_raster_zonal_statistics(req: ZonalStatsRequest):
    """
    Computes sub-50ms zonal statistics (min, max, mean, std, percentiles, inundation sqkm)
    over a bounding box or user-drawn GeoJSON boundary.
    """
    return veda_engine.compute_zonal_statistics(req)


@router.get("/raster/pipeline")
async def get_raster_pipeline_status():
    """
    Returns full telemetry diagnostics, circuit breaker state, and collection catalog summary.
    """
    return veda_engine.get_pipeline_diagnostics()


@router.get("/raster/health")
async def get_raster_health():
    """Lightweight health probe for VEDA raster service."""
    return {
        "status": "operational",
        "service": "NASA VEDA TiTiler Dynamic Raster Service",
        "circuit_state": veda_engine.circuit_state
    }
