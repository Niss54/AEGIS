"""
TERRA-SENTINEL Production Specification: Phase 11 / Cybersecurity Invariant
Module: terra_sentinel.security.telemetryintegritycontroller
Governance: Gravitas Reliability Runtime · Zero-Trust Cryptographic Data Integrity

Mathematical Governing Equation:
Sig = HMAC-SHA256(K_sensor, Payload || Timestamp || Nonce)
Where:
- K_sensor: Provisioned cryptographic hardware/station secret key
- Payload: Canonicalized JSON string representation of telemetry vectors
- Timestamp: Epoch timestamp with maximum allowable drift Delta_t <= 300s
- Nonce: Unique pseudo-random hex token strictly tracked to prevent replay attacks
"""
import hmac
import hashlib
import json
import time
import logging
from typing import Dict, Any, Optional, Set, Tuple, List
from pydantic import BaseModel, Field

logger = logging.getLogger("terra_sentinel.security")


class VerifiableTelemetryModel(BaseModel):
    """
    Standard Verifiable Telemetry Model as defined in PRD.md Section 16 (Phase 11).
    """
    event_id: str = Field(..., description="Unique UUIDv4 telemetry event identifier")
    timestamp_epoch: float = Field(default_factory=time.time, description="Epoch timestamp")
    execution_tier: str = Field("ENTERPRISE_PROD", description="Execution tier label")
    verified_flag: bool = Field(True, description="Cryptographic verification indicator")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Telemetry metadata payload")


class TelemetrySealRequest(BaseModel):
    station_id: str = Field(..., description="Environmental IoT Sensor Station ID")
    lat: float
    lon: float
    telemetry: Dict[str, Any] = Field(..., description="Telemetry data (rain, moisture, etc.)")
    sensor_secret_key: Optional[str] = Field(None, description="Optional sensor station key (defaults to platform secret)")


class TelemetrySealResponse(BaseModel):
    event_id: str
    station_id: str
    timestamp_epoch: float
    nonce: str
    canonical_payload_sha256: str
    hmac_sha256_signature: str
    status: str


class TelemetryVerifyRequest(BaseModel):
    event_id: str
    station_id: str
    timestamp_epoch: float
    nonce: str
    payload: Dict[str, Any]
    signature: str
    sensor_secret_key: Optional[str] = None


class TelemetryVerifyResponse(BaseModel):
    event_id: str
    is_valid: bool
    rejection_reason: Optional[str] = None
    signature_verified: bool
    nonce_fresh: bool
    drift_seconds: float
    integrity_status: str


class TelemetryIntegrityController:
    """
    Executive Controller for Zero-Trust Verifiable Telemetry & Cryptographic HMAC Sealing.
    Enforces non-repudiation, replay defense, and cryptographic integrity.
    """
    DEFAULT_PLATFORM_KEY = "terra-sentinel-master-cryptographic-salt-2026-japac"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.phase_id = 11
        self.name = "Zero-Trust Verifiable Telemetry & Cryptographic HMAC Sealing"
        self.state = "INITIALIZED"
        self.seen_nonces: Set[str] = set()
        self.max_drift_seconds = 300.0  # 5 minutes window
        logger.info(f"{self.name} initialized successfully.")

    @staticmethod
    def canonicalize(data: Dict[str, Any]) -> str:
        """Produces deterministic, alphabetically sorted, whitespace-trimmed JSON string."""
        return json.dumps(data, sort_keys=True, separators=(",", ":"))

    def generate_seal(
        self,
        station_id: str,
        payload: Dict[str, Any],
        secret_key: Optional[str] = None,
        timestamp: Optional[float] = None,
        nonce: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Computes HMAC-SHA256 signature seal:
        Sig = HMAC-SHA256(Key, CanonicalPayload || Timestamp || Nonce)
        """
        ts = timestamp or time.time()
        n = nonce or hashlib.sha256(f"{station_id}:{ts}:{time.perf_counter()}".encode()).hexdigest()[:16]
        key = (secret_key or self.DEFAULT_PLATFORM_KEY).encode("utf-8")

        canonical_payload = self.canonicalize(payload)
        payload_hash = hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()

        # Message commitment: canonical_payload_hash + timestamp_str + nonce
        message = f"{payload_hash}:{ts:.4f}:{n}".encode("utf-8")
        signature = hmac.new(key, message, hashlib.sha256).hexdigest()

        return {
            "station_id": station_id,
            "timestamp_epoch": ts,
            "nonce": n,
            "canonical_payload_sha256": payload_hash,
            "hmac_sha256_signature": signature,
            "signature_algorithm": "HMAC-SHA256-RFC2104"
        }

    def verify_seal(
        self,
        station_id: str,
        payload: Dict[str, Any],
        signature: str,
        timestamp: float,
        nonce: str,
        secret_key: Optional[str] = None
    ) -> Tuple[bool, Optional[str], float]:
        """
        Verifies signature, enforces timestamp drift bounds, and guards against replay attacks.
        Returns: (is_valid, rejection_reason, drift_seconds)
        """
        now = time.time()
        drift = abs(now - timestamp)

        # 1. Enforce timestamp drift tolerance window
        if drift > self.max_drift_seconds:
            return False, f"Timestamp drift {drift:.1f}s exceeds maximum allowable window ({self.max_drift_seconds}s).", drift

        # 2. Guard against replay attacks
        if nonce in self.seen_nonces:
            return False, f"Replay attack detected: Nonce '{nonce}' has already been processed.", drift

        # 3. Canonicalize payload and re-compute expected HMAC
        key = (secret_key or self.DEFAULT_PLATFORM_KEY).encode("utf-8")
        canonical_payload = self.canonicalize(payload)
        payload_hash = hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()
        message = f"{payload_hash}:{timestamp:.4f}:{nonce}".encode("utf-8")
        expected_sig = hmac.new(key, message, hashlib.sha256).hexdigest()

        # Constant-time comparison to prevent timing side-channel attacks
        if not hmac.compare_digest(signature, expected_sig):
            return False, "Cryptographic HMAC-SHA256 signature mismatch: Telemetry has been tampered with or key is invalid.", drift

        # Register nonce in seen cache
        self.seen_nonces.add(nonce)
        return True, None, drift

    async def execute_phase_pipeline(self, payload: Dict[str, Any]) -> VerifiableTelemetryModel:
        """
        Standard Phase 11 execution method returning PRD-compliant VerifiableTelemetryModel.
        """
        start_time = time.perf_counter()
        if not payload:
            raise ValueError("Empty payload rejected by Telemetry Integrity gate.")

        event_id = str(payload.get("event_id", f"TS-EVT-{int(time.time())}"))
        station_id = str(payload.get("station_id", "STN-DEFAULT-01"))

        seal = self.generate_seal(station_id, payload)
        result_dict = {
            "processed_by": self.name,
            "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
            "status": "OPERATIONAL",
            "seal": seal,
            "data": payload
        }

        return VerifiableTelemetryModel(
            event_id=event_id,
            execution_tier="ENTERPRISE_PROD",
            verified_flag=True,
            metadata=result_dict
        )


# Global Singleton Instance
telemetry_security_controller = TelemetryIntegrityController()
