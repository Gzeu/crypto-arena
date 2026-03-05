/**
 * Auto-verify all deployed contracts on BaseScan.
 * Requires BASESCAN_API_KEY in .env and config/contracts.json to exist.
 * Run: npx hardhat run scripts/hardhat_verify.js --network base-sepolia
 */

const { run } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function verify(address, constructorArguments = []) {
  try {
    await run("verify:verify", { address, constructorArguments });
    console.log(`  ✅ Verified: ${address}`);
  } catch (err) {
    if (err.message.includes("Already Verified")) {
      console.log(`  ℹ️  Already verified: ${address}`);
    } else {
      console.error(`  ❌ Failed: ${address} — ${err.message}`);
    }
  }
}

async function main() {
  const cfgPath = path.join(__dirname, "../config/contracts.json");
  if (!fs.existsSync(cfgPath)) {
    console.error("config/contracts.json not found. Deploy first.");
    process.exit(1);
  }
  const cfg = JSON.parse(fs.readFileSync(cfgPath, "utf8"));

  console.log("\n🔍 Verifying CryptoArena contracts on BaseScan...\n");
  if (cfg.karmaToken)  await verify(cfg.karmaToken);
  if (cfg.agentNft)    await verify(cfg.agentNft);
  if (cfg.leaderboard) await verify(cfg.leaderboard);
  console.log("\n✅ Verification complete.");
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
