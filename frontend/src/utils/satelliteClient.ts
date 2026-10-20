/**
 * AEGIS-CLIMATE Phase 16 Multimodal Earth Observation Client
 * Module: frontend/src/utils/satelliteClient.ts
 * Governance: Gravitas Reliability Runtime · Copernicus Sentinel-2 & ISRO Bhuvan Ingestion
 *
 * Mathematical Governing Equations:
 * NDWI = (Green - NIR) / (Green + NIR)
 * NDVI = (NIR - Red) / (NIR + Red)
 * MNDWI = (Green - SWIR) / (Green + SWIR)
 */

export interface SpectralBands {
  green_b03: number;
  red_b04: number;
  nir_b08: number;
  swir_b11?: number;
}

export interface SpectralIndicesResult {
  governing_equations: {
    NDWI: string;
    NDVI: string;
    MNDWI?: string;
  };
  bands: SpectralBands;
  ndwi: number;
  ndvi: number;
  mndwi?: number;
  estimated_surface_water_pct: number;
  water_detection_flag: boolean;
  vegetation_health_flag: boolean;
}

export interface SatelliteObservationHealth {
  phase: number;
  subsystem: string;
  circuit_state: string;
  consecutive_failures: number;
  failure_threshold: number;
  cooldown_period_sec: number;
  cached_observations: number;
  status: string;
}

export class SatelliteClient {
  private static instance: SatelliteClient;
  private apiBase: string;

  private constructor() {
    this.apiBase = import.meta.env?.VITE_API_URL || '';
  }

  public static getInstance(): SatelliteClient {
    if (!SatelliteClient.instance) {
      SatelliteClient.instance = new SatelliteClient();
    }
    return SatelliteClient.instance;
  }

  /**
   * Deterministic local calculation of NDWI, NDVI, and MNDWI.
   * Guarantees zero downtime when network partition occurs.
   */
  public computeSpectralIndicesLocal(
    green: number,
    red: number,
    nir: number,
    swir?: number
  ): SpectralIndicesResult {
    const g = Math.max(0, Math.min(1, green));
    const r = Math.max(0, Math.min(1, red));
    const n = Math.max(0, Math.min(1, nir));
    const s = swir !== undefined ? Math.max(0, Math.min(1, swir)) : 0;

    const ndwiDenom = g + n;
    const ndwi = Number((ndwiDenom > 1e-6 ? (g - n) / ndwiDenom : 0).toFixed(4));

    const ndviDenom = n + r;
    const ndvi = Number((ndviDenom > 1e-6 ? (n - r) / ndviDenom : 0).toFixed(4));

    const waterFraction = Math.max(0, Math.min(1, (ndwi + 1) / 2));

    const result: SpectralIndicesResult = {
      governing_equations: {
        NDWI: 'NDWI = (Green - NIR) / (Green + NIR)',
        NDVI: 'NDVI = (NIR - Red) / (NIR + Red)',
      },
      bands: {
        green_b03: g,
        red_b04: r,
        nir_b08: n,
        swir_b11: s,
      },
      ndwi: Math.max(-1, Math.min(1, ndwi)),
      ndvi: Math.max(-1, Math.min(1, ndvi)),
      estimated_surface_water_pct: Number((waterFraction * 100).toFixed(2)),
      water_detection_flag: ndwi > 0,
      vegetation_health_flag: ndvi > 0.2,
    };

    if (swir !== undefined) {
      const mndwiDenom = g + s;
      const mndwi = Number((mndwiDenom > 1e-6 ? (g - s) / mndwiDenom : 0).toFixed(4));
      result.mndwi = Math.max(-1, Math.min(1, mndwi));
      result.governing_equations.MNDWI = 'MNDWI = (Green - SWIR) / (Green + SWIR)';
    }

    return result;
  }

  /**
   * Calls the backend API to compute Sentinel-2 spectral indices with local fallback.
   */
  public async computeSpectralIndices(
    green: number,
    red: number,
    nir: number,
    swir?: number
  ): Promise<SpectralIndicesResult> {
    try {
      const resp = await fetch(`${this.apiBase}/satellite/indices/compute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ green, red, nir, swir }),
      });
      if (!resp.ok) {
        throw new Error(`API error: ${resp.status}`);
      }
      return await resp.json();
    } catch {
      return this.computeSpectralIndicesLocal(green, red, nir, swir);
    }
  }

  /**
   * Ingests multispectral, geological, and DEM telemetry for a coordinate.
   */
  public async ingestTelemetry(lat: number, lon: number, locationName?: string, elevationM: number = 12.0) {
    const resp = await fetch(`${this.apiBase}/satellite/ingest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        lat,
        lon,
        location_name: locationName || 'Corridor Telemetry',
        elevation_m: elevationM,
      }),
    });
    if (!resp.ok) {
      throw new Error(`Ingest failed: ${resp.status}`);
    }
    return await resp.json();
  }

  /**
   * Fetches Phase 16 health status.
   */
  public async getHealth(): Promise<SatelliteObservationHealth> {
    const resp = await fetch(`${this.apiBase}/satellite/phase16/health`);
    if (!resp.ok) {
      throw new Error(`Health check failed: ${resp.status}`);
    }
    return await resp.json();
  }
}

export const satelliteClient = SatelliteClient.getInstance();
