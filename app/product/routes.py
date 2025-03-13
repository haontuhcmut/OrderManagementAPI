from fastapi import APIRouter, Depends
from app.db.models import Product
from app.auth.dependencies import SessionDep, RoleChecker, AccessTokenBearer
from typing import Annotated
from app.product.services import ProductServices


access_token_bearer = AccessTokenBearer()
admin_role_checker = Depends(RoleChecker(["admin"]))
role_checker = Depends(RoleChecker(["admin", "user"]))
product_services = ProductServices()

product_route = APIRouter()

@product_route.get("/", response_model=list[Product], dependencies=[role_checker])
async def get_product(session: SessionDep, _: Annotated[dict, Depends(access_token_bearer)]):
    products = await product_services.get_product(session)
    return products


