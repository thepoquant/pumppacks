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
            "slippageBps": "1000",
            "excludeDexes": "Whirlpool,DefiTuna",
        }
        quote_resp = await client.get(JUPITER_QUOTE_URL, params=quote_params)
        if quote_resp.status_code != 200:
            raise Exception(
                f"Jupiter quote failed: {quote_resp.status_code} - {quote_resp.text}"
            )
        quote = quote_resp.json()
        if "routePlan" not in quote:
            raise Exception(f"Jupiter quote missing routePlan: {quote}")
        out_amount = int(quote["outAmount"])
        print(f"Quote received: {out_amount} tokens for {sol_amount} SOL")

        keypair = Keypair.from_base58_string(PACK_WALLET_PRIVATE_KEY)

        swap_body = {
            "quoteResponse": quote,
            "userPublicKey": str(keypair.pubkey()),
            "wrapAndUnwrapSol": True,
            "dynamicComputeUnitLimit": True,
            "prioritizationFeeLamports": "auto",
            "excludeDexes": "Whirlpool,DefiTuna",
        }
        print("Executing swap...")
        swap_resp = await client.post(
            JUPITER_SWAP_URL,
            headers={"Content-Type": "application/json"},
            json=swap_body,
            timeout=30,
        )
        if swap_resp.status_code != 200:
            raise Exception(
                f"Jupiter swap failed: {swap_resp.status_code} - {swap_resp.text}"
            )
        swap_data = swap_resp.json()

    unsigned_tx_b64 = swap_data["swapTransaction"]
    tx_bytes = base64.b64decode(unsigned_tx_b64)
    tx = VersionedTransaction.from_bytes(tx_bytes)
    signed_tx = VersionedTransaction(tx.message, [keypair])
    signed_b64 = base64.b64encode(bytes(signed_tx)).decode()

    async with httpx.AsyncClient(timeout=30) as client:
        send_resp = await client.post(
            SOLANA_RPC_URL,
            headers={"Content-Type": "application/json"},
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendTransaction",
                "params": [
                    signed_b64,
                    {"encoding": "base64", "skipPreflight": False, "maxRetries": 3},
                ],
            },
        )
        send_result = send_resp.json()
        if "error" in send_result:
            raise Exception(f"RPC sendTransaction error: {send_result['error']}")
        tx_sig = send_result["result"]

    print(f"Swap transaction sent: {tx_sig}")
    await asyncio.sleep(10)

    async with httpx.AsyncClient(timeout=30) as client:
        for attempt in range(30):
            try:
                confirm_resp = await client.post(
                    SOLANA_RPC_URL,
                    headers={"Content-Type": "application/json"},
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getTransaction",
                        "params": [tx_sig, {"encoding": "json", "commitment": "confirmed"}],
                    },
                    timeout=15,
                )
                confirm_data = confirm_resp.json()
                tx_result = confirm_data.get("result")
                if tx_result is not None:
                    meta = tx_result.get("meta")
                    if meta is not None:
                        if meta.get("err") is None:
                            print(f"Swap confirmed: {tx_sig}")
                            return (tx_sig, out_amount)
                        else:
                            raise Exception(f"Swap failed on-chain: {meta['err']}")
                await asyncio.sleep(5)
            except Exception as exc:
                print(f"Confirmation attempt {attempt + 1} failed: {exc}")
                await asyncio.sleep(5)

    raise Exception(f"Swap confirmation timeout after 150s: {tx_sig}")
