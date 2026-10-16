// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "./ClimateEvidenceRegistry.sol";
import "./IZKTelemetryVerifier.sol";

/**
 * @title AgenticSettlementPool
 * @notice Autonomous Stablecoin Emergency Relief Liquidity Pool.
 * @dev Direct implementation of Judge Revanth Reddy Airre's IEEE research on
 *      "Stablecoin Settlement Architectures for AI Agents".
 *
 *      Features:
 *      1. Programmatic USDC / ERC-20 micro-settlement tranches triggered by autonomous agents.
 *      2. Cryptographic verification against ClimateEvidenceRegistry anchored bundles.
 *      3. UNDP Double-Counting Prevention: strictly guarantees zero duplicate payouts per bundle.
 *      4. Pluggable Zero-Knowledge proof attestation interface (Groth16 telemetry bounds).
 */
contract AgenticSettlementPool is Ownable {

    // ─── STATE VARIABLES ────────────────────────────────────────────────────

    IERC20 public immutable stablecoin;
    ClimateEvidenceRegistry public immutable evidenceRegistry;
    IZKTelemetryVerifier public zkVerifier;

    // Minimum waterlogging depth in cm required to release emergency relief
    uint256 public triggerThresholdDepthCm;

    // Standard payout tranche in token units (e.g., 50,000 USDC with 6 decimals = 50_000 * 1e6)
    uint256 public standardReliefTranche;

    // UNDP Double-Counting Defense: tracks evidence digests already settled
    mapping(bytes32 => bool) public processedEvidenceDigests;

    // Authorized AI agents allowed to execute settlements
    mapping(address => bool) public authorizedAgents;

    // Cumulative metrics
    uint256 public totalSettledAmount;
    uint256 public totalSettlementEvents;

    // ─── EVENTS ─────────────────────────────────────────────────────────────

    event EmergencyReliefSettled(
        bytes32 indexed evidenceDigest,
        address indexed municipalBeneficiary,
        uint256 amountSettled,
        uint256 floodDepthCm,
        uint256 timestamp
    );

    event LiquidityFunded(
        address indexed donor,
        uint256 amount,
        uint256 timestamp
    );

    event AgentAuthorizationUpdated(
        address indexed agent,
        bool authorized
    );

    event ThresholdsUpdated(
        uint256 newTriggerDepthCm,
        uint256 newReliefTranche
    );

    event ZKVerifierUpdated(
        address indexed oldVerifier,
        address indexed newVerifier
    );

    // ─── CUSTOM ERRORS ──────────────────────────────────────────────────────

    error UnauthorizedAgent(address caller);
    error ZeroAddressForbidden();
    error ZeroDigestForbidden();
    error EvidenceNotAnchored(bytes32 digest);
    error DigestAlreadySettled(bytes32 digest);
    error FloodDepthBelowThreshold(uint256 depthCm, uint256 thresholdCm);
    error InsufficientLiquidity(uint256 available, uint256 required);
    error InvalidZKProof(bytes32 digest);

    // ─── MODIFIERS ──────────────────────────────────────────────────────────

    modifier onlyAuthorized() {
        if (msg.sender != owner() && !authorizedAgents[msg.sender]) {
            revert UnauthorizedAgent(msg.sender);
        }
        _;
    }

    // ─── CONSTRUCTOR ────────────────────────────────────────────────────────

    constructor(
        address _stablecoin,
        address _evidenceRegistry,
        uint256 _triggerThresholdDepthCm,
        uint256 _standardReliefTranche
    ) Ownable(msg.sender) {
        if (_stablecoin == address(0) || _evidenceRegistry == address(0)) {
            revert ZeroAddressForbidden();
        }
        stablecoin = IERC20(_stablecoin);
        evidenceRegistry = ClimateEvidenceRegistry(_evidenceRegistry);
        triggerThresholdDepthCm = _triggerThresholdDepthCm;
        standardReliefTranche = _standardReliefTranche;
        authorizedAgents[msg.sender] = true;
    }

    // ─── EXTERNAL FUNCTIONS ─────────────────────────────────────────────────

    /**
     * @notice Programmatic emergency relief settlement executed by autonomous AI agents.
     * @param evidenceDigest Keccak-256 digest of verified ClimateEvidenceBundle.
     * @param depthCm Flood waterlogging depth in centimeters estimated by Agent 2 DEM model.
     * @param municipalBeneficiary Address of the civic defense or municipal disaster authority.
     * @param zkProof Optional Groth16 cryptographic proof for telemetry verification.
     */
    function settleEmergencyRelief(
        bytes32 evidenceDigest,
        uint256 depthCm,
        address municipalBeneficiary,
        bytes calldata zkProof
    ) external onlyAuthorized returns (bool) {
        if (evidenceDigest == bytes32(0)) revert ZeroDigestForbidden();
        if (municipalBeneficiary == address(0)) revert ZeroAddressForbidden();

        // 1. Check UNDP Double-Counting Defense
        if (processedEvidenceDigests[evidenceDigest]) {
            revert DigestAlreadySettled(evidenceDigest);
        }

        // 2. Cryptographic Anchor Verification
        if (!evidenceRegistry.isAnchored(evidenceDigest)) {
            revert EvidenceNotAnchored(evidenceDigest);
        }

        // 3. Parametric Flood Depth Threshold Check
        if (depthCm < triggerThresholdDepthCm) {
            revert FloodDepthBelowThreshold(depthCm, triggerThresholdDepthCm);
        }

        // 4. Optional Zero-Knowledge Telemetry Attestation
        if (address(zkVerifier) != address(0)) {
            bool zkValid = zkVerifier.verifyTelemetryBounds(
                evidenceDigest,
                150, // maxRainfall24hMm bound
                0,   // minElevationM bound
                zkProof
            );
            if (!zkValid) {
                revert InvalidZKProof(evidenceDigest);
            }
        }

        // 5. Check Pool Liquidity
        uint256 poolBalance = stablecoin.balanceOf(address(this));
        if (poolBalance < standardReliefTranche) {
            revert InsufficientLiquidity(poolBalance, standardReliefTranche);
        }

        // 6. State Mutation & Double-Counting Lock
        processedEvidenceDigests[evidenceDigest] = true;
        totalSettledAmount += standardReliefTranche;
        totalSettlementEvents += 1;

        // 7. Atomic Stablecoin Transfer
        bool success = stablecoin.transfer(municipalBeneficiary, standardReliefTranche);
        require(success, "AgenticSettlementPool: transfer failed");

        emit EmergencyReliefSettled(
            evidenceDigest,
            municipalBeneficiary,
            standardReliefTranche,
            depthCm,
            block.timestamp
        );

        return true;
    }

    /**
     * @notice Allows liquidity providers, municipal treasuries, and donors to fund the pool.
     * @param amount Stablecoin amount to deposit into the relief reserve.
     */
    function fundLiquidityPool(uint256 amount) external returns (bool) {
        require(amount > 0, "AgenticSettlementPool: zero amount");
        bool success = stablecoin.transferFrom(msg.sender, address(this), amount);
        require(success, "AgenticSettlementPool: deposit transfer failed");

        emit LiquidityFunded(msg.sender, amount, block.timestamp);
        return true;
    }

    // ─── ADMIN CONFIGURATION ────────────────────────────────────────────────

    function setAgentAuthorization(address agent, bool authorized) external onlyOwner {
        if (agent == address(0)) revert ZeroAddressForbidden();
        authorizedAgents[agent] = authorized;
        emit AgentAuthorizationUpdated(agent, authorized);
    }

    function setThresholds(
        uint256 newTriggerDepthCm,
        uint256 newReliefTranche
    ) external onlyOwner {
        triggerThresholdDepthCm = newTriggerDepthCm;
        standardReliefTranche = newReliefTranche;
        emit ThresholdsUpdated(newTriggerDepthCm, newReliefTranche);
    }

    function setZKVerifier(address newVerifier) external onlyOwner {
        emit ZKVerifierUpdated(address(zkVerifier), newVerifier);
        zkVerifier = IZKTelemetryVerifier(newVerifier);
    }

    function getLiquidityBalance() external view returns (uint256) {
        return stablecoin.balanceOf(address(this));
    }
}
