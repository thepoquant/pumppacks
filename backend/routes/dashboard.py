from fastapi import APIRouter

router = APIRouter()

@router.get("/stats")
async def get_stats():
    return {
        "total_packs_opened": 0,
        "total_volume_sol": 0.0,
    }
