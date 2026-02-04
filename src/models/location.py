from typing import Optional
from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    """Geographic coordinates"""

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class Location(BaseModel):
    """Location information for weather queries"""

    location_id: str = Field(..., description="BBC Weather location ID")
    name: str = Field(..., description="Location name (e.g., 'London')")
    country: Optional[str] = Field(None, description="Country name")
    coordinates: Optional[Coordinates] = None

    class Config:
        populate_by_name = True
