const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("AgentNFT", function () {
  let nft, owner, holder1, holder2;

  beforeEach(async () => {
    [owner, holder1, holder2] = await ethers.getSigners();
    const AgentNFT = await ethers.getContractFactory("AgentNFT");
    nft = await AgentNFT.deploy();
  });

  it("has correct name and symbol", async () => {
    expect(await nft.name()).to.equal("CryptoArena Agent");
    expect(await nft.symbol()).to.equal("CAGENT");
  });

  it("owner can mint an agent NFT", async () => {
    await nft.mintAgent("A1", holder1.address, "ipfs://QmA1metadata");
    expect(await nft.totalMinted()).to.equal(1n);
    expect(await nft.ownerOf(1)).to.equal(holder1.address);
    expect(await nft.tokenURI(1)).to.equal("ipfs://QmA1metadata");
  });

  it("maps agentId <-> tokenId correctly", async () => {
    await nft.mintAgent("A2", holder1.address, "ipfs://QmA2");
    expect(await nft.agentTokenId("A2")).to.equal(1n);
    expect(await nft.tokenAgentId(1)).to.equal("A2");
  });

  it("cannot mint same agentId twice", async () => {
    await nft.mintAgent("A3", holder1.address, "ipfs://QmA3");
    await expect(
      nft.mintAgent("A3", holder2.address, "ipfs://QmA3v2")
    ).to.be.revertedWith("Agent already minted");
  });

  it("non-owner cannot mint", async () => {
    await expect(
      nft.connect(holder1).mintAgent("A4", holder2.address, "ipfs://QmA4")
    ).to.be.revertedWithCustomError(nft, "OwnableUnauthorizedAccount");
  });

  it("emits AgentMinted event", async () => {
    await expect(
      nft.mintAgent("A5", holder1.address, "ipfs://QmA5")
    )
      .to.emit(nft, "AgentMinted")
      .withArgs("A5", 1n, holder1.address);
  });
});
