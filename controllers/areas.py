from math import atan2, cos, radians, sin, sqrt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import sos


async def get_areas(db: Session):
    coords = sos.get_all_coords(db)
    return _group_points(coords)


# Helper functions to Calculate markers
async def _distance(lat1, lon1, lat2, lon2):
    # Calculate the Haversine distance between two points on the earth
    R = 6371.0  # radius of the Earth in kilometers

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


async def _group_points(points, threshold=0.2):  # Reduced threshold
    groups = []

    for point in points:
        added_to_group = False
        for group in groups:
            center = group["center"]
            if (
                await _distance(
                    point["latitude"],
                    point["longitude"],
                    center["latitude"],
                    center["longitude"],
                )
                <= threshold
            ):
                group["points"].append(point)
                group["center"]["latitude"] = sum(
                    p["latitude"] for p in group["points"]
                ) / len(group["points"])
                group["center"]["longitude"] = sum(
                    p["longitude"] for p in group["points"]
                ) / len(group["points"])
                added_to_group = True
                break

        if not added_to_group:
            groups.append({"center": point.copy(), "points": [point]})

    return [
        {"center": group["center"], "radius": min(2 * len(group["points"]), 40)}
        for group in groups
    ]
