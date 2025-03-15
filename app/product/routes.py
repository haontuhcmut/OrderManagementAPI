from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.db.models import Product
from app.auth.dependencies import SessionDep, RoleChecker, AccessTokenBearer
from typing import Annotated
from app.product.services import ProductServices
from app.product.schemas import ProductCreateModel


access_token_bearer = AccessTokenBearer()
admin_role_checker = Depends(RoleChecker(["admin"]))
role_checker = Depends(RoleChecker(["admin", "user"]))
product_services = ProductServices()

product_route = APIRouter()


@product_route.get("/", response_model=list[Product], dependencies=[role_checker])
async def get_product(
    session: SessionDep, _: Annotated[dict, Depends(access_token_bearer)]
):
    products = await product_services.get_product(session)
    return products


@product_route.get(
    "/{product_item}", response_model=Product, dependencies=[role_checker]
)
async def get_product_item(
    product_item: str,
    session: SessionDep,
    _: Annotated[dict, Depends(access_token_bearer)],
) -> dict:
    product = await product_services.get_product_item(product_item, session)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return product


@product_route.post("/", response_model=Product, dependencies=[admin_role_checker])
async def create_product(
    product_data: ProductCreateModel,
    token_data: Annotated[dict, Depends(access_token_bearer)],
    session: SessionDep,
):
    user_id = token_data.get("user_id")
    new_product = await product_services.create_product(product_data, user_id, session)
    return new_product

