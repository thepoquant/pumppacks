import random
from fastapi import APIRouter
from pydantic import BaseModel

from cards import CARDS_DATA

router = APIRouter()

class BuyPackRequest(BaseModel):
    buyer_wallet: str
    tx_signature: str

class BuyPackResponse(BaseModel):
    success: bool
    cards: list
    tx_signature: str

@router.post("/buy-pack", response_model=BuyPackResponse)
async def buy_pack(req: BuyPackRequest):
    selected = random.sample(CARDS_DATA, 3)
    return BuyPackResponse(
        success=True,
        cards=selected,
        tx_signature=req.tx_signature,
    )
