from app.product.schemas import ProductCreateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models import Product
from sqlmodel import select, desc

class ProductServices:
    async def get_product(self, session: AsyncSession):
        statement = select(Product).order_by(desc(Product.created_at))
        results = await session.exec(statement)
        products = results.all()
        return products

    async def get_product_item(self, product_item: str, session: AsyncSession):
        statement = select(Product).where(Product.name == product_item)
        result = await session.exec(statement)
        product = result.first()
        return product


    async def create_product(self, product_data: ProductCreateModel, session: AsyncSession):
        product_data_dict = product_data.model_dump()
        new_product = Product(**product_data_dict)
        session.add(new_product)
        await session.commit()
        return new_product




