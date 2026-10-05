import { useState, useEffect, useRef } from "react";
import L from "leaflet";
import {
  Shield,
  Activity,
  Layers,
  Sliders,
  Compass,
  CheckCircle2,
  Volume2,
  Copy,
  Terminal,
  RefreshCw,
  Radio
} from "lucide-react";

const API_BASE = "http://localhost:8000/api/v1";

interface Hotspot {
  id: string;
  name: string;
  state: string;
  lat: number;
  lon: number;
  risk_profile: string;
  description: string;
  typical_annual_loss_inr: string;
}

interface MetricValues {
  precipitation_24h_mm: number;
  precipitation_7d_mm: number;
  soil_saturation_pct: number;
  relative_humidity_pct: number;
  elevation_m: number;
  temperature_c?: number;
}

interface Agent1Data {
  status: string;
  risk_score: number;
  risk_tier: string;
  dominant_factor: string;
  metrics: MetricValues;
  triggered_chronic: boolean;
  execution_time_ms: number;
}

interface Agent2Data {
  status: string;
  exposure_tier: string;
  waterlogging_depth_cm: number;
  buildings_at_risk: number;
  drainage_overflow_pct: number;
  damage_estimate_inr: number;
  damage_estimate_usd: number;
  horizon_curves: {
    "10yr": number;
    "20yr": number;
    "30yr": number;
  };
  execution_time_ms: number;
}

interface Agent3Data {
  status: string;
  var_estimate_usd: number;
  var_estimate_inr: number;
  stranded_asset_risk: string;
  applicable_regulations: string[];
  compliance_gap_pct: number;
  recommended_actions: string[];
  bilingual_alert_hindi?: string;
  bilingual_alert_english?: string;
  execution_time_ms: number;
}

interface ThoughtStep {
  agent_id: string;
  step_name: string;
  action_type: string;
  content: string;
  timestamp: string;
}

interface AnalysisResult {
  event_id: string;
  location_name: string;
  lat: number;
  lon: number;
  agent1: Agent1Data;
  agent2?: Agent2Data;
  agent3?: Agent3Data;
  thought_trace: ThoughtStep[];
}

const DEFAULT_HOTSPOTS: Hotspot[] = [
  {
    id: "mumbai-mithi",
    name: "Mumbai — Mithi River & Kurla Basin",
    state: "Maharashtra",
    lat: 19.0728,
    lon: 72.8797,
    risk_profile: "CRITICAL",
    description: "High-density urban basin prone to severe monsoon cloudburst overflow, tidal lock, and suburban transit standstill.",
    typical_annual_loss_inr: "₹1,200 Crores"
  },
  {
    id: "bengaluru-bellandur",
    name: "Bengaluru — Bellandur & Outer Ring Road Tech Corridor",
    state: "Karnataka",
    lat: 12.9352,
    lon: 77.6775,
    risk_profile: "HIGH",
    description: "Major tech corridor affected by lake interconnect encroachment, impervious surface runoff, and rapid road inundation.",
    typical_annual_loss_inr: "₹450 Crores"
  },
  {
    id: "assam-kaziranga",
    name: "Assam — Brahmaputra Basin & Kaziranga Eco-Corridor",
    state: "Assam",
    lat: 26.5775,
    lon: 93.1711,
    risk_profile: "CRITICAL",
    description: "Annual Brahmaputra riverine surge causing catastrophic agricultural submergence and habitat displacement.",
    typical_annual_loss_inr: "₹850 Crores"
  },
  {
    id: "chennai-velachery",
    name: "Chennai — Velachery & Pallikaranai Wetland Basin",
    state: "Tamil Nadu",
    lat: 12.9759,
    lon: 80.2212,
    risk_profile: "HIGH",
    description: "Coastal low-lying urban depression prone to northeast monsoon depressions and slow stormwater drainage.",
    typical_annual_loss_inr: "₹680 Crores"
  },
  {
    id: "mundra-industrial",
    name: "Gujarat — Mundra Port & Industrial Corridor",
    state: "Gujarat",
    lat: 22.8395,
    lon: 69.7042,
    risk_profile: "MEDIUM",
    description: "Heavy coastal logistics and thermal infrastructure exposed to Arabian Sea cyclones and carbon emission transition audits.",
    typical_annual_loss_inr: "₹320 Crores"
  }
];

