from app.categories.schemas import CategoryCreateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.models import Category

class CategoryServices:
    async def create_category(category_data: CategoryCreateModel, session:AsyncSession):
        category_data_dict = category_data.model_dump()
        new_category = Category(**category_data_dict)

        session.add(new_category)
        await session.commit()
        return new_category
