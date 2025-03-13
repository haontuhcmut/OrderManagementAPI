from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from app.db.models import Category
from app.categories.schemas import CategoryCreateModel

class CategoryServices:
    async def create_category(self, category_data: CategoryCreateModel, session: AsyncSession):
        category_data_dict = category_data.model_dump()
        new_category = Category(**category_data_dict)

        session.add(new_category)
        await session.commit()
        return new_category

    async def category_item(self, category_name: str, session: AsyncSession):
        statement = select(Category).where(Category.name == category_name)
        result = await session.exec(statement)
        category = result.one_or_none()

        return category

    async def get_categories(self, session: AsyncSession):
        statement = select(Category).order_by(desc(Category.name))
        results = await session.exec(statement)
        categories = results.all()

        return categories

    async def update_category(self, category_name: str, update_data: CategoryCreateModel, session: AsyncSession):
        category_to_update = await self.category_item(category_name, session)

        if category_to_update is not None:
            update_data_dict = update_data.model_dump()

            for k, v in update_data_dict.items():
                setattr(category_to_update, k, v)

            await session.commit()
            return category_to_update
        else:
            return None

