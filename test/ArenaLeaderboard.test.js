const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("ArenaLeaderboard", function () {
  let lb, owner, agent1Wallet, agent2Wallet;

  beforeEach(async () => {
    [owner, agent1Wallet, agent2Wallet] = await ethers.getSigners();
    const Leaderboard = await ethers.getContractFactory("ArenaLeaderboard");
    lb = await Leaderboard.deploy();
  });

  it("owner can add an agent", async () => {
    await lb.updateAgent(
      "A1", agent1Wallet.address, 1, 1050, 6000, 500, 1
    );
    const stats = await lb.getAgent("A1");
    expect(stats.walletAddress).to.equal(agent1Wallet.address);
    expect(stats.rank).to.equal(1n);
    expect(stats.karmaBalance).to.equal(500n);
  });

  it("tracks agent count correctly", async () => {
    await lb.updateAgent("A1", agent1Wallet.address, 1, 1050, 6000, 500, 1);
    await lb.updateAgent("A2", agent2Wallet.address, 2, -200, 4000, 100, 2);
    expect(await lb.agentCount()).to.equal(2n);
  });

  it("emits AgentUpdated event", async () => {
    await expect(
      lb.updateAgent("A3", agent1Wallet.address, 3, 300, 7000, 750, 1)
    )
      .to.emit(lb, "AgentUpdated")
      .withArgs("A3", 300n, 1n, 750n);
  });

  it("non-owner cannot update", async () => {
    await expect(
      lb.connect(agent1Wallet).updateAgent(
        "A1", agent1Wallet.address, 1, 100, 5000, 500, 1
      )
    ).to.be.revertedWithCustomError(lb, "OwnableUnauthorizedAccount");
  });

  it("getTopN returns correct entries", async () => {
    await lb.updateAgent("A1", agent1Wallet.address, 1, 800, 7000, 1000, 1);
    await lb.updateAgent("A2", agent2Wallet.address, 2, 200, 4500, 300, 2);
    const [ids, stats] = await lb.getTopN(2);
    expect(ids[0]).to.equal("A1");
    expect(ids[1]).to.equal("A2");
    expect(stats[0].karmaBalance).to.equal(1000n);
  });

  it("updates existing agent without duplicating", async () => {
    await lb.updateAgent("A1", agent1Wallet.address, 1, 100, 5000, 100, 2);
    await lb.updateAgent("A1", agent1Wallet.address, 1, 500, 6000, 800, 1);
    expect(await lb.agentCount()).to.equal(1n);
    const stats = await lb.getAgent("A1");
    expect(stats.karmaBalance).to.equal(800n);
  });
});
