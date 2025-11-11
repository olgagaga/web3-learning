# Commitment Staking Smart Contract

## Overview

This smart contract enables commitment-based staking for the Web3 education platform. Users can stake testnet tokens to commit to learning goals (e.g., 7-day streaks). The backend provides signed attestations for milestone completion. Successful commitments earn rewards; failed ones contribute to a scholarship pool.

## Features

- **Individual Commitments**: Users stake tokens for personal learning goals
- **Accountability Pods**: Team-based commitments with shared goals
- **Backend Attestations**: Secure, signed proof of milestone completion
- **Reward Distribution**: Automatic reward calculation (10% bonus by default)
- **Scholarship Pool**: Failed commitment stakes fund learner scholarships
- **Time-locked Stakes**: Funds locked until deadline or completion
- **Configurable Rewards**: Admin can adjust reward multiplier (100-200%)

## Contract Architecture

### Key Components

1. **Commitment Struct**: Tracks individual stakes and progress
2. **Pod Struct**: Manages accountability group information
3. **Attestation System**: Backend-signed progress verification
4. **Scholarship Pool**: Accumulates penalty funds for distribution

### State Variables

- `commitmentCounter`: Unique ID for each commitment
- `podCounter`: Unique ID for each pod
- `attestationAuthority`: Backend signer address for attestations
- `scholarshipPool`: Address receiving failed commitment funds
- `rewardMultiplier`: Percentage reward (default 110 = 10% bonus)

## Deployment Guide

### Option 1: Deploy via Thirdweb Dashboard (Recommended for Hackathon)

1. **Install Thirdweb CLI**:
   ```bash
   npm install -g @thirdweb-dev/cli
   ```

2. **Login to Thirdweb**:
   ```bash
   npx thirdweb login
   ```

3. **Deploy Contract**:
   ```bash
   npx thirdweb deploy contracts/CommitmentStaking.sol
   ```

4. **Configure on Dashboard**:
   - Select **Polygon Amoy** testnet
   - Set constructor parameters:
     - `_attestationAuthority`: Your backend wallet address (will sign attestations)
     - `_scholarshipPool`: Treasury wallet address (receives penalties)
   - Click "Deploy Now"

