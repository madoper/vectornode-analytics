__anchor__ = "events"
# schema-ref: project-schema.yaml#/shared_modules/6

import json
from uuid import UUID

from sqlalchemy import text

from backend.shared.db.postgres import async_session_factory


class OutboxWriter:
    @staticmethod
    async def write(
        event_id: UUID, event_type: str, aggregate_id: str, payload: dict[str, object]
    ) -> None:
        async with async_session_factory() as session:
            await session.execute(
                text("""
                    INSERT INTO outbox_events (id, event_type, aggregate_id, payload)
                    VALUES (:id, :event_type, :aggregate_id, :payload)
                """),
                {
                    "id": event_id,
                    "event_type": event_type,
                    "aggregate_id": aggregate_id,
                    "payload": json.dumps(payload),
                },
            )
            await session.commit()
