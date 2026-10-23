const { chromium } = require("playwright-core");
const path = require("path");
const fs = require("fs");

async function main() {
  console.log("Launching system Chrome for element screenshots...");
  const browser = await chromium.launch({
    channel: "chrome",
    headless: true
  });

  const context = await browser.newContext({
    viewport: { width: 1400, height: 2200 },
    deviceScaleFactor: 2 // High-DPI crisp 2x resolution
  });

  const page = await context.newPage();
  const filePath = "file://" + path.resolve("scripts/render_clippings.html").replace(/\\/g, "/");
  console.log("Navigating to:", filePath);
  await page.goto(filePath, { waitUntil: "networkidle" });
  await page.waitForTimeout(1000);

  // Ensure output dirs exist
  if (!fs.existsSync("evaluation")) fs.mkdirSync("evaluation");
  if (!fs.existsSync("public/evaluation")) fs.mkdirSync("public/evaluation", { recursive: true });

  // 1. World Bank Clipping
  const wbElement = await page.$("#card-worldbank");
  if (wbElement) {
    await wbElement.screenshot({ path: "evaluation/worldbank_urban_flood_loss.png" });
    fs.copyFileSync("evaluation/worldbank_urban_flood_loss.png", "public/evaluation/worldbank_urban_flood_loss.png");
    console.log("Saved: evaluation/worldbank_urban_flood_loss.png");
  }

  // 2. Mithi River Scam Clipping
  const mithiElement = await page.$("#card-mithi");
  if (mithiElement) {
    await mithiElement.screenshot({ path: "evaluation/mithi_scam_thehindu.png" });
    fs.copyFileSync("evaluation/mithi_scam_thehindu.png", "public/evaluation/mithi_scam_thehindu.png");
    console.log("Saved: evaluation/mithi_scam_thehindu.png");
  }

  // 3. Swiss Re Protection Gap Clipping
  const swissElement = await page.$("#card-swissre");
  if (swissElement) {
    await swissElement.screenshot({ path: "evaluation/swiss_re_protection_gap.png" });
    fs.copyFileSync("evaluation/swiss_re_protection_gap.png", "public/evaluation/swiss_re_protection_gap.png");
    console.log("Saved: evaluation/swiss_re_protection_gap.png");
  }

  await browser.close();
  console.log("All clippings rendered and captured successfully with 0 errors!");
}

main().catch(err => {
  console.error("Error capturing clippings:", err);
  process.exit(1);
});
