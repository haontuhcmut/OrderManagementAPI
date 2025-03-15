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

        try:
            session.add(new_product)
            await session.commit()
            return new_product
        except IntegrityError as e:
            await session.rollback()
            if "1062" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "error": "IntegrityError",
                        "message": f"The product name {new_product.name} already exists.",
                        "hint": "Please choose a different name",
                    }
                )
            if "1452" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "IntegrityError",
                        "message": f"The selected category does not exists.",
                        "hint": "Please check and try again."
                    }
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Database integrity constraint failed. Please check your input and try again.",
                )
