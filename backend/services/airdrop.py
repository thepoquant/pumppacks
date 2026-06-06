import asyncio
import base64
import struct

import httpx
from solders.hash import Hash
from solders.instruction import AccountMeta, Instruction
from solders.keypair import Keypair
from solders.message import MessageV0
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction

from config import TEST_MODE, PACK_WALLET_PRIVATE_KEY, SOLANA_RPC_URL

ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
TOKEN_2022_PROGRAM_ID = Pubkey.from_string("TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb")
SYSTEM_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")
RENT_ID = Pubkey.from_string("SysvarRent111111111111111111111111111111111")


def get_associated_token_address(owner: Pubkey, mint: Pubkey, token_program_id: Pubkey) -> Pubkey:
    seeds = [bytes(owner), bytes(token_program_id), bytes(mint)]
    ata, _ = Pubkey.find_program_address(seeds, ASSOCIATED_TOKEN_PROGRAM_ID)
    return ata


def create_ata_instruction(payer: Pubkey, owner: Pubkey, mint: Pubkey, token_program_id: Pubkey) -> Instruction:
    ata = get_associated_token_address(owner, mint, token_program_id)
    accounts = [
        AccountMeta(payer, True, True),
        AccountMeta(ata, False, True),
        AccountMeta(owner, False, False),
        AccountMeta(mint, False, False),
        AccountMeta(SYSTEM_PROGRAM_ID, False, False),
        AccountMeta(token_program_id, False, False),
        AccountMeta(RENT_ID, False, False),
    ]
    return Instruction(ASSOCIATED_TOKEN_PROGRAM_ID, b"", accounts)


def transfer_checked_instruction(
    source: Pubkey, mint: Pubkey, dest: Pubkey, owner: Pubkey, amount: int, decimals: int, token_program_id: Pubkey,
) -> Instruction:
    accounts = [
        AccountMeta(source, False, True),
        AccountMeta(mint, False, False),
        AccountMeta(dest, False, True),
        AccountMeta(owner, True, False),
    ]
    data = struct.pack("<BQB", 12, amount, decimals)
    return Instruction(token_program_id, data, accounts)


