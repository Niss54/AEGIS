import React, { useState, useEffect } from "react";
import { Radio, RefreshCw, Zap } from "lucide-react";

export interface DuckNode {
  duck_id: string;
  duck_type: "DuckLink" | "MamaDuck" | "PapaDuck";
  name: string;
  lat: number;
  lon: number;
  battery_pct: number;
  status: "HEALTHY" | "WARNING" | "CRITICAL" | "SOS_ALERT";
  last_seen: string;
  last_rssi: number;
  water_level_cm?: number;
  total_packets_routed: number;
}

export interface MeshLink {
  source: string;
  target: string;
  rssi: number;
  quality: "EXCELLENT" | "GOOD" | "MARGINAL" | "CRITICAL";
}

export interface MeshTopology {
  nodes: DuckNode[];
  links: MeshLink[];
  total_active_nodes: number;
  active_sos_alerts: number;
  average_mesh_delivery_rate: number;
  dead_zones_detected: string[];
  gateway_status: string;
}

interface MeshTopologyRadarProps {
  backendBase?: string;
}

const DEFAULT_TOPOLOGY: MeshTopology = {
  nodes: [
    {
      duck_id: "PAPADUCK-GW-01",
      duck_type: "PapaDuck",
      name: "PapaDuck Central Command Gateway (Solar Base)",
      lat: 19.076,
      lon: 72.877,
      battery_pct: 98,
      status: "HEALTHY",
      last_seen: "Just now (Active)",
      last_rssi: -54,
      total_packets_routed: 1428
    },
    {
      duck_id: "MAMADUCK-RELAY-01",
      duck_type: "MamaDuck",
      name: "MamaDuck Kurla Elevated Repeater",
      lat: 19.073,
      lon: 72.881,
      battery_pct: 87,
      status: "HEALTHY",
      last_seen: "4s ago",
      last_rssi: -68,
      total_packets_routed: 864
    },
    {
      duck_id: "MAMADUCK-RELAY-02",
      duck_type: "MamaDuck",
      name: "MamaDuck Bandra East Repeater",
      lat: 19.062,
      lon: 72.868,
      battery_pct: 79,
      status: "HEALTHY",
      last_seen: "12s ago",
      last_rssi: -74,
      total_packets_routed: 512
    },
    {
      duck_id: "DUCKLINK-SENSOR-01",
      duck_type: "DuckLink",
      name: "DuckLink Mithi River Level Sensor 01",
      lat: 19.071,
      lon: 72.879,
      battery_pct: 82,
      status: "WARNING",
      last_seen: "8s ago",
      last_rssi: -82,
      water_level_cm: 85.0,
      total_packets_routed: 219
    },
    {
      duck_id: "DUCKLINK-SENSOR-02",
      duck_type: "DuckLink",
      name: "DuckLink CST Bridge Culvert Sensor",
      lat: 19.068,
      lon: 72.884,
      battery_pct: 91,
      status: "HEALTHY",
      last_seen: "15s ago",
      last_rssi: -71,
      water_level_cm: 42.0,
      total_packets_routed: 195
    },
    {
      duck_id: "DUCK-ISOLATED-07",
      duck_type: "DuckLink",
      name: "DuckLink Slum Cluster Emergency Beacon",
      lat: 19.074,
      lon: 72.886,
      battery_pct: 64,
      status: "HEALTHY",
      last_seen: "2s ago",
      last_rssi: -89,
      water_level_cm: 155.0,
      total_packets_routed: 42
    }
  ],
  links: [
    { source: "MAMADUCK-RELAY-01", target: "PAPADUCK-GW-01", rssi: -68, quality: "EXCELLENT" },
    { source: "MAMADUCK-RELAY-02", target: "PAPADUCK-GW-01", rssi: -74, quality: "GOOD" },
    { source: "DUCKLINK-SENSOR-01", target: "MAMADUCK-RELAY-01", rssi: -82, quality: "GOOD" },
    { source: "DUCKLINK-SENSOR-02", target: "MAMADUCK-RELAY-01", rssi: -71, quality: "EXCELLENT" },
    { source: "DUCK-ISOLATED-07", target: "MAMADUCK-RELAY-01", rssi: -89, quality: "MARGINAL" }
  ],
  total_active_nodes: 6,
  active_sos_alerts: 0,
  average_mesh_delivery_rate: 98.4,
  dead_zones_detected: ["Saki Naka East Gully (Blocked by high-rise ridge)"],
  gateway_status: "ONLINE_CELLULAR_FAILOVER"
};

