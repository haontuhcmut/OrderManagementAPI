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
    contact={
        "name": "Hao Nguyen",
        "url": "https://github.com/haontuhcmut",
        "email": "nguyenminhhao1188@gmail.com"
    },
    openapi_url= f"{version_prefix}/openapi.json",
    docs_url= f"{version_prefix}/docs",
    redoc_url=f"{version_prefix}/redoc",
    lifespan=lifespan
)

app.include_router(oauth_route, prefix=f"{version_prefix}/auth" , tags=["auth"])
app.include_router(product_route, prefix=f"{version_prefix}/products" , tags=["product"])
app.include_router(categories_routes, prefix=f"{version_prefix}/category", tags=["category"])

