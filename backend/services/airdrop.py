import asyncio
import base64
import struct

import httpx
from solders.hash import Hash
from solders.instruction import AccountMeta, Instruction
from solders.keypair import Keypair
from solders.message import Message
from solders.pubkey import Pubkey
from solders.transaction import Transaction

from config import TEST_MODE, PACK_WALLET_PRIVATE_KEY, SOLANA_RPC_URL

ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
SYSTEM_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")
RENT_ID = Pubkey.from_string("SysvarRent111111111111111111111111111111111")


def get_associated_token_address(owner: Pubkey, mint: Pubkey) -> Pubkey:
    seeds = [bytes(owner), bytes(TOKEN_PROGRAM_ID), bytes(mint)]
    ata, _ = Pubkey.find_program_address(seeds, ASSOCIATED_TOKEN_PROGRAM_ID)
    return ata


def create_ata_instruction(payer: Pubkey, owner: Pubkey, mint: Pubkey) -> Instruction:
    ata = get_associated_token_address(owner, mint)
    accounts = [
        AccountMeta(payer, True, True),
        AccountMeta(ata, False, True),
        AccountMeta(owner, False, False),
        AccountMeta(mint, False, False),
        AccountMeta(SYSTEM_PROGRAM_ID, False, False),
        AccountMeta(TOKEN_PROGRAM_ID, False, False),
        AccountMeta(RENT_ID, False, False),
    ]
    return Instruction(ASSOCIATED_TOKEN_PROGRAM_ID, accounts, b"")


def transfer_checked_instruction(
    source: Pubkey, mint: Pubkey, dest: Pubkey, owner: Pubkey, amount: int, decimals: int,
) -> Instruction:
    accounts = [
        AccountMeta(source, False, True),
        AccountMeta(mint, False, False),
        AccountMeta(dest, False, True),
        AccountMeta(owner, True, False),
    ]
    data = struct.pack("<BQB", 12, amount, decimals)
    return Instruction(TOKEN_PROGRAM_ID, accounts, data)


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

    sender_ata = get_associated_token_address(pack_pubkey, mint_pubkey)
    recipient_ata = get_associated_token_address(recipient_pubkey, mint_pubkey)

    rpc_url = SOLANA_RPC_URL.rstrip("/")

    async with httpx.AsyncClient(timeout=30) as client:
        ata_resp = await client.post(
            f"{rpc_url}",
            json={
                "jsonrpc": "2.0", "id": 1, "method": "getAccountInfo",
                "params": [str(recipient_ata), {"encoding": "base64"}],
            },
        )
        ata_data = ata_resp.json()
        ata_exists = ata_data.get("result", {}).get("value") is not None

        instructions = []

        if not ata_exists:
            print(f"Recipient ATA {recipient_ata} does not exist. Creating...")
            instructions.append(create_ata_instruction(pack_pubkey, recipient_pubkey, mint_pubkey))

        mint_resp = await client.post(
            f"{rpc_url}",
            json={
                "jsonrpc": "2.0", "id": 1, "method": "getAccountInfo",
                "params": [str(mint_pubkey), {"encoding": "base64"}],
            },
        )
        mint_result = mint_resp.json()
        mint_value = mint_result.get("result", {}).get("value")
        if mint_value is None:
            raise Exception(f"Mint {mint_address} does not exist")
        mint_data = base64.b64decode(mint_value["data"][0])
        decimals = mint_data[44]

        transfer_amount = int(amount)

        instructions.append(
            transfer_checked_instruction(
                sender_ata, mint_pubkey, recipient_ata, pack_pubkey, transfer_amount, decimals,
            )
        )

        blockhash_resp = await client.post(
            f"{rpc_url}",
            json={
                "jsonrpc": "2.0", "id": 1, "method": "getLatestBlockhash",
                "params": [],
            },
        )
        blockhash_result = blockhash_resp.json()
        recent_blockhash = Hash.from_string(blockhash_result["result"]["value"]["blockhash"])

        message = Message.new_with_blockhash(instructions, pack_pubkey, recent_blockhash)
        tx = Transaction.new_unsigned(message)
        tx.sign([keypair])
        signed_b64 = base64.b64encode(bytes(tx)).decode()

        send_resp = await client.post(
            f"{rpc_url}",
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

        for attempt in range(15):
            await asyncio.sleep(3)
            confirm_resp = await client.post(
                f"{rpc_url}",
                json={
                    "jsonrpc": "2.0", "id": 1, "method": "getTransaction",
                    "params": [tx_sig, {"encoding": "base64"}],
                },
            )
            if confirm_resp.status_code == 200:
                confirm_result = confirm_resp.json()
                if confirm_result.get("result") is not None:
                    print(f"Airdrop confirmed: {tx_sig}")
                    return

        print(f"Airdrop sent but confirmation timeout: {tx_sig}")
