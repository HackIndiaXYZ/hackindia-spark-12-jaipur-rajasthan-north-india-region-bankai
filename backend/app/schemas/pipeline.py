from pydantic import BaseModel, Field

class PipelineSegmentBase(BaseModel):
    segment_id: str = Field(..., json_schema_extra={"example": "B2-B3"})
    source_node: str = Field(..., json_schema_extra={"example": "B2"})
    destination_node: str = Field(..., json_schema_extra={"example": "B3"})
    zone_id: str = Field(..., json_schema_extra={"example": "Zone_B"})
    length_m: float = Field(..., json_schema_extra={"example": 220.0})
    nominal_min_flow: float = Field(50.0, json_schema_extra={"example": 70.0})
    nominal_max_flow: float = Field(150.0, json_schema_extra={"example": 180.0})
    nominal_min_pressure: float = Field(3.0, json_schema_extra={"example": 3.8})
    nominal_max_pressure: float = Field(5.0, json_schema_extra={"example": 4.8})

class PipelineSegmentCreate(PipelineSegmentBase):
    pass

class PipelineSegmentSchema(PipelineSegmentBase):
    model_config = {"from_attributes": True}
