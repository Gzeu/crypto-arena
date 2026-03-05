// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ArenaLeaderboard
 * @notice On-chain leaderboard for CryptoArena (Base L2)
 * @dev Records agent portfolios, PnL snapshots, and karma scores
 */
contract ArenaLeaderboard is Ownable {
    struct AgentScore {
        string agentId;
        string name;
        int256 pnlUsdc;      // 6 decimals (USDC convention)
        uint256 karmaScore;  // narrative + performance composite
        uint256 lastUpdate;
    }

    mapping(string => AgentScore) public scores;
    string[] public agentIds;
    uint256 public seasonId;
    uint256 public seasonStartTime;

    event ScoreUpdated(string indexed agentId, int256 pnl, uint256 karma);
    event SeasonStarted(uint256 indexed seasonId, uint256 startTime);

    constructor() {
        seasonId = 1;
        seasonStartTime = block.timestamp;
    }

    function updateScore(
        string calldata agentId,
        string calldata name,
        int256 pnlUsdc,
        uint256 karmaScore
    ) external onlyOwner {
        if (scores[agentId].lastUpdate == 0) {
            agentIds.push(agentId);
        }
        scores[agentId] = AgentScore({
            agentId: agentId,
            name: name,
            pnlUsdc: pnlUsdc,
            karmaScore: karmaScore,
            lastUpdate: block.timestamp
        });
        emit ScoreUpdated(agentId, pnlUsdc, karmaScore);
    }

    function startNewSeason() external onlyOwner {
        seasonId++;
        seasonStartTime = block.timestamp;
        // Reset all scores
        for (uint256 i = 0; i < agentIds.length; i++) {
            string memory id = agentIds[i];
            scores[id].pnlUsdc = 0;
            scores[id].karmaScore = 0;
            scores[id].lastUpdate = block.timestamp;
        }
        emit SeasonStarted(seasonId, seasonStartTime);
    }

    function getLeaderboard() external view returns (AgentScore[] memory) {
        AgentScore[] memory leaderboard = new AgentScore[](agentIds.length);
        for (uint256 i = 0; i < agentIds.length; i++) {
            leaderboard[i] = scores[agentIds[i]];
        }
        return leaderboard;
    }

    function getTopN(uint256 n) external view returns (AgentScore[] memory) {
        require(n > 0 && n <= agentIds.length, "Invalid n");
        AgentScore[] memory all = new AgentScore[](agentIds.length);
        for (uint256 i = 0; i < agentIds.length; i++) {
            all[i] = scores[agentIds[i]];
        }
        // Bubble sort top N by karma (simple for MVP)
        for (uint256 i = 0; i < n; i++) {
            for (uint256 j = i + 1; j < agentIds.length; j++) {
                if (all[j].karmaScore > all[i].karmaScore) {
                    AgentScore memory temp = all[i];
                    all[i] = all[j];
                    all[j] = temp;
                }
            }
        }
        AgentScore[] memory topN = new AgentScore[](n);
        for (uint256 i = 0; i < n; i++) {
            topN[i] = all[i];
        }
        return topN;
    }
}
