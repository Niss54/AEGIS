import { expect } from "chai";
import { ethers } from "hardhat";
import { CarbonFloodCredit } from "../typechain-types";
import { HardhatEthersSigner } from "@nomicfoundation/hardhat-ethers/signers";

describe("CarbonFloodCredit", () => {
  let cfmc: CarbonFloodCredit;
  let owner: HardhatEthersSigner;
  let backend: HardhatEthersSigner;
  let beneficiary: HardhatEthersSigner;

  const MITIGATION_REWARD = 100n * 10n ** 18n;

  before(async () => {
    [owner, backend, beneficiary] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory("CarbonFloodCredit");
    cfmc = await Factory.deploy(backend.address);
    await cfmc.waitForDeployment();
  });

  it("should initialize with correct token metadata", async () => {
    expect(await cfmc.name()).to.equal("Carbon Flood Mitigation Credit");
    expect(await cfmc.symbol()).to.equal("CFMC");
  });

  it("should mint CFMC when Agent 2 detects high risk but low damage (<20cm)", async () => {
    const assessmentId = ethers.keccak256(ethers.toUtf8Bytes("mitigation-event-1"));

    const tx = await cfmc.connect(backend).issueMitigationCredit(
      beneficiary.address,
      assessmentId,
      19072800n,
      72879700n,
      7500n, // Critical risk: 75%
      12n    // Low waterlogging depth: 12cm (<20cm)
    );
    await tx.wait();

    expect(await cfmc.balanceOf(beneficiary.address)).to.equal(MITIGATION_REWARD);
    expect(await cfmc.totalMitigationEvents()).to.equal(1n);
    expect(await cfmc.mitigationCount(beneficiary.address)).to.equal(1n);
  });

  it("should reject double-minting for the same assessment", async () => {
    const assessmentId = ethers.keccak256(ethers.toUtf8Bytes("mitigation-event-1"));
    await expect(
      cfmc.connect(backend).issueMitigationCredit(
        beneficiary.address,
        assessmentId,
        19072800n,
        72879700n,
        7500n,
        12n
      )
    ).to.be.revertedWith("CarbonFloodCredit: already recorded");
  });

  it("should reject credit issuance if risk is not critical (<6500 BPS)", async () => {
    const assessmentId = ethers.keccak256(ethers.toUtf8Bytes("low-risk-event"));
    await expect(
      cfmc.connect(backend).issueMitigationCredit(
        beneficiary.address,
        assessmentId,
        19072800n,
        72879700n,
        5000n, // only 50%
        10n
      )
    ).to.be.revertedWith("CarbonFloodCredit: risk not critical");
  });

  it("should reject credit issuance if damage is too high (>=20cm)", async () => {
    const assessmentId = ethers.keccak256(ethers.toUtf8Bytes("severe-damage-event"));
    await expect(
      cfmc.connect(backend).issueMitigationCredit(
        beneficiary.address,
        assessmentId,
        19072800n,
        72879700n,
        8000n,
        65n // 65cm damage
      )
    ).to.be.revertedWith("CarbonFloodCredit: damage not low enough");
  });

  it("should allow holder to retire credits", async () => {
    await cfmc.connect(beneficiary).retireCredits(
      50n * 10n ** 18n,
      "Corporate ESG Offset - FY2026"
    );
    expect(await cfmc.balanceOf(beneficiary.address)).to.equal(50n * 10n ** 18n);
  });
});
