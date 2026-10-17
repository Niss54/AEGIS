"""
TERRA-SENTINEL: ClusterDuck Protocol LoRa Mesh REST API Router
Derived from ClusterDuck-Protocol/ClusterDuck-Protocol
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from backend.app.cluster_duck import (
    cluster_duck_engine,
    DuckPacket,
    DuckPacketIngestResponse,
    MeshTopology,
    DuckNode,
    SosSimulationRequest
)

logger = logging.getLogger("terra_sentinel.routes.cluster_duck")

router = APIRouter(tags=["ClusterDuck LoRa Ad-Hoc Mesh Gateway"])


@router.post("/telemetry/duckpacket", response_model=DuckPacketIngestResponse)
async def ingest_lora_duck_packet(packet: DuckPacket):
    """
    Ingests an incoming LoRa DuckPacket from an edge DuckLink or PapaDuck Gateway.
    Performs packet deduplication, loop prevention check (hop_count <= max_hops),
    and updates the dynamic mesh network topology graph.
    """
    return cluster_duck_engine.ingest_duck_packet(packet)


@router.get("/mesh/topology", response_model=MeshTopology)
async def get_mesh_network_topology():
    """
    Retrieves the active LoRa ad-hoc mesh network topology graph,
    including DuckNodes (DuckLink, MamaDuck, PapaDuck), multi-hop links,
    RSSI signal strength indicators, and dead-zone alerts.
    """
    return cluster_duck_engine.get_mesh_topology()


@router.get("/mesh/nodes/{duck_id}", response_model=DuckNode)
async def get_mesh_node_details(duck_id: str):
    """
    Retrieves real-time diagnostics, battery voltage, water level telemetry,
    and routing statistics for an individual DuckNode.
    """
    node = cluster_duck_engine.get_node_by_id(duck_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"DuckNode '{duck_id}' not found in active mesh topology.")
    return node


@router.post("/mesh/simulate-sos", response_model=DuckPacketIngestResponse)
async def simulate_offgrid_emergency_sos(req: SosSimulationRequest):
    """
    Simulates a high-priority, off-grid emergency SOS broadcast from an isolated flood cluster.
    Bypasses standard telemetry throttling and logs urgent civic rescue dispatch.
    """
    return cluster_duck_engine.simulate_emergency_sos(req)


@router.get("/mesh/pipeline")
async def get_cluster_duck_pipeline_diagnostics():
    """
    Returns full ClusterDuck Protocol telemetry, circuit breaker metrics,
    and cache deduplication diagnostics.
    """
    return cluster_duck_engine.get_pipeline_diagnostics()


@router.get("/mesh/health")
async def get_cluster_duck_health():
    """Lightweight health probe for ClusterDuck LoRa Gateway."""
    return {
        "status": "operational",
        "service": "ClusterDuck Protocol LoRa Gateway",
        "circuit_state": cluster_duck_engine.circuit_state
    }
