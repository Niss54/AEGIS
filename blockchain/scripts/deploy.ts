import { ethers } from "hardhat";
import * as fs from "fs";
import * as path from "path";

async function main() {
  const [deployer] = await ethers.getSigners();
  const network = await ethers.provider.getNetwork();

  console.log("┌─────────────────────────────────────────┐");
  console.log("│  AEGIS-CHAIN v2.0 — Contract Deployment  │");
  console.log("└─────────────────────────────────────────┘");
  console.log(`Network: ${network.name} (chainId: ${network.chainId})`);
  console.log(`Deployer: ${deployer.address}`);

  // Deploy Mock USDC (for local or testnet demo)
  console.log("1. Deploying Mock USDC...");
  const MockUSDC = await ethers.getContractFactory("MockERC20");
  const usdc = await MockUSDC.deploy("USD Coin", "USDC", 6);
  await usdc.waitForDeployment();
  const usdcAddress = await usdc.getAddress();
  console.log(`   ✅ Mock USDC deployed at: ${usdcAddress}`);

  // Deploy AEGISRiskLedger
  console.log("2. Deploying AEGISRiskLedger...");
  const BACKEND_WALLET = process.env.AEGIS_BACKEND_WALLET || deployer.address;
  const AEGISRiskLedger = await ethers.getContractFactory("AEGISRiskLedger");
  const ledger = await AEGISRiskLedger.deploy(BACKEND_WALLET);
  await ledger.waitForDeployment();
  const ledgerAddress = await ledger.getAddress();
  console.log(`   ✅ AEGISRiskLedger deployed at: ${ledgerAddress}`);

  // Deploy DisasterBond
  console.log("3. Deploying DisasterBond...");
  const DisasterBond = await ethers.getContractFactory("DisasterBond");
  const bond = await DisasterBond.deploy(usdcAddress, ledgerAddress, BACKEND_WALLET);
  await bond.waitForDeployment();
  const bondAddress = await bond.getAddress();
  console.log(`   ✅ DisasterBond deployed at: ${bondAddress}`);

  // Deploy CarbonFloodCredit
  console.log("4. Deploying CarbonFloodCredit (CFMC Token)...");
  const CarbonFloodCredit = await ethers.getContractFactory("CarbonFloodCredit");
  const cfmc = await CarbonFloodCredit.deploy(BACKEND_WALLET);
  await cfmc.waitForDeployment();
  const cfmcAddress = await cfmc.getAddress();
  console.log(`   ✅ CarbonFloodCredit (CFMC) deployed at: ${cfmcAddress}`);

  const deployments = {
    network: network.name,
    chainId: Number(network.chainId),
    deployer: deployer.address,
    backendWallet: BACKEND_WALLET,
    timestamp: new Date().toISOString(),
    contracts: {
      MockUSDC: usdcAddress,
      AEGISRiskLedger: ledgerAddress,
      DisasterBond: bondAddress,
      CarbonFloodCredit: cfmcAddress,
    },
    explorer: `https://amoy.polygonscan.com/address/${ledgerAddress}`,
  };

  const deploymentsDir = path.join(__dirname, "../deployments");
  if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir, { recursive: true });
  }

  const outPath = path.join(deploymentsDir, `${network.name}.json`);
  fs.writeFileSync(outPath, JSON.stringify(deployments, null, 2));
  console.log(`\n✅ Deployments saved to ${outPath}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
