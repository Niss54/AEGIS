/**
 * TERRA-SENTINEL Phase 17 Bilingual Civic Advisory Synthesis Client
 * Module: frontend/src/utils/civicClient.ts
 * Governance: Gravitas Reliability Runtime · Bilingual Civic Advisory Generator
 *
 * Governing Equation:
 * Advisory_Devanagari = Gemini2.0(P_eff, D_water, Lang=hi)
 */

export interface CivicAdvisoryParams {
  eventId?: string;
  location: string;
  effectivePrecipMm: number;
  waterloggingDepthCm: number;
  buildingsAtRisk: number;
  varInr: number;
  policyContext?: string;
  generateSpeech?: boolean;
}

export interface BoundsMetadata {
  p_eff_original: number;
  p_eff_clamped: number;
  d_water_original: number;
  d_water_clamped: number;
  b_risk_original: number;
  b_risk_clamped: number;
  var_original: number;
  var_clamped: number;
  clamped_applied: boolean;
}

export interface CivicAdvisoryResult {
  status: string;
  eventId: string;
  location: string;
  englishAdvisory: string;
  hindiAdvisory: string;
  executionTier: string;
  modelUsed: string;
  ttsAudioSarvamB64?: string | null;
  ttsAudioElevenlabsB64?: string | null;
  latencyMs: number;
  boundsValidated: BoundsMetadata;
}

export interface CivicHealthStatus {
  status: string;
  phase: number;
  name: string;
  diagnostics: {
    circuit_state: string;
    failure_count: number;
    failure_threshold: number;
    cooldown_period_sec: number;
    total_requests: number;
    successful_requests: number;
    last_active_model: string;
  };
}

export class CivicClient {
  private static instance: CivicClient;
  private apiBase: string;

  private constructor() {
    this.apiBase = (import.meta as any).env?.VITE_API_URL || '';
  }

  public static getInstance(): CivicClient {
    if (!CivicClient.instance) {
      CivicClient.instance = new CivicClient();
    }
    return CivicClient.instance;
  }

  /**
   * Deterministic client-side bounds clamping obeying governing equations.
   */
  public clampBounds(params: CivicAdvisoryParams): {
    pEff: number;
    dWater: number;
    bRisk: number;
    vInr: number;
    meta: BoundsMetadata;
  } {
    const pEff = Math.max(0.0, Math.min(1000.0, params.effectivePrecipMm));
    const dWater = Math.max(0, Math.min(500, Math.round(params.waterloggingDepthCm)));
    const bRisk = Math.max(0, Math.min(10000, Math.round(params.buildingsAtRisk)));
    const vInr = Math.max(0.0, params.varInr);

    const meta: BoundsMetadata = {
      p_eff_original: params.effectivePrecipMm,
      p_eff_clamped: pEff,
      d_water_original: params.waterloggingDepthCm,
      d_water_clamped: dWater,
      b_risk_original: params.buildingsAtRisk,
      b_risk_clamped: bRisk,
      var_original: params.varInr,
      var_clamped: vInr,
      clamped_applied: (
        pEff !== params.effectivePrecipMm ||
        dWater !== params.waterloggingDepthCm ||
        bRisk !== params.buildingsAtRisk ||
        vInr !== params.varInr
      ),
    };

    return { pEff, dWater, bRisk, vInr, meta };
  }

  /**
   * Tier 5 Client-Side Deterministic Bhasha-AI Fallback Generator.
   */
  public generateLocalFallback(params: CivicAdvisoryParams): CivicAdvisoryResult {
    const { pEff, dWater, bRisk, vInr, meta } = this.clampBounds(params);
    const varCrores = (vInr / 10000000.0).toFixed(1);

    const hindi = `आपातकालीन चेतावनी (${params.location}): अत्यधिक वर्षा (${pEff.toFixed(1)} मिमी) एवं जलभराव (${dWater} सेमी) के कारण ${bRisk} महत्वपूर्ण इमारतों के प्रभावित होने की आशंका है। अनुमानित वित्तीय जोखिम ₹${varCrores} करोड़ है। एनडीएमए आपदा प्रतिक्रिया दल को तत्काल डीवाटरिंग पंप तैनात करने और विद्युत सबस्टेशनों को सुरक्षित करने का निर्देश दिया जाता है।`;
    const english = `EXECUTIVE ALERT: Intense precipitation of ${pEff.toFixed(1)} mm and inundation of ${dWater} cm projected across ${bRisk} critical assets in ${params.location}. Projected Enterprise Value-at-Risk stands at ₹${varCrores} Crores. Mandate immediate physical floodgate deployment and lifeline protocol actuation.`;

    return {
      status: 'COMPLETED',
      eventId: params.eventId || `TS-LOCAL-${Date.now()}`,
      location: params.location,
      englishAdvisory: english,
      hindiAdvisory: hindi,
      executionTier: 'LOCAL_FALLBACK',
      modelUsed: 'ClientDeterministicBhashaAI',
      latencyMs: 1.5,
      boundsValidated: meta,
    };
  }

  /**
   * Invokes REST pipeline with automated client-side failover.
   */
  public async generateAdvisory(params: CivicAdvisoryParams): Promise<CivicAdvisoryResult> {
    const { pEff, dWater, bRisk, vInr, meta } = this.clampBounds(params);

    try {
      const response = await fetch(`${this.apiBase}/civic/advisory/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event_id: params.eventId,
          location: params.location,
          effective_precip_mm: pEff,
          waterlogging_depth_cm: dWater,
          buildings_at_risk: bRisk,
          var_inr: vInr,
          policy_context: params.policyContext,
          generate_speech: Boolean(params.generateSpeech),
        }),
      });

      if (response.ok) {
        const data = await response.json();
        return {
          status: data.status || 'success',
          eventId: data.event_id,
          location: data.location,
          englishAdvisory: data.english_advisory,
          hindiAdvisory: data.hindi_advisory,
          executionTier: data.execution_tier,
          modelUsed: data.model_used,
          ttsAudioSarvamB64: data.tts_audio_sarvam_b64,
          ttsAudioElevenlabsB64: data.tts_audio_elevenlabs_b64,
          latencyMs: data.latency_ms,
          boundsValidated: data.bounds_validated || meta,
        };
      }
    } catch {
      // Fallback silently to Tier 5 client heuristics
    }

    return this.generateLocalFallback(params);
  }

  /**
   * Query Phase 17 Circuit Breaker & Health Status.
   */
  public async getHealth(): Promise<CivicHealthStatus | null> {
    try {
      const response = await fetch(`${this.apiBase}/civic/phase17/health`);
      if (response.ok) {
        return (await response.json()) as CivicHealthStatus;
      }
    } catch {
      return null;
    }
    return null;
  }

  /**
   * Audio player helper for base64 audio streams.
   */
  public playAudio(base64Audio: string, mimeType: string = 'audio/mp3'): HTMLAudioElement {
    const audio = new Audio(`data:${mimeType};base64,${base64Audio}`);
    audio.play().catch((err) => console.warn('Audio playback error:', err));
    return audio;
  }
}

export const civicClient = CivicClient.getInstance();
