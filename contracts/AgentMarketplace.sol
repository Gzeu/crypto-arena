// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title  AgentMarketplace
 * @notice Trustless marketplace for CryptoArena AI Agent NFTs.
 *         Sellers lock their AgentNFT into escrow; buyers pay in KARMA tokens.
 *         A configurable fee (default 2.5 %) goes to the Arena treasury.
 * @dev    Deployed on Base L2 alongside KarmaToken, ArenaLeaderboard, AgentNFT.
 */
contract AgentMarketplace is Ownable, ReentrancyGuard {
    IERC721 public immutable agentNFT;
    IERC20  public immutable karmaToken;
    address public treasury;
    uint256 public feeBps = 250; // 2.5 %

    struct Listing {
        address seller;
        uint256 priceKarma;
        bool    active;
    }

    /// @notice tokenId => Listing
    mapping(uint256 => Listing) public listings;

    // ------------------------------------------------------------------ //
    //  EVENTS                                                              //
    // ------------------------------------------------------------------ //

    event AgentListed(
        uint256 indexed tokenId,
        address indexed seller,
        uint256 priceKarma
    );
    event AgentSold(
        uint256 indexed tokenId,
        address indexed buyer,
        address indexed seller,
        uint256 priceKarma,
        uint256 fee
    );
    event AgentDelisted(uint256 indexed tokenId, address indexed seller);
    event FeeUpdated(uint256 newFeeBps);
    event TreasuryUpdated(address newTreasury);

    // ------------------------------------------------------------------ //
    //  CONSTRUCTOR                                                         //
    // ------------------------------------------------------------------ //

    constructor(
        address _agentNFT,
        address _karma,
        address _treasury
    ) Ownable(msg.sender) {
        require(_agentNFT  != address(0), "Zero agentNFT");
        require(_karma     != address(0), "Zero karma");
        require(_treasury  != address(0), "Zero treasury");
        agentNFT   = IERC721(_agentNFT);
        karmaToken = IERC20(_karma);
        treasury   = _treasury;
    }

    // ------------------------------------------------------------------ //
    //  SELLER ACTIONS                                                      //
    // ------------------------------------------------------------------ //

    /**
     * @notice List an agent NFT for sale. Transfers NFT into escrow.
     * @param tokenId    The AgentNFT token ID to sell.
     * @param priceKarma Price denominated in KARMA (18-decimal ERC-20).
     */
    function listAgent(uint256 tokenId, uint256 priceKarma) external nonReentrant {
        require(agentNFT.ownerOf(tokenId) == msg.sender, "Not owner");
        require(priceKarma > 0, "Price must be > 0");
        require(!listings[tokenId].active, "Already listed");

        agentNFT.transferFrom(msg.sender, address(this), tokenId);
        listings[tokenId] = Listing({
            seller:     msg.sender,
            priceKarma: priceKarma,
            active:     true
        });
        emit AgentListed(tokenId, msg.sender, priceKarma);
    }

    /**
     * @notice Delist an agent (seller only). Returns NFT to seller.
     */
    function delistAgent(uint256 tokenId) external nonReentrant {
        Listing storage l = listings[tokenId];
        require(l.active,              "Not listed");
        require(l.seller == msg.sender, "Not seller");

        l.active = false;
        agentNFT.transferFrom(address(this), msg.sender, tokenId);
        emit AgentDelisted(tokenId, msg.sender);
    }

    // ------------------------------------------------------------------ //
    //  BUYER ACTIONS                                                       //
    // ------------------------------------------------------------------ //

    /**
     * @notice Purchase a listed agent. Buyer must approve KARMA spend first.
     * @param tokenId The AgentNFT token ID to buy.
     */
    function buyAgent(uint256 tokenId) external nonReentrant {
        Listing storage l = listings[tokenId];
        require(l.active, "Not listed");

        uint256 fee          = (l.priceKarma * feeBps) / 10_000;
        uint256 sellerAmount = l.priceKarma - fee;
        address seller       = l.seller;

        l.active = false;

        // Payment: seller receives proceeds, treasury receives fee
        require(
            karmaToken.transferFrom(msg.sender, seller,   sellerAmount),
            "KARMA transfer to seller failed"
        );
        require(
            karmaToken.transferFrom(msg.sender, treasury, fee),
            "KARMA fee transfer failed"
        );

        // Transfer NFT from escrow to buyer
        agentNFT.transferFrom(address(this), msg.sender, tokenId);

        emit AgentSold(tokenId, msg.sender, seller, l.priceKarma, fee);
    }

    // ------------------------------------------------------------------ //
    //  ADMIN                                                               //
    // ------------------------------------------------------------------ //

    /// @notice Update marketplace fee. Max 10 %.
    function setFeeBps(uint256 _feeBps) external onlyOwner {
        require(_feeBps <= 1_000, "Max 10%");
        feeBps = _feeBps;
        emit FeeUpdated(_feeBps);
    }

    /// @notice Update treasury address.
    function setTreasury(address _treasury) external onlyOwner {
        require(_treasury != address(0), "Zero address");
        treasury = _treasury;
        emit TreasuryUpdated(_treasury);
    }

    // ------------------------------------------------------------------ //
    //  VIEW HELPERS                                                        //
    // ------------------------------------------------------------------ //

    function getListing(uint256 tokenId)
        external
        view
        returns (address seller, uint256 priceKarma, bool active)
    {
        Listing storage l = listings[tokenId];
        return (l.seller, l.priceKarma, l.active);
    }
}
