from pydantic import BaseModel, Field
from typing import List


class Markers(BaseModel):
    class Area(BaseModel):
        class Center(BaseModel):
            latitude: float = Field(
                title="Latitude", description="Latitude from the report"
            )
            longitude: float = Field(
                title="Longitude", description="Longitude from the report"
            )

        center: Center = Field(title="Center", description="Coordinates from report")
        radius: int = Field(
            title="Radius", description="Radius representing itensity of situation"
        )

    markers: List[Area]
