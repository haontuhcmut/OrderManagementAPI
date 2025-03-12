from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.auth.routes import oauth_route
from app.product.routes import product_route
from app.categories.routes import categories_routes
from app.db.session import create_event, engine, AsyncSessionLocal
from app.auth.schemas import AdminCreateModel
from app.auth.services import AdminService

version = "v1"

description = """
A REST API for a Raw Material Sample web service.

This REST API is able to:
- Create user validation using OAuth2 standard.
- Create CRUD product, categories,...
- User can send result.
"""

version_prefix = f"/api/{version}"

admin_service = AdminService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Connecting to MySQL and setting up event...")
    async with engine.begin() as conn:
        await create_event()
    async with AsyncSessionLocal() as session:
        admin_data = AdminCreateModel()
        await admin_service.create_admin(admin_data=admin_data, session=session)
    yield
    await engine.dispose()
    print("Database connection closed.")


app = FastAPI(
    title="Order Management",
    description=description,
    version=version,
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
    lifespan=lifespan
)

app.include_router(oauth_route, tags=["oauth"])
app.include_router(product_route, tags=["product"])
app.include_router(categories_routes, tags=["category"])

