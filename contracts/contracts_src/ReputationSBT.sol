// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ReputationSBT
 * @dev Soulbound Token (non-transferable NFT) for tutor reputation
 * Tutors earn these badges for completing tutoring sessions
 * Cannot be transferred - they represent portable, verifiable reputation
 */
contract ReputationSBT is ERC721, Ownable {

    // ============ Structs ============

    struct Badge {
        uint256 tokenId;
        address tutor;
        uint256 sessionId;
        string badgeType;       // e.g., "essay_feedback", "speaking_practice"
        uint256 mintedAt;
        string metadataURI;
    }

    // ============ State Variables ============

    uint256 public nextTokenId = 1;
    address public escrowContract;

    mapping(uint256 => Badge) public badges;
    mapping(address => uint256[]) public tutorBadges;
    mapping(address => mapping(string => uint256)) public tutorBadgeCount; // tutor => badgeType => count

    // Badge type metadata
    mapping(string => string) public badgeTypeMetadata;

    // ============ Events ============

    event BadgeMinted(uint256 indexed tokenId, address indexed tutor, uint256 sessionId, string badgeType);
    event BadgeTypeAdded(string badgeType, string metadataURI);

    // ============ Constructor ============

    constructor() ERC721("EduLearn Tutor Reputation", "EDUREP") {
        // Initialize default badge types
        badgeTypeMetadata["essay_feedback"] = "ipfs://QmEssayFeedback";
        badgeTypeMetadata["speaking_practice"] = "ipfs://QmSpeakingPractice";
        badgeTypeMetadata["reading_tutor"] = "ipfs://QmReadingTutor";
        badgeTypeMetadata["writing_coach"] = "ipfs://QmWritingCoach";
    }

    // ============ Modifiers ============

    modifier onlyEscrow() {
        require(msg.sender == escrowContract, "Only escrow contract");
        _;
    }

    // ============ Main Functions ============

    /**
     * @dev Mint a reputation badge (called by escrow contract)
     * @param _tutor Address of the tutor
     * @param _sessionId Session ID from escrow
     */
    function mintReputation(address _tutor, uint256 _sessionId) external onlyEscrow {
        require(_tutor != address(0), "Invalid tutor address");

        uint256 tokenId = nextTokenId++;
        string memory badgeType = "essay_feedback"; // Default type for MVP

        // Mint the SBT
        _safeMint(_tutor, tokenId);

        // Store badge data
        badges[tokenId] = Badge({
            tokenId: tokenId,
            tutor: _tutor,
            sessionId: _sessionId,
            badgeType: badgeType,
            mintedAt: block.timestamp,
            metadataURI: badgeTypeMetadata[badgeType]
        });

        // Update tutor's badge collection
        tutorBadges[_tutor].push(tokenId);
        tutorBadgeCount[_tutor][badgeType]++;

        emit BadgeMinted(tokenId, _tutor, _sessionId, badgeType);
    }

    /**
     * @dev Mint a reputation badge with specific type (owner only)
     * @param _tutor Address of the tutor
     * @param _sessionId Session ID
     * @param _badgeType Type of badge
     */
    function mintReputationWithType(
        address _tutor,
        uint256 _sessionId,
        string memory _badgeType
    ) external onlyOwner {
        require(_tutor != address(0), "Invalid tutor address");
        require(bytes(badgeTypeMetadata[_badgeType]).length > 0, "Invalid badge type");

        uint256 tokenId = nextTokenId++;

        _safeMint(_tutor, tokenId);

        badges[tokenId] = Badge({
            tokenId: tokenId,
            tutor: _tutor,
            sessionId: _sessionId,
            badgeType: _badgeType,
            mintedAt: block.timestamp,
            metadataURI: badgeTypeMetadata[_badgeType]
        });

        tutorBadges[_tutor].push(tokenId);
        tutorBadgeCount[_tutor][_badgeType]++;

        emit BadgeMinted(tokenId, _tutor, _sessionId, _badgeType);
    }

    // ============ Soulbound Functions (Non-transferable) ============

    /**
     * @dev Override transfer functions to make tokens non-transferable
     */
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 tokenId,
        uint256 batchSize
    ) internal virtual override {
        require(from == address(0) || to == address(0), "Soulbound: Transfer not allowed");
        super._beforeTokenTransfer(from, to, tokenId, batchSize);
    }

    /**
     * @dev Explicitly disable approvals for soulbound tokens
     */
    function approve(address /*to*/, uint256 /*tokenId*/) public virtual override {
        revert("Soulbound: Approvals not allowed");
    }

    /**
     * @dev Explicitly disable operator approvals
     */
    function setApprovalForAll(address /*operator*/, bool /*approved*/) public virtual override {
        revert("Soulbound: Approvals not allowed");
    }

    // ============ View Functions ============

    /**
     * @dev Get all badges for a tutor
     */
    function getTutorBadges(address _tutor) external view returns (uint256[] memory) {
        return tutorBadges[_tutor];
    }

    /**
     * @dev Get badge count by type for a tutor
     */
    function getTutorBadgeCount(address _tutor, string memory _badgeType) external view returns (uint256) {
        return tutorBadgeCount[_tutor][_badgeType];
    }

    /**
     * @dev Get total badges for a tutor
     */
    function getTotalBadges(address _tutor) external view returns (uint256) {
        return tutorBadges[_tutor].length;
    }

    /**
     * @dev Get badge details
     */
    function getBadge(uint256 _tokenId) external view returns (Badge memory) {
        require(_exists(_tokenId), "Badge does not exist");
        return badges[_tokenId];
    }

    /**
     * @dev Get tutor reputation summary
     */
    function getTutorReputation(address _tutor) external view returns (
        uint256 totalBadges,
        uint256 essayFeedback,
        uint256 speakingPractice,
        uint256 readingTutor,
        uint256 writingCoach
    ) {
        return (
            tutorBadges[_tutor].length,
            tutorBadgeCount[_tutor]["essay_feedback"],
            tutorBadgeCount[_tutor]["speaking_practice"],
            tutorBadgeCount[_tutor]["reading_tutor"],
            tutorBadgeCount[_tutor]["writing_coach"]
        );
    }

    /**
     * @dev Override tokenURI to return badge-specific metadata
     */
    function tokenURI(uint256 _tokenId) public view virtual override returns (string memory) {
        require(_exists(_tokenId), "Token does not exist");
        return badges[_tokenId].metadataURI;
    }

    // ============ Admin Functions ============

    /**
     * @dev Set the escrow contract address
     */
    function setEscrowContract(address _escrow) external onlyOwner {
        require(_escrow != address(0), "Invalid address");
        escrowContract = _escrow;
    }

    /**
     * @dev Add or update badge type metadata
     */
    function setBadgeTypeMetadata(string memory _badgeType, string memory _metadataURI) external onlyOwner {
        require(bytes(_badgeType).length > 0, "Invalid badge type");
        require(bytes(_metadataURI).length > 0, "Invalid metadata URI");

        badgeTypeMetadata[_badgeType] = _metadataURI;

        emit BadgeTypeAdded(_badgeType, _metadataURI);
    }

    /**
     * @dev Burn a badge (owner only, in case of fraud)
     */
    function burnBadge(uint256 _tokenId) external onlyOwner {
        require(_exists(_tokenId), "Badge does not exist");

        Badge memory badge = badges[_tokenId];

        // Update counts
        tutorBadgeCount[badge.tutor][badge.badgeType]--;

        // Remove from tutor's badge array (note: leaves a gap, but maintains other indices)
        uint256[] storage tutorBadgeArray = tutorBadges[badge.tutor];
        for (uint256 i = 0; i < tutorBadgeArray.length; i++) {
            if (tutorBadgeArray[i] == _tokenId) {
                tutorBadgeArray[i] = tutorBadgeArray[tutorBadgeArray.length - 1];
                tutorBadgeArray.pop();
                break;
            }
        }

        // Delete badge data
        delete badges[_tokenId];

        // Burn the token
        _burn(_tokenId);
    }

    /**
     * @dev Check if token exists (helper for external calls)
     */
    function exists(uint256 _tokenId) external view returns (bool) {
        return _exists(_tokenId);
    }
}
