from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.pack import router as pack_router
from routes.dashboard import router as dashboard_router
from database import init_db

app = FastAPI(title="Pumppacks API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pack_router)
app.include_router(dashboard_router)


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/health")
async def health():
    return {"status": "ok"}
