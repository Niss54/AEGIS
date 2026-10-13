// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title CarbonFloodCredit
 * @notice ERC-20 token representing Carbon Flood Mitigation Credits (CFMC).
 * @dev Minted when AEGIS Agent 2 detects effective flood mitigation:
 *      - Agent 1 risk score >= 0.65 (CRITICAL) but
 *      - Agent 2 DEM depth < LOW_DAMAGE_DEPTH_CM (<20cm)
 *      1 CFMC = 1 unit of verified flood resilience / avoided damage credit.
 */
contract CarbonFloodCredit is ERC20, Ownable {

    uint256 public constant MITIGATION_REWARD = 100 * 1e18; // 100 CFMC per mitigation event
    uint256 public constant CRITICAL_RISK_BPS = 6500;       // 0.65
    uint256 public constant LOW_DAMAGE_DEPTH_CM = 20;       // <20cm = effective mitigation

    address public aegisBackend;
    uint256 public totalMitigationEvents;
    uint256 public totalCFMCMinted;

    mapping(address => uint256) public mitigationCount;
    mapping(bytes32 => bool) public mitigationRecorded;

    event MitigationCreditIssued(
        address indexed beneficiary,
        uint256 amount,
        bytes32 indexed assessmentId,
        int256 latScaled,
        int256 lonScaled,
        uint256 riskScoreBps,
        uint256 demDepthCm
    );

    event CFMCRetired(address indexed holder, uint256 amount, string reason);
    event OffsetRetiredForResilience(
        address indexed retiree,
        uint256 amount,
        bytes32 indexed evidenceDigest,
        string memo,
        uint256 timestamp
    );
    event BackendUpdated(address indexed oldBackend, address indexed newBackend);

    constructor(address _aegisBackend)
        ERC20("Carbon Flood Mitigation Credit", "CFMC")
        Ownable(msg.sender)
    {
        require(_aegisBackend != address(0), "CarbonFloodCredit: zero address");
        aegisBackend = _aegisBackend;
        emit BackendUpdated(address(0), _aegisBackend);
    }

    function issueMitigationCredit(
        address beneficiary,
        bytes32 assessmentId,
        int256 latScaled,
        int256 lonScaled,
        uint256 riskScoreBps,
        uint256 demDepthCm
    ) external returns (bool) {
        require(
            msg.sender == aegisBackend || msg.sender == owner(),
            "CarbonFloodCredit: unauthorized"
        );
        require(!mitigationRecorded[assessmentId], "CarbonFloodCredit: already recorded");
        require(beneficiary != address(0), "CarbonFloodCredit: zero beneficiary");
        require(riskScoreBps >= CRITICAL_RISK_BPS, "CarbonFloodCredit: risk not critical");
        require(demDepthCm < LOW_DAMAGE_DEPTH_CM, "CarbonFloodCredit: damage not low enough");

        mitigationRecorded[assessmentId] = true;
        mitigationCount[beneficiary]++;
        totalMitigationEvents++;
        totalCFMCMinted += MITIGATION_REWARD;

        _mint(beneficiary, MITIGATION_REWARD);

        emit MitigationCreditIssued(
            beneficiary, MITIGATION_REWARD, assessmentId,
            latScaled, lonScaled, riskScoreBps, demDepthCm
        );

        return true;
    }

    function retireCredits(uint256 amount, string calldata reason) external {
        require(amount > 0, "CarbonFloodCredit: zero amount");
        _burn(msg.sender, amount);
        emit CFMCRetired(msg.sender, amount, reason);
    }

    function retireOffsetForFloodResilience(
        uint256 amount,
        bytes32 evidenceDigest,
        string calldata memo
    ) external {
        require(amount > 0, "CarbonFloodCredit: zero amount");
        require(evidenceDigest != bytes32(0), "CarbonFloodCredit: zero evidence digest");
        _burn(msg.sender, amount);
        emit OffsetRetiredForResilience(msg.sender, amount, evidenceDigest, memo, block.timestamp);
    }

    function setBackend(address newBackend) external onlyOwner {
        require(newBackend != address(0), "CarbonFloodCredit: zero address");
        emit BackendUpdated(aegisBackend, newBackend);
        aegisBackend = newBackend;
    }
}
