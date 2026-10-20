// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "./TerraSentinelRiskLedger.sol";

/**
 * @title AegisRiskLedger
 * @notice Immutable on-chain ledger for AEGIS-CLIMATE multi-agent risk assessments.
 * @dev Deployed on Polygon Amoy Testnet for IEEE ClimateChain Hackathon 2026.
 *      Anchors Agent 1, Agent 2, and Agent 3 outputs with their IPFS CIDs.
 */
contract AegisRiskLedger is TerraSentinelRiskLedger {
    constructor(address _initialOwner, address _backend) 
        TerraSentinelRiskLedger(_initialOwner, _backend) 
    {}
}