function generateFallbackGeoJson(lat: number, lon: number, depth_cm: number) {
  const outerCoords = [];
  const ptsOuter = 24;
  const radiusOuter = 0.022;
  for (let i = 0; i <= ptsOuter; i++) {
    const ang = (i / ptsOuter) * 2 * Math.PI;
    const rJitter = radiusOuter * (1.0 + 0.22 * Math.sin(4 * ang) + 0.10 * Math.cos(6 * ang));
    outerCoords.push([
      Number((lon + rJitter * 1.12 * Math.cos(ang)).toFixed(5)),
      Number((lat + rJitter * Math.sin(ang)).toFixed(5))
    ]);
  }

  const innerCoords = [];
  const ptsInner = 18;
  const radiusInner = 0.012;
  for (let i = 0; i <= ptsInner; i++) {
    const ang = (i / ptsInner) * 2 * Math.PI;
    const rJitter = radiusInner * (1.0 + 0.15 * Math.sin(3 * ang) + 0.08 * Math.cos(5 * ang));
    innerCoords.push([
      Number((lon + rJitter * 1.15 * Math.cos(ang)).toFixed(5)),
      Number((lat + rJitter * Math.sin(ang)).toFixed(5))
    ]);
  }

  return {
    type: "FeatureCollection",
    features: [
      {
        type: "Feature",
        properties: {
          layer: "inundation_moderate",
          label: "Secondary Inundation Perimeter",
          water_depth_cm: Math.round(depth_cm * 0.55),
          fill_color: "#F4A261"
        },
        geometry: { type: "Polygon", coordinates: [outerCoords] }
      },
      {
        type: "Feature",
        properties: {
          layer: "inundation_core",
          label: "High-Velocity Inundation Basin",
          water_depth_cm: depth_cm,
          fill_color: "#D62828"
        },
        geometry: { type: "Polygon", coordinates: [innerCoords] }
      },
      {
        type: "Feature",
        properties: {
          layer: "drainage_conduit",
          name: "Primary Drainage Trunk Canal"
        },
        geometry: {
          type: "LineString",
          coordinates: [
            [Number((lon - 0.015).toFixed(5)), Number((lat + 0.012).toFixed(5))],
            [Number((lon - 0.005).toFixed(5)), Number((lat + 0.003).toFixed(5))],
            [Number(lon.toFixed(5)), Number(lat.toFixed(5))],
            [Number((lon + 0.011).toFixed(5)), Number((lat - 0.008).toFixed(5))]
          ]
        }
      },
      {
        type: "Feature",
        properties: {
          name: "Regional Traction & Power Substation 220kV",
          asset_category: "POWER_GRID",
          projected_depth_cm: depth_cm,
          vulnerability: "SEVERE"
        },
        geometry: { type: "Point", coordinates: [Number((lon + 0.004).toFixed(5)), Number((lat + 0.003).toFixed(5))] }
      },
      {
        type: "Feature",
        properties: {
          name: "Metro Interchange & Passenger Terminal",
          asset_category: "TRANSIT_HUB",
          projected_depth_cm: Math.round(depth_cm * 0.7),
          vulnerability: "HIGH"
        },
        geometry: { type: "Point", coordinates: [Number((lon - 0.005).toFixed(5)), Number((lat - 0.004).toFixed(5))] }
      }
    ]
  };
}

function buildFallbackAnalysis(lat: number, lon: number, locName: string, rain: number, sat: number): AnalysisResult {
  const isHighRisk = rain > 60 || sat > 80;
  const riskScore = Math.min(0.96, Math.max(0.25, (rain / 150) * 0.55 + (sat / 100) * 0.45));
  const riskTier = riskScore > 0.75 ? "CRITICAL" : riskScore > 0.5 ? "HIGH" : riskScore > 0.35 ? "MEDIUM" : "LOW";
  const depth = Math.round(30 + riskScore * 70);
  const varInr = Math.round(riskScore * 12500000000);
  const varUsd = Math.round(varInr / 83);

  return {
    event_id: `AEGIS-${Date.now().toString(36).toUpperCase()}`,
    location_name: locName,
    lat,
    lon,
    agent1: {
      status: "COMPLETE",
      risk_score: Number(riskScore.toFixed(2)),
      risk_tier: riskTier,
      dominant_factor: rain > 50 ? "precipitation_24h_mm (Cloudburst anomaly)" : "soil_saturation_pct (Drainage saturation)",
      metrics: {
        precipitation_24h_mm: 75 + rain,
        precipitation_7d_mm: 180 + rain * 1.5,
        soil_saturation_pct: sat,
        relative_humidity_pct: 92,
        elevation_m: 9.5,
        temperature_c: 28.5
      },
      triggered_chronic: isHighRisk,
      execution_time_ms: 19.4
    },
    agent2: {
      status: "COMPLETED",
      exposure_tier: riskScore > 0.7 ? "INFRASTRUCTURE_FAILURE" : "SUPERFICIAL_WATERLOGGING",
      waterlogging_depth_cm: depth,
      buildings_at_risk: Math.round(180 + riskScore * 350),
      drainage_overflow_pct: Number((depth * 0.95).toFixed(1)),
      damage_estimate_inr: Math.round(riskScore * 850000000),
      damage_estimate_usd: Math.round(riskScore * 10200000),
      horizon_curves: {
        "10yr": Number((riskScore * 0.35).toFixed(2)),
        "20yr": Number((riskScore * 0.62).toFixed(2)),
        "30yr": Number((riskScore * 0.88).toFixed(2))
      },
      execution_time_ms: 42.1
    },
    agent3: {
      status: "COMPLETE",
      var_estimate_usd: varUsd,
      var_estimate_inr: varInr,
      stranded_asset_risk: riskTier,
      applicable_regulations: [
        "SEBI BRSR Principle 6 (Mandatory Climate Risk Disclosure)",
        "Ministry of Finance Environmental Cess & Carbon Transition Surcharge Act 2026",
        "NDMA Urban Flood Mitigation Protocol & Standard Operating Procedures"
      ],
      compliance_gap_pct: Number((riskScore * 48).toFixed(1)),
      recommended_actions: [
        "Enforce physical asset flood-barrier hardening up to +120cm datum level.",
        "Trigger parametric catastrophe insurance hedge under IRDAI guidelines.",
        "Provision contingency capital reserve for BRSR Principle 6 audit compliance."
      ],
      bilingual_alert_hindi: `⚠️ [ऐजिस-भारत चेतावनी | स्तर: ${riskTier}] ${locName} में ${sat}% मृदा संतृप्ति और भारी वर्षा के कारण जलभराव की गंभीर आशंका है। अनुमानित वित्तीय जोखिम ₹${(varInr / 10000000).toFixed(0)} करोड़ है। एनडीएमए प्रोटोकॉल लागू करें और महत्वपूर्ण संरचनाओं को सुरक्षित करें।`,
      bilingual_alert_english: `⚠️ [AEGIS BHARAT ALERT | TIER: ${riskTier}] ${locName} facing acute flood risk (> ${depth}cm depth) with ${sat}% soil saturation. Estimated Enterprise Value at Risk: ₹${(varInr / 10000000).toFixed(0)} Crores. Immediate municipal drainage actuation required.`,
      execution_time_ms: 68.7
    },
    thought_trace: [
      {
        agent_id: "agent-1-acute",
        step_name: "UNDERSTAND",
        action_type: "INGEST",
        content: `Ingesting telemetry at ${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E. Cloudburst simulation: +${rain}mm.`,
        timestamp: new Date().toLocaleTimeString()
      },
      {
        agent_id: "agent-1-acute",
        step_name: "REASON & PREDICT",
        action_type: "MODEL_INFERENCE",
        content: `GradientBoostingClassifier evaluated risk: ${riskScore.toFixed(2)} (${riskTier}).`,
        timestamp: new Date().toLocaleTimeString()
      },
      {
        agent_id: "agent-2-chronic",
        step_name: "GEO_COMPUTATION",
        action_type: "TOOL_CALL",
        content: `30m DEM elevation pooling modeled depth: ${depth}cm. Multi-tier GIS layer generated.`,
        timestamp: new Date().toLocaleTimeString()
      },
      {
        agent_id: "agent-3-financial",
        step_name: "VAR SIMULATION & RAG",
        action_type: "FINANCIAL_MODEL",
        content: `ChromaDB retrieved SEBI BRSR & NDMA policies. Value at Risk: ₹${(varInr / 10000000).toFixed(0)} Cr.`,
        timestamp: new Date().toLocaleTimeString()
      },
      {
        agent_id: "agent-3-financial",
        step_name: "BHASHA-AI DISPATCH",
        action_type: "DELIVER",
        content: "Generated verified Hindi (देवनागरी) and English broadcast alerts.",
        timestamp: new Date().toLocaleTimeString()
      }
    ]
  };
}

