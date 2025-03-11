from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends
from app.db.models import Product
from app.product.schemas import ProductCreateModel
from app.product.services import ProductService
from app.auth.dependencies import SessionDep, AccessTokenBearer, RoleChecker


access_token_bearer = AccessTokenBearer()
product_services = ProductService()
admin_role_checker = Depends(RoleChecker(["admin"]))

product_route = APIRouter()


@product_route.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Product,
    dependencies=[admin_role_checker],
)
async def create_a_product(
    product_data: ProductCreateModel,
    session: SessionDep,
    token_details: Annotated[dict, Depends(access_token_bearer)],
) -> dict:
    new_product = await product_services.create_product(product_data, session)
    return new_product
