import asyncpg
from config import DATABASE_URL

pool = None


async def init_db():
    global pool
    if not DATABASE_URL:
        print("DATABASE_URL not set — skipping database initialization")
        return

    try:
        pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)

        async with pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS pack_purchases (
                    id SERIAL PRIMARY KEY,
                    buyer_wallet TEXT NOT NULL,
                    tx_signature TEXT UNIQUE NOT NULL,
                    sol_amount FLOAT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS card_pulls (
                    id SERIAL PRIMARY KEY,
                    purchase_id INTEGER REFERENCES pack_purchases(id),
                    card_id TEXT NOT NULL,
                    card_name TEXT NOT NULL,
                    ticker TEXT NOT NULL,
                    mint_address TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS airdrops (
                    id SERIAL PRIMARY KEY,
                    purchase_id INTEGER REFERENCES pack_purchases(id),
                    recipient_wallet TEXT NOT NULL,
                    mint_address TEXT NOT NULL,
                    amount FLOAT NOT NULL,
                    tx_signature TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
        print("Database tables initialized")
    except Exception as e:
        print(f"Database initialization failed: {e}")


async def log_purchase(buyer_wallet: str, tx_signature: str, sol_amount: float) -> int:
    if not pool:
        print("DB not configured, skipping log")
        return 0
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO pack_purchases (buyer_wallet, tx_signature, sol_amount) VALUES ($1, $2, $3) RETURNING id",
            buyer_wallet, tx_signature, sol_amount,
        )
        return row["id"]


async def log_card_pull(purchase_id: int, card_id: str, card_name: str, ticker: str, mint_address: str):
    if not pool:
        return
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO card_pulls (purchase_id, card_id, card_name, ticker, mint_address) VALUES ($1, $2, $3, $4, $5)",
            purchase_id, card_id, card_name, ticker, mint_address,
        )


async def log_airdrop(purchase_id: int, recipient_wallet: str, mint_address: str, amount: float, tx_signature: str):
    if not pool:
        return
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO airdrops (purchase_id, recipient_wallet, mint_address, amount, tx_signature) VALUES ($1, $2, $3, $4, $5)",
            purchase_id, recipient_wallet, mint_address, amount, tx_signature,
        )


async def get_stats() -> dict:
    if not pool:
        return {"total_packs_opened": 0, "total_volume_sol": 0.0}
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT COUNT(*) as total_packs_opened, COALESCE(SUM(sol_amount), 0) as total_volume_sol FROM pack_purchases"
        )
        return {
            "total_packs_opened": row["total_packs_opened"],
            "total_volume_sol": float(row["total_volume_sol"]),
        }
