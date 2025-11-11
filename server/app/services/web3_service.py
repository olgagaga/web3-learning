"""
Web3 service for blockchain interactions
Handles smart contract interactions, transaction signing, and attestations
"""

import os
import json
import hashlib
from typing import Optional, Dict, Any, List
from datetime import datetime
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_account.messages import encode_defunct
from decimal import Decimal

# Contract ABI (simplified - you'll need to add full ABI after deployment)
STAKING_CONTRACT_ABI = json.loads('''[
    {
        "inputs": [
            {"internalType": "uint256", "name": "_targetValue", "type": "uint256"},
            {"internalType": "uint256", "name": "_durationDays", "type": "uint256"}
        ],
        "name": "createCommitment",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "_commitmentId", "type": "uint256"},
            {"internalType": "uint256", "name": "_progress", "type": "uint256"},
            {"internalType": "bytes32", "name": "_attestationHash", "type": "bytes32"},
            {"internalType": "bytes", "name": "_signature", "type": "bytes"}
        ],
        "name": "updateProgress",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "_commitmentId", "type": "uint256"}],
        "name": "claimReward",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "_commitmentId", "type": "uint256"}],
        "name": "failCommitment",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "_name", "type": "string"},
            {"internalType": "uint256", "name": "_stakeAmount", "type": "uint256"},
            {"internalType": "uint256", "name": "_targetValue", "type": "uint256"},
            {"internalType": "uint256", "name": "_durationDays", "type": "uint256"}
        ],
        "name": "createPod",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "_podId", "type": "uint256"}],
        "name": "joinPod",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "_user", "type": "address"}],
        "name": "getUserCommitments",
        "outputs": [{"internalType": "uint256[]", "name": "", "type": "uint256[]"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "_commitmentId", "type": "uint256"}],
        "name": "getCommitment",
        "outputs": [
            {
                "components": [
                    {"internalType": "address", "name": "user", "type": "address"},
                    {"internalType": "uint256", "name": "stakeAmount", "type": "uint256"},
                    {"internalType": "uint256", "name": "targetValue", "type": "uint256"},
                    {"internalType": "uint256", "name": "currentProgress", "type": "uint256"},
                    {"internalType": "uint256", "name": "startTime", "type": "uint256"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                    {"internalType": "uint256", "name": "podId", "type": "uint256"},
                    {"internalType": "bool", "name": "isActive", "type": "bool"},
                    {"internalType": "bool", "name": "isCompleted", "type": "bool"},
                    {"internalType": "bool", "name": "isClaimed", "type": "bool"}
                ],
                "internalType": "struct CommitmentStaking.Commitment",
                "name": "",
                "type": "tuple"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "_podId", "type": "uint256"}],
        "name": "getPod",
        "outputs": [
            {
                "components": [
                    {"internalType": "string", "name": "name", "type": "string"},
                    {"internalType": "uint256", "name": "stakeAmount", "type": "uint256"},
                    {"internalType": "uint256", "name": "targetValue", "type": "uint256"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                    {"internalType": "address[]", "name": "members", "type": "address[]"},
                    {"internalType": "uint256", "name": "successfulMembers", "type": "uint256"},
                    {"internalType": "uint256", "name": "failedMembers", "type": "uint256"},
                    {"internalType": "bool", "name": "isActive", "type": "bool"},
                    {"internalType": "bool", "name": "isStarted", "type": "bool"}
                ],
                "internalType": "struct CommitmentStaking.Pod",
                "name": "",
                "type": "tuple"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "anonymous": false,
        "inputs": [
            {"indexed": true, "internalType": "uint256", "name": "commitmentId", "type": "uint256"},
            {"indexed": true, "internalType": "address", "name": "user", "type": "address"},
            {"indexed": false, "internalType": "uint256", "name": "stakeAmount", "type": "uint256"},
            {"indexed": false, "internalType": "uint256", "name": "targetValue", "type": "uint256"},
            {"indexed": false, "internalType": "uint256", "name": "deadline", "type": "uint256"},
            {"indexed": false, "internalType": "uint256", "name": "podId", "type": "uint256"}
        ],
        "name": "CommitmentCreated",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
            {"indexed": true, "internalType": "uint256", "name": "commitmentId", "type": "uint256"},
            {"indexed": true, "internalType": "address", "name": "user", "type": "address"},
            {"indexed": false, "internalType": "uint256", "name": "progress", "type": "uint256"}
        ],
        "name": "CommitmentCompleted",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
            {"indexed": true, "internalType": "uint256", "name": "commitmentId", "type": "uint256"},
            {"indexed": false, "internalType": "uint256", "name": "progress", "type": "uint256"}
        ],
        "name": "ProgressUpdated",
        "type": "event"
    }
]''')


