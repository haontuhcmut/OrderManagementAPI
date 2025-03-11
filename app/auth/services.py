from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, or_, text
from app.db.models import User
from app.auth.schemas import CreateUser, AdminCreateModel
from app.auth.utils import get_hashed_password, verify_password


class UserService:
    async def get_user(self, user, session: AsyncSession):
        statement = select(User).where(or_(User.email == user, User.username == user))
        result = await session.exec(statement)
        user = result.one_or_none()
        return user

    async def user_exists(self, username_or_email, session: AsyncSession):
        user = await self.get_user(username_or_email, session)
        if user:
            if user.email == username_or_email:
                return "email_exists"
            if user.username == username_or_email:
                return "username_exists"
        return False


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

class AdminService(UserService):
    async def create_admin(self, admin_data: AdminCreateModel, session: AsyncSession):
        get_admin_email = await self.get_user(admin_data.email, session)
        if get_admin_email is not None:
            return "Root admin already exists. Skipping creation."
        get_admin_username = await self.get_user(admin_data.username, session)
        if get_admin_username is not None:
            return "Root admin already exists. Skipping creation."
        hashed_password = get_hashed_password(admin_data.password)
        admin_data_dict = admin_data.model_dump(exclude={"password"})
        new_admin = User(**admin_data_dict, hashed_password=hashed_password)
        session.add(new_admin)
        await session.commit()
