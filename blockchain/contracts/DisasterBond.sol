// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title DisasterBond
 * @notice Parametric disaster insurance smart contract.
 * @dev Pays out automatically when AEGISRiskLedger records CRITICAL
 *      tier for a covered location for consecutive assessments.
 */
contract DisasterBond is Ownable {

    // ─── STRUCTS ────────────────────────────────────────────────────────────

    struct Bond {
        bytes32  bondId;
        int256   latScaled;
        int256   lonScaled;
        address  beneficiary;         // Payout recipient
        uint256  payoutAmount;        // In token units (e.g., USDC 6 decimals)
        uint256  triggerThresholdBps; // Risk score BPS that triggers payout
        uint256  consecutiveRequired; // Required consecutive threshold breaches
        uint256  consecutiveCount;    // Current consecutive breach count
        bool     active;
        bool     triggered;
        uint256  createdAt;
        uint256  triggeredAt;
        bytes32  triggeringAssessmentId;
        string   locationName;
    }

    // ─── STATE ───────────────────────────────────────────────────────────────

    IERC20 public immutable usdc;
    address public aegisLedger;
    address public aegisBackend;

    mapping(bytes32 => Bond) public bonds;
    mapping(int256 => mapping(int256 => bytes32[])) public locationBonds;
    bytes32[] public allBondIds;

    uint256 public totalPayouts;
    uint256 public activeBondsCount;

    // ─── EVENTS ─────────────────────────────────────────────────────────────

    event BondCreated(
        bytes32 indexed bondId,
        int256 latScaled,
        int256 lonScaled,
        address indexed beneficiary,
        uint256 payoutAmount,
        string locationName
    );

    event BondTriggered(
        bytes32 indexed bondId,
        address indexed beneficiary,
        uint256 payoutAmount,
        bytes32 indexed triggeringAssessmentId,
        uint256 timestamp
    );

    event ConsecutiveThresholdUpdated(
        bytes32 indexed bondId,
        uint256 consecutiveCount,
        uint256 consecutiveRequired
    );

    // ─── CONSTRUCTOR ────────────────────────────────────────────────────────

    constructor(
        address _usdc,
        address _aegisLedger,
        address _aegisBackend
    ) Ownable(msg.sender) {
        usdc = IERC20(_usdc);
        aegisLedger = _aegisLedger;
        aegisBackend = _aegisBackend;
    }

    // ─── BOND MANAGEMENT ─────────────────────────────────────────────────────

    function createBond(
        int256 latScaled,
        int256 lonScaled,
        address beneficiary,
        uint256 payoutAmount,
        uint256 triggerThresholdBps,
        uint256 consecutiveRequired,
        string calldata locationName
    ) external onlyOwner returns (bytes32 bondId) {
        require(beneficiary != address(0), "DisasterBond: zero beneficiary");
        require(payoutAmount > 0, "DisasterBond: zero payout");
        require(triggerThresholdBps <= 10000, "DisasterBond: invalid threshold");
        require(consecutiveRequired >= 1, "DisasterBond: min 1 consecutive");

        bondId = keccak256(abi.encodePacked(
            latScaled, lonScaled, beneficiary, block.timestamp, allBondIds.length
        ));

        require(
            usdc.transferFrom(msg.sender, address(this), payoutAmount),
            "DisasterBond: USDC transfer failed"
        );

        Bond storage bond = bonds[bondId];
        bond.bondId = bondId;
        bond.latScaled = latScaled;
        bond.lonScaled = lonScaled;
        bond.beneficiary = beneficiary;
        bond.payoutAmount = payoutAmount;
        bond.triggerThresholdBps = triggerThresholdBps;
        bond.consecutiveRequired = consecutiveRequired;
        bond.active = true;
        bond.createdAt = block.timestamp;
        bond.locationName = locationName;

        allBondIds.push(bondId);
        locationBonds[latScaled][lonScaled].push(bondId);
        activeBondsCount++;

        emit BondCreated(bondId, latScaled, lonScaled, beneficiary, payoutAmount, locationName);
        return bondId;
    }

    function notifyAssessment(
        int256 latScaled,
        int256 lonScaled,
        uint256 riskScoreBps,
        bytes32 assessmentId
    ) external {
        require(
            msg.sender == aegisBackend || msg.sender == owner(),
            "DisasterBond: unauthorized"
        );

        bytes32[] storage bondIds = locationBonds[latScaled][lonScaled];
        for (uint256 i = 0; i < bondIds.length; i++) {
            Bond storage bond = bonds[bondIds[i]];
            if (!bond.active || bond.triggered) continue;

            if (riskScoreBps >= bond.triggerThresholdBps) {
                bond.consecutiveCount++;
                emit ConsecutiveThresholdUpdated(
                    bond.bondId,
                    bond.consecutiveCount,
                    bond.consecutiveRequired
                );

                if (bond.consecutiveCount >= bond.consecutiveRequired) {
                    _executePayout(bond, assessmentId);
                }
            } else {
                bond.consecutiveCount = 0;
            }
        }
    }

    function _executePayout(Bond storage bond, bytes32 assessmentId) internal {
        bond.triggered = true;
        bond.active = false;
        bond.triggeredAt = block.timestamp;
        bond.triggeringAssessmentId = assessmentId;
        activeBondsCount--;
        totalPayouts += bond.payoutAmount;

        require(
            usdc.transfer(bond.beneficiary, bond.payoutAmount),
            "DisasterBond: payout transfer failed"
        );

        emit BondTriggered(
            bond.bondId,
            bond.beneficiary,
            bond.payoutAmount,
            assessmentId,
            block.timestamp
        );
    }

    // ─── VIEW FUNCTIONS ──────────────────────────────────────────────────────

    function getBond(bytes32 bondId) external view returns (Bond memory) {
        return bonds[bondId];
    }

    function getLocationBonds(int256 latScaled, int256 lonScaled)
        external view returns (bytes32[] memory)
    {
        return locationBonds[latScaled][lonScaled];
    }

    function getAllBondsCount() external view returns (uint256) {
        return allBondIds.length;
    }

    function getContractBalance() external view returns (uint256) {
        return usdc.balanceOf(address(this));
    }

    function setBackend(address newBackend) external onlyOwner {
        require(newBackend != address(0), "DisasterBond: zero address");
        aegisBackend = newBackend;
    }
}
