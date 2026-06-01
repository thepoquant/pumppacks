from config import TEST_MODE

def buy_token(mint_address: str, sol_amount: float) -> float:
    if TEST_MODE:
        print("TEST MODE: skipping swap")
        return 0.0
    raise NotImplementedError("buy_token not implemented yet")
