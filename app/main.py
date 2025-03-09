from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.auth.routes import oauth_route
from app.db.session import create_event, create_db_and_tables, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Connecting to MySQL and setting up event...")
    async with engine.begin() as conn:
        await create_db_and_tables()
        await create_event()
    yield
    await engine.dispose()
    print("❌ Database connection closed.")


app = FastAPI(lifespan=lifespan)

app.include_router(oauth_route, tags=["oauth"])
