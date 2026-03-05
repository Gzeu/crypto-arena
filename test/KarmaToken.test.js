const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("KarmaToken", function () {
  let karma, owner, minter, user;

  beforeEach(async () => {
    [owner, minter, user] = await ethers.getSigners();
    const KarmaToken = await ethers.getContractFactory("KarmaToken");
    karma = await KarmaToken.deploy();
  });

  it("has correct name and symbol", async () => {
    expect(await karma.name()).to.equal("CryptoArena Karma");
    expect(await karma.symbol()).to.equal("KARMA");
  });

  it("owner can add a minter", async () => {
    await karma.addMinter(minter.address);
    expect(await karma.minters(minter.address)).to.equal(true);
  });

  it("minter can mint tokens", async () => {
    await karma.addMinter(minter.address);
    const amount = ethers.parseEther("1000");
    await karma.connect(minter).mint(user.address, amount);
    expect(await karma.balanceOf(user.address)).to.equal(amount);
  });

  it("non-minter cannot mint", async () => {
    const amount = ethers.parseEther("100");
    await expect(
      karma.connect(user).mint(user.address, amount)
    ).to.be.revertedWith("Not authorised");
  });

  it("minter can burn tokens", async () => {
    await karma.addMinter(minter.address);
    const amount = ethers.parseEther("500");
    await karma.connect(minter).mint(user.address, amount);
    const burnAmt = ethers.parseEther("200");
    await karma.connect(minter).burn(user.address, burnAmt);
    expect(await karma.balanceOf(user.address)).to.equal(
      ethers.parseEther("300")
    );
  });

  it("owner can remove minter", async () => {
    await karma.addMinter(minter.address);
    await karma.removeMinter(minter.address);
    expect(await karma.minters(minter.address)).to.equal(false);
  });

  it("total supply increases on mint", async () => {
    await karma.addMinter(owner.address);
    const amount = ethers.parseEther("10000");
    await karma.mint(user.address, amount);
    expect(await karma.totalSupply()).to.equal(amount);
  });
});
