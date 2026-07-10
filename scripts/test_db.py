import asyncio
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.database.postgres.models import Base, User
from app.database.postgres.operations import UserOperations
from dotenv import load_dotenv


async def main() -> None:
    load_dotenv()  # loads .env file
    database_url = os.getenv("POSTGRES_URL")
    if not database_url:
        raise RuntimeError("POSTGRES_URL environment variable not set")

    # Convert to asyncpg URL if needed
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://", "postgresql+asyncpg://", 1
        )

    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    async with async_session() as session:
        # Ensure tables exist (optional, but safe for a test)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        user_ops = UserOperations(session)

        # Create a test user
        user_data = {
            "email": "test@example.com",
            "name": "Test User",
        }
        print("Creating user...")
        user = await user_ops.create(user_data)
        print(f"Created user: id={user.id}, email={user.email}")

        # Read the user back
        fetched = await user_ops.get_by_id(user.id)
        print(
            f"Fetched user: id={fetched.id if fetched else None}, "
            f"email={fetched.email if fetched else None}"
        )

        # Delete the user
        deleted = await user_ops.delete(user.id)
        print(f"Deleted user (rows affected): {deleted}")

        # Verify deletion
        after = await user_ops.get_by_id(user.id)
        print(f"User after deletion: {after}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())