export const MeshTopologyRadar: React.FC<MeshTopologyRadarProps> = ({ backendBase = "" }) => {
  const [topology, setTopology] = useState<MeshTopology>(DEFAULT_TOPOLOGY);
  const [selectedNode, setSelectedNode] = useState<DuckNode | null>(DEFAULT_TOPOLOGY.nodes[0]);
  const [loading, setLoading] = useState<boolean>(false);
  const [sosInProgress, setSosInProgress] = useState<boolean>(false);
  const [lastSosEvent, setLastSosEvent] = useState<any | null>(null);

  const fetchTopology = async () => {
    setLoading(true);
    const endpoints = [
      backendBase ? `${backendBase}/api/v1/mesh/topology` : null,
      "/api/v1/mesh/topology",
      "http://127.0.0.1:8000/api/v1/mesh/topology"
    ].filter(Boolean) as string[];

    for (const url of endpoints) {
      try {
        const resp = await fetch(url, { headers: { "Accept": "application/json" } });
        if (resp.ok) {
          const contentType = resp.headers.get("content-type");
          if (contentType && contentType.includes("application/json")) {
            const data: MeshTopology = await resp.json();
            if (data && data.nodes && data.nodes.length > 0) {
              setTopology(data);
              if (!selectedNode) {
                setSelectedNode(data.nodes[0]);
              }
              break;
            }
          }
        }
      } catch {
        // Silently continue
      }
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchTopology();
    const interval = setInterval(fetchTopology, 8000);
    return () => clearInterval(interval);
  }, [backendBase]);

  const triggerSosSimulation = async () => {
    setSosInProgress(true);

    // Optimistically update topology and UI immediately
    const updatedNodes = topology.nodes.map((n) => {
      if (n.duck_id === "DUCK-ISOLATED-07") {
        return {
          ...n,
          status: "SOS_ALERT" as const,
          water_level_cm: 155.0,
          total_packets_routed: n.total_packets_routed + 1
        };
      }
      if (n.duck_type === "PapaDuck" || n.duck_type === "MamaDuck") {
        return {
          ...n,
          total_packets_routed: n.total_packets_routed + 1
        };
      }
      return n;
    });

    const sosInfo = {
      event_id: `SOS-LORA-${Date.now()}`,
      origin: "DUCK-ISOLATED-07",
      location: "Kurla West Submerged Slum Cluster",
      water_level_cm: 155.0,
      civilians_trapped: 32,
      hops_traversed: 2,
      path: ["DUCK-ISOLATED-07", "MAMADUCK-RELAY-01", "PAPADUCK-GW-01"],
      status: "DISPATCHED_TO_NDRF",
      message: "CRITICAL OFF-GRID SOS: Kurla West Submerged Slum Cluster — 32 civilians trapped, water depth 155cm. Multi-hop packet routed via MamaDuck-01 -> PapaDuck Gateway. Emergency boat rescue dispatched."
    };

    setTopology({
      ...topology,
      nodes: updatedNodes,
      active_sos_alerts: Math.max(1, topology.active_sos_alerts + 1)
    });
    setLastSosEvent(sosInfo);
    const targetNode = updatedNodes.find((n) => n.duck_id === "DUCK-ISOLATED-07");
    if (targetNode) setSelectedNode(targetNode);

    // Also attempt backend dispatch
    const endpoints = [
      backendBase ? `${backendBase}/api/v1/mesh/simulate-sos` : null,
      "/api/v1/mesh/simulate-sos",
      "http://127.0.0.1:8000/api/v1/mesh/simulate-sos"
    ].filter(Boolean) as string[];

    for (const url of endpoints) {
      try {
        const resp = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json", "Accept": "application/json" },
          body: JSON.stringify({
            origin_duck_id: "DUCK-ISOLATED-07",
            location_name: "Kurla West Submerged Slum Cluster",
            lat: 19.071,
            lon: 72.882,
            water_level_cm: 155.0,
            civilians_trapped: 32,
            urgency: "IMMEDIATE_AIRLIFT_RESCUE"
          })
        });
        if (resp.ok) {
          const contentType = resp.headers.get("content-type");
          if (contentType && contentType.includes("application/json")) {
            const result = await resp.json();
            setLastSosEvent(result);
            break;
          }
        }
      } catch {
        // Fallback already applied
      }
    }
    setSosInProgress(false);
  };

  const getNodeColor = (status: string, type: string) => {
    if (status === "SOS_ALERT") return "#ef4444";
    if (type === "PapaDuck") return "#3b82f6";
    if (type === "MamaDuck") return "#10b981";
    return "#f59e0b";
  };

  return (
    <div className="glass-card" style={{ padding: "20px", marginBottom: "20px", border: "1px solid rgba(239, 68, 68, 0.3)" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span className="badge" style={{ background: "rgba(239, 68, 68, 0.15)", color: "#f87171", border: "1px solid rgba(239, 68, 68, 0.3)" }}>
              CLUSTERDUCK PROTOCOL
            </span>
            <h3 style={{ fontSize: "1.1rem", color: "#FFF", margin: 0, display: "flex", alignItems: "center", gap: "6px" }}>
              <Radio size={18} style={{ color: "#f87171" }} />
              LoRa Ad-Hoc Emergency Mesh Radar & Gateway
            </h3>
          </div>
          <p style={{ fontSize: "0.78rem", color: "var(--color-text-muted)", margin: "4px 0 0 0" }}>
            Off-grid telemetry mesh network with loop prevention (H ≤ 6), deduplication, and direct rescue dispatch.
          </p>
        </div>

        <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
          <button
            onClick={triggerSosSimulation}
            disabled={sosInProgress}
            className="btn"
            style={{
              background: "linear-gradient(135deg, #ef4444, #b91c1c)",
              color: "#FFF",
              fontWeight: 700,
              fontSize: "0.75rem",
              padding: "6px 12px",
              boxShadow: "0 0 14px rgba(239, 68, 68, 0.5)",
              display: "flex",
              alignItems: "center",
              gap: "6px",
              border: "none",
              cursor: "pointer"
            }}
          >
            <Zap size={14} className={sosInProgress ? "spin" : ""} />
            {sosInProgress ? "DISPATCHING SOS..." : "BROADCAST OFF-GRID SOS"}
          </button>

          <button
            onClick={fetchTopology}
            disabled={loading}
            className="btn btn-secondary"
            style={{ padding: "6px 10px", fontSize: "0.75rem", display: "flex", alignItems: "center", gap: "4px" }}
          >
            <RefreshCw size={12} className={loading ? "spin" : ""} />
          </button>
        </div>
      </div>

      {/* SOS Alert Banner */}
      {topology && topology.active_sos_alerts > 0 && (
        <div
          style={{
            background: "rgba(239, 68, 68, 0.15)",
            border: "1px solid #ef4444",
            padding: "10px 14px",
            borderRadius: "8px",
            marginBottom: "14px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between"
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div style={{ width: "12px", height: "12px", borderRadius: "50%", background: "#ef4444", boxShadow: "0 0 8px #ef4444", animation: "pulse 1s infinite" }} />
            <div>
              <span style={{ fontWeight: 800, color: "#f87171", fontSize: "0.85rem", letterSpacing: "0.03em" }}>
                CRITICAL OFF-GRID SOS BROADCAST RECEIVED
              </span>
              <div style={{ fontSize: "0.75rem", color: "#fca5a5" }}>
                {lastSosEvent?.message || "Active emergency evacuation beacon detected over multi-hop LoRa mesh. Cellular grid offline."}
              </div>
            </div>
          </div>
          <span className="badge" style={{ background: "#ef4444", color: "#FFF", fontWeight: 800 }}>
            {topology.active_sos_alerts} RESCUE BEACON ACTIVE
          </span>
        </div>
      )}

      {/* Radar Map & Node Inspector Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: "16px" }}>
        {/* SVG Mesh Topology Visualizer */}
        <div
          style={{
            position: "relative",
            height: "300px",
            background: "radial-gradient(circle at center, #111d33 0%, #060b14 100%)",
            borderRadius: "10px",
            border: "1px solid rgba(255, 255, 255, 0.1)",
            overflow: "hidden"
          }}
        >
          {/* Radar Circles */}
          <svg style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", pointerEvents: "none" }}>
            <circle cx="50%" cy="50%" r="40" stroke="rgba(255,255,255,0.06)" fill="none" />
            <circle cx="50%" cy="50%" r="80" stroke="rgba(255,255,255,0.06)" fill="none" />
            <circle cx="50%" cy="50%" r="120" stroke="rgba(255,255,255,0.06)" fill="none" />
            <line x1="0" y1="50%" x2="100%" y2="50%" stroke="rgba(255,255,255,0.05)" />
            <line x1="50%" y1="0" x2="50%" y2="100%" stroke="rgba(255,255,255,0.05)" />

            {/* Links */}
            {topology?.links.map((link, idx) => {
              const srcNode = topology.nodes.find((n) => n.duck_id === link.source);
              const dstNode = topology.nodes.find((n) => n.duck_id === link.target);
              if (!srcNode || !dstNode) return null;

              // Normalized coordinates to canvas
              const srcX = `${25 + ((idx * 37) % 50)}%`;
              const srcY = `${30 + ((idx * 23) % 40)}%`;
              const dstX = "50%";
              const dstY = "50%";

              return (
                <line
                  key={idx}
                  x1={srcX}
                  y1={srcY}
                  x2={dstX}
                  y2={dstY}
                  stroke={link.quality === "EXCELLENT" ? "#10b981" : link.quality === "GOOD" ? "#f59e0b" : "#ef4444"}
                  strokeWidth="2"
                  strokeDasharray="4 2"
                  opacity="0.6"
                />
              );
            })}
          </svg>

          {/* Node Points on Radar */}
          <div style={{ position: "relative", width: "100%", height: "100%" }}>
            {topology?.nodes.map((node, i) => {
              const isSelected = selectedNode?.duck_id === node.duck_id;
              // Deterministic layout distribution
              const leftPct = node.duck_type === "PapaDuck" ? 50 : 20 + ((i * 31) % 60);
              const topPct = node.duck_type === "PapaDuck" ? 50 : 25 + ((i * 29) % 55);

              return (
                <div
                  key={node.duck_id}
                  onClick={() => setSelectedNode(node)}
                  style={{
                    position: "absolute",
                    left: `${leftPct}%`,
                    top: `${topPct}%`,
                    transform: "translate(-50%, -50%)",
                    cursor: "pointer",
                    textAlign: "center",
                    zIndex: isSelected ? 20 : 10
                  }}
                >
                  <div
                    style={{
                      width: node.duck_type === "PapaDuck" ? "22px" : "16px",
                      height: node.duck_type === "PapaDuck" ? "22px" : "16px",
                      borderRadius: node.duck_type === "MamaDuck" ? "4px" : "50%",
                      background: getNodeColor(node.status, node.duck_type),
                      border: isSelected ? "3px solid #FFF" : "2px solid rgba(255,255,255,0.4)",
                      boxShadow: `0 0 ${node.status === "SOS_ALERT" ? "16px #ef4444" : "8px rgba(0,0,0,0.6)"}`,
                      margin: "0 auto",
                      transition: "transform 0.2s ease"
                    }}
                  />
                  <div
                    className="mono"
                    style={{
                      fontSize: "0.62rem",
                      color: isSelected ? "#FFF" : "rgba(255,255,255,0.7)",
                      background: "rgba(0,0,0,0.75)",
                      padding: "1px 4px",
                      borderRadius: "3px",
                      marginTop: "3px",
                      whiteSpace: "nowrap"
                    }}
                  >
                    {node.duck_id}
                  </div>
                </div>
              );
            })}
          </div>

          <div style={{ position: "absolute", bottom: "8px", left: "10px", fontSize: "0.68rem", color: "#64748b" }}>
            ● PapaDuck Gateway (Center) • ▲ MamaDuck Relay • ● DuckLink Sensor
          </div>
        </div>

        {/* Selected Node Details Drawer */}
        <div style={{ background: "rgba(255, 255, 255, 0.03)", padding: "14px", borderRadius: "8px", border: "1px solid rgba(255,255,255,0.08)" }}>
          <div style={{ fontSize: "0.72rem", color: "var(--color-text-muted)", marginBottom: "4px" }}>TELEMETRY NODE INSPECTOR</div>
          {selectedNode ? (
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                <span className="mono" style={{ fontSize: "1rem", fontWeight: 800, color: "#FFF" }}>
                  {selectedNode.duck_id}
                </span>
                <span
                  className="badge"
                  style={{
                    background: selectedNode.status === "SOS_ALERT" ? "rgba(239, 68, 68, 0.2)" : "rgba(16, 185, 129, 0.2)",
                    color: selectedNode.status === "SOS_ALERT" ? "#f87171" : "#34d399",
                    border: `1px solid ${selectedNode.status === "SOS_ALERT" ? "#ef4444" : "#10b981"}`
                  }}
                >
                  {selectedNode.status}
                </span>
              </div>

              <div style={{ fontSize: "0.8rem", color: "#cbd5e1", marginBottom: "10px" }}>{selectedNode.name}</div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", fontSize: "0.72rem" }}>
                <div style={{ background: "rgba(0,0,0,0.3)", padding: "6px 8px", borderRadius: "6px" }}>
                  <div style={{ color: "var(--color-text-muted)" }}>Node Role</div>
                  <div className="mono" style={{ fontWeight: 700, color: "#FFF" }}>{selectedNode.duck_type}</div>
                </div>

                <div style={{ background: "rgba(0,0,0,0.3)", padding: "6px 8px", borderRadius: "6px" }}>
                  <div style={{ color: "var(--color-text-muted)" }}>Signal (RSSI)</div>
                  <div className="mono" style={{ fontWeight: 700, color: selectedNode.last_rssi > -80 ? "#34d399" : "#fbbf24" }}>
                    {selectedNode.last_rssi} dBm
                  </div>
                </div>

                <div style={{ background: "rgba(0,0,0,0.3)", padding: "6px 8px", borderRadius: "6px" }}>
                  <div style={{ color: "var(--color-text-muted)" }}>Battery Level</div>
                  <div className="mono" style={{ fontWeight: 700, color: selectedNode.battery_pct > 30 ? "#34d399" : "#f87171" }}>
                    {selectedNode.battery_pct.toFixed(1)}%
                  </div>
                </div>

                <div style={{ background: "rgba(0,0,0,0.3)", padding: "6px 8px", borderRadius: "6px" }}>
                  <div style={{ color: "var(--color-text-muted)" }}>Water Level</div>
                  <div className="mono" style={{ fontWeight: 700, color: (selectedNode.water_level_cm || 0) > 100 ? "#f87171" : "#60a5fa" }}>
                    {selectedNode.water_level_cm || 0} cm
                  </div>
                </div>
              </div>

              <div style={{ marginTop: "10px", paddingTop: "8px", borderTop: "1px solid rgba(255,255,255,0.06)", fontSize: "0.68rem", color: "var(--color-text-muted)" }}>
                Total Packets Routed: <b style={{ color: "#FFF" }}>{selectedNode.total_packets_routed}</b> • Max Hops: <b style={{ color: "#FFF" }}>6</b>
              </div>
            </div>
          ) : (
            <div style={{ color: "var(--color-text-muted)", fontSize: "0.78rem" }}>Click any radar node to inspect diagnostics.</div>
          )}
        </div>
      </div>

      {/* Dead Zones & Delivery Summary Footer */}
      {topology && (
        <div style={{ marginTop: "14px", display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "0.72rem", color: "var(--color-text-muted)", borderTop: "1px solid rgba(255,255,255,0.06)", paddingTop: "10px" }}>
          <div>
            Mesh Backhaul Delivery Rate: <b style={{ color: "#34d399" }}>{topology.average_mesh_delivery_rate}%</b> • Gateway: <b style={{ color: "#60a5fa" }}>{topology.gateway_status}</b>
          </div>
          <div style={{ color: "#fca5a5" }}>
            Dead-Zone Alerts: {topology.dead_zones_detected[0]}
          </div>
        </div>
      )}
    </div>
  );
};
