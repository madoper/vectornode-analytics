__anchor__ = "repositories"

from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.models.orm.models import (
    AuthUserModel,
    DocCheckJobModel,
    DraftModel,
    InternalDocumentModel,
)
from backend.shared.repositories.base import BaseRepository


class DocCheckJobRepository(BaseRepository[DocCheckJobModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DocCheckJobModel)


class InternalDocumentRepository(BaseRepository[InternalDocumentModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, InternalDocumentModel)


class AuthUserRepository(BaseRepository[AuthUserModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AuthUserModel)


class DraftRepository(BaseRepository[DraftModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DraftModel)
