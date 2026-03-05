// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @title  KarmaToken (KARMA)
// @notice ERC-20 reward token for CryptoArena v1.1.
//         Authorised minters can mint/burn on behalf of the Arena.

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract KarmaToken is ERC20, Ownable {

    mapping(address => bool) public minters;

    event MinterAdded(address indexed minter);
    event MinterRemoved(address indexed minter);

    constructor() ERC20("CryptoArena Karma", "KARMA") Ownable(msg.sender) {}

    modifier onlyMinter() {
        require(minters[msg.sender] || msg.sender == owner(), "Not authorised");
        _;
    }

    function addMinter(address minter) external onlyOwner {
        minters[minter] = true;
        emit MinterAdded(minter);
    }

    function removeMinter(address minter) external onlyOwner {
        minters[minter] = false;
        emit MinterRemoved(minter);
    }

    function mint(address to, uint256 amount) external onlyMinter {
        _mint(to, amount);
    }

    function burn(address from, uint256 amount) external onlyMinter {
        _burn(from, amount);
    }
}
