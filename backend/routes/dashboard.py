from fastapi import APIRouter
from database import get_stats as db_get_stats

router = APIRouter()


@router.get("/stats")
async def stats():
    return await db_get_stats()
