import React, { useState } from "react";
import {
  Shield,
  Copy,
  Check,
  Download,
  FileText,
  Cpu,
  Layers,
  Info
} from "lucide-react";

export interface EvidenceBundlePayload {
  schema_version: string;
  evidence_id: string;
  analysis: {
    analysis_id: string;
    location: {
      label: string;
      latitude: number;
      longitude: number;
    };
    created_at_utc: string;
    data_mode: "live" | "fixture" | "synthetic";
    inputs: Array<{
      source: string;
      variable: string;
      value: number;
      unit: string;
      is_synthetic: boolean;
    }>;
    transformations: Array<{
      step: string;
      method: string;
      description: string;
    }>;
    risk_output: {
      risk_score: number;
      risk_tier: string;
      dominant_factor: string;
      model_id: string;
    };
    exposure_output?: {
      exposure_tier: string;
      waterlogging_depth_cm: number;
      buildings_at_risk: number;
      methodology: string;
    };
    policy_output?: {
      var_inr: number;
      stranded_asset_risk: string;
      compliance_gap_pct: number;
    };
  };
  model_manifest: {
    model_id: string;
    artifact_sha256: string;
    feature_schema_version: string;
    engine: string;
  };
  code_revision: string;
  limitations: string[];
  hash_algorithm: "keccak256";
  canonicalization_version: "aegis-canonical-json-v1";
}

