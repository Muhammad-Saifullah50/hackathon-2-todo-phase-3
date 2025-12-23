import asyncio
import logging
from uuid import uuid4

import bcrypt
from sqlmodel import select

from src.config import settings
from src.db.session import session_manager
from src.models import Task, TaskPriority, TaskStatus, User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_data():
    """Seed the database with development data."""
    async with session_manager.session() as session:
        # 1. Create test user if not exists
        test_email = "test@example.com"
        result = await session.execute(select(User).where(User.email == test_email))
        user = result.scalar_one_or_none()

        if not user:
            logger.info(f"Creating test user: {test_email}")
            password = "password123"
            hashed_password = bcrypt.hashpw(
                password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

            user = User(
                email=test_email,
                name="Test User",
                password_hash=hashed_password,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        else:
            logger.info(f"Test user already exists: {test_email}")

        # 2. Create sample tasks if user has none
        result = await session.execute(select(Task).where(Task.user_id == user.id))
        existing_tasks = result.scalars().all()

        if not existing_tasks:
            logger.info(f"Creating sample tasks for user: {test_email}")
            sample_tasks = [
                Task(
                    title="Complete project setup",
                    description="Set up the backend with FastAPI and SQLModel",
                    status=TaskStatus.COMPLETED,
                    priority=TaskPriority.HIGH,
                    user_id=user.id,
                ),
                Task(
                    title="Implement database migrations",
                    description="Use Alembic for async migrations",
                    status=TaskStatus.COMPLETED,
                    priority=TaskPriority.HIGH,
                    user_id=user.id,
                ),
                Task(
                    title="Write integration tests",
                    description="Verify database connection and CRUD operations",
                    status=TaskStatus.PENDING,
                    priority=TaskPriority.MEDIUM,
                    user_id=user.id,
                ),
                Task(
                    title="Add authentication",
                    description="Implement JWT based auth",
                    status=TaskStatus.PENDING,
                    priority=TaskPriority.MEDIUM,
                    user_id=user.id,
                ),
                Task(
                    title="Polish UI",
                    description="Make the frontend look beautiful",
                    status=TaskStatus.PENDING,
                    priority=TaskPriority.LOW,
                    user_id=user.id,
                ),
            ]
            for task in sample_tasks:
                session.add(task)
            await session.commit()
            logger.info("Sample tasks created successfully")
        else:
            logger.info(f"User already has {len(existing_tasks)} tasks, skipping task seed.")


if __name__ == "__main__":
    asyncio.run(seed_data())
