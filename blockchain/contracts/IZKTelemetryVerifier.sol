// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title IZKTelemetryVerifier
 * @notice Standard interface for Groth16 Zero-Knowledge proof verification of sensor telemetry bounds.
 * @dev Enables autonomous AI agents to prove that telemetry (rainfall, elevation deltas) respects
 *      physical cryptographic thresholds without exposing raw private sensor parameters on-chain.
 */
interface IZKTelemetryVerifier {
    function verifyTelemetryBounds(
        bytes32 evidenceDigest,
        uint256 maxRainfall24hMm,
        uint256 minElevationM,
        bytes calldata zkProof
    ) external view returns (bool);
}
