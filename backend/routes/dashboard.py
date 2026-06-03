from fastapi import APIRouter
from database import get_stats

router = APIRouter()

@router.get("/stats")
async def stats():
    return await get_stats()
