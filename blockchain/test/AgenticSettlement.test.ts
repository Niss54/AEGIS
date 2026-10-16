import { expect } from "chai";
import { ethers } from "hardhat";
import {
  AgenticSettlementPool,
  ClimateEvidenceRegistry,
  CarbonFloodCredit,
  MockERC20,
  MockZKTelemetryVerifier
} from "../typechain-types";
import { SignerWithAddress } from "@nomicfoundation/hardhat-ethers/signers";

describe("AgenticSettlementPool & CarbonFloodCredit (Phase 4)", function () {
  let owner: SignerWithAddress;
  let aiAgent: SignerWithAddress;
  let municipalBeneficiary: SignerWithAddress;
  let unauthorizedUser: SignerWithAddress;

  let usdc: MockERC20;
  let registry: ClimateEvidenceRegistry;
  let pool: AgenticSettlementPool;
  let zkVerifier: MockZKTelemetryVerifier;
  let carbonCredit: CarbonFloodCredit;

  const TRIGGER_DEPTH_CM = 50; // 50 cm threshold for emergency tranche
  const RELIEF_TRANCHE = ethers.parseUnits("50000", 6); // 50,000 USDC
  const INITIAL_POOL_FUNDING = ethers.parseUnits("500000", 6); // 500,000 USDC

  beforeEach(async function () {
    [owner, aiAgent, municipalBeneficiary, unauthorizedUser] = await ethers.getSigners();

    // 1. Deploy Mock USDC (6 decimals)
    const MockERC20Factory = await ethers.getContractFactory("MockERC20");
    usdc = await MockERC20Factory.deploy("USD Coin", "USDC", 6);
    await usdc.waitForDeployment();

    // 2. Deploy ClimateEvidenceRegistry
    const RegistryFactory = await ethers.getContractFactory("ClimateEvidenceRegistry");
    registry = await RegistryFactory.deploy();
    await registry.waitForDeployment();

    // Authorize AI agent to anchor evidence in registry
    await registry.setIssuerAuthorization(aiAgent.address, true);

    // 3. Deploy AgenticSettlementPool
    const PoolFactory = await ethers.getContractFactory("AgenticSettlementPool");
    pool = await PoolFactory.deploy(
      await usdc.getAddress(),
      await registry.getAddress(),
      TRIGGER_DEPTH_CM,
      RELIEF_TRANCHE
    );
    await pool.waitForDeployment();

    // Authorize AI agent to execute settlements
    await pool.setAgentAuthorization(aiAgent.address, true);

    // 4. Fund the Liquidity Pool with 500,000 USDC
    await usdc.mint(owner.address, INITIAL_POOL_FUNDING);
    await usdc.approve(await pool.getAddress(), INITIAL_POOL_FUNDING);
    await pool.fundLiquidityPool(INITIAL_POOL_FUNDING);

    // 5. Deploy MockZKTelemetryVerifier
    const ZKFactory = await ethers.getContractFactory("MockZKTelemetryVerifier");
    zkVerifier = await ZKFactory.deploy();
    await zkVerifier.waitForDeployment();

    // 6. Deploy CarbonFloodCredit
    const CarbonCreditFactory = await ethers.getContractFactory("CarbonFloodCredit");
    carbonCredit = await CarbonCreditFactory.deploy(owner.address);
    await carbonCredit.waitForDeployment();
  });

  describe("Deployment & Pool Liquidity", function () {
    it("should initialize with correct stablecoin, registry, and liquidity balance", async function () {
      expect(await pool.stablecoin()).to.equal(await usdc.getAddress());
      expect(await pool.evidenceRegistry()).to.equal(await registry.getAddress());
      expect(await pool.triggerThresholdDepthCm()).to.equal(TRIGGER_DEPTH_CM);
      expect(await pool.standardReliefTranche()).to.equal(RELIEF_TRANCHE);
      expect(await pool.getLiquidityBalance()).to.equal(INITIAL_POOL_FUNDING);
    });

    it("should allow donors and treasuries to fund the pool", async function () {
      const topUpAmount = ethers.parseUnits("25000", 6);
      await usdc.mint(owner.address, topUpAmount);
      await usdc.approve(await pool.getAddress(), topUpAmount);

      await expect(pool.fundLiquidityPool(topUpAmount))
        .to.emit(pool, "LiquidityFunded");

      expect(await pool.getLiquidityBalance()).to.equal(INITIAL_POOL_FUNDING + topUpAmount);
    });
  });

  describe("Autonomous Emergency Relief Settlement", function () {
    let validEvidenceDigest: string;
    let reportRef: string;

    beforeEach(async function () {
      validEvidenceDigest = ethers.keccak256(ethers.toUtf8Bytes("canonical-evidence-istanbul-surge-2026"));
      reportRef = ethers.keccak256(ethers.toUtf8Bytes("analysis-evt-istanbul-001"));

      // Anchor evidence in registry
      await registry.connect(aiAgent).anchorEvidence(validEvidenceDigest, reportRef, 1);
    });

    it("should REJECT settlement call from unauthorized address", async function () {
      await expect(
        pool.connect(unauthorizedUser).settleEmergencyRelief(
          validEvidenceDigest,
          65, // 65cm flood depth
          municipalBeneficiary.address,
          "0x"
        )
      ).to.be.revertedWithCustomError(pool, "UnauthorizedAgent");
    });

    it("should REJECT settlement if evidence digest is NOT anchored", async function () {
      const unanchoredDigest = ethers.keccak256(ethers.toUtf8Bytes("unanchored-fake-evidence"));

      await expect(
        pool.connect(aiAgent).settleEmergencyRelief(
          unanchoredDigest,
          65,
          municipalBeneficiary.address,
          "0x"
        )
      ).to.be.revertedWithCustomError(pool, "EvidenceNotAnchored");
    });

    it("should REJECT settlement if flood depth is BELOW trigger threshold", async function () {
      const shallowDepthCm = 35; // Below 50cm threshold

      await expect(
        pool.connect(aiAgent).settleEmergencyRelief(
          validEvidenceDigest,
          shallowDepthCm,
          municipalBeneficiary.address,
          "0x"
        )
      ).to.be.revertedWithCustomError(pool, "FloodDepthBelowThreshold");
    });

    it("should REJECT settlement to zero address beneficiary", async function () {
      await expect(
        pool.connect(aiAgent).settleEmergencyRelief(
          validEvidenceDigest,
          65,
          ethers.ZeroAddress,
          "0x"
        )
      ).to.be.revertedWithCustomError(pool, "ZeroAddressForbidden");
    });

    it("should EXECUTE autonomous stablecoin settlement and transfer USDC to municipal beneficiary", async function () {
      const initialBeneficiaryBalance = await usdc.balanceOf(municipalBeneficiary.address);
      const initialPoolBalance = await pool.getLiquidityBalance();
      const floodDepthCm = 72;

      const tx = await pool.connect(aiAgent).settleEmergencyRelief(
        validEvidenceDigest,
        floodDepthCm,
        municipalBeneficiary.address,
        "0x"
      );

      // Verify event emission
      await expect(tx)
        .to.emit(pool, "EmergencyReliefSettled")
        .withArgs(
          validEvidenceDigest,
          municipalBeneficiary.address,
          RELIEF_TRANCHE,
          floodDepthCm,
          (await ethers.provider.getBlock("latest"))!.timestamp
        );

      // Verify token balances
      expect(await usdc.balanceOf(municipalBeneficiary.address)).to.equal(
        initialBeneficiaryBalance + RELIEF_TRANCHE
      );
      expect(await pool.getLiquidityBalance()).to.equal(
        initialPoolBalance - RELIEF_TRANCHE
      );

      // Verify settlement state
      expect(await pool.processedEvidenceDigests(validEvidenceDigest)).to.be.true;
      expect(await pool.totalSettledAmount()).to.equal(RELIEF_TRANCHE);
      expect(await pool.totalSettlementEvents()).to.equal(1);
    });

    it("UNDP DOUBLE-COUNTING DEFENSE: should REVERT duplicate settlement claim for the same evidence digest", async function () {
      // First settlement passes
      await pool.connect(aiAgent).settleEmergencyRelief(
        validEvidenceDigest,
        65,
        municipalBeneficiary.address,
        "0x"
      );

      // Second settlement with identical evidence MUST be rejected
      await expect(
        pool.connect(aiAgent).settleEmergencyRelief(
          validEvidenceDigest,
          65,
          municipalBeneficiary.address,
          "0x"
        )
      ).to.be.revertedWithCustomError(pool, "DigestAlreadySettled");
    });

    it("ZERO-KNOWLEDGE ATTESTATION: should enforce ZK proof verification when ZKVerifier is set", async function () {
      // Attach Mock ZK Verifier
      await pool.setZKVerifier(await zkVerifier.getAddress());

      // Valid mock proof
      const dummyProof = ethers.toUtf8Bytes("groth16-valid-telemetry-proof-bounds-ok");

      const secondEvidenceDigest = ethers.keccak256(ethers.toUtf8Bytes("canonical-evidence-orange-county-2026"));
      await registry.connect(aiAgent).anchorEvidence(secondEvidenceDigest, reportRef, 1);

      // Should succeed with valid proof
      await expect(
        pool.connect(aiAgent).settleEmergencyRelief(
          secondEvidenceDigest,
          85,
          municipalBeneficiary.address,
          dummyProof
        )
      ).to.emit(pool, "EmergencyReliefSettled");

      // Now set ZK verifier to fail
      await zkVerifier.setShouldVerify(false);

      const thirdEvidenceDigest = ethers.keccak256(ethers.toUtf8Bytes("canonical-evidence-parnu-baltic-2026"));
      await registry.connect(aiAgent).anchorEvidence(thirdEvidenceDigest, reportRef, 1);

      // Should revert with InvalidZKProof
      await expect(
        pool.connect(aiAgent).settleEmergencyRelief(
          thirdEvidenceDigest,
          85,
          municipalBeneficiary.address,
          dummyProof
        )
      ).to.be.revertedWithCustomError(pool, "InvalidZKProof");
    });
  });

  describe("Carbon Offset Retirement for Flood Resilience", function () {
    const mintAmount = ethers.parseUnits("100", 18);
    const retireAmount = ethers.parseUnits("50", 18);
    let sampleEvidenceDigest: string;

    beforeEach(async function () {
      sampleEvidenceDigest = ethers.keccak256(ethers.toUtf8Bytes("carbon-offset-resilience-lucknow-gomti"));

      // Mint CFMC tokens to owner via simulated mitigation (100 CFMC)
      const assessmentId = ethers.keccak256(ethers.toUtf8Bytes("assessment-001"));
      await carbonCredit.issueMitigationCredit(
        owner.address,
        assessmentId,
        268467,
        809462,
        8500, // Critical risk
        15    // <20cm DEM depth = effective mitigation
      );
    });

    it("should allow holder to retire offsets tied to a flood resilience evidence digest", async function () {
      const initialBalance = await carbonCredit.balanceOf(owner.address);
      const memo = "Toucan / KlimaDAO programmatic offset retirement for Gomti Basin flood barrier";

      const tx = await carbonCredit.retireOffsetForFloodResilience(
        retireAmount,
        sampleEvidenceDigest,
        memo
      );

      await expect(tx)
        .to.emit(carbonCredit, "OffsetRetiredForResilience");

      expect(await carbonCredit.balanceOf(owner.address)).to.equal(initialBalance - retireAmount);
    });

    it("should REJECT offset retirement with zero amount or zero evidence digest", async function () {
      await expect(
        carbonCredit.retireOffsetForFloodResilience(0, sampleEvidenceDigest, "memo")
      ).to.be.revertedWith("CarbonFloodCredit: zero amount");

      await expect(
        carbonCredit.retireOffsetForFloodResilience(retireAmount, ethers.ZeroHash, "memo")
      ).to.be.revertedWith("CarbonFloodCredit: zero evidence digest");
    });
  });
});