5. **Get Testnet MATIC**:
   - Visit [Polygon Amoy Faucet](https://faucet.polygon.technology/)
   - Enter your wallet address
   - Receive testnet MATIC for gas fees

6. **Save Contract Address**:
   - Copy the deployed contract address
   - Add to `.env` file: `VITE_STAKING_CONTRACT_ADDRESS=<address>`

### Option 2: Deploy via Hardhat

1. **Install Dependencies**:
   ```bash
   cd contracts
   npm install --save-dev hardhat @nomiclabs/hardhat-ethers ethers
   npm install @openzeppelin/contracts
   ```

2. **Create Hardhat Config** (`hardhat.config.js`):
   ```javascript
   require("@nomiclabs/hardhat-ethers");

   module.exports = {
     solidity: "0.8.20",
     networks: {
       polygonAmoy: {
         url: "https://rpc-amoy.polygon.technology/",
         accounts: [process.env.DEPLOYER_PRIVATE_KEY],
       },
     },
   };
   ```

3. **Create Deployment Script** (`scripts/deploy.js`):
   ```javascript
   async function main() {
     const [deployer] = await ethers.getSigners();

     console.log("Deploying with account:", deployer.address);

     const attestationAuthority = process.env.ATTESTATION_AUTHORITY;
     const scholarshipPool = process.env.SCHOLARSHIP_POOL;

     const CommitmentStaking = await ethers.getContractFactory("CommitmentStaking");
     const contract = await CommitmentStaking.deploy(
       attestationAuthority,
       scholarshipPool
     );

     await contract.deployed();

     console.log("Contract deployed to:", contract.address);
   }

   main().catch((error) => {
     console.error(error);
     process.exitCode = 1;
   });
   ```

4. **Deploy**:
   ```bash
   npx hardhat run scripts/deploy.js --network polygonAmoy
   ```

## Contract Functions

### User Functions

#### `createCommitment(uint256 _targetValue, uint256 _durationDays)`
Create an individual commitment by staking tokens.
- **Parameters**: Target value (e.g., 7 days), duration in days
- **Payable**: Yes (stake amount: 0.01-1.0 ether)
- **Returns**: Commitment ID

#### `claimReward(uint256 _commitmentId)`
Claim rewards after completing a commitment.
- **Parameters**: Commitment ID
- **Requirements**: Must be completed, not yet claimed
- **Transfers**: Stake + bonus (default 10%)

#### `failCommitment(uint256 _commitmentId)`
Mark commitment as failed after deadline passes.
- **Parameters**: Commitment ID
- **Requirements**: Deadline passed, not completed
- **Transfers**: Stake to scholarship pool

#### `createPod(string _name, uint256 _stakeAmount, uint256 _targetValue, uint256 _durationDays)`
Create an accountability pod for team commitments.
- **Parameters**: Pod name, required stake, target, duration
- **Returns**: Pod ID

#### `joinPod(uint256 _podId)`
Join an accountability pod by staking.
- **Parameters**: Pod ID
- **Payable**: Yes (exact pod stake amount)
- **Returns**: Commitment ID

### Backend Functions

#### `updateProgress(uint256 _commitmentId, uint256 _progress, bytes32 _attestationHash, bytes memory _signature)`
Update commitment progress with signed attestation.
- **Parameters**: Commitment ID, progress value, attestation hash, signature
- **Requirements**: Valid signature from attestation authority
- **Effects**: Updates progress, marks completed if target reached

### Admin Functions

#### `setAttestationAuthority(address _newAuthority)`
Update the backend signer address.

#### `setRewardMultiplier(uint256 _newMultiplier)`
Adjust reward percentage (100-200).

#### `distributeScholarship(address _recipient, uint256 _amount)`
Send scholarship funds to a recipient.

#### `pause()` / `unpause()`
Emergency pause/unpause contract.

## Attestation Signature Generation

The backend must sign attestations for progress updates. Here's how to generate signatures:

### Python Example (FastAPI Backend)

```python
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3

def sign_attestation(commitment_id: int, user_address: str, progress: int, attestation_hash: bytes):
    # Load backend private key
    private_key = os.getenv("ATTESTATION_PRIVATE_KEY")
    account = Account.from_key(private_key)

    # Create message hash
    message_hash = Web3.solidityKeccak(
        ['uint256', 'address', 'uint256', 'bytes32'],
        [commitment_id, user_address, progress, attestation_hash]
    )

    # Sign message
    message = encode_defunct(hexstr=message_hash.hex())
    signed_message = account.sign_message(message)

    return signed_message.signature.hex()
```

## Testing

### Test on Polygon Amoy

1. **Get Testnet MATIC**: Use [Polygon Faucet](https://faucet.polygon.technology/)
2. **Create Commitment**: Call `createCommitment(7, 7)` with 0.1 test MATIC
3. **Complete Activities**: Use the learning platform
4. **Update Progress**: Backend calls `updateProgress` with signed attestation
5. **Claim Reward**: Call `claimReward` to receive stake + bonus

### Expected Flow

```
User creates commitment -> Stake locked in contract
  ↓
User completes daily activities
  ↓
Backend generates signed attestation
  ↓
Backend calls updateProgress() with signature
  ↓
Progress reaches target -> Commitment marked completed
  ↓
User calls claimReward() -> Receives 1.1x stake
```

## Security Features

- **ReentrancyGuard**: Prevents reentrancy attacks
- **Pausable**: Emergency stop mechanism
- **Ownable**: Admin functions restricted to owner
- **Signature Verification**: Only authorized backend can update progress
- **Used Attestation Tracking**: Prevents replay attacks
- **Stake Limits**: 0.01-1.0 ether range prevents large losses

## Gas Optimization

- Minimal storage variables
- Events for off-chain tracking
- Batch operations where possible
- Efficient signature verification

## Upgrade Path

For production, consider:
- Upgradeable proxy pattern (UUPS or Transparent Proxy)
- Multi-signature admin wallet
- Time-locked admin functions
- Chainlink VRF for random scholarship selection
- Layer 2 deployment for lower fees

## Support

- **Thirdweb Docs**: https://portal.thirdweb.com/
- **Polygon Amoy Explorer**: https://amoy.polygonscan.com/
- **OpenZeppelin Contracts**: https://docs.openzeppelin.com/contracts/

## License

MIT
