/**
 * TERRA-SENTINEL Phase 14 Smart Contract Deployment Script
 * Module: blockchain/scripts/deploy.js
 * Governance: Gravitas Reliability Runtime · Polygon Amoy Network Deployment
 *
 * Deploys:
 * 1. MockERC20 (USDC collateral token)
 * 2. TerraSentinelRiskLedger (immutable risk audit ledger)
 * 3. DisasterBond (parametric catastrophe bond settlement engine)
 * 4. CarbonFloodCredit (CFMC mitigation reward ERC-20 token)
 */
const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const [deployer] = await ethers.getSigners();
  const network = await ethers.provider.getNetwork();

  console.log("┌─────────────────────────────────────────┐");
  console.log("│  TERRA-CHAIN v2.0 — Phase 14 Deployer   │");
  console.log("└─────────────────────────────────────────┘");
  console.log(`Network: ${network.name} (ChainID: ${network.chainId})`);
  console.log(`Deployer Account: ${deployer.address}`);

  const BACKEND_WALLET = process.env.TERRA_SENTINEL_BACKEND_WALLET || deployer.address;

  // 1. Deploy Mock USDC
  console.log("1. Deploying Mock USDC Collateral...");
  const MockUSDC = await ethers.getContractFactory("MockERC20");
  const usdc = await MockUSDC.deploy("USD Coin", "USDC", 6);
  await usdc.waitForDeployment();
  const usdcAddress = await usdc.getAddress();
  console.log(`   ✅ Mock USDC deployed at: ${usdcAddress}`);

  // 2. Deploy TerraSentinelRiskLedger
  console.log("2. Deploying TerraSentinelRiskLedger...");
  const TerraSentinelRiskLedger = await ethers.getContractFactory("TerraSentinelRiskLedger");
  const ledger = await TerraSentinelRiskLedger.deploy(BACKEND_WALLET);
  await ledger.waitForDeployment();
  const ledgerAddress = await ledger.getAddress();
  console.log(`   ✅ TerraSentinelRiskLedger deployed at: ${ledgerAddress}`);

  // 3. Deploy DisasterBond
  console.log("3. Deploying DisasterBond...");
  const DisasterBond = await ethers.getContractFactory("DisasterBond");
  const bond = await DisasterBond.deploy(usdcAddress, ledgerAddress, BACKEND_WALLET);
  await bond.waitForDeployment();
  const bondAddress = await bond.getAddress();
  console.log(`   ✅ DisasterBond deployed at: ${bondAddress}`);

  // 4. Deploy CarbonFloodCredit
  console.log("4. Deploying CarbonFloodCredit (CFMC)...");
  const CarbonFloodCredit = await ethers.getContractFactory("CarbonFloodCredit");
  const cfmc = await CarbonFloodCredit.deploy(BACKEND_WALLET);
  await cfmc.waitForDeployment();
  const cfmcAddress = await cfmc.getAddress();
  console.log(`   ✅ CarbonFloodCredit deployed at: ${cfmcAddress}`);

  const deploymentRecord = {
    network: network.name,
    chainId: Number(network.chainId),
    deployer: deployer.address,
    backendWallet: BACKEND_WALLET,
    timestamp: new Date().toISOString(),
    contracts: {
      MockUSDC: usdcAddress,
      TerraSentinelRiskLedger: ledgerAddress,
      DisasterBond: bondAddress,
      CarbonFloodCredit: cfmcAddress
    },
    explorer: `https://amoy.polygonscan.com/address/${ledgerAddress}`
  };

  const deploymentsDir = path.join(__dirname, "../deployments");
  if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir, { recursive: true });
  }

  const outPath = path.join(deploymentsDir, `${network.name}.json`);
  fs.writeFileSync(outPath, JSON.stringify(deploymentRecord, null, 2));
  console.log(`\n✅ Phase 14 Smart Contracts deployed and saved to: ${outPath}`);
}

main().catch((error) => {
  console.error("Phase 14 Deployment Error:", error);
  process.exitCode = 1;
});
