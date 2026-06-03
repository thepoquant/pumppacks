import os
from dotenv import load_dotenv

load_dotenv()

PACK_WALLET_PRIVATE_KEY = os.getenv("PACK_WALLET_PRIVATE_KEY", "")
PACK_WALLET_ADDRESS = os.getenv("PACK_WALLET_ADDRESS", "vEeSPZdVd4S8owp686hhfqwtwZr337zJGd5YqDEDUMM")
DATABASE_URL = os.getenv("DATABASE_URL", "")
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY", "")
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")
TEST_MODE = os.getenv("TEST_MODE", "true").lower() == "true"
