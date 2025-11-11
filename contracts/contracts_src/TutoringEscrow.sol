// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

interface IReputationSBT {
    function mintReputation(address tutor, uint256 sessionId) external;
}

/**
 * @title TutoringEscrow
 * @dev Escrow smart contract for peer tutoring sessions
 * Students pay tutors through escrow. Funds release when platform verifies milestone completion.
 * Tutors earn reputation SBTs for completed sessions.
 */
contract TutoringEscrow is Ownable, ReentrancyGuard, Pausable {

    // ============ Structs ============

    struct Session {
        uint256 id;
        address learner;
        address tutor;
        uint256 amount;
        string serviceType;          // e.g., "essay_feedback", "speaking_practice"
        string description;
        uint256 createdAt;
        uint256 completedAt;
        SessionStatus status;
        bool fundsReleased;
    }

    enum SessionStatus {
        Created,        // Session created, funds in escrow
        InProgress,     // Tutor accepted, working on it
        PendingReview,  // Tutor submitted, waiting for verification
        Completed,      // Platform verified, funds released
        Disputed,       // Dispute raised
        Cancelled       // Session cancelled, funds returned
    }

    // ============ State Variables ============

    uint256 public nextSessionId = 1;
    uint256 public platformFeePercent = 5; // 5% platform fee
    address public attestationAuthority;
    address public reputationSBT;

    mapping(uint256 => Session) public sessions;
    mapping(address => uint256[]) public learnerSessions;
    mapping(address => uint256[]) public tutorSessions;
    mapping(address => uint256) public tutorEarnings;
    mapping(address => uint256) public tutorCompletedSessions;

    // ============ Events ============

    event SessionCreated(uint256 indexed sessionId, address indexed learner, uint256 amount, string serviceType);
    event SessionAccepted(uint256 indexed sessionId, address indexed tutor);
    event SessionSubmitted(uint256 indexed sessionId, address indexed tutor);
    event SessionCompleted(uint256 indexed sessionId, address indexed tutor, uint256 amount);
    event SessionCancelled(uint256 indexed sessionId, address indexed learner);
    event DisputeRaised(uint256 indexed sessionId, address indexed raiser);
    event FundsReleased(uint256 indexed sessionId, address indexed tutor, uint256 tutorAmount, uint256 platformFee);

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

    // ============ Main Functions ============

    /**
     * @dev Create a new tutoring session
     * @param _tutor Address of the tutor (0x0 for open marketplace)
     * @param _serviceType Type of service (essay_feedback, speaking_practice, etc.)
     * @param _description Session description
     */
    function createSession(
        address _tutor,
        string memory _serviceType,
        string memory _description
    ) external payable whenNotPaused nonReentrant returns (uint256) {
        require(msg.value > 0, "Payment required");
        require(msg.sender != _tutor, "Cannot hire yourself");

        uint256 sessionId = nextSessionId++;

        sessions[sessionId] = Session({
            id: sessionId,
            learner: msg.sender,
            tutor: _tutor,
            amount: msg.value,
            serviceType: _serviceType,
            description: _description,
            createdAt: block.timestamp,
            completedAt: 0,
            status: SessionStatus.Created,
            fundsReleased: false
        });

        learnerSessions[msg.sender].push(sessionId);

        if (_tutor != address(0)) {
            tutorSessions[_tutor].push(sessionId);
            sessions[sessionId].status = SessionStatus.InProgress;
            emit SessionAccepted(sessionId, _tutor);
        }

        emit SessionCreated(sessionId, msg.sender, msg.value, _serviceType);

        return sessionId;
    }

    /**
     * @dev Tutor accepts an open session
     * @param _sessionId The session ID
     */
    function acceptSession(uint256 _sessionId) external whenNotPaused {
        Session storage session = sessions[_sessionId];
        require(session.status == SessionStatus.Created, "Session not available");
        require(session.tutor == address(0), "Session already assigned");
        require(session.learner != msg.sender, "Cannot tutor yourself");

        session.tutor = msg.sender;
        session.status = SessionStatus.InProgress;
        tutorSessions[msg.sender].push(_sessionId);

        emit SessionAccepted(_sessionId, msg.sender);
    }

    /**
     * @dev Tutor submits completed work
     * @param _sessionId The session ID
     */
    function submitSession(uint256 _sessionId) external {
        Session storage session = sessions[_sessionId];
        require(session.tutor == msg.sender, "Not the tutor");
        require(session.status == SessionStatus.InProgress, "Invalid status");

        session.status = SessionStatus.PendingReview;

        emit SessionSubmitted(_sessionId, msg.sender);
    }

    /**
     * @dev Platform verifies and completes session (requires attestation)
     * @param _sessionId The session ID
     * @param _signature Attestation signature from platform
     */
    function completeSession(
        uint256 _sessionId,
        bytes memory _signature
    ) external onlyAttestationAuthority nonReentrant {
        Session storage session = sessions[_sessionId];
        require(session.status == SessionStatus.PendingReview, "Not pending review");
        require(!session.fundsReleased, "Funds already released");

        // Verify signature (simplified for MVP)
        require(_signature.length > 0, "Invalid signature");

        // Calculate amounts
        uint256 platformFee = (session.amount * platformFeePercent) / 100;
        uint256 tutorAmount = session.amount - platformFee;

        // Update session
        session.status = SessionStatus.Completed;
        session.completedAt = block.timestamp;
        session.fundsReleased = true;

        // Update tutor stats
        tutorEarnings[session.tutor] += tutorAmount;
        tutorCompletedSessions[session.tutor]++;

        // Transfer funds
        (bool success, ) = payable(session.tutor).call{value: tutorAmount}("");
        require(success, "Transfer to tutor failed");

        (bool feeSuccess, ) = payable(owner()).call{value: platformFee}("");
        require(feeSuccess, "Platform fee transfer failed");

        // Mint reputation SBT
        if (reputationSBT != address(0)) {
            IReputationSBT(reputationSBT).mintReputation(session.tutor, _sessionId);
        }

        emit SessionCompleted(_sessionId, session.tutor, tutorAmount);
        emit FundsReleased(_sessionId, session.tutor, tutorAmount, platformFee);
    }

    /**
     * @dev Learner cancels session before tutor accepts
     * @param _sessionId The session ID
     */
    function cancelSession(uint256 _sessionId) external nonReentrant {
        Session storage session = sessions[_sessionId];
        require(session.learner == msg.sender, "Not the learner");
        require(session.status == SessionStatus.Created, "Cannot cancel");
        require(!session.fundsReleased, "Funds already released");

        session.status = SessionStatus.Cancelled;
        session.fundsReleased = true;

        // Refund learner
        (bool success, ) = payable(session.learner).call{value: session.amount}("");
        require(success, "Refund failed");

        emit SessionCancelled(_sessionId, msg.sender);
    }

    /**
     * @dev Raise a dispute
     * @param _sessionId The session ID
     */
    function raiseDispute(uint256 _sessionId) external {
        Session storage session = sessions[_sessionId];
        require(
            msg.sender == session.learner || msg.sender == session.tutor,
            "Not involved in session"
        );
        require(
            session.status == SessionStatus.InProgress ||
            session.status == SessionStatus.PendingReview,
            "Invalid status for dispute"
        );

        session.status = SessionStatus.Disputed;

        emit DisputeRaised(_sessionId, msg.sender);
    }

    /**
     * @dev Resolve dispute (owner only)
     * @param _sessionId The session ID
     * @param _refundToLearner If true, refund to learner; else pay tutor
     */
    function resolveDispute(
        uint256 _sessionId,
        bool _refundToLearner
    ) external onlyOwner nonReentrant {
        Session storage session = sessions[_sessionId];
        require(session.status == SessionStatus.Disputed, "Not disputed");
        require(!session.fundsReleased, "Funds already released");

        session.fundsReleased = true;

        if (_refundToLearner) {
            session.status = SessionStatus.Cancelled;
            (bool success, ) = payable(session.learner).call{value: session.amount}("");
            require(success, "Refund failed");
        } else {
            session.status = SessionStatus.Completed;
            session.completedAt = block.timestamp;

            uint256 platformFee = (session.amount * platformFeePercent) / 100;
            uint256 tutorAmount = session.amount - platformFee;

            tutorEarnings[session.tutor] += tutorAmount;
            tutorCompletedSessions[session.tutor]++;

            (bool success, ) = payable(session.tutor).call{value: tutorAmount}("");
            require(success, "Transfer failed");

            (bool feeSuccess, ) = payable(owner()).call{value: platformFee}("");
            require(feeSuccess, "Fee transfer failed");

            if (reputationSBT != address(0)) {
                IReputationSBT(reputationSBT).mintReputation(session.tutor, _sessionId);
            }
        }
    }

    // ============ View Functions ============

    function getSession(uint256 _sessionId) external view returns (Session memory) {
        return sessions[_sessionId];
    }

    function getLearnerSessions(address _learner) external view returns (uint256[] memory) {
        return learnerSessions[_learner];
    }

    function getTutorSessions(address _tutor) external view returns (uint256[] memory) {
        return tutorSessions[_tutor];
    }

    function getTutorStats(address _tutor) external view returns (
        uint256 completed,
        uint256 earnings
    ) {
        return (tutorCompletedSessions[_tutor], tutorEarnings[_tutor]);
    }

    // ============ Admin Functions ============

    function setAttestationAuthority(address _authority) external onlyOwner {
        require(_authority != address(0), "Invalid address");
        attestationAuthority = _authority;
    }

    function setReputationSBT(address _sbt) external onlyOwner {
        require(_sbt != address(0), "Invalid address");
        reputationSBT = _sbt;
    }

    function setPlatformFee(uint256 _feePercent) external onlyOwner {
        require(_feePercent <= 20, "Fee too high");
        platformFeePercent = _feePercent;
    }

    function pause() external onlyOwner {
        _pause();
    }

    function unpause() external onlyOwner {
        _unpause();
    }

    // Emergency withdraw (only if paused)
    function emergencyWithdraw() external onlyOwner {
        require(paused(), "Not paused");
        (bool success, ) = payable(owner()).call{value: address(this).balance}("");
        require(success, "Withdrawal failed");
    }
}
