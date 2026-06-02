import base64
import json
import httpx
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts

from config import TEST_MODE, PACK_WALLET_PRIVATE_KEY, PACK_WALLET_ADDRESS, SOLANA_RPC_URL

SOL_MINT = "So11111111111111111111111111111111111111112"
JUPITER_QUOTE_URL = "https://public.jupiterapi.com/quote"
JUPITER_SWAP_URL = "https://public.jupiterapi.com/swap"
LAMPORTS_PER_SOL = 1_000_000_000


async def buy_token(mint_address: str, sol_amount: float) -> float:
    if TEST_MODE:
        print("TEST MODE: skipping swap")
        return 0.0

    print(f"Getting Jupiter quote for {mint_address}...")
    amount_lamports = int(sol_amount * LAMPORTS_PER_SOL)

    async with httpx.AsyncClient(timeout=30) as client:
        quote_params = {
            "inputMint": SOL_MINT,
            "outputMint": mint_address,
            "amount": str(amount_lamports),
            "slippageBps": "300",
        }
        quote_resp = await client.get(JUPITER_QUOTE_URL, params=quote_params)
        if quote_resp.status_code != 200:
            raise Exception(
                f"Jupiter quote failed: {quote_resp.status_code} - {quote_resp.text}"
            )
        quote = quote_resp.json()
        out_amount = float(quote["outAmount"])

        print(f"Quote received: {out_amount} tokens for {sol_amount} SOL")

        print("Executing swap...")
        swap_body = {
            "quoteResponse": quote,
            "userPublicKey": PACK_WALLET_ADDRESS,
            "wrapAndUnwrapSol": True,
            "useSharedAccounts": False,
        }
        swap_resp = await client.post(JUPITER_SWAP_URL, json=swap_body)
        if swap_resp.status_code != 200:
            raise Exception(
                f"Jupiter swap failed: {swap_resp.status_code} - {swap_resp.text}"
            )
        swap_data = swap_resp.json()

    swap_tx_b64 = swap_data["swapTransaction"]
    last_valid_block_height = swap_data.get("lastValidBlockHeight")

    keypair_bytes = json.loads(PACK_WALLET_PRIVATE_KEY)
    keypair = Keypair.from_bytes(bytes(keypair_bytes))

    tx_bytes = base64.b64decode(swap_tx_b64)
    tx = VersionedTransaction.from_bytes(tx_bytes)

    sig = keypair.sign_message(bytes(tx.message.serialize()))
    signed_tx = VersionedTransaction.populate(tx.message, [sig])

    rpc_client = Client(SOLANA_RPC_URL)
    tx_opts = TxOpts(skip_preflight=False)
    result = rpc_client.send_raw_transaction(bytes(signed_tx), opts=tx_opts)
    tx_sig = result.value

    print(f"Swap transaction sent: {tx_sig}")

    rpc_client.confirm_transaction(
        tx_sig,
        commitment=Confirmed,
        last_valid_block_height=last_valid_block_height,
    )

    print(f"Swap confirmed: {tx_sig}")
    return out_amount
