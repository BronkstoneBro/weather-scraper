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


COMMON_LOCATIONS = {
    "london": "2643743",
    "manchester": "2643123",
    "birmingham": "2655603",
    "edinburgh": "2650225",
    "glasgow": "2648579",
    "cardiff": "2653822",
    "liverpool": "2644210",
    "bristol": "2654675",
    "leeds": "2644688",
    "sheffield": "2638077",
}


def get_location_id(location_name: str) -> Optional[str]:
    return COMMON_LOCATIONS.get(location_name.lower())


def get_location(location_name: str) -> Optional[Location]:
    location_id = get_location_id(location_name)
    if location_id:
        return Location(
            location_id=location_id,
            name=location_name.title(),
            country="United Kingdom",
        )
    return None
