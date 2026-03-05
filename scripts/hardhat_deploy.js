/**
 * Hardhat deploy script for CryptoArena v1.2 contracts.
 * Run: npx hardhat run scripts/hardhat_deploy.js --network base-sepolia
 */

const { ethers, network } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const [deployer] = await ethers.getSigners();
  const balance = await ethers.provider.getBalance(deployer.address);

  console.log("\n=====================================");
  console.log("  CryptoArena v1.2 Contract Deploy");
  console.log("=====================================");
  console.log(`Network  : ${network.name}`);
  console.log(`Deployer : ${deployer.address}`);
  console.log(`Balance  : ${ethers.formatEther(balance)} ETH\n`);

  const addresses = {};

  // --- KarmaToken ---
  console.log("Deploying KarmaToken...");
  const KarmaToken = await ethers.getContractFactory("KarmaToken");
  const karma = await KarmaToken.deploy();
  await karma.waitForDeployment();
  addresses.karmaToken = await karma.getAddress();
  console.log(`  ✅ KarmaToken: ${addresses.karmaToken}`);

  // --- AgentNFT ---
  console.log("Deploying AgentNFT...");
  const AgentNFT = await ethers.getContractFactory("AgentNFT");
  const agentNft = await AgentNFT.deploy();
  await agentNft.waitForDeployment();
  addresses.agentNft = await agentNft.getAddress();
  console.log(`  ✅ AgentNFT: ${addresses.agentNft}`);

  // --- ArenaLeaderboard ---
  console.log("Deploying ArenaLeaderboard...");
  const Leaderboard = await ethers.getContractFactory("ArenaLeaderboard");
  const leaderboard = await Leaderboard.deploy();
  await leaderboard.waitForDeployment();
  addresses.leaderboard = await leaderboard.getAddress();
  console.log(`  ✅ ArenaLeaderboard: ${addresses.leaderboard}`);

  // Grant KarmaToken minter role to deployer (arena wallet)
  await karma.addMinter(deployer.address);
  console.log(`  ✅ Minter role granted to ${deployer.address}`);

  // Save addresses
  const config = {
    ...addresses,
    network: network.name,
    chainId: network.config.chainId,
    deployer: deployer.address,
    deployedAt: new Date().toISOString(),
  };

  const configPath = path.join(__dirname, "../config/contracts.json");
  fs.mkdirSync(path.dirname(configPath), { recursive: true });
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2));

  console.log(`\n📄 Addresses saved to config/contracts.json`);
  console.log("\n🎉 Deployment complete!");
  console.log("\nNext step — verify contracts:");
  console.log(`  npx hardhat run scripts/hardhat_verify.js --network ${network.name}`);
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
