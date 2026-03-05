const { expect } = require("chai");
const { ethers }  = require("hardhat");

/**
 * AgentMarketplace.sol — Contract Tests (v1.3)
 * 7 tests covering: list, buy, delist, fee, access control
 */
describe("AgentMarketplace", function () {
  let marketplace, agentNFT, karma;
  let owner, seller, buyer, treasury;
  const PRICE = ethers.parseEther("500"); // 500 KARMA
  const TOKEN_ID = 1;

  beforeEach(async () => {
    [owner, seller, buyer, treasury] = await ethers.getSigners();

    // Deploy mock KarmaToken (mintable ERC-20)
    const KarmaToken = await ethers.getContractFactory("KarmaToken");
    karma = await KarmaToken.deploy();

    // Deploy mock AgentNFT (mintable ERC-721)
    const AgentNFT = await ethers.getContractFactory("AgentNFT");
    agentNFT = await AgentNFT.deploy();

    // Deploy marketplace
    const Marketplace = await ethers.getContractFactory("AgentMarketplace");
    marketplace = await Marketplace.deploy(
      await agentNFT.getAddress(),
      await karma.getAddress(),
      treasury.address
    );

    // Mint NFT to seller
    await agentNFT.connect(owner).mintAgent("test-agent-1", seller.address, "ipfs://QmTest");

    // Approve marketplace to spend seller's NFT
    await agentNFT.connect(seller).approve(await marketplace.getAddress(), TOKEN_ID);

    // Mint KARMA to buyer and approve marketplace
    const buyerAmount = ethers.parseEther("1000");
    await karma.connect(owner).mint(buyer.address, buyerAmount);
    await karma.connect(buyer).approve(await marketplace.getAddress(), buyerAmount);
  });

  it("should list an agent NFT", async () => {
    await marketplace.connect(seller).listAgent(TOKEN_ID, PRICE);
    const [lSeller, lPrice, lActive] = await marketplace.getListing(TOKEN_ID);
    expect(lSeller).to.equal(seller.address);
    expect(lPrice).to.equal(PRICE);
    expect(lActive).to.be.true;
  });

  it("should emit AgentListed event", async () => {
    await expect(marketplace.connect(seller).listAgent(TOKEN_ID, PRICE))
      .to.emit(marketplace, "AgentListed")
      .withArgs(TOKEN_ID, seller.address, PRICE);
  });

  it("should buy an agent and transfer NFT + KARMA", async () => {
    await marketplace.connect(seller).listAgent(TOKEN_ID, PRICE);
    await marketplace.connect(buyer).buyAgent(TOKEN_ID);
    expect(await agentNFT.ownerOf(TOKEN_ID)).to.equal(buyer.address);
  });

  it("should split fee correctly (2.5%)", async () => {
    await marketplace.connect(seller).listAgent(TOKEN_ID, PRICE);
    const treasuryBefore = await karma.balanceOf(treasury.address);
    await marketplace.connect(buyer).buyAgent(TOKEN_ID);
    const treasuryAfter = await karma.balanceOf(treasury.address);
    const expectedFee = PRICE * 250n / 10000n; // 2.5%
    expect(treasuryAfter - treasuryBefore).to.equal(expectedFee);
  });

  it("should delist an agent and return NFT", async () => {
    await marketplace.connect(seller).listAgent(TOKEN_ID, PRICE);
    await marketplace.connect(seller).delistAgent(TOKEN_ID);
    expect(await agentNFT.ownerOf(TOKEN_ID)).to.equal(seller.address);
    const [, , lActive] = await marketplace.getListing(TOKEN_ID);
    expect(lActive).to.be.false;
  });

  it("should revert if non-seller tries to delist", async () => {
    await marketplace.connect(seller).listAgent(TOKEN_ID, PRICE);
    await expect(
      marketplace.connect(buyer).delistAgent(TOKEN_ID)
    ).to.be.revertedWith("Not seller");
  });

  it("should allow owner to update fee (max 10%)", async () => {
    await marketplace.connect(owner).setFeeBps(300); // 3%
    expect(await marketplace.feeBps()).to.equal(300);
    await expect(
      marketplace.connect(owner).setFeeBps(1001)
    ).to.be.revertedWith("Max 10%");
  });
});
