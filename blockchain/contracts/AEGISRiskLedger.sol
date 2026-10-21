// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title AEGISRiskLedger
 * @notice Immutable on-chain ledger for AEGIS-CLIMATE multi-agent risk assessments.
 * @dev Deployed on Polygon Amoy Testnet for IEEE ClimateChain Hackathon 2026.
 *      Anchors Agent 1, Agent 2, and Agent 3 outputs with their IPFS CIDs.
 */
contract AEGISRiskLedger is Ownable {

    // ─── STRUCTS ────────────────────────────────────────────────────────────

    struct RiskAssessment {
        bytes32  assessmentId;      // keccak256(lat_scaled, lon_scaled, timestamp_bucket)
        int256   latScaled;         // latitude × 1e6 (e.g. 19.0728 -> 19072800)
        int256   lonScaled;         // longitude × 1e6 (e.g. 72.8797 -> 72879700)
        uint256  riskScoreBps;      // risk score in basis points (0–10000)
        uint8    riskTier;          // 0=LOW, 1=MEDIUM, 2=HIGH, 3=CRITICAL
        bytes32  ipfsCid;           // First 32 bytes of IPFS CID
        string   ipfsCidFull;       // Full IPFS CIDv1 string
        uint256  timestamp;         // Block timestamp of anchoring
        address  anchoredBy;        // AEGIS backend wallet address
        bool     demTriggered;      // Did Agent 2 cascade trigger?
        bool     varTriggered;      // Did Agent 3 cascade trigger?
        uint256  demDepthCm;        // Agent 2: waterlogging depth in cm
        uint256  varInrLakhs;       // Agent 3: VaR in Indian Rupees (lakhs)
        string   locationName;      // Human-readable location name
    }

    // ─── STATE VARIABLES ────────────────────────────────────────────────────

    mapping(bytes32 => RiskAssessment) public assessments;
    mapping(bytes32 => bool) public assessmentExists;
    bytes32[] public assessmentIds;

    mapping(int256 => mapping(int256 => bytes32[])) public locationHistory;

    uint256 public constant PRECISION = 1e6;
    uint256 public constant CRITICAL_THRESHOLD_BPS = 6500;  // 0.65
    uint256 public constant HIGH_THRESHOLD_BPS = 4000;      // 0.40
    uint256 public constant MEDIUM_THRESHOLD_BPS = 2000;    // 0.20

    uint256 public totalAssessments;
    uint256 public criticalAlerts;
    address public aegisBackend;

    // ─── EVENTS ─────────────────────────────────────────────────────────────

    event RiskAssessmentAnchored(
        bytes32 indexed assessmentId,
        int256 indexed latScaled,
        int256 indexed lonScaled,
        uint256 riskScoreBps,
        uint8 riskTier,
        string ipfsCidFull,
        uint256 timestamp,
        string locationName
    );

    event DEMCascadeAnchored(
        bytes32 indexed assessmentId,
        uint256 demDepthCm,
        uint256 exposedStructures,
        string ipfsCidFull
    );

    event VaRCascadeAnchored(
        bytes32 indexed assessmentId,
        uint256 varInrLakhs,
        uint256 varUsdCents,
        uint256 carbonPenaltyInrLakhs,
        string ipfsCidFull
    );

    event CriticalAlertEmitted(
        bytes32 indexed assessmentId,
        string locationName,
        uint256 riskScoreBps,
        uint256 timestamp
    );

    event BackendUpdated(address indexed oldBackend, address indexed newBackend);

    // ─── MODIFIERS ───────────────────────────────────────────────────────────

    modifier onlyBackend() {
        require(
            msg.sender == aegisBackend || msg.sender == owner(),
            "AEGISRiskLedger: caller is not authorized"
        );
        _;
    }

    modifier assessmentMustExist(bytes32 assessmentId) {
        require(assessmentExists[assessmentId], "AEGISRiskLedger: assessment not found");
        _;
    }

    // ─── CONSTRUCTOR ────────────────────────────────────────────────────────

    constructor(address _aegisBackend) Ownable(msg.sender) {
        require(_aegisBackend != address(0), "AEGISRiskLedger: zero address");
        aegisBackend = _aegisBackend;
        emit BackendUpdated(address(0), _aegisBackend);
    }

    // ─── CORE FUNCTIONS ──────────────────────────────────────────────────────

    function anchorRiskAssessment(
        int256 latScaled,
        int256 lonScaled,
        uint256 riskScoreBps,
        string calldata ipfsCidFull,
        string calldata locationName
    ) external onlyBackend returns (bytes32 assessmentId) {
        require(riskScoreBps <= 10000, "AEGISRiskLedger: score exceeds max BPS");
        require(bytes(ipfsCidFull).length > 0, "AEGISRiskLedger: empty IPFS CID");

        uint256 timeBucket = (block.timestamp / 900) * 900;
        assessmentId = keccak256(abi.encodePacked(latScaled, lonScaled, timeBucket));

        if (assessmentExists[assessmentId]) {
            return assessmentId;
        }

        uint8 tier = _computeRiskTier(riskScoreBps);
        bytes32 cidBytes = _cidToBytes32(ipfsCidFull);

        RiskAssessment storage assessment = assessments[assessmentId];
        assessment.assessmentId = assessmentId;
        assessment.latScaled = latScaled;
        assessment.lonScaled = lonScaled;
        assessment.riskScoreBps = riskScoreBps;
        assessment.riskTier = tier;
        assessment.ipfsCid = cidBytes;
        assessment.ipfsCidFull = ipfsCidFull;
        assessment.timestamp = block.timestamp;
        assessment.anchoredBy = msg.sender;
        assessment.locationName = locationName;

        assessmentExists[assessmentId] = true;
        assessmentIds.push(assessmentId);
        locationHistory[latScaled][lonScaled].push(assessmentId);
        totalAssessments++;

        if (tier == 3) {
            criticalAlerts++;
            emit CriticalAlertEmitted(assessmentId, locationName, riskScoreBps, block.timestamp);
        }

        emit RiskAssessmentAnchored(
            assessmentId, latScaled, lonScaled, riskScoreBps, tier,
            ipfsCidFull, block.timestamp, locationName
        );

        return assessmentId;
    }

    function anchorDEMCascade(
        bytes32 assessmentId,
        uint256 demDepthCm,
        uint256 exposedStructures,
        uint256 drainageChokePct,
        string calldata ipfsCidFull
    ) external onlyBackend assessmentMustExist(assessmentId) {
        RiskAssessment storage assessment = assessments[assessmentId];
        require(
            assessment.riskScoreBps >= CRITICAL_THRESHOLD_BPS,
            "DEM cascade requires CRITICAL"
        );
        require(!assessment.demTriggered, "AEGISRiskLedger: DEM already anchored");

        assessment.demTriggered = true;
        assessment.demDepthCm = demDepthCm;

        emit DEMCascadeAnchored(assessmentId, demDepthCm, exposedStructures, ipfsCidFull);
    }

    function anchorVaRCascade(
        bytes32 assessmentId,
        uint256 varInrLakhs,
        uint256 varUsdCents,
        uint256 carbonPenaltyInrLakhs,
        uint256 strandedAssetRiskBps,
        string calldata ipfsCidFull
    ) external onlyBackend assessmentMustExist(assessmentId) {
        RiskAssessment storage assessment = assessments[assessmentId];
        require(assessment.demTriggered, "AEGISRiskLedger: DEM cascade must precede VaR");
        require(!assessment.varTriggered, "AEGISRiskLedger: VaR already anchored");

        assessment.varTriggered = true;
        assessment.varInrLakhs = varInrLakhs;

        emit VaRCascadeAnchored(assessmentId, varInrLakhs, varUsdCents, carbonPenaltyInrLakhs, ipfsCidFull);
    }

    // ─── VIEW FUNCTIONS ──────────────────────────────────────────────────────

    function getAssessment(bytes32 assessmentId)
        external view returns (RiskAssessment memory)
    {
        return assessments[assessmentId];
    }

    function getLocationHistory(int256 latScaled, int256 lonScaled)
        external view returns (bytes32[] memory)
    {
        return locationHistory[latScaled][lonScaled];
    }

    function getRecentAssessments(uint256 count)
        external view returns (bytes32[] memory ids)
    {
        uint256 total = assessmentIds.length;
        uint256 n = count > total ? total : count;
        ids = new bytes32[](n);
        for (uint256 i = 0; i < n; i++) {
            ids[i] = assessmentIds[total - 1 - i];
        }
    }

    function getStats() external view returns (
        uint256 _totalAssessments,
        uint256 _criticalAlerts
    ) {
        return (totalAssessments, criticalAlerts);
    }

    // ─── ADMIN FUNCTIONS ─────────────────────────────────────────────────────

    function setBackend(address newBackend) external onlyOwner {
        require(newBackend != address(0), "AEGISRiskLedger: zero address");
        emit BackendUpdated(aegisBackend, newBackend);
        aegisBackend = newBackend;
    }

    // ─── INTERNAL HELPERS ────────────────────────────────────────────────────

    function _computeRiskTier(uint256 scoreBps) internal pure returns (uint8) {
        if (scoreBps >= CRITICAL_THRESHOLD_BPS) return 3;  // CRITICAL
        if (scoreBps >= HIGH_THRESHOLD_BPS)     return 2;  // HIGH
        if (scoreBps >= MEDIUM_THRESHOLD_BPS)   return 1;  // MEDIUM
        return 0;                                           // LOW
    }

    function _cidToBytes32(string memory cid) internal pure returns (bytes32) {
        bytes memory cidBytes = bytes(cid);
        if (cidBytes.length == 0) return bytes32(0);
        bytes32 result;
        assembly {
            result := mload(add(cidBytes, 32))
        }
        return result;
    }
}
