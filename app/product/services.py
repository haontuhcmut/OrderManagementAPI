from app.product.schemas import ProductCreateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models import Product

class ProductService:
    async def create_product(self, book_data: ProductCreateModel, session: AsyncSession):
        book_data_dict = book_data.model_dump()
        new_product = Product(**book_data_dict)

        session.add(new_product)
        await session.commit()
        return new_product



