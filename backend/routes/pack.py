import random
from fastapi import APIRouter
from pydantic import BaseModel

from cards import CARDS_DATA
from config import PACK_WALLET_ADDRESS
from services.verify import verify_transaction
from services.jupiter import buy_token
from services.airdrop import airdrop_tokens

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
    verify_transaction(req.tx_signature, SOL_PER_PACK, PACK_WALLET_ADDRESS)

    selected = random.sample(CARDS_DATA, 3)

    for card in selected:
        await buy_token(card["mint_address"], SOL_PER_CARD)
        airdrop_tokens(req.buyer_wallet, card["mint_address"], 0.0)

    return BuyPackResponse(
        success=True,
        cards=selected,
        tx_signature=req.tx_signature,
    )