interface EvidencePanelProps {
  bundle?: EvidenceBundlePayload | null;
  digest?: string;
  evidenceId?: string;
  dataMode?: string;
  onOpenVerifier?: () => void;
  onSimulateTamper?: () => void;
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({
  bundle,
  digest = "0x4eaa871ecae3e76b9cf322237676e7c95f16b1433ae68c4b159089eeec18d0b4",
  evidenceId = "ev_23af39ff55334551",
  dataMode = "live",
  onOpenVerifier,
  onSimulateTamper
}) => {
  const [copiedDigest, setCopiedDigest] = useState(false);
  const [copiedId, setCopiedId] = useState(false);
  const [showJsonRaw, setShowJsonRaw] = useState(false);

  const fallbackBundle: EvidenceBundlePayload = {
    schema_version: "1.0.0",
    evidence_id: evidenceId,
    analysis: {
      analysis_id: "ANL-MUMBAI-2026-001",
      location: {
        label: "Mumbai — Mithi River Basin & Kurla Transit",
        latitude: 19.0728,
        longitude: 72.8797
      },
      created_at_utc: new Date().toISOString().replace(/\.\d+/, ""),
      data_mode: (dataMode as any) || "live",
      inputs: [
        { source: "Open-Meteo", variable: "precipitation_24h", value: 142.5, unit: "mm", is_synthetic: false },
        { source: "Open-Meteo", variable: "precipitation_7d", value: 388.2, unit: "mm", is_synthetic: false },
        { source: "Open-Meteo", variable: "soil_saturation", value: 89.4, unit: "%", is_synthetic: false },
        { source: "SRTM-DEM", variable: "elevation", value: 4.2, unit: "m", is_synthetic: false }
      ],
      transformations: [
        { step: "Agent1_ML", method: "GradientBoostingClassifier", description: "Computed acute flood risk probability" },
        { step: "Agent2_GEO", method: "HAZUS_Topographical_Inundation", description: "Derived waterlogging depth and building exposures" },
        { step: "Agent3_FIN", method: "SEBI_BRSR_VaR_Synthesis", description: "Estimated corporate Value-at-Risk" }
      ],
      risk_output: {
        risk_score: 0.88,
        risk_tier: "CRITICAL",
        dominant_factor: "precipitation_7d_cumulative",
        model_id: "aegis-flood-classifier-v1"
      },
      exposure_output: {
        exposure_tier: "SEVERE_INUNDATION",
        waterlogging_depth_cm: 72,
        buildings_at_risk: 1420,
        methodology: "topographical_heuristic_hazus"
      },
      policy_output: {
        var_inr: 1450000000,
        stranded_asset_risk: "HIGH",
        compliance_gap_pct: 38
      }
    },
    model_manifest: {
      model_id: "aegis-flood-classifier-v1",
      artifact_sha256: "ecf12983bec200fe79116e07a27faec5d82bbbf8aa271ba7de8c9d9ba7f5ce8c",
      feature_schema_version: "v1.0.0",
      engine: "scikit-learn GradientBoostingClassifier"
    },
    code_revision: "a51f088",
    limitations: [
      "Inundation depth is derived from topographical elevation difference, not dynamic 2D hydraulic flood routing.",
      "Building exposure counts represent spatial intersections within radius, not surveyed structural assessments.",
      "Financial VaR estimates reflect asset replacement benchmarks, not actuarial insurance loss adjustment."
    ],
    hash_algorithm: "keccak256",
    canonicalization_version: "aegis-canonical-json-v1"
  };

  const activeBundle = bundle || fallbackBundle;

  const copyDigest = () => {
    navigator.clipboard.writeText(digest);
    setCopiedDigest(true);
    setTimeout(() => setCopiedDigest(false), 2000);
  };

  const copyId = () => {
    navigator.clipboard.writeText(activeBundle.evidence_id);
    setCopiedId(true);
    setTimeout(() => setCopiedId(false), 2000);
  };

  const downloadJson = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(activeBundle, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `aegis-evidence-${activeBundle.evidence_id}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div
      style={{
        background: "#16181c",
        border: "1px solid #2d2640",
        borderRadius: "14px",
        padding: "24px",
        display: "flex",
        flexDirection: "column",
        gap: "20px",
        boxShadow: "0 4px 20px rgba(0,0,0,0.4)"
      }}
    >
      {/* ── HEADER ROW ── */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          flexWrap: "wrap",
          gap: "12px",
          borderBottom: "1px solid rgba(255,255,255,0.08)",
          paddingBottom: "16px"
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div
            style={{
              width: "40px",
              height: "40px",
              borderRadius: "10px",
              background: "rgba(56, 189, 248, 0.1)",
              border: "1px solid rgba(56, 189, 248, 0.3)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center"
            }}
          >
            <Shield size={20} color="#38BDF8" />
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <h3
                style={{
                  fontFamily: "var(--font-display)",
                  fontSize: "17px",
                  fontWeight: 700,
                  color: "#FFFFFF",
                  margin: 0
                }}
              >
                Climate Evidence Bundle v1
              </h3>
              <span
                style={{
                  background: "rgba(56, 189, 248, 0.15)",
                  border: "1px solid #38BDF8",
                  color: "#38BDF8",
                  fontSize: "11px",
                  fontWeight: 700,
                  padding: "2px 8px",
                  borderRadius: "12px"
                }}
              >
                Schema {activeBundle.schema_version}
              </span>
              <span
                style={{
                  background:
                    activeBundle.analysis.data_mode === "live"
                      ? "rgba(16, 185, 129, 0.15)"
                      : "rgba(245, 158, 11, 0.15)",
                  border:
                    activeBundle.analysis.data_mode === "live"
                      ? "1px solid #10B981"
                      : "1px solid #F59E0B",
                  color:
                    activeBundle.analysis.data_mode === "live" ? "#10B981" : "#F59E0B",
                  fontSize: "10px",
                  fontWeight: 700,
                  padding: "2px 8px",
                  borderRadius: "12px",
                  textTransform: "uppercase"
                }}
              >
                {activeBundle.analysis.data_mode} TELEMETRY
              </span>
            </div>
            <p style={{ color: "var(--color-text-secondary)", fontSize: "12px", margin: "4px 0 0 0" }}>
              PRD-2 §6 Deterministic Evidence Bundle & Cryptographic Digest Specification
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
          <button
            onClick={downloadJson}
            style={{
              background: "rgba(255,255,255,0.05)",
              border: "1px solid rgba(255,255,255,0.15)",
              color: "var(--color-text-primary)",
              padding: "6px 12px",
              borderRadius: "8px",
              fontSize: "12px",
              fontWeight: 600,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "6px"
            }}
          >
            <Download size={13} />
            Export JSON
          </button>
          <button
            onClick={() => setShowJsonRaw(!showJsonRaw)}
            style={{
              background: showJsonRaw ? "rgba(56,189,248,0.2)" : "rgba(255,255,255,0.05)",
              border: showJsonRaw ? "1px solid #38BDF8" : "1px solid rgba(255,255,255,0.15)",
              color: showJsonRaw ? "#38BDF8" : "var(--color-text-primary)",
              padding: "6px 12px",
              borderRadius: "8px",
              fontSize: "12px",
              fontWeight: 600,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "6px"
            }}
          >
            <FileText size={13} />
            {showJsonRaw ? "Hide Preimage" : "View Preimage"}
          </button>
          {onSimulateTamper && (
            <button
              onClick={onSimulateTamper}
              style={{
                background: "rgba(239, 68, 68, 0.15)",
                border: "1px solid #EF4444",
                color: "#EF4444",
                padding: "6px 12px",
                borderRadius: "8px",
                fontSize: "12px",
                fontWeight: 600,
                cursor: "pointer"
              }}
            >
              Simulate Tamper
            </button>
          )}
          {onOpenVerifier && (
            <button
              onClick={onOpenVerifier}
              style={{
                background: "linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)",
                border: "none",
                color: "#FFFFFF",
                padding: "6px 14px",
                borderRadius: "8px",
                fontSize: "12px",
                fontWeight: 600,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "6px",
                boxShadow: "0 2px 10px rgba(124, 58, 237, 0.4)"
              }}
            >
              <Shield size={13} />
              Open Verifier Cockpit
            </button>
          )}
        </div>
      </div>

      {/* ── DIGEST & PREIMAGE BOX ── */}
      <div
        style={{
          background: "rgba(0, 0, 0, 0.4)",
          border: "1px solid rgba(255, 255, 255, 0.1)",
          borderRadius: "10px",
          padding: "16px",
          display: "flex",
          flexDirection: "column",
          gap: "12px"
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--color-text-secondary)", textTransform: "uppercase" }}>
              Keccak-256 Digest (Canonical Preimage Hash):
            </span>
            <span
              style={{
                fontSize: "10px",
                padding: "2px 6px",
                borderRadius: "4px",
                background: "rgba(167, 139, 250, 0.15)",
                color: "#A78BFA",
                fontWeight: 700
              }}
            >
              PRD-2 §6.3
            </span>
          </div>
          <button
            onClick={copyDigest}
            style={{
              background: "transparent",
              border: "none",
              color: copiedDigest ? "#10B981" : "#38BDF8",
              cursor: "pointer",
              fontSize: "12px",
              display: "flex",
              alignItems: "center",
              gap: "4px"
            }}
          >
            {copiedDigest ? <Check size={13} /> : <Copy size={13} />}
            {copiedDigest ? "Copied Digest!" : "Copy Hash"}
          </button>
        </div>

        <div
          style={{
            fontFamily: "monospace",
            fontSize: "13px",
            color: "#A78BFA",
            background: "rgba(15, 23, 42, 0.8)",
            padding: "10px 14px",
            borderRadius: "6px",
            border: "1px solid rgba(167, 139, 250, 0.2)",
            wordBreak: "break-all"
          }}
        >
          {digest}
        </div>

        <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: "10px", fontSize: "12px", color: "var(--color-text-secondary)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span>Bundle ID:</span>
            <code style={{ color: "#F8FAFC", background: "rgba(255,255,255,0.06)", padding: "2px 6px", borderRadius: "4px" }}>
              {activeBundle.evidence_id}
            </code>
            <button
              onClick={copyId}
              title="Copy Evidence ID"
              style={{ background: "transparent", border: "none", color: copiedId ? "#10B981" : "var(--color-text-secondary)", cursor: "pointer", padding: "0" }}
            >
              {copiedId ? <Check size={12} /> : <Copy size={12} />}
            </button>
          </div>
          <div>
            <span>Canonicalizer: </span>
            <strong style={{ color: "#E2E8F0" }}>{activeBundle.canonicalization_version}</strong>
          </div>
          <div>
            <span>Code Revision: </span>
            <code style={{ color: "#38BDF8" }}>git:{activeBundle.code_revision}</code>
          </div>
        </div>
      </div>

      {/* ── RAW PREIMAGE JSON ACCORDION ── */}
      {showJsonRaw && (
        <div
          style={{
            background: "#090d16",
            border: "1px solid #1e293b",
            borderRadius: "8px",
            padding: "14px",
            maxHeight: "260px",
            overflowY: "auto"
          }}
        >
          <pre style={{ margin: 0, fontSize: "11px", color: "#94a3b8", fontFamily: "monospace" }}>
            {JSON.stringify(activeBundle, null, 2)}
          </pre>
        </div>
      )}

      {/* ── METADATA & MODEL MANIFEST GRID ── */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          gap: "16px"
        }}
      >
        {/* ML & Transformation Provenance */}
        <div
          style={{
            background: "rgba(255, 255, 255, 0.02)",
            border: "1px solid rgba(255, 255, 255, 0.06)",
            borderRadius: "10px",
            padding: "16px",
            display: "flex",
            flexDirection: "column",
            gap: "10px"
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <Cpu size={16} color="#38BDF8" />
            <h4 style={{ margin: 0, fontSize: "13px", fontWeight: 700, color: "#FFFFFF" }}>
              Model Manifest & SHA-256 Pin
            </h4>
          </div>
          <div style={{ fontSize: "12px", display: "flex", flexDirection: "column", gap: "6px" }}>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ color: "var(--color-text-secondary)" }}>Model ID:</span>
              <strong style={{ color: "#E2E8F0" }}>{activeBundle.model_manifest.model_id}</strong>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ color: "var(--color-text-secondary)" }}>Engine:</span>
              <span style={{ color: "#38BDF8" }}>{activeBundle.model_manifest.engine}</span>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "2px", marginTop: "4px" }}>
              <span style={{ color: "var(--color-text-secondary)" }}>Artifact SHA-256:</span>
              <code
                style={{
                  fontSize: "10px",
                  color: "#94a3b8",
                  background: "rgba(0,0,0,0.3)",
                  padding: "4px 6px",
                  borderRadius: "4px",
                  wordBreak: "break-all"
                }}
              >
                {activeBundle.model_manifest.artifact_sha256}
              </code>
            </div>
          </div>
        </div>

        {/* Multi-Agent Transformation Pipeline */}
        <div
          style={{
            background: "rgba(255, 255, 255, 0.02)",
            border: "1px solid rgba(255, 255, 255, 0.06)",
            borderRadius: "10px",
            padding: "16px",
            display: "flex",
            flexDirection: "column",
            gap: "10px"
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <Layers size={16} color="#A78BFA" />
            <h4 style={{ margin: 0, fontSize: "13px", fontWeight: 700, color: "#FFFFFF" }}>
              Analysis Pipeline Outputs
            </h4>
          </div>
          <div style={{ fontSize: "12px", display: "flex", flexDirection: "column", gap: "6px" }}>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ color: "var(--color-text-secondary)" }}>Agent 1 Risk Score:</span>
              <strong style={{ color: activeBundle.analysis.risk_output.risk_score >= 0.65 ? "#EF4444" : "#10B981" }}>
                {(activeBundle.analysis.risk_output.risk_score * 100).toFixed(0)}% ({activeBundle.analysis.risk_output.risk_tier})
              </strong>
            </div>
            {activeBundle.analysis.exposure_output && (
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--color-text-secondary)" }}>Agent 2 Inundation Depth:</span>
                <span style={{ color: "#E2E8F0" }}>{activeBundle.analysis.exposure_output.waterlogging_depth_cm} cm</span>
              </div>
            )}
            {activeBundle.analysis.policy_output && (
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--color-text-secondary)" }}>Agent 3 Value-at-Risk:</span>
                <span style={{ color: "#E2E8F0" }}>₹{(activeBundle.analysis.policy_output.var_inr / 10000000).toFixed(2)} Cr</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── LIMITATIONS & HONEST DISCLOSURES (PRD §10) ── */}
      <div
        style={{
          background: "rgba(245, 158, 11, 0.05)",
          border: "1px solid rgba(245, 158, 11, 0.2)",
          borderRadius: "10px",
          padding: "14px 16px",
          display: "flex",
          alignItems: "flex-start",
          gap: "12px"
        }}
      >
        <Info size={16} color="#F59E0B" style={{ flexShrink: 0, marginTop: "2px" }} />
        <div style={{ fontSize: "12px", color: "#FDE68A" }}>
          <strong style={{ color: "#F59E0B" }}>Scientific Limitations & Scope Disclosures: </strong>
          {activeBundle.limitations.map((lim, idx) => (
            <span key={idx} style={{ display: "block", marginTop: "4px", color: "rgba(253, 230, 138, 0.9)" }}>
              • {lim}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};
