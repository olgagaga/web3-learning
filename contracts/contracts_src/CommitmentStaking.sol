// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title CommitmentStaking
 * @dev Smart contract for commitment-based staking with accountability pods
 * Users stake tokens to commit to learning streaks/goals. Backend signs attestations
 * for milestone completion. Successful commitments earn rewards, failed ones go to scholarship pool.
 */
contract CommitmentStaking is Ownable, ReentrancyGuard, Pausable {

    // ============ Structs ============

    struct Commitment {
        address user;
        uint256 stakeAmount;
        uint256 targetValue;        // e.g., 7 for 7-day streak
        uint256 currentProgress;    // Current progress toward target
        uint256 startTime;
        uint256 deadline;
        uint256 podId;              // 0 for individual, >0 for pod commitments
        bool isActive;
        bool isCompleted;
        bool isClaimed;
    }

    struct Pod {
        string name;
        uint256 stakeAmount;        // Required stake per member
        uint256 targetValue;
        uint256 deadline;
        address[] members;
        uint256 successfulMembers;
        uint256 failedMembers;
        bool isActive;
        bool isStarted;
    }

    // ============ State Variables ============

    // Commitment tracking
    mapping(uint256 => Commitment) public commitments;
    uint256 public commitmentCounter;

    // Pod tracking
    mapping(uint256 => Pod) public pods;
    uint256 public podCounter;
    mapping(address => uint256[]) public userCommitments;
    mapping(uint256 => mapping(address => bool)) public podMemberships;

    // Attestation authority (backend signer)
    address public attestationAuthority;
    mapping(bytes32 => bool) public usedAttestations;

    // Scholarship pool
    address public scholarshipPool;
    uint256 public totalScholarshipFunds;

    // Reward settings
    uint256 public rewardMultiplier = 110; // 110% = 10% bonus on success
    uint256 public constant BASIS_POINTS = 100;

    // ============ Events ============

    event CommitmentCreated(
        uint256 indexed commitmentId,
        address indexed user,
        uint256 stakeAmount,
        uint256 targetValue,
        uint256 deadline,
        uint256 podId
    );

    event CommitmentCompleted(
        uint256 indexed commitmentId,
        address indexed user,
        uint256 progress
    );

    event CommitmentClaimed(
        uint256 indexed commitmentId,
        address indexed user,
        uint256 rewardAmount
    );

    event CommitmentFailed(
        uint256 indexed commitmentId,
        address indexed user,
        uint256 penaltyAmount
    );

    event PodCreated(
        uint256 indexed podId,
        string name,
        uint256 stakeAmount,
        uint256 targetValue,
        uint256 deadline
    );

    event PodMemberJoined(
        uint256 indexed podId,
        address indexed member,
        uint256 commitmentId
    );

    event ScholarshipDistributed(
        address indexed recipient,
        uint256 amount
    );

    event ProgressUpdated(
        uint256 indexed commitmentId,
        uint256 progress
    );

    // ============ Constructor ============

    constructor(
        address _attestationAuthority,
        address _scholarshipPool
    ) {
        require(_attestationAuthority != address(0), "Invalid attestation authority");
        require(_scholarshipPool != address(0), "Invalid scholarship pool");

        attestationAuthority = _attestationAuthority;
        scholarshipPool = _scholarshipPool;
    }

    // ============ Commitment Functions ============

    /**
     * @dev Create a new individual commitment
     */
    function createCommitment(
        uint256 _targetValue,
        uint256 _durationDays
    ) external payable nonReentrant whenNotPaused returns (uint256) {
        require(msg.value > 0, "Stake amount must be greater than 0");
        require(_targetValue > 0, "Target value must be greater than 0");
        require(_durationDays > 0, "Duration must be greater than 0");
        require(msg.value >= 0.01 ether && msg.value <= 1 ether, "Stake must be between 0.01 and 1.0");

        uint256 commitmentId = commitmentCounter++;
        uint256 deadline = block.timestamp + (_durationDays * 1 days);

        commitments[commitmentId] = Commitment({
            user: msg.sender,
            stakeAmount: msg.value,
            targetValue: _targetValue,
            currentProgress: 0,
            startTime: block.timestamp,
            deadline: deadline,
            podId: 0,
            isActive: true,
            isCompleted: false,
            isClaimed: false
        });

        userCommitments[msg.sender].push(commitmentId);

        emit CommitmentCreated(
            commitmentId,
            msg.sender,
            msg.value,
            _targetValue,
            deadline,
            0
        );

        return commitmentId;
    }

    /**
     * @dev Update commitment progress with backend attestation
     */
    function updateProgress(
        uint256 _commitmentId,
        uint256 _progress,
        bytes32 _attestationHash,
        bytes memory _signature
    ) external nonReentrant {
        Commitment storage commitment = commitments[_commitmentId];

        require(commitment.isActive, "Commitment not active");
        require(!commitment.isCompleted, "Commitment already completed");
        require(block.timestamp <= commitment.deadline, "Commitment deadline passed");
        require(!usedAttestations[_attestationHash], "Attestation already used");
        require(_progress <= commitment.targetValue, "Progress cannot exceed target");

        // Verify attestation signature
        bytes32 messageHash = keccak256(abi.encodePacked(
            _commitmentId,
            commitment.user,
            _progress,
            _attestationHash
        ));

        bytes32 ethSignedMessageHash = getEthSignedMessageHash(messageHash);
        require(recoverSigner(ethSignedMessageHash, _signature) == attestationAuthority, "Invalid attestation");

        // Mark attestation as used
        usedAttestations[_attestationHash] = true;

        // Update progress
        commitment.currentProgress = _progress;

        // Check if commitment is completed
        if (_progress >= commitment.targetValue) {
            commitment.isCompleted = true;
            emit CommitmentCompleted(_commitmentId, commitment.user, _progress);

            // Update pod stats if part of a pod
            if (commitment.podId > 0) {
                pods[commitment.podId].successfulMembers++;
            }
        }

        emit ProgressUpdated(_commitmentId, _progress);
    }

    /**
     * @dev Claim rewards for completed commitment
     */
    function claimReward(uint256 _commitmentId) external nonReentrant {
        Commitment storage commitment = commitments[_commitmentId];

        require(msg.sender == commitment.user, "Not commitment owner");
        require(commitment.isCompleted, "Commitment not completed");
        require(!commitment.isClaimed, "Already claimed");
        require(commitment.isActive, "Commitment not active");

        commitment.isClaimed = true;
        commitment.isActive = false;

        // Calculate reward (stake + bonus)
        uint256 reward = (commitment.stakeAmount * rewardMultiplier) / BASIS_POINTS;

        // Transfer reward
        (bool success, ) = msg.sender.call{value: reward}("");
        require(success, "Reward transfer failed");

        emit CommitmentClaimed(_commitmentId, msg.sender, reward);
    }

    /**
     * @dev Mark commitment as failed and send stake to scholarship pool
     */
    function failCommitment(uint256 _commitmentId) external {
        Commitment storage commitment = commitments[_commitmentId];

        require(
            msg.sender == commitment.user || msg.sender == owner(),
            "Not authorized"
        );
        require(commitment.isActive, "Commitment not active");
        require(!commitment.isCompleted, "Commitment already completed");
        require(block.timestamp > commitment.deadline, "Deadline not passed");
        require(!commitment.isClaimed, "Already claimed");

        commitment.isActive = false;

        // Send stake to scholarship pool
        uint256 penalty = commitment.stakeAmount;
        totalScholarshipFunds += penalty;

        (bool success, ) = scholarshipPool.call{value: penalty}("");
        require(success, "Scholarship transfer failed");

        // Update pod stats if part of a pod
        if (commitment.podId > 0) {
            pods[commitment.podId].failedMembers++;
        }

        emit CommitmentFailed(_commitmentId, commitment.user, penalty);
    }

    // ============ Pod Functions ============

    /**
     * @dev Create a new accountability pod
     */
    function createPod(
        string memory _name,
        uint256 _stakeAmount,
        uint256 _targetValue,
        uint256 _durationDays
    ) external whenNotPaused returns (uint256) {
        require(_stakeAmount >= 0.01 ether && _stakeAmount <= 1 ether, "Invalid stake amount");
        require(_targetValue > 0, "Target value must be greater than 0");
        require(_durationDays > 0, "Duration must be greater than 0");

        uint256 podId = podCounter++;
        uint256 deadline = block.timestamp + (_durationDays * 1 days);

        pods[podId] = Pod({
            name: _name,
            stakeAmount: _stakeAmount,
            targetValue: _targetValue,
            deadline: deadline,
            members: new address[](0),
            successfulMembers: 0,
            failedMembers: 0,
            isActive: true,
            isStarted: false
        });

        emit PodCreated(podId, _name, _stakeAmount, _targetValue, deadline);

        return podId;
    }

    /**
     * @dev Join an accountability pod
     */
    function joinPod(uint256 _podId) external payable nonReentrant whenNotPaused returns (uint256) {
        Pod storage pod = pods[_podId];

        require(pod.isActive, "Pod not active");
        require(!pod.isStarted, "Pod already started");
        require(msg.value == pod.stakeAmount, "Incorrect stake amount");
        require(!podMemberships[_podId][msg.sender], "Already in pod");

        // Create commitment for pod member
        uint256 commitmentId = commitmentCounter++;

        commitments[commitmentId] = Commitment({
            user: msg.sender,
            stakeAmount: msg.value,
            targetValue: pod.targetValue,
            currentProgress: 0,
            startTime: block.timestamp,
            deadline: pod.deadline,
            podId: _podId,
            isActive: true,
            isCompleted: false,
            isClaimed: false
        });

        // Update pod
        pod.members.push(msg.sender);
        podMemberships[_podId][msg.sender] = true;
        userCommitments[msg.sender].push(commitmentId);

        emit PodMemberJoined(_podId, msg.sender, commitmentId);
        emit CommitmentCreated(
            commitmentId,
            msg.sender,
            msg.value,
            pod.targetValue,
            pod.deadline,
            _podId
        );

        return commitmentId;
    }

    /**
     * @dev Start a pod (locks it from new members)
     */
    function startPod(uint256 _podId) external {
        Pod storage pod = pods[_podId];
        require(pod.isActive, "Pod not active");
        require(!pod.isStarted, "Pod already started");
        require(pod.members.length >= 2, "Need at least 2 members");

        pod.isStarted = true;
    }

    // ============ Admin Functions ============

    /**
     * @dev Update attestation authority
     */
    function setAttestationAuthority(address _newAuthority) external onlyOwner {
        require(_newAuthority != address(0), "Invalid address");
        attestationAuthority = _newAuthority;
    }

    /**
     * @dev Update scholarship pool address
     */
    function setScholarshipPool(address _newPool) external onlyOwner {
        require(_newPool != address(0), "Invalid address");
        scholarshipPool = _newPool;
    }

    /**
     * @dev Update reward multiplier
     */
    function setRewardMultiplier(uint256 _newMultiplier) external onlyOwner {
        require(_newMultiplier >= 100 && _newMultiplier <= 200, "Invalid multiplier");
        rewardMultiplier = _newMultiplier;
    }

    /**
     * @dev Distribute scholarship from pool
     */
    function distributeScholarship(
        address _recipient,
        uint256 _amount
    ) external onlyOwner nonReentrant {
        require(_amount <= totalScholarshipFunds, "Insufficient scholarship funds");

        totalScholarshipFunds -= _amount;

        (bool success, ) = _recipient.call{value: _amount}("");
        require(success, "Scholarship distribution failed");

        emit ScholarshipDistributed(_recipient, _amount);
    }

    /**
     * @dev Pause contract
     */
    function pause() external onlyOwner {
        _pause();
    }

    /**
     * @dev Unpause contract
     */
    function unpause() external onlyOwner {
        _unpause();
    }

    // ============ View Functions ============

    function getUserCommitments(address _user) external view returns (uint256[] memory) {
        return userCommitments[_user];
    }

    function getPodMembers(uint256 _podId) external view returns (address[] memory) {
        return pods[_podId].members;
    }

    function getCommitment(uint256 _commitmentId) external view returns (Commitment memory) {
        return commitments[_commitmentId];
    }

    function getPod(uint256 _podId) external view returns (Pod memory) {
        return pods[_podId];
    }

    // ============ Signature Helper Functions ============

    function getEthSignedMessageHash(bytes32 _messageHash) internal pure returns (bytes32) {
        return keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", _messageHash));
    }

    function recoverSigner(bytes32 _ethSignedMessageHash, bytes memory _signature)
        internal
        pure
        returns (address)
    {
        (bytes32 r, bytes32 s, uint8 v) = splitSignature(_signature);
        return ecrecover(_ethSignedMessageHash, v, r, s);
    }

    function splitSignature(bytes memory _sig)
        internal
        pure
        returns (bytes32 r, bytes32 s, uint8 v)
    {
        require(_sig.length == 65, "Invalid signature length");

        assembly {
            r := mload(add(_sig, 32))
            s := mload(add(_sig, 64))
            v := byte(0, mload(add(_sig, 96)))
        }
    }

    // ============ Receive Function ============

    receive() external payable {
        // Accept donations to reward pool
    }
}
