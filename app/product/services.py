import uuid

from app.product.schemas import ProductCreateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models import Product
from sqlmodel import select, desc
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status


class ProductServices:
    async def get_product(self, session: AsyncSession):
        statement = select(Product).order_by(desc(Product.created_at))
        results = await session.exec(statement)
        products = results.all()
        return products

    async def get_product_item(self, product_item: str, session: AsyncSession):
        statement = select(Product).where(Product.id == uuid.UUID(product_item))
        result = await session.exec(statement)
        product = result.first()
        return product

    async def create_product(
        self, product_data: ProductCreateModel, user_id: str, session: AsyncSession
    ):
        product_data_dict = product_data.model_dump()
        new_product = Product(**product_data_dict)
        new_product.user_id = uuid.UUID(user_id)

        session.add(new_product)
        await session.commit()
        return new_product
