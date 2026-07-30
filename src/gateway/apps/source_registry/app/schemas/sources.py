__anchor__ = "source-registry"
# schema-ref: project-schema.yaml#/services/2

from pydantic import BaseModel


class SourceDomainResponse(BaseModel):
    id: str
    domain: str
    source_type: str
    regulator_name: str
    tier: int
    is_active: bool
    anchor: str = "source-registry"


class CreateSourceRequest(BaseModel):
    domain: str
    source_type: str
    regulator_name: str
    tier: int = 1
    is_active: bool = True


class UpdateSourceRequest(BaseModel):
    domain: str | None = None
    source_type: str | None = None
    regulator_name: str | None = None
    tier: int | None = None
    is_active: bool | None = None
