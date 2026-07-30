__anchor__ = "db-clients"
# schema-ref: project-schema.yaml#/shared_modules/2

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.shared.settings import settings

engine = create_async_engine(
    settings.postgres_dsn, echo=settings.app_debug, pool_size=10, max_overflow=20
)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
