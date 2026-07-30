__anchor__ = "repositories"

import uuid
from collections.abc import Sequence
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy import delete as sa_delete
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.db.base import Base


class BaseRepository[ModelT: Base]:
    def __init__(self, session: AsyncSession, model_cls: type[ModelT]) -> None:
        self._session = session
        self._model = model_cls

    async def create(self, **kwargs: Any) -> ModelT:
        if "id" not in kwargs:
            kwargs["id"] = uuid.uuid4()
        instance = self._model(**kwargs)
        self._session.add(instance)
        await self._session.commit()
        return instance

    async def get(self, id: str | uuid.UUID) -> ModelT | None:
        pk = uuid.UUID(id) if isinstance(id, str) else id
        return await self._session.get(self._model, pk)

    async def list(self, **filters: Any) -> Sequence[ModelT]:
        stmt: Select = select(self._model)
        for col, val in filters.items():
            if hasattr(self._model, col):
                stmt = stmt.where(getattr(self._model, col) == val)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def update(self, id: str | uuid.UUID, **kwargs: Any) -> ModelT | None:
        pk = uuid.UUID(id) if isinstance(id, str) else id
        stmt = (
            sa_update(self._model)
            .where(self._model.id == pk)
            .values(**kwargs)
            .returning(self._model)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalar_one_or_none()

    async def delete(self, id: str | uuid.UUID) -> bool:
        pk = uuid.UUID(id) if isinstance(id, str) else id
        stmt = sa_delete(self._model).where(self._model.id == pk)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount > 0
