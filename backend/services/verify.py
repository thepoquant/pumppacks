import asyncio
import logging
from solana.rpc.async_api import AsyncClient
from solders.signature import Signature
from config import TEST_MODE, SOLANA_RPC_URL

logger = logging.getLogger(__name__)

LAMPORTS_PER_SOL = 1_000_000_000
LAMPORT_TOLERANCE = 10_000
MAX_RETRIES = 20
RETRY_DELAY = 3

async def verify_transaction(
    tx_signature: str, expected_amount: float, expected_recipient: str
) -> bool:
    if TEST_MODE:
        return True

    print(f"Verifying transaction {tx_signature}...")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with AsyncClient(SOLANA_RPC_URL) as client:
                sig = Signature.from_string(tx_signature)
                resp = await client.get_transaction(sig, max_supported_transaction_version=0)
                result = resp.value

                if result is None:
                    print(f"Attempt {attempt}/{MAX_RETRIES}: Transaction not found or not yet confirmed")
                    if attempt < MAX_RETRIES:
                        await asyncio.sleep(RETRY_DELAY)
                    continue

                logger.info(f"Result attrs: {[a for a in dir(result) if not a.startswith('_')]}")

                meta = result.transaction.meta
                pre_balances = meta.pre_balances
                post_balances = meta.post_balances
                account_keys = result.transaction.transaction.message.account_keys

                recipient_index = None
                for i, key in enumerate(account_keys):
                    if str(key) == expected_recipient:
                        recipient_index = i
                        break

                if recipient_index is None:
                    print("Recipient not found in transaction")
                    return False

                balance_change = post_balances[recipient_index] - pre_balances[recipient_index]
                expected_lamports = int(expected_amount * LAMPORTS_PER_SOL)

                if balance_change < expected_lamports - LAMPORT_TOLERANCE:
                    print(f"Expected at least {expected_lamports} lamports, got {balance_change}")
                    return False

                print("Transaction verified successfully")
                return True

        except Exception as e:
            print(f"Attempt {attempt}/{MAX_RETRIES}: Transaction verification failed: {e}")
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAY)

    print("Transaction verification failed after all retries")
    return False
