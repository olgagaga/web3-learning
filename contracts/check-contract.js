const { ethers } = require('ethers');

// Contract address from your deployment
const CONTRACT_ADDRESS = process.env.CONTRACT_ADDRESS || '0x76342058da66b1ba50ff62bce2e4934dd03b5d32';

// Minimal ABI for checking state
const ABI = [
  'function paused() public view returns (bool)',
  'function attestationAuthority() public view returns (address)',
  'function scholarshipPool() public view returns (address)',
  'function owner() public view returns (address)',
  'function rewardMultiplier() public view returns (uint256)',
];

async function checkContract() {
  console.log('🔍 Checking contract state...\n');

  // Connect to Sepolia (ethers v6 syntax)
  // Using public Sepolia RPC
  const provider = new ethers.JsonRpcProvider('https://ethereum-sepolia-rpc.publicnode.com');
  const contract = new ethers.Contract(CONTRACT_ADDRESS, ABI, provider);

  try {
    console.log('Contract Address:', CONTRACT_ADDRESS);
    console.log('---');

    // Check if paused
    const isPaused = await contract.paused();
    console.log('✓ Paused:', isPaused);
    if (isPaused) {
      console.log('  ⚠️  CONTRACT IS PAUSED! This is why transactions are failing.');
    }

    // Check attestation authority
    const attestationAuthority = await contract.attestationAuthority();
    console.log('✓ Attestation Authority:', attestationAuthority);

    // Check scholarship pool
    const scholarshipPool = await contract.scholarshipPool();
    console.log('✓ Scholarship Pool:', scholarshipPool);

    // Check owner
    const owner = await contract.owner();
    console.log('✓ Owner:', owner);

    // Check reward multiplier
    const rewardMultiplier = await contract.rewardMultiplier();
    console.log('✓ Reward Multiplier:', rewardMultiplier.toString(), '(110 = 10% bonus)');

    console.log('\n---');
    if (isPaused) {
      console.log('\n❌ CONTRACT IS PAUSED');
      console.log('To unpause, the owner needs to call: contract.unpause()');
      console.log('Owner address:', owner);
    } else {
      console.log('\n✅ Contract is ready to use!');
    }
  } catch (error) {
    console.error('❌ Error checking contract:', error.message);
  }
}

checkContract();
