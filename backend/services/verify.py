from solana.rpc.async_api import AsyncClient
from solders.signature import Signature
from solders.commitment_config import CommitmentLevel
from config import TEST_MODE, SOLANA_RPC_URL

LAMPORTS_PER_SOL = 1_000_000_000
LAMPORT_TOLERANCE = 10_000


async def verify_transaction(
    tx_signature: str, expected_amount: float, expected_recipient: str
) -> bool:
    if TEST_MODE:
        return True

    print(f"Verifying transaction {tx_signature}...")

    try:
        async with AsyncClient(SOLANA_RPC_URL) as client:
            sig = Signature.from_string(tx_signature)
            resp = await client.get_transaction(sig)
            result = resp.value

            if result is None:
                print("Transaction not found or not yet confirmed")
                return False

            meta = result.meta
            if meta is None or meta.err is not None:
                print(f"Transaction failed on-chain: {meta.err if meta else 'no meta'}")
                return False

            account_keys = result.transaction.message.account_keys
            pre_balances = meta.pre_balances
            post_balances = meta.post_balances

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
        print(f"Transaction verification failed: {e}")
        return False
