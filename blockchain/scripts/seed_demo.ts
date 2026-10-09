import { ethers } from "hardhat";
import * as fs from "fs";
import * as path from "path";

async function main() {
  const [deployer] = await ethers.getSigners();
  const network = await ethers.provider.getNetwork();

  const depPath = path.join(__dirname, `../deployments/${network.name}.json`);
  if (!fs.existsSync(depPath)) {
    throw new Error(`Deployment file not found at ${depPath}. Run deploy.ts first.`);
  }

  const deployments = JSON.parse(fs.readFileSync(depPath, "utf-8"));
  const bondAddress = deployments.contracts.DisasterBond;
  const usdcAddress = deployments.contracts.MockUSDC;
  const ledgerAddress = deployments.contracts.AEGISRiskLedger;

  const bond = await ethers.getContractAt("DisasterBond", bondAddress);
  const usdc = await ethers.getContractAt("MockERC20", usdcAddress);
  const ledger = await ethers.getContractAt("AEGISRiskLedger", ledgerAddress);

  console.log("Seeding demo disaster bonds...");
  const DEMO_LOCATIONS = [
    { name: "Mumbai — Mithi River Basin", lat: 19072800, lon: 72879700 },
    { name: "Chennai — Adyar River Corridor", lat: 13082700, lon: 80270700 },
    { name: "Delhi — Yamuna Floodplain", lat: 28613900, lon: 77209100 },
  ];

  const DEMO_PAYOUT = ethers.parseUnits("50000", 6);
  await usdc.mint(deployer.address, DEMO_PAYOUT * 3n);
  await usdc.approve(bondAddress, DEMO_PAYOUT * 3n);

  for (const loc of DEMO_LOCATIONS) {
    const tx = await bond.createBond(
      loc.lat,
      loc.lon,
      deployer.address,
      DEMO_PAYOUT,
      6500, // 0.65 threshold
      2,    // 2 consecutive breaches
      loc.name
    );
    await tx.wait();
    console.log(`✅ Bond created for ${loc.name}`);
  }

  console.log("Seeding initial risk assessment on-chain...");
  await ledger.anchorRiskAssessment(
    19072800,
    72879700,
    7800,
    "bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi",
    "Mumbai — Mithi River Basin"
  );
  console.log("✅ Seed complete!");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
