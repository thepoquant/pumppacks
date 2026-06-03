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

TOKEN_BUY_PCT = 0.70
AIRDROP_PCT   = 0.20
PROFIT_PCT    = 0.10

CARDS_PER_PACK = 3
SOL_PER_CARD_AIRDROP = (SOL_PER_PACK * AIRDROP_PCT) / CARDS_PER_PACK

RARITY_WEIGHTS = {
    "common":    30,
    "rare":      7,
    "epic":      2.5,
    "legendary": 1,
}
