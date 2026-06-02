from solders.pubkey import Pubkey
from solders.signature import Signature
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed

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
        client = Client(SOLANA_RPC_URL)
        sig = Signature.from_string(tx_signature)

        resp = client.get_transaction(sig, commitment=Confirmed)
        if resp.value is None:
            print("Transaction not found or not yet confirmed")
            return False

        meta = resp.value.transaction.meta

        if meta.err is not None:
            print(f"Transaction failed: {meta.err}")
            return False

        expected_lamports = int(expected_amount * LAMPORTS_PER_SOL)

        tx_data = resp.value.transaction.transaction
        account_keys = tx_data.message.account_keys

        recipient_index = None
        for i, key in enumerate(account_keys):
            if str(key) == expected_recipient:
                recipient_index = i
                break

        if recipient_index is None:
            print("Recipient not found in transaction")
            return False

        pre = meta.pre_balances[recipient_index]
        post = meta.post_balances[recipient_index]
        balance_change = post - pre

        if balance_change < expected_lamports - LAMPORT_TOLERANCE:
            print(
                f"Expected at least {expected_lamports} lamports, "
                f"got {balance_change}"
            )
            return False

        print("Transaction verified successfully")
        return True

    except Exception as e:
        print(f"Transaction verification failed: {e}")
        return False
