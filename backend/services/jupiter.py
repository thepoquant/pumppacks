import asyncio
import base64
import httpx
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

from config import TEST_MODE, PACK_WALLET_PRIVATE_KEY, SOLANA_RPC_URL

SOL_MINT = "So11111111111111111111111111111111111111112"
JUPITER_QUOTE_URL = "https://api.jup.ag/swap/v1/quote"
JUPITER_SWAP_URL = "https://api.jup.ag/swap/v1/swap"
LAMPORTS_PER_SOL = 1_000_000_000


async def buy_token(mint_address: str, sol_amount: float) -> tuple[str, int]:
    if TEST_MODE:
        print("TEST MODE: skipping swap")
        return ("", 0)

    print(f"Getting Jupiter quote for {mint_address}...")
    amount_lamports = int(sol_amount * LAMPORTS_PER_SOL)

    async with httpx.AsyncClient(timeout=30) as client:
        quote_params = {
            "inputMint": SOL_MINT,
            "outputMint": mint_address,
            "amount": str(amount_lamports),
            "slippageBps": "300",
            "restrictIntermediateTokens": "true",
        }
        quote_resp = await client.get(JUPITER_QUOTE_URL, params=quote_params)
        if quote_resp.status_code != 200:
            raise Exception(
                f"Jupiter quote failed: {quote_resp.status_code} - {quote_resp.text}"
            )
        quote = quote_resp.json()
        out_amount = int(quote["outAmount"])

        print(f"Quote received: {out_amount} tokens for {sol_amount} SOL")

        print("Executing swap...")
        swap_body = {
            "quoteResponse": quote,
            "userPublicKey": str(Keypair.from_base58_string(PACK_WALLET_PRIVATE_KEY).pubkey()),
            "wrapAndUnwrapSol": True,
            "useSharedAccounts": False,
        }
        swap_resp = await client.post(JUPITER_SWAP_URL, json=swap_body)
        if swap_resp.status_code != 200:
            raise Exception(
                f"Jupiter swap failed: {swap_resp.status_code} - {swap_resp.text}"
            )
        swap_data = swap_resp.json()

    unsigned_tx_b64 = swap_data["swapTransaction"]

    keypair = Keypair.from_base58_string(PACK_WALLET_PRIVATE_KEY)

    tx_bytes = base64.b64decode(unsigned_tx_b64)
    tx = VersionedTransaction.from_bytes(tx_bytes)
    signed_tx = VersionedTransaction(tx.message, [keypair])
    signed_b64 = base64.b64encode(bytes(signed_tx)).decode()

    rpc_url = SOLANA_RPC_URL.rstrip("/")
    async with httpx.AsyncClient(timeout=30) as client:
        send_resp = await client.post(
            f"{rpc_url}",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendTransaction",
                "params": [
                    signed_b64,
                    {"skipPreflight": False, "encoding": "base64"},
                ],
            },
        )
        if send_resp.status_code != 200:
            raise Exception(f"RPC sendTransaction failed: {send_resp.status_code} - {send_resp.text}")
        send_result = send_resp.json()
        if "error" in send_result:
            raise Exception(f"RPC sendTransaction error: {send_result['error']}")
        tx_sig = send_result["result"]

    print(f"Swap transaction sent: {tx_sig}")

    for attempt in range(15):
        await asyncio.sleep(3)
        async with httpx.AsyncClient(timeout=30) as client:
            confirm_resp = await client.post(
                f"{rpc_url}",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTransaction",
                    "params": [tx_sig, {"encoding": "base64"}],
                },
            )
            if confirm_resp.status_code == 200:
                confirm_result = confirm_resp.json()
                if confirm_result.get("result") is not None:
                    print(f"Swap confirmed: {tx_sig}")
                    return (tx_sig, out_amount)

    raise Exception(f"Swap confirmation timeout after 45s: {tx_sig}")