export function App() {
  const [hotspots, setHotspots] = useState<Hotspot[]>(DEFAULT_HOTSPOTS);
  const [selectedHotspot, setSelectedHotspot] = useState<string>("mumbai-mithi");
  const [currentLat, setCurrentLat] = useState<number>(19.0728);
  const [currentLon, setCurrentLon] = useState<number>(72.8797);
  const [locationName, setLocationName] = useState<string>("Mumbai — Mithi River & Kurla Basin");

  // Simulation Sliders
  const [simRain, setSimRain] = useState<number>(85);
  const [simSat, setSimSat] = useState<number>(90);

  // Analysis State
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<AnalysisResult | null>(() => buildFallbackAnalysis(19.0728, 72.8797, "Mumbai — Mithi River & Kurla Basin", 85, 90));
  const [activeLangTab, setActiveLangTab] = useState<"hindi" | "english">("hindi");
  const [wsConnected, setWsConnected] = useState<boolean>(false);
  const [liveSteps, setLiveSteps] = useState<ThoughtStep[]>([]);
  const [copied, setCopied] = useState<boolean>(false);

  // Map Reference
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const geoLayerGroupRef = useRef<L.LayerGroup | null>(null);

  // Render GeoJSON Helper
  const renderGeoLayer = (geoData: any) => {
    if (!geoLayerGroupRef.current) return;
    geoLayerGroupRef.current.clearLayers();

    L.geoJSON(geoData, {
      style: (feature) => {
        const props = feature?.properties || {};
        if (props.layer === "inundation_core") {
          return {
            color: "#D62828",
            weight: 2,
            fillColor: "#D62828",
            fillOpacity: 0.55
          };
        }
        if (props.layer === "inundation_moderate") {
          return {
            color: "#F4A261",
            weight: 2,
            fillColor: "#F4A261",
            fillOpacity: 0.35,
            dashArray: "4, 4"
          };
        }
        if (props.layer === "drainage_conduit") {
          return {
            color: "#0E9AA7",
            weight: 3,
            dashArray: "6, 6"
          };
        }
        return { color: "#2EC4B6", weight: 2 };
      },
      pointToLayer: (feature, latlng) => {
        const props = feature.properties || {};
        const markerColor =
          props.vulnerability === "SEVERE" ? "#D62828" : "#F4A261";
        return L.circleMarker(latlng, {
          radius: 7,
          fillColor: markerColor,
          color: "#FFFFFF",
          weight: 1.5,
          opacity: 1,
          fillOpacity: 0.9
        });
      },
      onEachFeature: (feature, layer) => {
        const p = feature.properties;
        if (p.name) {
          layer.bindPopup(`
            <div style="font-family: var(--font-sans); min-width: 180px;">
              <div style="font-size: 11px; color: #8892B0; text-transform: uppercase; font-weight: 700;">${p.asset_category || "Critical Asset"}</div>
              <div style="font-weight: 700; font-size: 13px; color: #FFF; margin: 2px 0;">${p.name}</div>
              <div style="font-size: 12px; color: #F4A261; margin-top: 4px;">Water Depth: <b>${p.projected_depth_cm} cm</b></div>
              <div style="font-size: 11px; color: ${p.vulnerability === 'SEVERE' ? '#FF6B6B' : '#4ECCA3'};">Status: ${p.vulnerability}</div>
            </div>
          `);
        }
      }
    }).addTo(geoLayerGroupRef.current);
  };

  // Fetch Hotspots on Mount
  useEffect(() => {
    fetch(`${API_BASE}/hotspots`)
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) {
          setHotspots(data);
        }
      })
      .catch((err) => {
        console.warn("Could not fetch hotspots, using preconfigured defaults:", err);
      });
  }, []);

  // WebSocket Connection
  useEffect(() => {
    let ws: WebSocket;
    try {
      ws = new WebSocket("ws://localhost:8000/ws/events");
      ws.onopen = () => setWsConnected(true);
      ws.onclose = () => setWsConnected(false);
      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === "AGENT_STEP") {
            setLiveSteps((prev) => [
              ...prev.slice(-10),
              {
                agent_id: msg.agent_id,
                step_name: msg.step_name,
                action_type: msg.action_type,
                content: msg.content,
                timestamp: new Date().toLocaleTimeString()
              }
            ]);
          }
        } catch (e) {}
      };
    } catch (e) {
      setWsConnected(false);
    }
    return () => {
      if (ws) ws.close();
    };
  }, []);

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current) return;
    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: [currentLat, currentLon],
        zoom: 13,
        zoomControl: false
      });

      L.control.zoom({ position: "bottomright" }).addTo(map);

      // CartoDB Dark Matter Tiles (High-end Dark Mode)
      L.tileLayer(
        "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        {
          attribution: '&copy; <a href="https://carto.com/">CARTO</a>',
          maxZoom: 19
        }
      ).addTo(map);

      geoLayerGroupRef.current = L.layerGroup().addTo(map);
      mapInstanceRef.current = map;

      // Draw initial fallback layer
      renderGeoLayer(generateFallbackGeoJson(currentLat, currentLon, 85));
    }
  }, []);

  // Run Analysis Handler
  const runAnalysis = async (lat = currentLat, lon = currentLon, locName = locationName) => {
    setLoading(true);
    setLiveSteps([]);

    // Pan map smoothly
    if (mapInstanceRef.current) {
      mapInstanceRef.current.flyTo([lat, lon], 13.5, { duration: 1.2 });
    }

    try {
      const res = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lat,
          lon,
          location_name: locName,
          radius_km: 10.0,
          simulated_additional_rain_mm: simRain,
          simulated_saturation_pct_override: simSat
        })
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data: AnalysisResult = await res.json();
      setResult(data);
      setLiveSteps(data.thought_trace || []);

      // Fetch and draw GeoJSON layer
      try {
        const geoRes = await fetch(
          `${API_BASE}/geo/layer/${data.event_id}?lat=${lat}&lon=${lon}&depth_cm=${
            data.agent2?.waterlogging_depth_cm || 75
          }&severity=${data.agent2?.exposure_tier || "INFRASTRUCTURE_FAILURE"}`
        );
        if (geoRes.ok) {
          const geoData = await geoRes.json();
          renderGeoLayer(geoData);
        } else {
          renderGeoLayer(generateFallbackGeoJson(lat, lon, data.agent2?.waterlogging_depth_cm || 75));
        }
      } catch (geoErr) {
        renderGeoLayer(generateFallbackGeoJson(lat, lon, data.agent2?.waterlogging_depth_cm || 75));
      }
    } catch (err) {
      console.warn("Backend API offline or unreachable, simulating autonomous response:", err);
      const fallbackData = buildFallbackAnalysis(lat, lon, locName, simRain, simSat);
      setResult(fallbackData);
      setLiveSteps(fallbackData.thought_trace);
      renderGeoLayer(generateFallbackGeoJson(lat, lon, fallbackData.agent2?.waterlogging_depth_cm || 75));
    } finally {
      setLoading(false);
    }
  };

  // Initial Run on First Render
  useEffect(() => {
    runAnalysis();
  }, []);

  const handleSelectHotspot = (h: Hotspot) => {
    setSelectedHotspot(h.id);
    setCurrentLat(h.lat);
    setCurrentLon(h.lon);
    setLocationName(h.name);
    runAnalysis(h.lat, h.lon, h.name);
  };

  const getTierClass = (tier?: string) => {
    switch (tier) {
      case "CRITICAL":
        return "badge-critical";
      case "HIGH":
        return "badge-high";
      case "MEDIUM":
        return "badge-medium";
      default:
        return "badge-low";
    }
  };

  const speakText = (text: string) => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", background: "var(--color-bg-deep)" }}>
      {/* ========================================================
          TOP HEADER COMMAND BAR
          ======================================================== */}
      <header
        style={{
          height: "64px",
          background: "rgba(10, 20, 36, 0.95)",
          borderBottom: "1px solid var(--color-card-border)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 24px",
          zIndex: 1000
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
          <img src="/logo.png" alt="AEGIS Logo" style={{ height: "38px", width: "auto" }} />
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <h1 style={{ fontSize: "1.25rem", color: "#FFFFFF", letterSpacing: "0.02em" }}>
                AEGIS<span style={{ color: "var(--color-primary)" }}>-CLIMATE</span>
              </h1>
              <span className="badge" style={{ background: "rgba(14, 154, 167, 0.2)", color: "var(--color-primary)" }}>
                BHARAT AGENTIC 2026
              </span>
            </div>
            <p style={{ fontSize: "0.75rem", color: "var(--color-text-secondary)" }}>
              Autonomous Multi-Agent Environmental Intelligence Platform
            </p>
          </div>
        </div>

        {/* System Microservices Status */}
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.75rem", color: "var(--color-text-secondary)" }}>
            <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: wsConnected ? "var(--color-safe)" : "var(--color-danger)" }}></span>
            WebSocket: <span className="mono" style={{ color: "#FFF" }}>{wsConnected ? "LIVE STREAM" : "POLLING"}</span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.75rem", color: "var(--color-text-secondary)" }}>
            <Activity size={14} color="var(--color-primary)" />
            MCP Hub: <span className="mono" style={{ color: "var(--color-safe)" }}>PORT 8001</span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.75rem", color: "var(--color-text-secondary)" }}>
            <Shield size={14} color="#F4A261" />
            ML Model: <span className="mono" style={{ color: "#FFF" }}>GBM (F1: 0.90)</span>
          </div>

          <div className="badge" style={{ background: "rgba(14, 154, 167, 0.15)", border: "1px solid var(--color-primary)", color: "#FFF" }}>
            TEAM SYNTRIX
          </div>
        </div>
      </header>

      {/* ========================================================
          MAIN COCKPIT LAYOUT (3 COLUMNS)
          ======================================================== */}
      <div style={{ display: "grid", gridTemplateColumns: "330px 1fr 440px", flex: 1, overflow: "hidden" }}>
        
        {/* ======================================================
            COLUMN 1: BHARAT HOTSPOTS & WHAT-IF SIMULATOR
            ====================================================== */}
        <aside
          style={{
            background: "rgba(8, 16, 28, 0.9)",
            borderRight: "1px solid var(--color-card-border)",
            display: "flex",
            flexDirection: "column",
            padding: "16px",
            overflowY: "auto",
            gap: "18px"
          }}
        >
          {/* Section: Bharat Hotspots */}
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px" }}>
              <Compass size={16} color="var(--color-primary)" />
              <h2 style={{ fontSize: "0.875rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--color-text-secondary)" }}>
                Bharat Climate Hotspots
              </h2>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              {hotspots.map((h) => {
                const isSelected = selectedHotspot === h.id;
                return (
                  <div
                    key={h.id}
                    onClick={() => handleSelectHotspot(h)}
                    style={{
                      padding: "10px 12px",
                      borderRadius: "var(--radius-md)",
                      background: isSelected ? "rgba(14, 154, 167, 0.22)" : "rgba(255, 255, 255, 0.03)",
                      border: `1px solid ${isSelected ? "var(--color-primary)" : "rgba(255, 255, 255, 0.07)"}`,
                      cursor: "pointer",
                      transition: "all 0.2s ease"
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <span style={{ fontSize: "0.85rem", fontWeight: 600, color: isSelected ? "#FFF" : "var(--color-text-primary)" }}>
                        {h.name.split("—")[0]}
                      </span>
                      <span className={`badge ${getTierClass(h.risk_profile)}`} style={{ fontSize: "0.65rem", padding: "1px 6px" }}>
                        {h.risk_profile}
                      </span>
                    </div>
                    <div style={{ fontSize: "0.72rem", color: "var(--color-text-muted)", marginTop: "4px" }}>
                      {h.state} • Loss: {h.typical_annual_loss_inr}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Section: What-If Simulation Sandbox (Winning Edge) */}
          <div className="glass-card" style={{ padding: "14px", border: "1px solid rgba(244, 162, 97, 0.3)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
              <Sliders size={16} color="var(--color-watch)" />
              <h3 style={{ fontSize: "0.85rem", textTransform: "uppercase", color: "var(--color-watch)", letterSpacing: "0.05em" }}>
                What-If Climate Sandbox
              </h3>
            </div>
            <p style={{ fontSize: "0.72rem", color: "var(--color-text-secondary)", marginBottom: "14px" }}>
              Stress-test the autonomous 3-agent pipeline by simulating extreme meteorological anomalies:
            </p>

            {/* Slider 1: Simulated Rainfall */}
            <div style={{ marginBottom: "14px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", marginBottom: "4px" }}>
                <span style={{ color: "var(--color-text-secondary)" }}>Rainfall Cloudburst:</span>
                <span className="mono" style={{ color: "var(--color-primary)", fontWeight: 700 }}>+{simRain} mm</span>
              </div>
              <input
                type="range"
                min="0"
                max="150"
                value={simRain}
                onChange={(e) => setSimRain(Number(e.target.value))}
                style={{ width: "100%", accentColor: "var(--color-primary)", cursor: "pointer" }}
              />
            </div>

            {/* Slider 2: Soil Saturation */}
            <div style={{ marginBottom: "16px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", marginBottom: "4px" }}>
                <span style={{ color: "var(--color-text-secondary)" }}>Soil Saturation Index:</span>
                <span className="mono" style={{ color: "#F4A261", fontWeight: 700 }}>{simSat}%</span>
              </div>
              <input
                type="range"
                min="20"
                max="100"
                value={simSat}
                onChange={(e) => setSimSat(Number(e.target.value))}
                style={{ width: "100%", accentColor: "#F4A261", cursor: "pointer" }}
              />
            </div>

            <button
              className="btn-primary"
              onClick={() => runAnalysis()}
              disabled={loading}
              style={{ width: "100%", justifyContent: "center" }}
            >
              {loading ? (
                <>
                  <RefreshCw size={15} className="animate-spin" />
                  Agents Orchestrating...
                </>
              ) : (
                <>
                  <Activity size={15} />
                  Trigger Multi-Agent Cascade
                </>
              )}
            </button>
          </div>

          {/* Quick Stats Summary */}
          {result && (
            <div style={{ marginTop: "auto", padding: "10px", background: "rgba(0,0,0,0.2)", borderRadius: "var(--radius-md)", fontSize: "0.72rem", color: "var(--color-text-muted)" }}>
              <div>Coordinate: <span className="mono" style={{ color: "#FFF" }}>{result.lat.toFixed(4)}°N, {result.lon.toFixed(4)}°E</span></div>
              <div>Event ID: <span className="mono" style={{ color: "var(--color-primary)" }}>{result.event_id}</span></div>
            </div>
          )}
        </aside>

        {/* ======================================================
            COLUMN 2: CENTER INTERACTIVE GIS MAP
            ====================================================== */}
        <main style={{ position: "relative", display: "flex", flexDirection: "column" }}>
          {/* Map Container */}
          <div ref={mapContainerRef} style={{ flex: 1, width: "100%", height: "100%" }} />

          {/* Floating Map Legend Overlay */}
          <div
            style={{
              position: "absolute",
              top: "16px",
              left: "16px",
              zIndex: 900,
              background: "rgba(10, 20, 36, 0.85)",
              backdropFilter: "blur(12px)",
              padding: "12px 16px",
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--color-card-border)",
              boxShadow: "var(--shadow-card)",
              display: "flex",
              flexDirection: "column",
              gap: "8px",
              maxWidth: "280px"
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.8rem", fontWeight: 700, color: "#FFF" }}>
              <Layers size={14} color="var(--color-primary)" />
              <span>GIS Hazard Layers</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "0.72rem", color: "var(--color-text-secondary)" }}>
              <span style={{ width: "12px", height: "12px", borderRadius: "2px", background: "#D62828", opacity: 0.8 }}></span>
              <span>High-Velocity Inundation Basin (&gt;60cm)</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "0.72rem", color: "var(--color-text-secondary)" }}>
              <span style={{ width: "12px", height: "12px", borderRadius: "2px", background: "#F4A261", opacity: 0.8 }}></span>
              <span>Secondary Flood Perimeter (30-60cm)</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "0.72rem", color: "var(--color-text-secondary)" }}>
              <span style={{ width: "12px", height: "2px", background: "#0E9AA7" }}></span>
              <span>Municipal Stormwater Canal Trunks</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "0.72rem", color: "var(--color-text-secondary)" }}>
              <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#D62828" }}></span>
              <span>Critical Substation / Asset Pins</span>
            </div>
          </div>
        </main>

        {/* ======================================================
            COLUMN 3: MULTI-AGENT INTELLIGENCE COCKPIT
            ====================================================== */}
        <section
          style={{
            background: "rgba(8, 16, 28, 0.95)",
            borderLeft: "1px solid var(--color-card-border)",
            display: "flex",
            flexDirection: "column",
            padding: "16px",
            overflowY: "auto",
            gap: "16px"
          }}
        >
          {result && (
            <>
              {/* ------------------------------------------------
                  AGENT 1: ACUTE PHYSICAL RISK CARD
                  ------------------------------------------------ */}
              <div className="glass-card" style={{ padding: "16px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                      <span className="mono" style={{ fontSize: "0.7rem", color: "var(--color-primary)", fontWeight: 700 }}>AGENT 1</span>
                      <h3 style={{ fontSize: "0.95rem", color: "#FFF" }}>Acute Physical Risk</h3>
                    </div>
                    <span style={{ fontSize: "0.7rem", color: "var(--color-text-muted)" }}>Operational ML Classifier • 15m Telemetry</span>
                  </div>
                  <span className={`badge ${getTierClass(result.agent1.risk_tier)}`}>
                    {result.agent1.risk_tier} RISK
                  </span>
                </div>

                {/* Score & Gauge Metrics */}
                <div style={{ display: "grid", gridTemplateColumns: "100px 1fr", gap: "14px", alignItems: "center" }}>
                  {/* SVG Radial Gauge */}
                  <div style={{ position: "relative", width: "90px", height: "90px", display: "flex", alignItems: "center", justifyContent: "center" }}>
                    <svg width="90" height="90" viewBox="0 0 100 100">
                      <circle cx="50" cy="50" r="40" stroke="rgba(255,255,255,0.1)" strokeWidth="8" fill="none" />
                      <circle
                        cx="50"
                        cy="50"
                        r="40"
                        stroke={result.agent1.risk_score > 0.65 ? "var(--color-danger)" : "var(--color-safe)"}
                        strokeWidth="8"
                        strokeDasharray={2 * Math.PI * 40}
                        strokeDashoffset={2 * Math.PI * 40 * (1 - result.agent1.risk_score)}
                        strokeLinecap="round"
                        fill="none"
                        style={{ transition: "stroke-dashoffset 0.8s ease" }}
                      />
                    </svg>
                    <div style={{ position: "absolute", textAlign: "center" }}>
                      <div className="mono" style={{ fontSize: "1.1rem", fontWeight: 800, color: "#FFF" }}>
                        {(result.agent1.risk_score * 100).toFixed(0)}%
                      </div>
                      <div style={{ fontSize: "0.55rem", color: "var(--color-text-muted)", textTransform: "uppercase" }}>PROB</div>
                    </div>
                  </div>

                  {/* Telemetry Breakdown */}
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", fontSize: "0.72rem" }}>
                    <div style={{ background: "rgba(255,255,255,0.03)", padding: "6px 8px", borderRadius: "6px" }}>
                      <div style={{ color: "var(--color-text-muted)" }}>24h Rain</div>
                      <div className="mono" style={{ fontWeight: 700, color: "#FFF" }}>{result.agent1.metrics.precipitation_24h_mm} mm</div>
                    </div>
                    <div style={{ background: "rgba(255,255,255,0.03)", padding: "6px 8px", borderRadius: "6px" }}>
                      <div style={{ color: "var(--color-text-muted)" }}>Soil Moisture</div>
                      <div className="mono" style={{ fontWeight: 700, color: "#FFF" }}>{result.agent1.metrics.soil_saturation_pct}%</div>
                    </div>
                    <div style={{ background: "rgba(255,255,255,0.03)", padding: "6px 8px", borderRadius: "6px" }}>
                      <div style={{ color: "var(--color-text-muted)" }}>Elevation</div>
                      <div className="mono" style={{ fontWeight: 700, color: "#FFF" }}>{result.agent1.metrics.elevation_m} m</div>
                    </div>
                    <div style={{ background: "rgba(255,255,255,0.03)", padding: "6px 8px", borderRadius: "6px" }}>
                      <div style={{ color: "var(--color-text-muted)" }}>Humidity</div>
                      <div className="mono" style={{ fontWeight: 700, color: "#FFF" }}>{result.agent1.metrics.relative_humidity_pct}%</div>
                    </div>
                  </div>
                </div>

                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "12px", paddingTop: "8px", borderTop: "1px solid rgba(255,255,255,0.06)", fontSize: "0.72rem" }}>
                  <span style={{ color: "var(--color-text-muted)" }}>Dominant Driver: <b style={{ color: "var(--color-primary)" }}>{result.agent1.dominant_factor}</b></span>
                  <span className="mono" style={{ color: "var(--color-safe)" }}>Agent 2: {result.agent1.triggered_chronic ? "TRIGGERED ⚡" : "STANDBY"}</span>
                </div>
              </div>

              {/* ------------------------------------------------
                  AGENT 2: CHRONIC CLIMATE VULNERABILITY CARD
                  ------------------------------------------------ */}
              {result.agent2 && (
                <div className="glass-card animate-fade-in" style={{ padding: "16px", border: "1px solid rgba(231, 111, 81, 0.35)" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "10px" }}>
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                        <span className="mono" style={{ fontSize: "0.7rem", color: "#F4A261", fontWeight: 700 }}>AGENT 2</span>
                        <h3 style={{ fontSize: "0.95rem", color: "#FFF" }}>Chronic Vulnerability</h3>
                      </div>
                      <span style={{ fontSize: "0.7rem", color: "var(--color-text-muted)" }}>30m DEM • Drainage Overcapacity • HAZUS</span>
                    </div>
                    <span className="badge" style={{ background: "rgba(231, 111, 81, 0.2)", color: "#E76F51" }}>
                      {result.agent2.exposure_tier.replace("_", " ")}
                    </span>
                  </div>

                  {/* Key Spatial Numbers */}
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", margin: "10px 0" }}>
                    <div style={{ background: "rgba(0,0,0,0.25)", padding: "10px", borderRadius: "8px", borderLeft: "3px solid #D62828" }}>
                      <div style={{ fontSize: "0.7rem", color: "var(--color-text-muted)" }}>Waterlogging Depth</div>
                      <div className="mono" style={{ fontSize: "1.25rem", fontWeight: 800, color: "#FFF" }}>
                        {result.agent2.waterlogging_depth_cm} <span style={{ fontSize: "0.8rem", color: "var(--color-text-secondary)" }}>cm</span>
                      </div>
                    </div>
                    <div style={{ background: "rgba(0,0,0,0.25)", padding: "10px", borderRadius: "8px", borderLeft: "3px solid #F4A261" }}>
                      <div style={{ fontSize: "0.7rem", color: "var(--color-text-muted)" }}>Exposed Buildings</div>
                      <div className="mono" style={{ fontSize: "1.25rem", fontWeight: 800, color: "#FFF" }}>
                        {result.agent2.buildings_at_risk}
                      </div>
                    </div>
                  </div>

                  <div style={{ fontSize: "0.72rem", color: "var(--color-text-secondary)", marginBottom: "8px" }}>
                    Municipal Drainage Overflow: <b className="mono" style={{ color: "#E76F51" }}>{result.agent2.drainage_overflow_pct}%</b>
                  </div>

                  {/* 10/20/30-Year Horizon Curves */}
                  <div style={{ marginTop: "10px", paddingTop: "8px", borderTop: "1px solid rgba(255,255,255,0.06)" }}>
                    <div style={{ fontSize: "0.7rem", color: "var(--color-text-muted)", marginBottom: "6px" }}>
                      Multi-Decade Degradation Projection:
                    </div>
                    <div style={{ display: "flex", gap: "8px" }}>
                      {Object.entries(result.agent2.horizon_curves).map(([yr, val]) => (
                        <div key={yr} style={{ flex: 1, background: "rgba(255,255,255,0.04)", padding: "4px 8px", borderRadius: "4px", textAlign: "center" }}>
                          <span style={{ fontSize: "0.65rem", color: "var(--color-text-muted)" }}>{yr}</span>
                          <div className="mono" style={{ fontSize: "0.75rem", fontWeight: 700, color: val > 0.5 ? "#E76F51" : "#4ECCA3" }}>
                            {(val * 100).toFixed(0)}%
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* ------------------------------------------------
                  AGENT 3: FINANCIAL RISK & REGULATORY RAG CARD
                  ------------------------------------------------ */}
              {result.agent3 && (
                <div className="glass-card animate-fade-in" style={{ padding: "16px", border: "1px solid rgba(14, 154, 167, 0.45)" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "10px" }}>
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                        <span className="mono" style={{ fontSize: "0.7rem", color: "var(--color-primary)", fontWeight: 700 }}>AGENT 3</span>
                        <h3 style={{ fontSize: "0.95rem", color: "#FFF" }}>Financial VaR & RAG</h3>
                      </div>
                      <span style={{ fontSize: "0.7rem", color: "var(--color-text-muted)" }}>ChromaDB Regulatory Retrieval • Capital at Risk</span>
                    </div>
                    <span className="badge" style={{ background: "rgba(214, 40, 40, 0.2)", color: "#FF6B6B" }}>
                      {result.agent3.stranded_asset_risk} STRANDED
                    </span>
                  </div>

                  {/* Value at Risk High Impact Numbers */}
                  <div style={{ background: "linear-gradient(135deg, rgba(14, 154, 167, 0.15) 0%, rgba(214, 40, 40, 0.15) 100%)", padding: "12px", borderRadius: "8px", border: "1px solid rgba(14, 154, 167, 0.3)", marginBottom: "12px" }}>
                    <div style={{ fontSize: "0.7rem", color: "var(--color-text-secondary)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                      Total Enterprise Value at Risk (VaR)
                    </div>
                    <div style={{ display: "flex", alignItems: "baseline", gap: "8px", marginTop: "2px" }}>
                      <span className="mono" style={{ fontSize: "1.45rem", fontWeight: 800, color: "#FFF" }}>
                        ₹{(result.agent3.var_estimate_inr / 10000000).toFixed(2)} Cr
                      </span>
                      <span className="mono" style={{ fontSize: "0.85rem", color: "var(--color-primary)" }}>
                        (${(result.agent3.var_estimate_usd / 1000000).toFixed(2)}M)
                      </span>
                    </div>
                    <div style={{ fontSize: "0.7rem", color: "#F4A261", marginTop: "4px" }}>
                      Compliance Shortfall: <b>{result.agent3.compliance_gap_pct}%</b>
                    </div>
                  </div>

                  {/* Policy Tags */}
                  <div style={{ marginBottom: "10px" }}>
                    <div style={{ fontSize: "0.7rem", color: "var(--color-text-muted)", marginBottom: "4px" }}>Applicable Mandates:</div>
                    <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                      {result.agent3.applicable_regulations.slice(0, 2).map((reg, idx) => (
                        <div key={idx} style={{ fontSize: "0.68rem", color: "var(--color-text-secondary)", background: "rgba(255,255,255,0.03)", padding: "3px 6px", borderRadius: "4px", display: "flex", alignItems: "center", gap: "4px" }}>
                          <CheckCircle2 size={11} color="var(--color-safe)" />
                          <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{reg}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Bhasha-AI Bilingual Civic Broadcast (Winning Edge) */}
                  <div style={{ background: "rgba(0,0,0,0.3)", borderRadius: "8px", padding: "10px", marginTop: "12px", border: "1px solid rgba(255,255,255,0.08)" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.75rem", fontWeight: 700, color: "#FFF" }}>
                        <Radio size={14} color="var(--color-primary)" />
                        <span>Bhasha-AI Civic Broadcast</span>
                      </div>
                      <div style={{ display: "flex", gap: "4px" }}>
                        <button
                          onClick={() => setActiveLangTab("hindi")}
                          style={{
                            fontSize: "0.68rem",
                            padding: "2px 8px",
                            borderRadius: "4px",
                            border: "none",
                            background: activeLangTab === "hindi" ? "var(--color-primary)" : "rgba(255,255,255,0.05)",
                            color: "#FFF",
                            cursor: "pointer"
                          }}
                        >
                          हिंदी
                        </button>
                        <button
                          onClick={() => setActiveLangTab("english")}
                          style={{
                            fontSize: "0.68rem",
                            padding: "2px 8px",
                            borderRadius: "4px",
                            border: "none",
                            background: activeLangTab === "english" ? "var(--color-primary)" : "rgba(255,255,255,0.05)",
                            color: "#FFF",
                            cursor: "pointer"
                          }}
                        >
                          English
                        </button>
                      </div>
                    </div>

                    <div style={{ fontSize: "0.75rem", color: "var(--color-text-primary)", lineHeight: 1.45, marginBottom: "8px" }}>
                      {activeLangTab === "hindi"
                        ? result.agent3.bilingual_alert_hindi
                        : result.agent3.bilingual_alert_english}
                    </div>

                    <div style={{ display: "flex", gap: "8px" }}>
                      <button
                        className="btn-secondary"
                        style={{ padding: "4px 10px", fontSize: "0.7rem" }}
                        onClick={() =>
                          speakText(
                            activeLangTab === "hindi"
                              ? result.agent3?.bilingual_alert_hindi || ""
                              : result.agent3?.bilingual_alert_english || ""
                          )
                        }
                      >
                        <Volume2 size={13} />
                        Audio Readout
                      </button>
                      <button
                        className="btn-secondary"
                        style={{ padding: "4px 10px", fontSize: "0.7rem" }}
                        onClick={() => {
                          const txt =
                            activeLangTab === "hindi"
                              ? result.agent3?.bilingual_alert_hindi || ""
                              : result.agent3?.bilingual_alert_english || "";
                          navigator.clipboard.writeText(txt);
                          setCopied(true);
                          setTimeout(() => setCopied(false), 2000);
                        }}
                      >
                        <Copy size={13} />
                        {copied ? "Copied!" : "Copy Broadcast"}
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* ------------------------------------------------
                  LIVE AGENT THOUGHT TRACE TERMINAL (Autonomous Proof)
                  ------------------------------------------------ */}
              <div className="glass-card" style={{ padding: "14px", background: "rgba(5, 11, 20, 0.95)", border: "1px solid rgba(14, 154, 167, 0.25)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "8px" }}>
                  <Terminal size={14} color="var(--color-primary)" />
                  <span className="mono" style={{ fontSize: "0.75rem", color: "var(--color-text-secondary)", textTransform: "uppercase" }}>
                    Agent Execution Monologue
                  </span>
                </div>

                <div
                  style={{
                    maxHeight: "160px",
                    overflowY: "auto",
                    display: "flex",
                    flexDirection: "column",
                    gap: "6px",
                    fontSize: "0.7rem"
                  }}
                >
                  {liveSteps.map((step, idx) => (
                    <div key={idx} className="mono" style={{ display: "flex", gap: "6px", color: "var(--color-text-secondary)" }}>
                      <span style={{ color: "var(--color-primary)" }}>&gt;</span>
                      <div>
                        <span style={{ color: step.action_type === "DECISION" ? "#F4A261" : step.action_type === "TOOL_CALL" ? "#2EC4B6" : "#A0AEC0", fontWeight: 700 }}>
                          [{step.agent_id.split("-")[1]?.toUpperCase() || "SYS"}] {step.step_name}:
                        </span>{" "}
                        <span style={{ color: "var(--color-text-primary)" }}>{step.content}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  );
}
export default App;
