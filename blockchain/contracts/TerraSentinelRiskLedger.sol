// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title TerraSentinelRiskLedger
 * @notice Immutable on-chain ledger for TERRA-SENTINEL multi-agent risk assessments.
 * @dev Deployed on Polygon Amoy Testnet for IEEE ClimateChain Hackathon 2026.
 *      Anchors Agent 1, Agent 2, and Agent 3 outputs with their IPFS CIDs.
 */
contract TerraSentinelRiskLedger is Ownable {

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
        address  anchoredBy;        // TERRA-SENTINEL backend wallet address
        bool     demTriggered;      // Did Agent 2 cascade trigger?
        bool     varTriggered;      // Did Agent 3 cascade trigger?
        uint256  demDepthCm;        // Agent 2: waterlogging depth in cm
        uint256  varInrLakhs;       // Agent 3: VaR in Indian Rupees (lakhs)
        string   locationName;      // Human-readable location name
    }

    struct RiskCommitment {
        bytes32 onchainHash;         // keccak256(abi.encode(hotspot, varScaled, ipfsCid))
        bytes32 onchainHashPacked;   // keccak256(abi.encodePacked(hotspot, varScaled, ipfsCid))
        string  hotspot;             // Hotspot corridor identifier
        uint256 varScaled;           // VaR scaled by 1e4 (e.g. 250.00 -> 2500000)
        string  ipfsCid;             // IPFS CIDv1
        uint256 timestamp;           // Block timestamp
        address anchoredBy;          // Backend authorized wallet
        bool    verified;            // Data integrity confirmation flag
    }

    // ─── STATE VARIABLES ────────────────────────────────────────────────────

    mapping(bytes32 => RiskAssessment) public assessments;
    mapping(bytes32 => bool) public assessmentExists;
    bytes32[] public assessmentIds;

    mapping(bytes32 => RiskCommitment) public commitments;
    mapping(string => bytes32) public latestCommitmentByHotspot;
    bytes32[] public commitmentHashes;

    mapping(int256 => mapping(int256 => bytes32[])) public locationHistory;

    uint256 public constant PRECISION = 1e6;
    uint256 public constant VAR_PRECISION_SCALE = 1e4;      // 4 decimal places (basis points precision for VaR)
    uint256 public constant CRITICAL_THRESHOLD_BPS = 6500;  // 0.65
    uint256 public constant HIGH_THRESHOLD_BPS = 4000;      // 0.40
    uint256 public constant MEDIUM_THRESHOLD_BPS = 2000;    // 0.20

    uint256 public totalAssessments;
    uint256 public criticalAlerts;
    address public terraSentinelBackend;

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

    event RiskCommitmentAnchored(
        bytes32 indexed onchainHash,
        bytes32 indexed onchainHashPacked,
        string hotspot,
        uint256 varScaled,
        string ipfsCid,
        address indexed anchoredBy,
        uint256 timestamp
    );

    // ─── MODIFIERS ───────────────────────────────────────────────────────────

    modifier onlyBackend() {
        require(
            msg.sender == terraSentinelBackend || msg.sender == owner(),
            "TerraSentinelRiskLedger: caller is not authorized"
        );
        _;
    }

    modifier assessmentMustExist(bytes32 assessmentId) {
        require(assessmentExists[assessmentId], "TerraSentinelRiskLedger: assessment not found");
        _;
    }

    // ─── CONSTRUCTOR ────────────────────────────────────────────────────────

    constructor(address _terraSentinelBackend) Ownable(msg.sender) {
        require(_terraSentinelBackend != address(0), "TerraSentinelRiskLedger: zero address");
        terraSentinelBackend = _terraSentinelBackend;
        emit BackendUpdated(address(0), _terraSentinelBackend);
    }

    // ─── CORE FUNCTIONS ──────────────────────────────────────────────────────

    function anchorRiskAssessment(
        int256 latScaled,
        int256 lonScaled,
        uint256 riskScoreBps,
        string calldata ipfsCidFull,
        string calldata locationName
    ) external onlyBackend returns (bytes32 assessmentId) {
        require(riskScoreBps <= 10000, "TerraSentinelRiskLedger: score exceeds max BPS");
        require(bytes(ipfsCidFull).length > 0, "TerraSentinelRiskLedger: empty IPFS CID");

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
        require(!assessment.demTriggered, "TerraSentinelRiskLedger: DEM already anchored");

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
        require(assessment.demTriggered, "TerraSentinelRiskLedger: DEM cascade must precede VaR");
        require(!assessment.varTriggered, "TerraSentinelRiskLedger: VaR already anchored");

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

    // ─── MATHEMATICAL COMMITMENT FUNCTIONS ──────────────────────────────────

    /**
     * @notice Computes deterministic on-chain hash using canonical ABI encoding.
     * @dev Hash_onchain = keccak256(abi.encode(hotspot, varScaled, ipfsCid))
     */
    function computeOnchainHash(
        string calldata hotspot,
        uint256 varScaled,
        string calldata ipfsCid
    ) public pure returns (bytes32) {
        return keccak256(abi.encode(hotspot, varScaled, ipfsCid));
    }

    /**
     * @notice Computes deterministic on-chain hash using Solidity packed encoding.
     * @dev Hash_onchain = keccak256(abi.encodePacked(hotspot, varScaled, ipfsCid))
     */
    function computeOnchainHashPacked(
        string calldata hotspot,
        uint256 varScaled,
        string calldata ipfsCid
    ) public pure returns (bytes32) {
        return keccak256(abi.encodePacked(hotspot, varScaled, ipfsCid));
    }

    /**
     * @notice Anchors an immutable cryptographic risk commitment on-chain.
     */
    function anchorRiskCommitment(
        string calldata hotspot,
        uint256 varScaled,
        string calldata ipfsCid
    ) external onlyBackend returns (bytes32 onchainHash, bytes32 onchainHashPacked) {
        require(bytes(hotspot).length > 0, "TerraSentinelRiskLedger: empty hotspot");
        require(bytes(ipfsCid).length > 0, "TerraSentinelRiskLedger: empty IPFS CID");

        onchainHash = computeOnchainHash(hotspot, varScaled, ipfsCid);
        onchainHashPacked = computeOnchainHashPacked(hotspot, varScaled, ipfsCid);

        commitments[onchainHash] = RiskCommitment({
            onchainHash: onchainHash,
            onchainHashPacked: onchainHashPacked,
            hotspot: hotspot,
            varScaled: varScaled,
            ipfsCid: ipfsCid,
            timestamp: block.timestamp,
            anchoredBy: msg.sender,
            verified: true
        });

        latestCommitmentByHotspot[hotspot] = onchainHash;
        commitmentHashes.push(onchainHash);

        emit RiskCommitmentAnchored(
            onchainHash,
            onchainHashPacked,
            hotspot,
            varScaled,
            ipfsCid,
            msg.sender,
            block.timestamp
        );

        return (onchainHash, onchainHashPacked);
    }

    /**
     * @notice Verifies data integrity against an anchored on-chain cryptographic commitment.
     */
    function verifyRiskCommitment(
        bytes32 onchainHash,
        string calldata hotspot,
        uint256 varScaled,
        string calldata ipfsCid
    ) external view returns (bool isValid, bool existsOnchain, uint256 timestamp, address anchoredBy) {
        bytes32 computed = computeOnchainHash(hotspot, varScaled, ipfsCid);
        isValid = (computed == onchainHash);
        RiskCommitment memory comm = commitments[onchainHash];
        existsOnchain = comm.verified;
        timestamp = comm.timestamp;
        anchoredBy = comm.anchoredBy;
    }

    function getCommitment(bytes32 onchainHash) external view returns (RiskCommitment memory) {
        return commitments[onchainHash];
    }

    // ─── ADMIN FUNCTIONS ─────────────────────────────────────────────────────

    function setBackend(address newBackend) external onlyOwner {
        require(newBackend != address(0), "TerraSentinelRiskLedger: zero address");
        emit BackendUpdated(terraSentinelBackend, newBackend);
        terraSentinelBackend = newBackend;
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
