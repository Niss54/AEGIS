import { expect } from "chai";
import { ethers } from "hardhat";
import { DisasterBond, MockERC20, AEGISRiskLedger } from "../typechain-types";
import { HardhatEthersSigner } from "@nomicfoundation/hardhat-ethers/signers";

describe("DisasterBond", () => {
  let bond: DisasterBond;
  let usdc: MockERC20;
  let ledger: AEGISRiskLedger;
  let owner: HardhatEthersSigner;
  let backend: HardhatEthersSigner;
  let beneficiary: HardhatEthersSigner;
  let createdBondId: string;

  const PAYOUT_AMOUNT = 50000n * 1000000n; // 50,000 USDC (6 decimals)
  const LAT = 19072800n;
  const LON = 72879700n;

  before(async () => {
    [owner, backend, beneficiary] = await ethers.getSigners();

    const MockFactory = await ethers.getContractFactory("MockERC20");
    usdc = await MockFactory.deploy("USD Coin", "USDC", 6);
    await usdc.waitForDeployment();

    const LedgerFactory = await ethers.getContractFactory("AEGISRiskLedger");
    ledger = await LedgerFactory.deploy(backend.address);
    await ledger.waitForDeployment();

    const BondFactory = await ethers.getContractFactory("DisasterBond");
    bond = await BondFactory.deploy(await usdc.getAddress(), await ledger.getAddress(), backend.address);
    await bond.waitForDeployment();

    // Mint USDC to owner and approve DisasterBond
    await usdc.mint(owner.address, PAYOUT_AMOUNT * 10n);
    await usdc.approve(await bond.getAddress(), PAYOUT_AMOUNT * 10n);
  });

  it("should create a parametric disaster bond with escrowed USDC", async () => {
    const tx = await bond.createBond(
      LAT,
      LON,
      beneficiary.address,
      PAYOUT_AMOUNT,
      6500n, // 0.65 threshold
      2n,    // 2 consecutive breaches
      "Mumbai — Mithi River Basin"
    );
    await tx.wait();

    const locationBonds = await bond.getLocationBonds(LAT, LON);
    expect(locationBonds.length).to.equal(1);
    createdBondId = locationBonds[0];

    const bondData = await bond.getBond(createdBondId);
    expect(bondData.active).to.be.true;
    expect(bondData.triggered).to.be.false;
    expect(bondData.payoutAmount).to.equal(PAYOUT_AMOUNT);
    expect(bondData.consecutiveRequired).to.equal(2n);

    const contractBal = await bond.getContractBalance();
    expect(contractBal).to.equal(PAYOUT_AMOUNT);
  });

  it("should increment consecutive counter on 1st critical breach without triggering", async () => {
    const fakeAssessmentId = ethers.keccak256(ethers.toUtf8Bytes("assessment-1"));
    await bond.connect(backend).notifyAssessment(LAT, LON, 7800n, fakeAssessmentId);

    const bondData = await bond.getBond(createdBondId);
    expect(bondData.consecutiveCount).to.equal(1n);
    expect(bondData.triggered).to.be.false;
    expect(bondData.active).to.be.true;
  });

  it("should reset consecutive counter if risk drops below threshold", async () => {
    const fakeAssessmentId = ethers.keccak256(ethers.toUtf8Bytes("assessment-2"));
    await bond.connect(backend).notifyAssessment(LAT, LON, 3000n, fakeAssessmentId);

    const bondData = await bond.getBond(createdBondId);
    expect(bondData.consecutiveCount).to.equal(0n);
  });

  it("should auto-pay beneficiary when consecutive threshold is reached", async () => {
    const initialBeneficiaryBal = await usdc.balanceOf(beneficiary.address);

    const a1 = ethers.keccak256(ethers.toUtf8Bytes("assess-breach-1"));
    const a2 = ethers.keccak256(ethers.toUtf8Bytes("assess-breach-2"));

    await bond.connect(backend).notifyAssessment(LAT, LON, 8500n, a1);
    await bond.connect(backend).notifyAssessment(LAT, LON, 8900n, a2);

    const bondData = await bond.getBond(createdBondId);
    expect(bondData.triggered).to.be.true;
    expect(bondData.active).to.be.false;

    const finalBeneficiaryBal = await usdc.balanceOf(beneficiary.address);
    expect(finalBeneficiaryBal - initialBeneficiaryBal).to.equal(PAYOUT_AMOUNT);
  });
});
