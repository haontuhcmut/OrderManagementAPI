from fastapi import APIRouter, HTTPException, status, Depends
from app.db.models import Product
from app.product.schemas import ProductCreateModel
from app.product.services import ProductService
from app.auth.dependencies import SessionDep, AccessTokenBearer


access_token_bearer = AccessTokenBearer()
product_services = ProductService()

product_route = APIRouter()


@product_route.post("/", status_code=status.HTTP_201_CREATED, response_model=Product)
async def create_a_product(
    product_data: ProductCreateModel,
    token_details: Depends(access_token_bearer),
    session: SessionDep,
) -> dict:
    new_product = product_services.create_product(product_data, session)
