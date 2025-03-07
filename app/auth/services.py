from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, or_
from app.db.models import User
from app.auth.schemas import CreateUser
from app.auth.utils import get_hashed_password, verify_password


class UserService:
    async def get_user(self, user, session: AsyncSession):
        statement = select(User).where(or_(User.email == user, User.username == user))
        result = await session.exec(statement)
        user = result.one_or_none()
        return user

    async def user_exists(self, username, email, session: AsyncSession):
        statement = select(User).where(or_(User.username == username, User.email == email))
        results = await session.exec(statement)
        existing_user = results.first()
        if existing_user.email == email:
            return "email_exists"
        if existing_user.username == username:
            return "username_exists"
        return False



    async def get_username(self, username, session: AsyncSession):
        statement = select(User).where(User.username == username)
        results = await session.exec(statement)
        user = results.first()
        return user

    async def email_exists(self, email, session: AsyncSession):
        user = await self.get_user(email, session)
        return True if user is not None else False

    async def username_exists(self, username, session: AsyncSession):
        user = await self.get_username(username, session)
        return True if user is not None else False

    async def create_user(self, user_data: CreateUser, session: AsyncSession):
        hashed_password = get_hashed_password(user_data.password)
        user_dict = user_data.model_dump(exclude="password")
        new_user = User(**user_dict, hashed_password=hashed_password)
        new_user.role = "user"

        session.add(new_user)
        await session.commit()
        return new_user

    async def authenticate_user(self, login_input: str, password: str, session: AsyncSession):
        user = await self.get_user(login_input, session)
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user

    async def update_user(self, user: User, user_data: dict, session: AsyncSession):
        for k, v in user_data.items():
            setattr(user, k, v)
        session.add(user)
        await session.commit()
        return user
