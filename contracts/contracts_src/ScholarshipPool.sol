// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title ScholarshipPool
 * @dev Quadratic funding-based scholarship pool for learners with verifiable improvement
 * Donors contribute to pool, learners receive rewards based on improvement attestations.
 * Uses quadratic funding to favor broad community support.
 */
contract ScholarshipPool is Ownable, ReentrancyGuard, Pausable {

    // ============ Structs ============

    struct Round {
        uint256 id;
        uint256 startTime;
        uint256 endTime;
        uint256 matchingPool;       // Platform matching funds
        uint256 totalDonations;     // Total community donations
        uint256 totalDistributed;   // Total rewards distributed
        bool finalized;
        uint256 learnerCount;       // Number of eligible learners
    }

    struct Donation {
        address donor;
        uint256 roundId;
        uint256 amount;
        uint256 timestamp;
    }

    struct ImprovementClaim {
        uint256 id;
        address learner;
        uint256 roundId;
        string metricType;          // e.g., "reading_score", "writing_score"
        uint256 beforeScore;
        uint256 afterScore;
        uint256 improvementPercent;
        uint256 timeframe;          // Days of improvement period
        bool verified;
        bool rewarded;
        uint256 rewardAmount;
        uint256 claimedAt;
    }

    struct LearnerStats {
        uint256 totalRewards;
        uint256 claimsCount;
        uint256 averageImprovement;
        uint256 donationsReceived;  // For QF calculation
    }

    // ============ State Variables ============

    uint256 public currentRoundId = 0;
    uint256 public nextClaimId = 1;
    address public attestationAuthority;

    // Quadratic Funding parameters
    uint256 public constant QF_MULTIPLIER = 100;  // Basis points for matching
    uint256 public minImprovementPercent = 10;    // Minimum 10% improvement required

    mapping(uint256 => Round) public rounds;
    mapping(uint256 => Donation[]) public roundDonations;
    mapping(uint256 => ImprovementClaim) public claims;
    mapping(uint256 => uint256[]) public roundClaims;  // roundId => claimIds[]
    mapping(address => LearnerStats) public learnerStats;
    mapping(address => mapping(uint256 => uint256)) public learnerRoundDonations;  // learner => roundId => donation count
    mapping(uint256 => address[]) public roundLearners;  // roundId => learner addresses

    // Donor tracking
    mapping(address => uint256) public totalDonatedByDonor;
    mapping(address => uint256[]) public donorDonations;  // donor => donation indices

    // ============ Events ============

    event RoundCreated(uint256 indexed roundId, uint256 startTime, uint256 endTime, uint256 matchingPool);
    event DonationMade(uint256 indexed roundId, address indexed donor, uint256 amount);
    event ImprovementClaimed(uint256 indexed claimId, address indexed learner, uint256 roundId, uint256 improvementPercent);
    event ClaimVerified(uint256 indexed claimId, address indexed learner, bool verified);
    event RewardDistributed(uint256 indexed claimId, address indexed learner, uint256 amount);
    event RoundFinalized(uint256 indexed roundId, uint256 totalDistributed);

    // ============ Constructor ============

    constructor(address _attestationAuthority) {
        require(_attestationAuthority != address(0), "Invalid attestation authority");
        attestationAuthority = _attestationAuthority;
    }

    // ============ Modifiers ============

    modifier onlyAttestationAuthority() {
        require(msg.sender == attestationAuthority, "Not attestation authority");
        _;
    }

    modifier roundActive(uint256 _roundId) {
        require(_roundId > 0 && _roundId <= currentRoundId, "Invalid round");
        require(block.timestamp >= rounds[_roundId].startTime, "Round not started");
        require(block.timestamp <= rounds[_roundId].endTime, "Round ended");
        require(!rounds[_roundId].finalized, "Round finalized");
        _;
    }

    // ============ Main Functions ============

    /**
     * @dev Create a new scholarship round
     * @param _duration Duration in seconds
     * @param _matchingPool Matching pool amount
     */
    function createRound(uint256 _duration, uint256 _matchingPool) external payable onlyOwner {
        require(_duration > 0, "Invalid duration");
        require(msg.value >= _matchingPool, "Insufficient matching pool");

        currentRoundId++;
        uint256 startTime = block.timestamp;
        uint256 endTime = startTime + _duration;

        rounds[currentRoundId] = Round({
            id: currentRoundId,
            startTime: startTime,
            endTime: endTime,
            matchingPool: _matchingPool,
            totalDonations: 0,
            totalDistributed: 0,
            finalized: false,
            learnerCount: 0
        });

        emit RoundCreated(currentRoundId, startTime, endTime, _matchingPool);
    }

    /**
     * @dev Donate to current round
     */
    function donate(uint256 _roundId) external payable roundActive(_roundId) nonReentrant {
        require(msg.value > 0, "Donation must be > 0");

        Round storage round = rounds[_roundId];
        round.totalDonations += msg.value;

        Donation memory donation = Donation({
            donor: msg.sender,
            roundId: _roundId,
            amount: msg.value,
            timestamp: block.timestamp
        });

        roundDonations[_roundId].push(donation);
        totalDonatedByDonor[msg.sender] += msg.value;
        donorDonations[msg.sender].push(roundDonations[_roundId].length - 1);

        emit DonationMade(_roundId, msg.sender, msg.value);
    }

    /**
     * @dev Learner claims improvement for reward eligibility
     * @param _roundId Round ID
     * @param _metricType Type of improvement (reading_score, writing_score, etc.)
     * @param _beforeScore Score before improvement period
     * @param _afterScore Score after improvement period
     * @param _timeframe Days of improvement period
     */
    function claimImprovement(
        uint256 _roundId,
        string memory _metricType,
        uint256 _beforeScore,
        uint256 _afterScore,
        uint256 _timeframe
    ) external roundActive(_roundId) {
        require(_beforeScore > 0, "Before score must be > 0");
        require(_afterScore > _beforeScore, "No improvement");
        require(_timeframe >= 7, "Minimum 7 days required");

        uint256 improvementPercent = ((_afterScore - _beforeScore) * 100) / _beforeScore;
        require(improvementPercent >= minImprovementPercent, "Insufficient improvement");

        uint256 claimId = nextClaimId++;

        claims[claimId] = ImprovementClaim({
            id: claimId,
            learner: msg.sender,
            roundId: _roundId,
            metricType: _metricType,
            beforeScore: _beforeScore,
            afterScore: _afterScore,
            improvementPercent: improvementPercent,
            timeframe: _timeframe,
            verified: false,
            rewarded: false,
            rewardAmount: 0,
            claimedAt: block.timestamp
        });

        roundClaims[_roundId].push(claimId);

        // Track learner for QF calculation
        if (learnerRoundDonations[msg.sender][_roundId] == 0) {
            roundLearners[_roundId].push(msg.sender);
            rounds[_roundId].learnerCount++;
        }
        learnerRoundDonations[msg.sender][_roundId]++;

        emit ImprovementClaimed(claimId, msg.sender, _roundId, improvementPercent);
    }

    /**
     * @dev Platform verifies improvement claim with attestation
     * @param _claimId Claim ID
     * @param _signature Platform attestation signature
     */
    function verifyImprovement(
        uint256 _claimId,
        bytes memory _signature
    ) external onlyAttestationAuthority {
        ImprovementClaim storage claim = claims[_claimId];
        require(!claim.verified, "Already verified");
        require(_signature.length > 0, "Invalid signature");

        claim.verified = true;

        // Update learner stats
        learnerStats[claim.learner].claimsCount++;
        learnerStats[claim.learner].averageImprovement =
            (learnerStats[claim.learner].averageImprovement * (learnerStats[claim.learner].claimsCount - 1) + claim.improvementPercent) /
            learnerStats[claim.learner].claimsCount;

        emit ClaimVerified(_claimId, claim.learner, true);
    }

    /**
     * @dev Finalize round and calculate QF rewards
     * @param _roundId Round ID to finalize
     */
    function finalizeRound(uint256 _roundId) external onlyOwner nonReentrant {
        Round storage round = rounds[_roundId];
        require(block.timestamp > round.endTime, "Round not ended");
        require(!round.finalized, "Already finalized");

        uint256[] memory claimIds = roundClaims[_roundId];
        require(claimIds.length > 0, "No claims");

        // Calculate QF allocations
        uint256 totalQFScore = 0;
        uint256[] memory qfScores = new uint256[](claimIds.length);

        // Calculate individual QF scores (simplified quadratic funding)
        for (uint256 i = 0; i < claimIds.length; i++) {
            ImprovementClaim storage claim = claims[claimIds[i]];
            if (claim.verified && !claim.rewarded) {
                // QF score = sqrt(donations) * improvement weight
                uint256 donationCount = learnerRoundDonations[claim.learner][_roundId];
                uint256 qfScore = sqrt(donationCount) * claim.improvementPercent;
                qfScores[i] = qfScore;
                totalQFScore += qfScore;
            }
        }

        // Distribute rewards based on QF scores
        uint256 availableFunds = round.matchingPool + round.totalDonations;

        for (uint256 i = 0; i < claimIds.length; i++) {
            ImprovementClaim storage claim = claims[claimIds[i]];
            if (claim.verified && !claim.rewarded && qfScores[i] > 0) {
                uint256 rewardAmount = (availableFunds * qfScores[i]) / totalQFScore;

                if (rewardAmount > 0) {
                    claim.rewarded = true;
                    claim.rewardAmount = rewardAmount;
                    round.totalDistributed += rewardAmount;

                    learnerStats[claim.learner].totalRewards += rewardAmount;
                    learnerStats[claim.learner].donationsReceived += rewardAmount;

                    // Transfer reward
                    (bool success, ) = payable(claim.learner).call{value: rewardAmount}("");
                    require(success, "Transfer failed");

                    emit RewardDistributed(claimIds[i], claim.learner, rewardAmount);
                }
            }
        }

        round.finalized = true;
        emit RoundFinalized(_roundId, round.totalDistributed);
    }

    // ============ View Functions ============

    function getCurrentRound() external view returns (Round memory) {
        return rounds[currentRoundId];
    }

    function getRound(uint256 _roundId) external view returns (Round memory) {
        return rounds[_roundId];
    }

    function getClaim(uint256 _claimId) external view returns (ImprovementClaim memory) {
        return claims[_claimId];
    }

    function getRoundClaims(uint256 _roundId) external view returns (uint256[] memory) {
        return roundClaims[_roundId];
    }

    function getRoundDonations(uint256 _roundId) external view returns (Donation[] memory) {
        return roundDonations[_roundId];
    }

    function getLearnerStats(address _learner) external view returns (LearnerStats memory) {
        return learnerStats[_learner];
    }

    function getRoundLearners(uint256 _roundId) external view returns (address[] memory) {
        return roundLearners[_roundId];
    }

    function getContractBalance() external view returns (uint256) {
        return address(this).balance;
    }

    // ============ Helper Functions ============

    /**
     * @dev Calculate square root (Babylonian method)
     */
    function sqrt(uint256 x) internal pure returns (uint256) {
        if (x == 0) return 0;
        uint256 z = (x + 1) / 2;
        uint256 y = x;
        while (z < y) {
            y = z;
            z = (x / z + z) / 2;
        }
        return y;
    }

    // ============ Admin Functions ============

    function setAttestationAuthority(address _authority) external onlyOwner {
        require(_authority != address(0), "Invalid address");
        attestationAuthority = _authority;
    }

    function setMinImprovementPercent(uint256 _percent) external onlyOwner {
        require(_percent > 0 && _percent <= 100, "Invalid percentage");
        minImprovementPercent = _percent;
    }

    function pause() external onlyOwner {
        _pause();
    }

    function unpause() external onlyOwner {
        _unpause();
    }

    // Emergency withdraw (only if paused and no active rounds)
    function emergencyWithdraw() external onlyOwner {
        require(paused(), "Not paused");
        if (currentRoundId > 0) {
            require(rounds[currentRoundId].finalized, "Active round exists");
        }

        (bool success, ) = payable(owner()).call{value: address(this).balance}("");
        require(success, "Withdrawal failed");
    }

    // Accept ETH
    receive() external payable {
        if (currentRoundId > 0 && block.timestamp <= rounds[currentRoundId].endTime) {
            donate(currentRoundId);
        }
    }
}
