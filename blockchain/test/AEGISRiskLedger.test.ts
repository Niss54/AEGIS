import { expect } from "chai";
import { ethers } from "hardhat";
import { AEGISRiskLedger } from "../typechain-types";
import { HardhatEthersSigner } from "@nomicfoundation/hardhat-ethers/signers";

describe("AEGISRiskLedger", () => {
  let ledger: AEGISRiskLedger;
  let owner: HardhatEthersSigner;
  let backend: HardhatEthersSigner;
  let attacker: HardhatEthersSigner;

  before(async () => {
    [owner, backend, attacker] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory("AEGISRiskLedger");
    ledger = await Factory.deploy(backend.address);
    await ledger.waitForDeployment();
  });

  describe("anchorRiskAssessment", () => {
    it("should anchor a valid risk assessment and emit event", async () => {
      const tx = await ledger.connect(backend).anchorRiskAssessment(
        19072800n,
        72879700n,
        7800n,
        "bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi",
        "Mumbai — Mithi River Basin"
      );
      const receipt = await tx.wait();
      expect(receipt).to.not.be.null;

      const ids = await ledger.getRecentAssessments(1);
      expect(ids.length).to.equal(1);
      const assessment = await ledger.getAssessment(ids[0]);
      expect(assessment.locationName).to.equal("Mumbai — Mithi River Basin");
      expect(assessment.riskScoreBps).to.equal(7800n);
      expect(assessment.riskTier).to.equal(3); // CRITICAL
    });

    it("should assign CRITICAL tier when score >= 6500 BPS", async () => {
      const ids = await ledger.getRecentAssessments(1);
      const assessment = await ledger.getAssessment(ids[0]);
      expect(assessment.riskTier).to.equal(3);
    });

    it("should be idempotent within the same 15-minute window", async () => {
      const before = await ledger.totalAssessments();
      await ledger.connect(backend).anchorRiskAssessment(
        19072800n,
        72879700n,
        7800n,
        "bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi",
        "Mumbai — Mithi River Basin"
      );
      const after = await ledger.totalAssessments();
      expect(after).to.equal(before);
    });

    it("should REJECT anchoring from unauthorized address", async () => {
      await expect(
        ledger.connect(attacker).anchorRiskAssessment(
          19072800n, 72879700n, 7800n, "bafybei...", "Mumbai"
        )
      ).to.be.revertedWith("AEGISRiskLedger: caller is not authorized");
    });

    it("should reject invalid risk score > 10000 BPS", async () => {
      await expect(
        ledger.connect(backend).anchorRiskAssessment(
          19072800n, 72879700n, 10001n, "bafybei...", "Mumbai"
        )
      ).to.be.revertedWith("AEGISRiskLedger: score exceeds max BPS");
    });

    it("should emit CriticalAlertEmitted for CRITICAL tier", async () => {
      await expect(
        ledger.connect(backend).anchorRiskAssessment(
          28613900n, 77209100n, 9500n, "bafybei...", "Delhi — Yamuna Floodplain"
        )
      ).to.emit(ledger, "CriticalAlertEmitted");
    });
  });

  describe("anchorDEMCascade", () => {
    it("should anchor DEM cascade for critical assessment", async () => {
      const ids = await ledger.getRecentAssessments(1);
      const assessmentId = ids[0];
      await expect(
        ledger.connect(backend).anchorDEMCascade(
          assessmentId, 75n, 320n, 82n, "bafybei-dem"
        )
      ).to.emit(ledger, "DEMCascadeAnchored");

      const updated = await ledger.getAssessment(assessmentId);
      expect(updated.demTriggered).to.be.true;
      expect(updated.demDepthCm).to.equal(75n);
    });

    it("should reject DEM cascade for non-critical assessment", async () => {
      await ledger.connect(backend).anchorRiskAssessment(
        13082700n, 80270700n, 1500n, "bafybei...", "Chennai — Low Risk Area"
      );
      const ids = await ledger.getRecentAssessments(1);
      await expect(
        ledger.connect(backend).anchorDEMCascade(
          ids[0], 30n, 100n, 45n, "bafybei..."
        )
      ).to.be.revertedWith("DEM cascade requires CRITICAL");
    });
  });

  describe("anchorVaRCascade", () => {
    it("should anchor VaR cascade when DEM was triggered", async () => {
      const history = await ledger.getLocationHistory(28613900n, 77209100n);
      const assessmentId = history[0];
      await expect(
        ledger.connect(backend).anchorVaRCascade(
          assessmentId, 45000n, 54000000n, 2500n, 3000n, "bafybei-var"
        )
      ).to.emit(ledger, "VaRCascadeAnchored");

      const assessment = await ledger.getAssessment(assessmentId);
      expect(assessment.varTriggered).to.be.true;
      expect(assessment.varInrLakhs).to.equal(45000n);
    });
  });

  describe("getLocationHistory and stats", () => {
    it("should return assessment history for a coordinate", async () => {
      const history = await ledger.getLocationHistory(19072800n, 72879700n);
      expect(history.length).to.be.greaterThan(0);
    });

    it("should report non-zero stats", async () => {
      const [total, critical] = await ledger.getStats();
      expect(total).to.be.greaterThan(0);
      expect(critical).to.be.greaterThan(0);
    });
  });
});
