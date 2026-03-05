// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @title  ArenaLeaderboard
// @notice On-chain leaderboard for CryptoArena v1.1
//         Stores agent stats and emits events for indexers.

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract ArenaLeaderboard is Ownable, ReentrancyGuard {

    struct AgentStats {
        address walletAddress;
        uint256 nftTokenId;
        int256  totalPnLCents;   // USDC-denominated, scaled x100
        uint256 winRateBP;       // basis points (10000 = 100%)
        uint256 karmaBalance;
        uint256 rank;
        uint256 lastUpdate;
    }

    mapping(string => AgentStats) public agents;
    string[] public agentIds;

    event AgentUpdated(
        string  indexed agentId,
        int256  pnl,
        uint256 rank,
        uint256 karma
    );

    constructor() Ownable(msg.sender) {}

    // ---------- Write ----------

    function updateAgent(
        string  calldata agentId,
        address walletAddress,
        uint256 nftTokenId,
        int256  totalPnLCents,
        uint256 winRateBP,
        uint256 karmaBalance,
        uint256 rank
    ) external onlyOwner {
        require(walletAddress != address(0), "Invalid wallet");
        if (agents[agentId].walletAddress == address(0)) {
            agentIds.push(agentId);
        }
        agents[agentId] = AgentStats({
            walletAddress : walletAddress,
            nftTokenId    : nftTokenId,
            totalPnLCents : totalPnLCents,
            winRateBP     : winRateBP,
            karmaBalance  : karmaBalance,
            rank          : rank,
            lastUpdate    : block.timestamp
        });
        emit AgentUpdated(agentId, totalPnLCents, rank, karmaBalance);
    }

    // ---------- Read ----------

    function getAgent(string calldata agentId)
        external view
        returns (AgentStats memory)
    {
        return agents[agentId];
    }

    function agentCount() external view returns (uint256) {
        return agentIds.length;
    }

    function getTopN(uint256 n)
        external view
        returns (string[] memory ids, AgentStats[] memory stats)
    {
        uint256 len = n < agentIds.length ? n : agentIds.length;
        ids   = new string[](len);
        stats = new AgentStats[](len);
        for (uint256 i; i < len; ++i) {
            ids[i]   = agentIds[i];
            stats[i] = agents[agentIds[i]];
        }
    }
}
