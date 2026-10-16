import { expect } from "chai";
import { ethers } from "hardhat";
import { HardhatEthersSigner } from "@nomicfoundation/hardhat-ethers/signers";

describe("ClimateEvidenceRegistry (PRD-2 Section 7 & 8)", () => {
  let registry: any;
  let owner: HardhatEthersSigner;
  let authorizedIssuer: HardhatEthersSigner;
  let unauthorizedCaller: HardhatEthersSigner;

  const sampleDigest = "0x68c3317c08fe764a5a01a69896e2328ef793b4343264242205250028ec255d21";
  const sampleReportRef = ethers.encodeBytes32String("ev_smoke_run_01");

  before(async () => {
    [owner, authorizedIssuer, unauthorizedCaller] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory("ClimateEvidenceRegistry");
    registry = await Factory.deploy();
    await registry.waitForDeployment();

    // Authorize the issuer
    await registry.connect(owner).setIssuerAuthorization(authorizedIssuer.address, true);
  });

  describe("Access Control & Authorization (E-077)", () => {
    it("should authorize issuer by owner and emit event", async () => {
      const isAuth = await registry.authorizedIssuers(authorizedIssuer.address);
      expect(isAuth).to.be.true;
    });

    it("should reject unauthorized caller anchoring evidence", async () => {
      await expect(
        registry.connect(unauthorizedCaller).anchorEvidence(sampleDigest, sampleReportRef, 1)
      ).to.be.revertedWithCustomError(registry, "UnauthorizedCaller");
    });
  });

  describe("Input Validation Constraints (E-078)", () => {
    it("should reject zero digest", async () => {
      const zeroDigest = ethers.ZeroHash;
      await expect(
        registry.connect(authorizedIssuer).anchorEvidence(zeroDigest, sampleReportRef, 1)
      ).to.be.revertedWithCustomError(registry, "ZeroDigestForbidden");
    });

    it("should reject empty reportRef", async () => {
      const emptyReportRef = ethers.ZeroHash;
      await expect(
        registry.connect(authorizedIssuer).anchorEvidence(sampleDigest, emptyReportRef, 1)
      ).to.be.revertedWithCustomError(registry, "EmptyReportRefForbidden");
    });

    it("should reject schemaVersion 0", async () => {
      await expect(
        registry.connect(authorizedIssuer).anchorEvidence(sampleDigest, sampleReportRef, 0)
      ).to.be.revertedWithCustomError(registry, "InvalidSchemaVersion");
    });
  });

  describe("Anchoring & Event Emission (E-074, E-075)", () => {
    it("should anchor valid evidence and emit EvidenceAnchored event", async () => {
      const tx = await registry.connect(authorizedIssuer).anchorEvidence(sampleDigest, sampleReportRef, 1);
      const receipt = await tx.wait();
      expect(receipt).to.not.be.null;

      await expect(tx)
        .to.emit(registry, "EvidenceAnchored")
        .withArgs(
          sampleDigest,
          sampleReportRef,
          1,
          authorizedIssuer.address,
          (val: any) => val > 0
        );

      expect(await registry.totalAnchored()).to.equal(1n);
      expect(await registry.isAnchored(sampleDigest)).to.be.true;
    });

    it("should retrieve stored evidence record details", async () => {
      const record = await registry.getEvidenceRecord(sampleDigest);
      expect(record[0]).to.equal(sampleDigest);
      expect(record[1]).to.equal(sampleReportRef);
      expect(record[2]).to.equal(1);
      expect(record[3]).to.equal(authorizedIssuer.address);
      expect(record[4]).to.be.gt(0);
    });
  });

  describe("Duplicate Digest Defense (E-076)", () => {
    it("should revert on duplicate digest submission", async () => {
      await expect(
        registry.connect(authorizedIssuer).anchorEvidence(sampleDigest, sampleReportRef, 1)
      ).to.be.revertedWithCustomError(registry, "DigestAlreadyAnchored");
    });
  });
});
