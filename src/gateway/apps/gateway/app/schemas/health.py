__anchor__ = "gateway"
# schema-ref: project-schema.yaml#/services/0

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str = "0.5.0"
    anchor: str = "gateway"
