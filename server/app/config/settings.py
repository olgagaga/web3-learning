from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/web3_edu_platform"

    # JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Gemini AI
    gemini_api_key: Optional[str] = None

    # Server
    debug: bool = True
    port: int = 8001

    # Web3 Configuration
    web3_rpc_url: str = "https://rpc-amoy.polygon.technology/"
    web3_chain_id: int = 80002
    staking_contract_address: str = "0x0000000000000000000000000000000000000000"
    attestation_private_key: str = "your-attestation-private-key-here"
    scholarship_pool_address: str = "0x0000000000000000000000000000000000000000"

    # Thirdweb Configuration
    thirdweb_client_id: Optional[str] = None
    thirdweb_secret_key: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
