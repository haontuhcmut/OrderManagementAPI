from sqlmodel import SQLModel, text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from app.config import Config

database_url = Config.DATABASE_URL

engine = create_async_engine(url=database_url, future=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False, # ⚠️ Objects will NOT be automatically refreshed after commit!
)
"""
Important Note:
- `expire_on_commit=False` means objects **retain their state** after commit.
- This prevents automatic expiration, avoiding additional queries.
- Use `session.refresh(object)` if you need updated values from the database.
"""

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def create_event():
    """
    Create a MYSQL event to delete unverified users every 5 minutes.
    Important Note:
    You need either the SUPER or SYSTEM_VARIABLES_ADMIN privilege in database.
    """
    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: sync_conn.execute(text("""SET GLOBAL event_scheduler = ON;""")))
        await conn.execute(text("""DROP EVENT IF EXISTS delete_unverified_users;"""))
        await conn.execute(text("""
            CREATE EVENT IF NOT EXISTS delete_unverified_users
            ON SCHEDULE EVERY 5 MINUTE
            DO
            DELETE FROM users 
            WHERE is_verified = FALSE 
            AND created_at < NOW() - INTERVAL 1 HOUR
            LIMIT 100;
        """))
        await conn.commit()
        print("Event 'delete_unverified_users' has been created!")


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session




