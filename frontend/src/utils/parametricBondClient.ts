/**
 * AEGIS-CLIMATE Phase 15 Parametric Disaster Insurance & Smart Bond Client
 * Module: frontend/src/utils/parametricBondClient.ts
 * Governance: Gravitas Reliability Runtime · Polygon Amoy Smart Contract Integration
 *
 * Mathematical Governing Equation:
 * Trigger(D) = I_{D >= D_threshold} => Payout(Beneficiary)
 */

export interface TriggerEvaluationResult {
  governing_equation: string;
  indicator: number;
  triggered: boolean;
  depth_triggered: boolean;
  risk_triggered: boolean;
  waterlogging_depth_cm: number;
  threshold_depth_cm: number;
  risk_score_bps: number;
  threshold_risk_bps: number;
  severity_ratio: number;
  payout_amount_usd: number;
  notional_principal_usd: number;
  coverage_limit_usd: number;
}

export interface BondSettlementRecord {
  settlement_id: string;
  bond_id: string;
  assessment_id: string;
  beneficiary: string;
  payout_amount_usd: number;
  settlement_tier: string;
  receipt_hash: string;
  tx_hash: string;
  timestamp: number;
  circuit_state: string;
  status: string;
}

export interface CFMCRewardResult {
  eligible: boolean;
  minted: boolean;
  reward_amount_cfmc: number;
  beneficiary: string;
  assessment_id: string;
  risk_score_bps: number;
  dem_depth_cm: number;
  rule: string;
  tx_hash: string | null;
  timestamp: number;
}

export interface ParametricHealthStatus {
  phase: number;
  subsystem: string;
  circuit_state: string;
  consecutive_failures: number;
  failure_threshold: number;
  cooldown_period_sec: number;
  total_settlements: number;
  total_cfmc_rewards: number;
  status: string;
}

export class ParametricBondClient {
  private static instance: ParametricBondClient;
  private apiBase: string;

  private constructor() {
    this.apiBase = import.meta.env?.VITE_API_URL || '';
  }

  public static getInstance(): ParametricBondClient {
    if (!ParametricBondClient.instance) {
      ParametricBondClient.instance = new ParametricBondClient();
    }
    return ParametricBondClient.instance;
  }

  /**
   * Deterministic local evaluation of Trigger(D) = I_{D >= D_threshold} => Payout(Beneficiary)
   * Guaranteed to operate offline or during high-latency network conditions.
   */
  public evaluateTriggerLocal(
    depthCm: number,
    thresholdCm: number = 50.0,
    riskScoreBps: number = 7000,
    thresholdRiskBps: number = 6500,
    principalUsd: number = 100000.0,
    coverageLimitUsd: number = 250000.0
  ): TriggerEvaluationResult {
    const depthTriggered = depthCm >= thresholdCm;
    const riskTriggered = riskScoreBps >= thresholdRiskBps;
    const indicator = depthTriggered || riskTriggered ? 1 : 0;
    const triggered = indicator === 1;

    let severityRatio = 0.0;
    let payoutAmount = 0.0;

    if (triggered) {
      const depthRatio = Math.min(1.0, depthCm / Math.max(1.0, thresholdCm * 1.5));
      const riskRatio = Math.min(1.0, riskScoreBps / 10000.0);
      severityRatio = Number(Math.max(depthRatio, riskRatio).toFixed(4));
      payoutAmount = Number(Math.min(coverageLimitUsd, principalUsd * severityRatio).toFixed(2));
    }

    return {
      governing_equation: 'Trigger(D) = I_{D >= D_threshold} => Payout(Beneficiary)',
      indicator,
      triggered,
      depth_triggered: depthTriggered,
      risk_triggered: riskTriggered,
      waterlogging_depth_cm: depthCm,
      threshold_depth_cm: thresholdCm,
      risk_score_bps: riskScoreBps,
      threshold_risk_bps: thresholdRiskBps,
      severity_ratio: severityRatio,
      payout_amount_usd: payoutAmount,
      notional_principal_usd: principalUsd,
      coverage_limit_usd: coverageLimitUsd
    };
  }

  /**
   * Calls the backend API to evaluate parametric bond trigger condition.
   */
  public async evaluateTrigger(
    depthCm: number,
    thresholdCm: number = 50.0,
    riskScoreBps: number = 7000,
    thresholdRiskBps: number = 6500,
    principalUsd: number = 100000.0,
    coverageLimitUsd: number = 250000.0,
    beneficiary: string = '0x71C2E696688b14AE0D78278fCeB78C2651F87bF9'
  ): Promise<TriggerEvaluationResult> {
    try {
      const resp = await fetch(`${this.apiBase}/api/v2/blockchain/parametric/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          waterlogging_depth_cm: depthCm,
          threshold_depth_cm: thresholdCm,
          risk_score_bps: riskScoreBps,
          threshold_risk_bps: thresholdRiskBps,
          notional_principal_usd: principalUsd,
          coverage_limit_usd: coverageLimitUsd,
          beneficiary
        })
      });
      if (!resp.ok) {
        throw new Error(`API error: ${resp.statusText}`);
      }
      return await resp.json();
    } catch {
      return this.evaluateTriggerLocal(
        depthCm,
        thresholdCm,
        riskScoreBps,
        thresholdRiskBps,
        principalUsd,
        coverageLimitUsd
      );
    }
  }

  /**
   * Settles a parametric disaster bond.
   */
  public async settleBond(params: {
    bondId: string;
    assessmentId: string;
    depthCm: number;
    riskScoreBps: number;
    beneficiary: string;
    payoutAmountUsd?: number;
    forceFallback?: boolean;
  }): Promise<BondSettlementRecord> {
    const resp = await fetch(`${this.apiBase}/api/v2/blockchain/parametric/settle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        bond_id: params.bondId,
        assessment_id: params.assessmentId,
        waterlogging_depth_cm: params.depthCm,
        risk_score_bps: params.riskScoreBps,
        beneficiary: params.beneficiary,
        payout_amount_usd: params.payoutAmountUsd,
        force_fallback: params.forceFallback ?? false
      })
    });
    if (!resp.ok) {
      throw new Error(`Failed to settle bond: ${resp.statusText}`);
    }
    return await resp.json();
  }

  /**
   * Evaluates Carbon Flood Mitigation Credit (CFMC) reward.
   */
  public async evaluateCfmcReward(params: {
    beneficiary: string;
    assessmentId: string;
    riskScoreBps: number;
    demDepthCm: number;
    lat?: number;
    lon?: number;
  }): Promise<CFMCRewardResult> {
    const resp = await fetch(`${this.apiBase}/api/v2/blockchain/parametric/cfmc/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        beneficiary: params.beneficiary,
        assessment_id: params.assessmentId,
        risk_score_bps: params.riskScoreBps,
        dem_depth_cm: params.demDepthCm,
        lat: params.lat ?? 19.0728,
        lon: params.lon ?? 72.8797
      })
    });
    if (!resp.ok) {
      throw new Error(`Failed to evaluate CFMC reward: ${resp.statusText}`);
    }
    return await resp.json();
  }

  /**
   * Fetches Phase 15 health status.
   */
  public async getHealth(): Promise<ParametricHealthStatus> {
    const resp = await fetch(`${this.apiBase}/api/v2/blockchain/phase15/health`);
    if (!resp.ok) {
      throw new Error(`Failed to fetch health: ${resp.statusText}`);
    }
    return await resp.json();
  }
}

export const parametricBondClient = ParametricBondClient.getInstance();