async def airdrop_tokens(recipient_wallet: str, mint_address: str, amount: int) -> None:
    # amount is in base units (already scaled by token decimals)
    if TEST_MODE:
        print("TEST MODE: skipping airdrop")
        return

    print(f"Airdropping {amount} of {mint_address} to {recipient_wallet}...")

    keypair = Keypair.from_base58_string(PACK_WALLET_PRIVATE_KEY)
    pack_pubkey = keypair.pubkey()

    mint_pubkey = Pubkey.from_string(mint_address)
    recipient_pubkey = Pubkey.from_string(recipient_wallet)

    rpc_url = SOLANA_RPC_URL.rstrip("/")

    async with httpx.AsyncClient(timeout=30) as client:
        # Detect token program by checking mint account owner
        mint_resp = await client.post(
            rpc_url,
            headers={"Content-Type": "application/json"},
            json={
                "jsonrpc": "2.0", "id": 1, "method": "getAccountInfo",
                "params": [str(mint_pubkey), {"encoding": "base64"}],
            },
        )
        mint_result = mint_resp.json()
        mint_value = mint_result.get("result", {}).get("value")
        if mint_value is None:
            raise Exception(f"Mint {mint_address} does not exist")

        TOKEN_2022_STR = "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"
        mint_owner = mint_value.get("owner", "")
        print(f"Mint owner program: {mint_owner}")
        if TOKEN_2022_STR in mint_owner:
            token_program_id = TOKEN_2022_PROGRAM_ID
            print(f"Using Token-2022 program for {mint_address}")
        else:
            token_program_id = TOKEN_PROGRAM_ID
            print(f"Using Token program for {mint_address}")

        mint_data = base64.b64decode(mint_value["data"][0])
        decimals = mint_data[44]

        sender_ata = get_associated_token_address(pack_pubkey, mint_pubkey, token_program_id)
        recipient_ata = get_associated_token_address(recipient_pubkey, mint_pubkey, token_program_id)

        # Check if recipient ATA exists
        ata_resp = await client.post(
            rpc_url,
            headers={"Content-Type": "application/json"},
            json={
                "jsonrpc": "2.0", "id": 1, "method": "getAccountInfo",
                "params": [str(recipient_ata), {"encoding": "base64"}],
            },
        )
        ata_data = ata_resp.json()
        ata_exists = ata_data.get("result", {}).get("value") is not None

        # Verify sender ATA exists and has balance
        sender_amount = 0
        for balance_attempt in range(10):
            sender_ata_resp = await client.post(
                rpc_url,
                headers={"Content-Type": "application/json"},
                json={
                    "jsonrpc": "2.0", "id": 1, "method": "getTokenAccountBalance",
                    "params": [str(sender_ata)],
                },
            )
            sender_balance = sender_ata_resp.json()
            sender_amount = int(sender_balance.get("result", {}).get("value", {}).get("amount", "0"))
            print(f"Sender ATA {sender_ata} balance attempt {balance_attempt + 1}: {sender_amount}")
            if sender_amount > 0:
                break
            await asyncio.sleep(3)

        if sender_amount == 0:
            raise Exception(f"Sender ATA has no tokens after 30s for mint {mint_address}")

        # Use actual balance if out_amount exceeds it
        transfer_amount = min(int(amount), sender_amount)

        instructions = []

        if not ata_exists:
            print(f"Recipient ATA {recipient_ata} does not exist. Creating...")
            instructions.append(create_ata_instruction(pack_pubkey, recipient_pubkey, mint_pubkey, token_program_id))

        instructions.append(
            transfer_checked_instruction(
                sender_ata, mint_pubkey, recipient_ata, pack_pubkey, transfer_amount, decimals, token_program_id,
            )
        )

        # Get latest blockhash
        blockhash_resp = await client.post(
            rpc_url,
            headers={"Content-Type": "application/json"},
            json={
                "jsonrpc": "2.0", "id": 1, "method": "getLatestBlockhash",
                "params": [],
            },
        )
        blockhash_result = blockhash_resp.json()
        recent_blockhash = Hash.from_string(blockhash_result["result"]["value"]["blockhash"])

        msg = MessageV0.try_compile(pack_pubkey, instructions, [], recent_blockhash)
        tx = VersionedTransaction(msg, [keypair])
        signed_b64 = base64.b64encode(bytes(tx)).decode()

        send_resp = await client.post(
            rpc_url,
            headers={"Content-Type": "application/json"},
            json={
                "jsonrpc": "2.0", "id": 1, "method": "sendTransaction",
                "params": [signed_b64, {"skipPreflight": False, "encoding": "base64"}],
            },
        )
        send_result = send_resp.json()
        if "error" in send_result:
            raise Exception(f"RPC sendTransaction error: {send_result['error']}")
        tx_sig = send_result["result"]

        print(f"Airdrop transaction sent: {tx_sig}")

        for attempt in range(30):
            try:
                status_resp = await client.post(
                    rpc_url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getSignatureStatuses",
                        "params": [[tx_sig], {"searchTransactionHistory": True}],
                    },
                    timeout=15,
                )
                status_data = status_resp.json()
                statuses = status_data.get("result", {}).get("value", [])
                if statuses and statuses[0] is not None:
                    status = statuses[0]
                    if status.get("err") is not None:
                        raise Exception(f"Airdrop failed on-chain: {status['err']}")
                    confirmation = status.get("confirmationStatus", "")
                    if confirmation in ("confirmed", "finalized"):
                        print(f"Airdrop confirmed: {tx_sig}")
                        return
                await asyncio.sleep(3)
            except Exception as exc:
                print(f"Airdrop confirmation attempt {attempt + 1} failed: {exc}")
                await asyncio.sleep(3)

        print(f"Airdrop sent but confirmation timeout: {tx_sig}")
