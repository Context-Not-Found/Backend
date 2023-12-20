from pydantic import BaseModel, Field


class SOSBase(BaseModel):
    lat: float = Field(title="Latitude", description="Latitude from the ticket report")
    long: float = Field(
        title="Longitude", description="Longitude from the ticket report"
    )


class SOSCreate(SOSBase):
    pass


class SOS(SOSBase):
    user_id: int = Field(title="User ID", description="User ID of the User")
    sos_id: int = Field(title="SOS ID", description="Generated SOS ID")
    is_open: bool = Field(description="If SOS is Open or not")