class Web3Service:
    """Service for interacting with blockchain and smart contracts"""

    def __init__(self):
        self.rpc_url = os.getenv("WEB3_RPC_URL", "https://rpc-amoy.polygon.technology/")
        self.chain_id = int(os.getenv("WEB3_CHAIN_ID", "80002"))
        self.contract_address = os.getenv("STAKING_CONTRACT_ADDRESS")
        self.attestation_private_key = os.getenv("ATTESTATION_PRIVATE_KEY")

        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))

        # Add PoA middleware for Polygon
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        # Initialize attestation account
        if self.attestation_private_key and self.attestation_private_key != "your-attestation-private-key-here":
            self.attestation_account = Account.from_key(self.attestation_private_key)
        else:
            self.attestation_account = None

        # Initialize contract
        if self.contract_address and self.contract_address != "0x0000000000000000000000000000000000000000":
            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contract_address),
                abi=STAKING_CONTRACT_ABI
            )
        else:
            self.contract = None

    def is_connected(self) -> bool:
        """Check if connected to blockchain"""
        try:
            return self.w3.is_connected()
        except Exception:
            return False

    def get_balance(self, address: str) -> Decimal:
        """Get wallet balance in MATIC"""
        try:
            checksum_address = Web3.to_checksum_address(address)
            balance_wei = self.w3.eth.get_balance(checksum_address)
            balance_matic = self.w3.from_wei(balance_wei, 'ether')
            return Decimal(str(balance_matic))
        except Exception as e:
            print(f"Error getting balance: {e}")
            return Decimal("0")

    def generate_attestation_hash(
        self,
        commitment_id: int,
        user_address: str,
        progress: int,
        timestamp: Optional[datetime] = None
    ) -> str:
        """Generate unique attestation hash for milestone"""
        if timestamp is None:
            timestamp = datetime.utcnow()

        data = f"{commitment_id}-{user_address}-{progress}-{timestamp.isoformat()}"
        return "0x" + hashlib.sha256(data.encode()).hexdigest()

    def sign_attestation(
        self,
        commitment_id: int,
        user_address: str,
        progress: int,
        attestation_hash: str
    ) -> Dict[str, str]:
        """
        Sign an attestation for milestone completion
        Returns signature and message hash
        """
        if not self.attestation_account:
            raise ValueError("Attestation private key not configured")

        # Create message hash matching contract's encoding
        checksum_address = Web3.to_checksum_address(user_address)

        message_hash = Web3.solidity_keccak(
            ['uint256', 'address', 'uint256', 'bytes32'],
            [commitment_id, checksum_address, progress, bytes.fromhex(attestation_hash[2:])]
        )

        # Sign the message
        message = encode_defunct(message_hash)
        signed_message = self.attestation_account.sign_message(message)

        return {
            "signature": signed_message.signature.hex(),
            "message_hash": message_hash.hex(),
            "attestation_hash": attestation_hash,
            "signer": self.attestation_account.address
        }

    def verify_attestation(
        self,
        commitment_id: int,
        user_address: str,
        progress: int,
        attestation_hash: str,
        signature: str
    ) -> bool:
        """Verify that an attestation signature is valid"""
        try:
            checksum_address = Web3.to_checksum_address(user_address)

            message_hash = Web3.solidity_keccak(
                ['uint256', 'address', 'uint256', 'bytes32'],
                [commitment_id, checksum_address, progress, bytes.fromhex(attestation_hash[2:])]
            )

            message = encode_defunct(message_hash)
            recovered_address = Account.recover_message(message, signature=bytes.fromhex(signature[2:] if signature.startswith('0x') else signature))

            return recovered_address.lower() == self.attestation_account.address.lower()
        except Exception as e:
            print(f"Error verifying attestation: {e}")
            return False

    async def get_commitment(self, commitment_id: int) -> Optional[Dict[str, Any]]:
        """Get commitment details from blockchain"""
        if not self.contract:
            raise ValueError("Contract not initialized")

        try:
            commitment = self.contract.functions.getCommitment(commitment_id).call()

            return {
                "user": commitment[0],
                "stake_amount": str(self.w3.from_wei(commitment[1], 'ether')),
                "target_value": commitment[2],
                "current_progress": commitment[3],
                "start_time": datetime.fromtimestamp(commitment[4]),
                "deadline": datetime.fromtimestamp(commitment[5]),
                "pod_id": commitment[6],
                "is_active": commitment[7],
                "is_completed": commitment[8],
                "is_claimed": commitment[9]
            }
        except Exception as e:
            print(f"Error getting commitment: {e}")
            return None

    async def get_user_commitments(self, user_address: str) -> List[int]:
        """Get all commitment IDs for a user"""
        if not self.contract:
            raise ValueError("Contract not initialized")

        try:
            checksum_address = Web3.to_checksum_address(user_address)
            commitment_ids = self.contract.functions.getUserCommitments(checksum_address).call()
            return list(commitment_ids)
        except Exception as e:
            print(f"Error getting user commitments: {e}")
            return []

    async def get_pod(self, pod_id: int) -> Optional[Dict[str, Any]]:
        """Get pod details from blockchain"""
        if not self.contract:
            raise ValueError("Contract not initialized")

        try:
            pod = self.contract.functions.getPod(pod_id).call()

            return {
                "name": pod[0],
                "stake_amount": str(self.w3.from_wei(pod[1], 'ether')),
                "target_value": pod[2],
                "deadline": datetime.fromtimestamp(pod[3]),
                "members": pod[4],
                "successful_members": pod[5],
                "failed_members": pod[6],
                "is_active": pod[7],
                "is_started": pod[8]
            }
        except Exception as e:
            print(f"Error getting pod: {e}")
            return None

    def build_update_progress_transaction(
        self,
        commitment_id: int,
        progress: int,
        attestation_hash: str,
        signature: str,
        from_address: str,
        gas_price: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Build transaction data for updating progress
        Returns transaction object that frontend can sign
        """
        if not self.contract:
            raise ValueError("Contract not initialized")

        checksum_address = Web3.to_checksum_address(from_address)

        # Build transaction
        tx = self.contract.functions.updateProgress(
            commitment_id,
            progress,
            bytes.fromhex(attestation_hash[2:]),
            bytes.fromhex(signature[2:] if signature.startswith('0x') else signature)
        ).build_transaction({
            'from': checksum_address,
            'chainId': self.chain_id,
            'gas': 200000,
            'gasPrice': gas_price or self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(checksum_address)
        })

        return tx

    def estimate_gas(self, transaction: Dict[str, Any]) -> int:
        """Estimate gas for a transaction"""
        try:
            return self.w3.eth.estimate_gas(transaction)
        except Exception as e:
            print(f"Error estimating gas: {e}")
            return 200000  # Default gas limit

    def wait_for_transaction(self, tx_hash: str, timeout: int = 120) -> Optional[Dict[str, Any]]:
        """
        Wait for transaction to be mined and return receipt
        """
        try:
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
            return {
                "transaction_hash": receipt['transactionHash'].hex(),
                "block_number": receipt['blockNumber'],
                "gas_used": receipt['gasUsed'],
                "status": receipt['status'],  # 1 = success, 0 = failure
                "logs": receipt['logs']
            }
        except Exception as e:
            print(f"Error waiting for transaction: {e}")
            return None

    def get_transaction_status(self, tx_hash: str) -> str:
        """Get status of a transaction"""
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            if receipt['status'] == 1:
                return "confirmed"
            else:
                return "failed"
        except Exception:
            return "pending"

    def parse_commitment_created_event(self, receipt: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse CommitmentCreated event from transaction receipt"""
        if not self.contract:
            return None

        try:
            events = self.contract.events.CommitmentCreated().process_receipt(receipt)
            if events:
                event = events[0]
                return {
                    "commitment_id": event['args']['commitmentId'],
                    "user": event['args']['user'],
                    "stake_amount": str(self.w3.from_wei(event['args']['stakeAmount'], 'ether')),
                    "target_value": event['args']['targetValue'],
                    "deadline": datetime.fromtimestamp(event['args']['deadline']),
                    "pod_id": event['args']['podId']
                }
            return None
        except Exception as e:
            print(f"Error parsing event: {e}")
            return None


# Singleton instance
_web3_service: Optional[Web3Service] = None


def get_web3_service() -> Web3Service:
    """Get Web3 service singleton instance"""
    global _web3_service
    if _web3_service is None:
        _web3_service = Web3Service()
    return _web3_service
