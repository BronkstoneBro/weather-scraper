from typing import Optional
from src.models.location import Location


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
    """Get BBC Weather location ID by location name"""
    return COMMON_LOCATIONS.get(location_name.lower())


def get_location(location_name: str) -> Optional[Location]:
    """Get Location object by location name"""
    location_id = get_location_id(location_name)
    if location_id:
        return Location(
            location_id=location_id,
            name=location_name.title(),
            country="United Kingdom",
        )
    return None
