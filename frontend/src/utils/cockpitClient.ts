/**
 * AEGIS-CLIMATE Phase 18 Mission-Control Cockpit Client & Frame Budget Monitor
 * Module: frontend/src/utils/cockpitClient.ts
 * Governance: Gravitas Reliability Runtime · 60fps GIS Web Cockpit
 *
 * Mathematical Governing Equation:
 * FrameBudget <= 16.67ms ==> FPS >= 60
 */

export interface FrameBudgetEvaluation {
  governing_equation: string;
  render_time_ms: number;
  fps: number;
  is_60fps: boolean;
  budget_utilization_pct: number;
  degradation_risk: 'NONE' | 'MODERATE' | 'CRITICAL';
  recommended_simplification: boolean;
  vertex_count: number;
  optimal_target_vertices: number;
}

export interface CockpitDiagnostics {
  status: string;
  phase: number;
  name: string;
  target_fps: number;
  frame_budget_ms: number;
  circuit_state: string;
  failure_count: number;
  total_requests: number;
  active_tileset: string;
  supported_overlays: string[];
}

export interface OptimizedContourResult {
  type: string;
  features: any[];
  optimized: boolean;
  original_vertices: number;
  result_vertices: number;
  reduction_pct: number;
}

export class FrameBudgetMonitor {
  private lastTimestamp: number = 0;
  private frameCount: number = 0;
  private currentFps: number = 60;
  private currentFrameTimeMs: number = 16.6;
  private isRunning: boolean = false;
  private listeners: ((fps: number, frameTimeMs: number, is60Fps: boolean) => void)[] = [];

  public start(): void {
    if (this.isRunning) return;
    this.isRunning = true;
    this.lastTimestamp = performance.now();
    this.scheduleTick();
  }

  public stop(): void {
    this.isRunning = false;
  }

  public subscribe(callback: (fps: number, frameTimeMs: number, is60Fps: boolean) => void): () => void {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter((cb) => cb !== callback);
    };
  }

  private scheduleTick(): void {
    if (!this.isRunning) return;
    requestAnimationFrame((now) => {
      const delta = now - this.lastTimestamp;
      this.lastTimestamp = now;

      if (delta > 0) {
        this.currentFrameTimeMs = delta;
        this.currentFps = Math.min(120, Math.round(1000 / delta));
        const is60Fps = delta <= 16.67;

        this.frameCount++;
        if (this.frameCount % 5 === 0) {
          for (const listener of this.listeners) {
            listener(this.currentFps, this.currentFrameTimeMs, is60Fps);
          }
        }
      }
      this.scheduleTick();
    });
  }

  public getStatus(): { fps: number; frameTimeMs: number; is60Fps: boolean } {
    return {
      fps: this.currentFps,
      frameTimeMs: this.currentFrameTimeMs,
      is60Fps: this.currentFrameTimeMs <= 16.67,
    };
  }
}

export class CockpitClient {
  private static instance: CockpitClient;
  private apiBase: string;
  public frameMonitor: FrameBudgetMonitor;

  private constructor() {
    this.apiBase = (import.meta as any).env?.VITE_API_URL || '';
    this.frameMonitor = new FrameBudgetMonitor();
  }

  public static getInstance(): CockpitClient {
    if (!CockpitClient.instance) {
      CockpitClient.instance = new CockpitClient();
    }
    return CockpitClient.instance;
  }

  /**
   * Deterministic client-side evaluation obeying FrameBudget <= 16.67ms ==> FPS >= 60.
   */
  public evaluateFrameBudgetLocal(renderTimeMs: number, vertexCount: number = 0): FrameBudgetEvaluation {
    const clampedTime = Math.max(0.001, renderTimeMs);
    const fps = Math.round((1000.0 / clampedTime) * 100) / 100;
    const is60fps = clampedTime <= 16.6667;
    const budgetUtil = Math.round((clampedTime / 16.6667) * 10000) / 100;

    let risk: 'NONE' | 'MODERATE' | 'CRITICAL' = 'NONE';
    if (!is60fps) {
      risk = clampedTime <= 33.33 ? 'MODERATE' : 'CRITICAL';
    }

    const needsSimplification = vertexCount > 3000 || !is60fps;
    const optimalVertices = needsSimplification ? Math.min(vertexCount, 2500) : vertexCount;

    return {
      governing_equation: 'FrameBudget <= 16.67ms ==> FPS >= 60',
      render_time_ms: Math.round(clampedTime * 100) / 100,
      fps,
      is_60fps: is60fps,
      budget_utilization_pct: budgetUtil,
      degradation_risk: risk,
      recommended_simplification: needsSimplification,
      vertex_count: vertexCount,
      optimal_target_vertices: optimalVertices,
    };
  }

  /**
   * Evaluates frame budget via REST API with offline fallback.
   */
  public async evaluateFrameBudget(renderTimeMs: number, vertexCount: number = 0): Promise<FrameBudgetEvaluation> {
    try {
      const response = await fetch(`${this.apiBase}/cockpit/frame-budget/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          render_time_ms: renderTimeMs,
          vertex_count: vertexCount,
          dom_nodes: 120,
          active_layers: ['core_basin', 'asset_pins'],
        }),
      });

      if (response.ok) {
        return (await response.json()) as FrameBudgetEvaluation;
      }
    } catch {
      // Fallback seamlessly to local computation
    }

    return this.evaluateFrameBudgetLocal(renderTimeMs, vertexCount);
  }

  /**
   * Optimizes GeoJSON contour vertices to prevent frame drops.
   */
  public async optimizeContours(geojsonData: any, maxVertices: number = 3000): Promise<OptimizedContourResult> {
    try {
      const response = await fetch(`${this.apiBase}/cockpit/contours/optimize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          geojson_data: geojsonData,
          max_vertices: maxVertices,
        }),
      });

      if (response.ok) {
        return (await response.json()) as OptimizedContourResult;
      }
    } catch {
      // Return untouched data if API unreachable
    }

    return {
      type: geojsonData?.type || 'FeatureCollection',
      features: geojsonData?.features || [],
      optimized: false,
      original_vertices: 0,
      result_vertices: 0,
      reduction_pct: 0,
    };
  }

  /**
   * Fetches real-time cockpit diagnostics.
   */
  public async getCockpitState(): Promise<CockpitDiagnostics | null> {
    try {
      const response = await fetch(`${this.apiBase}/cockpit/state`);
      if (response.ok) {
        return (await response.json()) as CockpitDiagnostics;
      }
    } catch {
      return null;
    }
    return null;
  }
}

export const cockpitClient = CockpitClient.getInstance();
