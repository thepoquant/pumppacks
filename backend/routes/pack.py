import random
from fastapi import APIRouter
from pydantic import BaseModel

from cards import CARDS_DATA
from config import PACK_WALLET_ADDRESS
from services.verify import verify_transaction
from services.jupiter import buy_token
from services.airdrop import airdrop_tokens
from database import log_purchase, log_card_pull, log_airdrop

router = APIRouter()

SOL_PER_PACK = 0.5
SOL_PER_CARD = SOL_PER_PACK / 3


class BuyPackRequest(BaseModel):
    buyer_wallet: str
    tx_signature: str


class BuyPackResponse(BaseModel):
    success: bool
    cards: list
    tx_signature: str


@router.post("/buy-pack", response_model=BuyPackResponse)
async def buy_pack(req: BuyPackRequest):
    await verify_transaction(req.tx_signature, SOL_PER_PACK, PACK_WALLET_ADDRESS)

    purchase_id = await log_purchase(req.buyer_wallet, req.tx_signature, SOL_PER_PACK)

    selected = random.sample(CARDS_DATA, 3)

    for card in selected:
        swap_sig, out_amount = await buy_token(card["mint_address"], SOL_PER_CARD)
        await log_card_pull(
            purchase_id,
            card["id"],
            card["name"],
            card["ticker"],
            card["mint_address"],
        )
        await airdrop_tokens(req.buyer_wallet, card["mint_address"], out_amount)
        await log_airdrop(purchase_id, req.buyer_wallet, card["mint_address"], out_amount, swap_sig)

    return BuyPackResponse(
        success=True,
        cards=selected,
        tx_signature=req.tx_signature,
    )
