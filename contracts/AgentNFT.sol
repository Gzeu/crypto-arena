// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @title  AgentNFT
// @notice ERC-721 identity NFT for each CryptoArena agent.
//         One token per agent; metadata stored on IPFS.

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract AgentNFT is ERC721URIStorage, Ownable {

    uint256 private _nextTokenId;
    mapping(string => uint256) public agentTokenId;   // agentId => tokenId
    mapping(uint256 => string) public tokenAgentId;   // tokenId => agentId

    event AgentMinted(string indexed agentId, uint256 tokenId, address owner);

    constructor() ERC721("CryptoArena Agent", "CAGENT") Ownable(msg.sender) {}

    function mintAgent(
        string calldata agentId,
        address to,
        string calldata metadataURI
    ) external onlyOwner returns (uint256 tokenId) {
        require(agentTokenId[agentId] == 0, "Agent already minted");
        tokenId = ++_nextTokenId;
        agentTokenId[agentId] = tokenId;
        tokenAgentId[tokenId] = agentId;
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, metadataURI);
        emit AgentMinted(agentId, tokenId, to);
    }

    function totalMinted() external view returns (uint256) {
        return _nextTokenId;
    }
}
