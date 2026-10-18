"""
FastAPI Route Module: Phase 17 - Bilingual Civic Advisory Synthesis
(English & Devanagari Hindi)
Endpoints:
  - POST /civic/advisory/generate
  - GET  /civic/phase17/health
  - POST /civic/phase17/pipeline
  - POST /civic/speech/synthesize
"""
import time
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.app.civic_advisory import (
    CivicAdvisoryModel,
    CivicAdvisoryRequest,
    CivicAdvisoryResponse,
    civic_advisory_controller,
    validate_and_clamp_advisory_bounds
)

router = APIRouter(prefix="/civic", tags=["Phase 17 - Bilingual Civic Advisory"])


class SpeechSynthesisRequest(BaseModel):
    text: str = Field(..., description="Text string to synthesize")
    language: str = Field("hi", description="Target language ('hi' for Hindi or 'en' for English)")
    speaker: Optional[str] = Field("priya", description="Voice speaker profile")


@router.post("/advisory/generate", response_model=CivicAdvisoryResponse)
async def generate_bilingual_advisory_endpoint(req: CivicAdvisoryRequest):
    """
    POST /civic/advisory/generate
    Synthesizes emergency civic advisory in English and Devanagari Hindi.
    Governing Equation:
        Advisory_Devanagari = Gemini2.0(P_eff, D_water, Lang=hi)
    """
    try:
        res = await civic_advisory_controller.synthesize_bilingual_advisory(
            location=req.location,
            effective_precip_mm=req.effective_precip_mm,
            waterlogging_depth_cm=req.waterlogging_depth_cm,
            buildings_at_risk=req.buildings_at_risk,
            var_inr=req.var_inr,
            policy_context=req.policy_context,
            generate_speech=req.generate_speech
        )
        return CivicAdvisoryResponse(
            status="success",
            event_id=req.event_id or f"TS-EVT-{int(time.time() * 1000)}",
            location=res["location"],
            english_advisory=res["english_advisory"],
            hindi_advisory=res["hindi_advisory"],
            execution_tier=res["execution_tier"],
            model_used=res["model_used"],
            tts_audio_sarvam_b64=res.get("tts_audio_sarvam_b64"),
            tts_audio_elevenlabs_b64=res.get("tts_audio_elevenlabs_b64"),
            latency_ms=res["latency_ms"],
            bounds_validated=res["bounds_validated"]
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Advisory generation failed: {str(exc)}")


@router.get("/phase17/health")
async def civic_phase17_health_endpoint():
    """
    GET /civic/phase17/health
    Returns operational health status, circuit breaker state, and failover diagnostics.
    """
    return {
        "status": "healthy",
        "phase": 17,
        "name": "Bilingual Civic Advisory Synthesis (English & Devanagari Hindi)",
        "diagnostics": civic_advisory_controller.get_circuit_status()
    }


@router.post("/phase17/pipeline", response_model=CivicAdvisoryModel)
async def civic_phase17_pipeline_endpoint(payload: Dict[str, Any]):
    """
    POST /civic/phase17/pipeline
    Executes the standard Phase 17 Gravitas verification pipeline.
    """
    try:
        res = await civic_advisory_controller.execute_phase_pipeline(payload)
        return res
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(exc)}")


@router.post("/speech/synthesize")
async def synthesize_speech_endpoint(req: SpeechSynthesisRequest):
    """
    POST /civic/speech/synthesize
    Synthesizes neural voice audio for emergency broadcasts using Sarvam AI (Hindi) or ElevenLabs (English).
    """
    try:
        from backend.app.agent3_financial import financial_risk_engine

        if req.language.lower() in ("hi", "hindi"):
            audio_b64 = financial_risk_engine.synthesize_sarvam_speech(req.text, speaker=req.speaker or "priya")
            provider = "Sarvam AI"
        else:
            audio_b64 = financial_risk_engine.synthesize_elevenlabs_speech(req.text)
            provider = "ElevenLabs"

        return {
            "status": "success" if audio_b64 else "unavailable",
            "provider": provider,
            "language": req.language,
            "has_audio": audio_b64 is not None,
            "audio_base64": audio_b64
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(exc)}")
