from pydantic import BaseModel, HttpUrl

class OpenDoorCommand(BaseModel):
    action: str = "OPEN_DOOR"

