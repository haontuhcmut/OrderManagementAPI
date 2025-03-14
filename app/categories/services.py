from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from sqlalchemy.exc import IntegrityError
from app.db.models import Category
from app.categories.schemas import CategoryCreateModel
from fastapi import HTTPException, status
import uuid


class CategoryServices:
    async def create_category(self, category_data: CategoryCreateModel, user_id: str, session: AsyncSession):
        category_data_dict = category_data.model_dump()
        new_category = Category(**category_data_dict)
        new_category.user_id = uuid.UUID(user_id)
        try:
            session.add(new_category)
            await session.commit()
            return new_category
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")

    async def category_item(self, category_id: str, session: AsyncSession):
        statement = select(Category).where(Category.id == uuid.UUID(category_id))
        result = await session.exec(statement)
        category = result.first()
        return category

    async def get_categories(self, session: AsyncSession):
        statement = select(Category).order_by(desc(Category.name))
        results = await session.exec(statement)
        categories = results.all()
        return categories


    async def update_category(self, category_id: str, update_data: CategoryCreateModel, session: AsyncSession):
        category_to_update = await self.category_item(category_id, session)

        if category_to_update is not None:
            update_data_dict = update_data.model_dump()

            for k, v in update_data_dict.items():
                setattr(category_to_update, k, v)

            await session.commit()
            return category_to_update
        else:
            return None

    async def delete_category(self, category_id: str, session: AsyncSession):
        category_to_delete = await self.category_item(category_id, session)

        if category_to_delete is not None:
            await session.delete(category_to_delete)
            await session.commit()

            return category_to_delete
        else:
            return None
