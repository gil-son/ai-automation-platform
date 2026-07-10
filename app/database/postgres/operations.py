"""Database operations for the AI automation platform."""

from typing import List, Optional, Type, TypeVar, Generic, Dict, Any
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Base, User, Agent, Conversation, Document, Client, Message, Evaluation

# Generic type variable for model classes
ModelType = TypeVar("ModelType", bound=Base)


class BaseOperations(Generic[ModelType]):
    """Base class for CRUD operations."""

    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        self.model = model
        self.db_session = db_session

    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**obj_in)
        self.db_session.add(db_obj)
        await self.db_session.commit()
        await self.db_session.refresh(db_obj)
        return db_obj

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get a record by ID."""
        result = await self.db_session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get multiple records."""
        result = await self.db_session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def update(self, id: int, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """Update a record by ID."""
        await self.db_session.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**obj_in)
        )
        await self.db_session.commit()
        return await self.get_by_id(id)

    async def delete(self, id: int) -> bool:
        """Delete a record by ID."""
        result = await self.db_session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.db_session.commit()
        return result.rowcount > 0


# Specific operations for each model

class UserOperations(BaseOperations[User]):
    """User operations."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(User, db_session)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db_session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()


class AgentOperations(BaseOperations[Agent]):
    """Agent operations."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(Agent, db_session)

    async def get_by_user_and_name(self, user_id: int, name: str) -> Optional[Agent]:
        """Get agent by user ID and name."""
        result = await self.db_session.execute(
            select(Agent).where(Agent.user_id == user_id, Agent.name == name)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Agent]:
        """Get agents by user ID."""
        result = await self.db_session.execute(
            select(Agent)
            .where(Agent.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


class ConversationOperations(BaseOperations[Conversation]):
    """Conversation operations."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(Conversation, db_session)

    async def get_by_agent_id(self, agent_id: int, skip: int = 0, limit: int = 100) -> List[Conversation]:
        """Get conversations by agent ID."""
        result = await self.db_session.execute(
            select(Conversation)
            .where(Conversation.agent_id == agent_id)
            .order_by(Conversation.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


class DocumentOperations(BaseOperations[Document]):
    """Document operations."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(Document, db_session)

    async def get_by_agent_id(self, agent_id: int, skip: int = 0, limit: int = 100) -> List[Document]:
        """Get documents by agent ID."""
        result = await self.db_session.execute(
            select(Document)
            .where(Document.agent_id == agent_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_filename_and_agent(self, filename: str, agent_id: int) -> Optional[Document]:
        """Get document by filename and agent ID."""
        result = await self.db_session.execute(
            select(Document).where(Document.filename == filename, Document.agent_id == agent_id)
        )
        return result.scalar_one_or_none()


class ClientOperations(BaseOperations[Client]):
    """Client operations."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(Client, db_session)

    async def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Client]:
        """Get clients by user ID."""
        result = await self.db_session.execute(
            select(Client)
            .where(Client.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


class MessageOperations(BaseOperations[Message]):
    """Message operations."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(Message, db_session)

    async def get_by_agent_id(self, agent_id: int, skip: int = 0, limit: int = 100) -> List[Message]:
        """Get messages by agent ID."""
        result = await self.db_session.execute(
            select(Message)
            .where(Message.agent_id == agent_id)
            .order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_client_id(self, client_id: int, skip: int = 0, limit: int = 100) -> List[Message]:
        """Get messages by client ID."""
        result = await self.db_session.execute(
            select(Message)
            .where(Message.client_id == client_id)
            .order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


class EvaluationOperations(BaseOperations[Evaluation]):
    """Evaluation operations."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(Evaluation, db_session)

    async def get_by_agent_id(self, agent_id: int, skip: int = 0, limit: int = 100) -> List[Evaluation]:
        """Get evaluations by agent ID."""
        result = await self.db_session.execute(
            select(Evaluation)
            .where(Evaluation.agent_id == agent_id)
            .order_by(Evaluation.timestamp.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


# Dependency to get DB session
async def get_db() -> AsyncSession:
    """
    Dependency function that yields a database session.
    This should be overridden by the application's dependency injection system.
    """
    # This is a placeholder - the actual implementation will be provided by the app
    from app.database.postgres import async_session
    async with async_session() as session:
        yield session