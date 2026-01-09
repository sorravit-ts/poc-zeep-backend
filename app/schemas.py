# app/schemas.py
from pydantic import BaseModel

class OpenDoorCommand(BaseModel):
    action: str = "OPEN_DOOR"
