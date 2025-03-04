from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.db.models import User
from app.auth.schemas import CreateUser
from app.auth.utils import get_hashed_password


class UserService:
    async def get_email(self, email, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        user = result.first()
        return user

    async def get_username(self, username, session: AsyncSession):
        statement = select(User).where(User.username == username)
        results = await session.exec(statement)
        user = results.first()
        return user

    async def email_exists(self, email, session: AsyncSession):
        user = await self.get_email(email, session)
        return True if user is not None else False

    async def username_exists(self, username, session: AsyncSession):
        username = await self.get_username(username, session)
        return True if username is not None else False

    async def create_user(self, user_data: CreateUser, session: AsyncSession):
        hashed_password = get_hashed_password(user_data.password)
        user_dict = user_data.model_dump(exclude="password")
        new_user = User(user_dict, hashed_password=hashed_password)
        new_user.role = "user"

        session.add(new_user)
        await session.commit()
        return new_user

    async def update_user(self, user: User, user_data: dict, session: AsyncSession):
        for k, v in user_data.items():
            setattr(user, k, v)
        session.add(user)
        await session.commit()
        return user

