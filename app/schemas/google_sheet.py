from pydantic import BaseModel, HttpUrl

class GoogleSheetRequest(BaseModel):
    sheet_url: HttpUrl