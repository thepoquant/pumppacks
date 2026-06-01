from config import TEST_MODE

def airdrop_tokens(recipient_wallet: str, mint_address: str, amount: float) -> None:
    if TEST_MODE:
        print("TEST MODE: skipping airdrop")
        return
    raise NotImplementedError("airdrop_tokens not implemented yet")
