"""
Zero-Trust Verifiable Telemetry & Cryptographic HMAC Sealing Router
Exposes cryptographic sealing, verification, and tamper detection endpoints.
"""
import time
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException

from backend.app.security import (
    telemetry_security_controller,
    VerifiableTelemetryModel,
    TelemetrySealRequest,
    TelemetrySealResponse,
    TelemetryVerifyRequest,
    TelemetryVerifyResponse
)

router = APIRouter(prefix="/telemetry", tags=["Zero-Trust Verifiable Telemetry"])


@router.post("/seal", response_model=TelemetrySealResponse)
async def seal_telemetry(req: TelemetrySealRequest):
    """
    Computes an HMAC-SHA256 non-repudiation signature for an IoT sensor station telemetry packet.
    """
    try:
        payload_data = {
            "station_id": req.station_id,
            "lat": req.lat,
            "lon": req.lon,
            "telemetry": req.telemetry
        }
        seal = telemetry_security_controller.generate_seal(
            station_id=req.station_id,
            payload=payload_data,
            secret_key=req.sensor_secret_key
        )
        return TelemetrySealResponse(
            event_id=f"SEAL-{req.station_id}-{int(time.time())}",
            station_id=req.station_id,
            timestamp_epoch=seal["timestamp_epoch"],
            nonce=seal["nonce"],
            canonical_payload_sha256=seal["canonical_payload_sha256"],
            hmac_sha256_signature=seal["hmac_sha256_signature"],
            status="CRYPTOGRAPHICALLY_SEALED"
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to seal telemetry: {str(exc)}")


@router.post("/verify", response_model=TelemetryVerifyResponse)
async def verify_telemetry(req: TelemetryVerifyRequest):
    """
    Verifies cryptographic seal, guards against replay attacks, and detects in-transit data tampering.
    """
    is_valid, reason, drift = telemetry_security_controller.verify_seal(
        station_id=req.station_id,
        payload=req.payload,
        signature=req.signature,
        timestamp=req.timestamp_epoch,
        nonce=req.nonce,
        secret_key=req.sensor_secret_key
    )

    return TelemetryVerifyResponse(
        event_id=req.event_id,
        is_valid=is_valid,
        rejection_reason=reason,
        signature_verified=is_valid,
        nonce_fresh=is_valid or "Replay" not in str(reason),
        drift_seconds=round(drift, 2),
        integrity_status="VERIFIED_TAMPER_FREE" if is_valid else "INTEGRITY_VIOLATION_DETECTED"
    )


@router.get("/security-spec")
async def get_security_specification():
    """
    Returns cryptographic specification and compliance profile for enterprise audits.
    """
    return {
        "framework": "Zero-Trust Verifiable Telemetry Architecture",
        "hash_algorithm": "SHA-256",
        "mac_algorithm": "HMAC-SHA256 (RFC 2104)",
        "replay_defense": "Stateful Nonce Registry + Anti-Replay Cache",
        "max_allowable_clock_drift_sec": telemetry_security_controller.max_drift_seconds,
        "standard_adherence": ["NIST SP 800-107", "FIPS 198-1", "ISO/IEC 9797-2"]
    }


@router.post("/pipeline", response_model=VerifiableTelemetryModel)
async def execute_phase11_pipeline(payload: Dict[str, Any]):
    """
    Executes standard PRD Phase 11 Zero-Trust Verifiable Telemetry pipeline returning VerifiableTelemetryModel.
    """
    try:
        return await telemetry_security_controller.execute_phase_pipeline(payload)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

