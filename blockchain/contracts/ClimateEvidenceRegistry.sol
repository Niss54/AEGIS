// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ClimateEvidenceRegistry
 * @notice Normative Ethereum/Polygon Registry for AEGIS-CLIMATE Evidence Bundles.
 * @dev Conforms to PRD 2: Section 7 and E-073 through E-084.
 *      Anchors Keccak-256 evidence digests with strict schema versioning and access control.
 *      Preserves data privacy: strictly zero raw weather telemetry or personal data on-chain.
 */
contract ClimateEvidenceRegistry is Ownable {

    struct EvidenceRecord {
        bytes32 digest;            // Keccak-256 of canonical JSON bundle
        bytes32 reportRef;         // Truncated/hashed analysis identifier reference
        uint32  schemaVersion;     // e.g. 1 (corresponds to "1.0.0")
        address issuer;            // Authorized AEGIS backend or issuer address
        uint64  blockTimestamp;    // Timestamp recorded on chain
        bool    exists;            // Exists flag for O(1) lookup
    }

    // Mapping from digest to EvidenceRecord
    mapping(bytes32 => EvidenceRecord) public records;

    // Authorized issuers allowlist (in addition to contract owner)
    mapping(address => bool) public authorizedIssuers;

    // Counter of total unique anchored evidence bundles
    uint256 public totalAnchored;

    // ─── EVENTS ─────────────────────────────────────────────────────────────
    event EvidenceAnchored(
        bytes32 indexed digest,
        bytes32 indexed reportRef,
        uint32 schemaVersion,
        address indexed issuer,
        uint256 blockTimestamp
    );

    event IssuerAuthorized(address indexed issuer);
    event IssuerRevoked(address indexed issuer);

    // ─── ERRORS ─────────────────────────────────────────────────────────────
    error UnauthorizedCaller(address caller);
    error ZeroDigestForbidden();
    error InvalidSchemaVersion(uint32 version);
    error EmptyReportRefForbidden();
    error DigestAlreadyAnchored(bytes32 digest);

    modifier onlyAuthorized() {
        if (msg.sender != owner() && !authorizedIssuers[msg.sender]) {
            revert UnauthorizedCaller(msg.sender);
        }
        _;
    }

    constructor() Ownable(msg.sender) {
        authorizedIssuers[msg.sender] = true;
    }

    function setIssuerAuthorization(address issuer, bool authorized) external onlyOwner {
        authorizedIssuers[issuer] = authorized;
        if (authorized) {
            emit IssuerAuthorized(issuer);
        } else {
            emit IssuerRevoked(issuer);
        }
    }

    function anchorEvidence(
        bytes32 digest,
        bytes32 reportRef,
        uint32 schemaVersion
    ) external onlyAuthorized returns (bool) {
        if (digest == bytes32(0)) revert ZeroDigestForbidden();
        if (reportRef == bytes32(0)) revert EmptyReportRefForbidden();
        if (schemaVersion == 0) revert InvalidSchemaVersion(schemaVersion);
        if (records[digest].exists) revert DigestAlreadyAnchored(digest);

        uint64 ts = uint64(block.timestamp);
        records[digest] = EvidenceRecord({
            digest: digest,
            reportRef: reportRef,
            schemaVersion: schemaVersion,
            issuer: msg.sender,
            blockTimestamp: ts,
            exists: true
        });

        totalAnchored += 1;

        emit EvidenceAnchored(digest, reportRef, schemaVersion, msg.sender, ts);
        return true;
    }

    function isAnchored(bytes32 digest) external view returns (bool) {
        return records[digest].exists;
    }

    function getEvidenceRecord(bytes32 digest) external view returns (
        bytes32,
        bytes32,
        uint32,
        address,
        uint64
    ) {
        EvidenceRecord memory rec = records[digest];
        require(rec.exists, "Evidence digest not anchored");
        return (rec.digest, rec.reportRef, rec.schemaVersion, rec.issuer, rec.blockTimestamp);
    }
}
