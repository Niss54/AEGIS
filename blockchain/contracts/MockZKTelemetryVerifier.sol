// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "./IZKTelemetryVerifier.sol";

/**
 * @title MockZKTelemetryVerifier
 * @notice Deterministic mock verifier for local testing of ZK telemetry bounds proofs.
 */
contract MockZKTelemetryVerifier is IZKTelemetryVerifier {
    bool public shouldVerify = true;

    function setShouldVerify(bool _shouldVerify) external {
        shouldVerify = _shouldVerify;
    }

    function verifyTelemetryBounds(
        bytes32 evidenceDigest,
        uint256 /* maxRainfall24hMm */,
        uint256 /* minElevationM */,
        bytes calldata zkProof
    ) external view override returns (bool) {
        if (!shouldVerify) return false;
        if (evidenceDigest == bytes32(0)) return false;
        if (zkProof.length == 0) return false;
        return true;
    }
}
