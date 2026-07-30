__anchor__ = "models"
# schema-ref: project-schema.yaml#/shared_modules/5

from uuid import UUID, uuid4


def new_id() -> UUID:
    return uuid4()
