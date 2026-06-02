import json
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.instruction import AccountMeta, Instruction
from solders.transaction import Transaction
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
from spl.token.instructions import (
    get_associated_token_address,
    create_associated_token_account,
    transfer_checked,
    TransferCheckedParams,
)

from config import TEST_MODE, PACK_WALLET_PRIVATE_KEY, SOLANA_RPC_URL

SYS_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")
RENT = Pubkey.from_string("SysvarRent111111111111111111111111111111111")


async def airdrop_tokens(recipient_wallet: str, mint_address: str, amount: float) -> None:
    if TEST_MODE:
        print("TEST MODE: skipping airdrop")
        return

    print(f"Airdropping {amount} of {mint_address} to {recipient_wallet}...")

    keypair_bytes = json.loads(PACK_WALLET_PRIVATE_KEY)
    keypair = Keypair.from_bytes(bytes(keypair_bytes))
    pack_pubkey = keypair.pubkey()

    mint_pubkey = Pubkey.from_string(mint_address)
    recipient_pubkey = Pubkey.from_string(recipient_wallet)

    sender_ata = get_associated_token_address(pack_pubkey, mint_pubkey)
    recipient_ata = get_associated_token_address(recipient_pubkey, mint_pubkey)

    rpc_client = Client(SOLANA_RPC_URL)

    existing = rpc_client.get_account_info(recipient_ata)
    instructions = []

    if existing.value is None:
        print(f"Recipient ATA {recipient_ata} does not exist. Creating...")
        create_ix = create_associated_token_account(
            payer=pack_pubkey,
            owner=recipient_pubkey,
            mint=mint_pubkey,
        )
        instructions.append(create_ix)

    mint_info = rpc_client.get_account_info_json_parsed(mint_pubkey)
    if mint_info.value is None:
        raise Exception(f"Mint {mint_address} does not exist")
    decimals = mint_info.value.data.parsed["info"]["decimals"]

    transfer_amount = int(amount * (10 ** decimals))

    transfer_ix = transfer_checked(
        TransferCheckedParams(
            program_id=TOKEN_PROGRAM_ID,
            source=sender_ata,
            mint=mint_pubkey,
            dest=recipient_ata,
            owner=pack_pubkey,
            amount=transfer_amount,
            decimals=decimals,
        )
    )
    instructions.append(transfer_ix)

    blockhash_resp = rpc_client.get_latest_blockhash()
    recent_blockhash = blockhash_resp.value.blockhash

    tx = Transaction.new_with_payer(instructions, payer=pack_pubkey)
    tx.sign([keypair], recent_blockhash)

    result = rpc_client.send_raw_transaction(bytes(tx))
    tx_sig = result.value

    rpc_client.confirm_transaction(tx_sig, commitment=Confirmed)

    print(f"Airdrop confirmed: {tx_sig}")
