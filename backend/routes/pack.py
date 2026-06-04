import random
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import BaseModel

from cards import CARDS_DATA
from config import (
    PACK_WALLET_ADDRESS,
    PUMPPACKS_TOKEN_MINT,
    SOL_PER_PACK,
    SOL_PER_CARD_AIRDROP,
    CARDS_PER_PACK,
    RARITY_WEIGHTS,
)
from services.verify import verify_transaction
from services.jupiter import buy_token
from services.airdrop import airdrop_tokens
from database import log_purchase, log_card_pull, log_airdrop, check_signature_used

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


def weighted_card_draw(n: int) -> list:
    weights = [RARITY_WEIGHTS[card["rarity"]] for card in CARDS_DATA]
    selected = []
    pool = list(zip(CARDS_DATA, weights))
    while len(selected) < n and pool:
        cards, w = zip(*pool)
        chosen = random.choices(cards, weights=w, k=1)[0]
        selected.append(chosen)
        pool = [(c, wt) for c, wt in pool if c["id"] != chosen["id"]]
    return selected


async def process_pack_background(purchase_id: int, buyer_wallet: str, selected_cards: list):
    if PUMPPACKS_TOKEN_MINT:
        try:
            await buy_token(PUMPPACKS_TOKEN_MINT, SOL_PER_PACK * 0.70)
        except Exception as e:
            print(f"Flywheel buy failed: {e}")

    for card in selected_cards:
        try:
            swap_sig, out_amount = await buy_token(card["mint_address"], SOL_PER_CARD_AIRDROP)
            await log_card_pull(purchase_id, card["id"], card["name"], card["ticker"], card["mint_address"])
            if out_amount > 0:
                await airdrop_tokens(buyer_wallet, card["mint_address"], int(out_amount))
                await log_airdrop(purchase_id, buyer_wallet, card["mint_address"], out_amount, swap_sig)
        except Exception as e:
            print(f"Error processing card {card['id']}: {e}")


class BuyPackRequest(BaseModel):
    buyer_wallet: str
    tx_signature: str


class BuyPackResponse(BaseModel):
    success: bool
    cards: list
    tx_signature: str


@router.post("/buy-pack", response_model=BuyPackResponse)
@limiter.limit("10/minute")
async def buy_pack(request: Request, req: BuyPackRequest, background_tasks: BackgroundTasks):
    verified = await verify_transaction(req.tx_signature, SOL_PER_PACK, PACK_WALLET_ADDRESS)
    if not verified:
        raise HTTPException(status_code=400, detail="Transaction verification failed")

    if await check_signature_used(req.tx_signature):
        raise HTTPException(status_code=400, detail="Transaction already used")

    try:
        purchase_id = await log_purchase(req.buyer_wallet, req.tx_signature, SOL_PER_PACK)
    except Exception:
        raise HTTPException(status_code=400, detail="Transaction already processed")

    selected_cards = weighted_card_draw(CARDS_PER_PACK)
    background_tasks.add_task(process_pack_background, purchase_id, req.buyer_wallet, selected_cards)

    return BuyPackResponse(
        success=True,
        cards=selected_cards,
        tx_signature=req.tx_signature,
    )
