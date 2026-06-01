from config import TEST_MODE

def verify_transaction(tx_signature: str, expected_amount: float, expected_recipient: str) -> bool:
    if TEST_MODE:
        return True
    raise NotImplementedError("verify_transaction not implemented yet")
