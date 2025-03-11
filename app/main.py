from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.auth.routes import oauth_route
from app.product.routes import product_route
from app.db.session import create_event, create_db_and_tables, engine, AsyncSessionLocal
from app.auth.schemas import AdminCreateModel
from app.auth.services import AdminService

admin_service = AdminService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Connecting to MySQL and setting up event...")
    async with engine.begin() as conn:
        await create_db_and_tables()
        await create_event()
    async with AsyncSessionLocal() as session:
        admin_data = AdminCreateModel()
        await admin_service.create_admin(admin_data=admin_data, session=session)
    yield
    await engine.dispose()
    print("Database connection closed.")


app = FastAPI(lifespan=lifespan)

app.include_router(oauth_route, tags=["oauth"])
app.include_router(product_route, tags=["product"])
