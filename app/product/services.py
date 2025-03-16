import uuid
from typing import Annotated

from app.product.schemas import ProductCreateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models import Product
from sqlmodel import select, desc
from sqlalchemy.exc import IntegrityError
from app.error.error_handler import DataBaseErrorHandler


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
            await DataBaseErrorHandler.handler_integrity_error(
                e, session, "product"
            )  # The use error_handler module was customized

    async def update_product(
        self,
        product_item: str,
        update_data: ProductCreateModel,
        user_id: str,
        session: AsyncSession,
    ):
        product_to_update = await self.get_product_item(product_item, session)

        if product_to_update is not None:
            update_data_dict = product_to_update.model_dump()

            for k, v in update_data_dict.item():
                setattr(product_to_update, k, v)
            product_to_update.user_id = uuid.UUID(user_id)
            try:
                await session.commit()
                return product_to_update
            except IntegrityError as e:
                await DataBaseErrorHandler.handler_integrity_error(e, session, "product")
        else:
            return None

    async def delete_product(self, product_item: str, session: AsyncSession):
        product_to_delete = await self.get_product_item(product_item, session)

        if product_to_delete is not None:
            await session.delete(product_to_delete)
            await session.commit()

            return product_to_delete
        else:
            return None
