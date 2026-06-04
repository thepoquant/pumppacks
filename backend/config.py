import os
from dotenv import load_dotenv

load_dotenv()

PACK_WALLET_PRIVATE_KEY = os.getenv("PACK_WALLET_PRIVATE_KEY", "")
PACK_WALLET_ADDRESS = os.getenv("PACK_WALLET_ADDRESS", "vEeSPZdVd4S8owp686hhfqwtwZr337zJGd5YqDEDUMM")
DATABASE_URL = os.getenv("DATABASE_URL", "")
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY", "")
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
TEST_MODE = os.getenv("TEST_MODE", "true").lower() == "true"

PUMPPACKS_TOKEN_MINT = os.getenv("PUMPPACKS_TOKEN_MINT", "")

SOL_PER_PACK = float(os.getenv("SOL_PER_PACK", "0.5"))
CARDS_PER_PACK = 3
RARITY_SOL_PAYOUT = {
    "common": 0.03,
    "rare": 0.08,
    "epic": 0.20,
    "legendary": 0.60,
}

RARITY_WEIGHTS = {
    "common": 60,
    "rare": 25,
    "epic": 12,
    "legendary": 3,
}
