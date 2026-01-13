# app/schemas.py
from pydantic import BaseModel, HttpUrl

class OpenDoorCommand(BaseModel):
    action: str = "OPEN_DOOR"

class GoogleSheetRequest(BaseModel):
    sheet_url: HttpUrl